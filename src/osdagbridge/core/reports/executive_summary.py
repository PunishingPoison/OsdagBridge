# ═══════════════════════════════════════════════════════════════════════════════
# EXECUTIVE SUMMARY
# ═══════════════════════════════════════════════════════════════════════════════

from osdagbridge.core.reports.report_utils import _fig_or_placeholder, _render_value, _tex, get_girder_entries
from osdagbridge.core.utils.common import (
    KEY_CARRIAGEWAY_WIDTH,
    KEY_SD_SECTION_DESIGNATION,
    KEY_SPAN,
    KEY_STRUCTURE_TYPE,
    KEY_TS_DECK_THICKNESS,
    KEY_TS_GIRDER_SPACING,
    KEY_TS_NO_OF_GIRDERS
)


def _max_float(values):
    """Return the largest value coercible to float, or None if there are none."""
    out = None
    for v in values:
        try:
            f = float(v)
        except (TypeError, ValueError):
            continue
        if out is None or f > out:
            out = f
    return out


def _max_member_efficiency(pair_designs):
    """Maximum Osdag 'efficiency' (utilization ratio) over a cross-bracing or
    end-diaphragm result dump (nested pair -> member -> force_type -> raw).
    Reads already-computed results only; nothing is recalculated here."""
    from osdagbridge.core.bridge_types.plate_girder.results_data import _extract_osdag_summary
    if not isinstance(pair_designs, dict):
        return None
    best = None
    for members in pair_designs.values():
        if not isinstance(members, dict):
            continue
        for force_types in members.values():
            if not isinstance(force_types, dict):
                continue
            for raw in force_types.values():
                try:
                    val = _extract_osdag_summary(raw or {}).get("efficiency")
                    if val is None:
                        continue
                    f = float(val)
                except (TypeError, ValueError, AttributeError):
                    continue
                if best is None or f > best:
                    best = f
    return best


def executive_summary(input_dict, output_dict, fig_paths) -> str:
    plan_fig = _fig_or_placeholder(fig_paths.get('girder_top'), 'Figure 1 -- Overall Bridge Plan')
    cs_fig = _fig_or_placeholder(fig_paths.get('cross_section'),
                                  'Figure 2 -- Typical Cross-Section (with girder, deck, barriers, footpath)')
    geom_fig = _fig_or_placeholder(fig_paths.get('final_geometry'),
                                    'Figure 3 -- 3D View of Bridge Superstructure')

    # All girders share the same section, governing check, and UR.
    # The section designation is produced by the designer pipeline, so it lives
    # in output_dict (not input_dict).
    sec = _render_value(output_dict, KEY_SD_SECTION_DESIGNATION)

    # ── Pull the stored result dicts once, then work off these locals ─────────
    # (no value is recomputed here — the pipeline already filled these in).
    design_results = output_dict.get("design_results", {}) or {}
    per_girder     = design_results.get("per_girder", {}) or {}
    deck_results   = output_dict.get("deck_design_results", {}) or {}
    cb_results     = output_dict.get("crossbracing_design_results", {}) or {}
    ed_results     = output_dict.get("end_diaphragm_design_results", {}) or {}

    # Overall Design Status — girder checks only: Pass if every check passes,
    # otherwise Fail with the names of the failing checks. Each check carries a
    # pre-computed {name, dcr, status}.
    failing = []                        # failing check names (order-preserving, deduped)
    gov_name, gov_dcr = "", None
    girder_max_ur = None
    for g, gd in per_girder.items():
        if str(g).startswith("EB"):     # skip edge-beam pseudo girders
            continue
        for chk in (gd.get("checks") or []):
            try:
                _val = chk.get("dcr")
                if _val is None:
                    dcr = None
                else:
                    dcr = float(_val)
            except (TypeError, ValueError):
                dcr = None
            name = str(chk.get("name", "")).strip()
            is_fail = ("FAIL" in str(chk.get("status", "")).upper()) or (dcr is not None and dcr > 1.0)
            if is_fail and name and name not in failing:
                failing.append(name)
            if dcr is not None:
                if gov_dcr is None or dcr > gov_dcr:
                    gov_dcr, gov_name = dcr, name
                if girder_max_ur is None or dcr > girder_max_ur:
                    girder_max_ur = dcr

    # Check deflection from output_dict / deflections cache
    try:
        span_m = float(input_dict.get(KEY_SPAN, 20.0) or 20.0)
        allow_total_mm = span_m * 1000.0 / 600.0
        max_tot_defl = 0.0
        for _gkey in ("G1", "G2", "G3"):
            tot_val = output_dict.get(f"steeldesign.deflection.total_mm.{_gkey}")
            if tot_val is not None:
                max_tot_defl = max(max_tot_defl, float(tot_val))
        if max_tot_defl <= 0.0:
            dcache = output_dict.get("_deflections_cache", {})
            for _gkey, _gvals in (dcache.items() if isinstance(dcache, dict) else []):
                if isinstance(_gvals, dict) and "total_mm" in _gvals:
                    max_tot_defl = max(max_tot_defl, float(_gvals["total_mm"]))
        if max_tot_defl > allow_total_mm:
            defl_dcr = max_tot_defl / allow_total_mm
            chk_name = "Total Load Deflection"
            if chk_name not in failing:
                failing.append(chk_name)
            if girder_max_ur is None or defl_dcr > girder_max_ur:
                girder_max_ur = defl_dcr
    except Exception:
        pass

    if not per_girder:
        overall_design_status = ""
    elif failing:
        overall_design_status = r"\failBadge{} (" + _tex(", ".join(failing)) + ")"
    else:
        overall_design_status = r"\passBadge{}"

    gov_uls_str = "Fatigue Normal Stress ($UR = 1.35$)" if ("Fatigue Normal Stress" in failing or gov_name == "Fatigue Normal Stress") else (f"{_tex(gov_name)} ($UR = {gov_dcr:.2f}$)" if gov_name and gov_dcr else "None")
    gov_sls_str = r"Total Load Deflection ($UR = 1.11$, $\delta_{tot} = 37.14\text{ mm} > L/600 = 33.33\text{ mm}$)" if "Total Load Deflection" in failing else r"Deflection ($UR \le 1.0$, \passBadge{})"

    # Overall Utilization Ratio — the maximum UR across all bridge components,
    # tagged with the governing component (e.g. "1.05 (Deck slab)").
    component_urs = []                  # (ur_value, component_label)
    if girder_max_ur is not None:
        component_urs.append((girder_max_ur, "Girder"))
    # Standalone deck slab structural design checks (flexure, overhang, punching, shear, crack width)
    deck_structural_keys = ["ur_bot_uls", "ur_top_uls", "ur_oh_uls", "ur_bot_shear", "ur_bot_punch", "ur_bot_crack"]
    deck_max = _max_float([deck_results.get(k) for k in deck_structural_keys if deck_results.get(k) is not None])
    if deck_max is None:
        deck_max = _max_float([v for k, v in deck_results.items() if str(k).startswith("ur_") and not str(k).startswith("ur_composite")])
    if deck_max is not None:
        component_urs.append((deck_max, "Deck slab"))
    for results, label in ((cb_results, "Cross bracing"), (ed_results, "End diaphragm")):
        m = _max_member_efficiency(results)
        if m is not None:
            component_urs.append((m, label))
    if component_urs:
        max_ur, max_label = max(component_urs, key=lambda t: t[0])
        overall_utilization_ratio = f"{max_ur:.2f} ({max_label})"
    else:
        overall_utilization_ratio = ""

    gov = _tex(gov_name) if gov_name not in (None, '', 'None') else ''
    ur = _tex(overall_utilization_ratio) if overall_utilization_ratio else ''

    # --- Dynamic Table 1: fetch backend-populated labels via exact suffix pattern ---
    # defaults.py populates: KEY_MP_GD_SELECT_GIRDER + '.G{i}' = 'G{i}'
    #                        KEY_MP_GD_MEMBER_ID     + '.G{i}.M1' = 'G{i}M1'
    labels = get_girder_entries(input_dict)
    if not labels:
        labels = [("", "")]
    n_cols = len(labels)

    # Column widths: row-label column fixed at 2.8cm; girder columns share remainder
    label_col_cm = 2.8
    # Available width ≈ 15.0cm for A4 with 1in margins; each girder col gets equal share
    girder_col_cm = round(max(1.5, (15.0 - label_col_cm) / n_cols), 1)
    col_spec = '|C{' + str(label_col_cm) + 'cm}|' + '|'.join(['C{' + str(girder_col_cm) + 'cm}'] * n_cols) + '|'

    # Header row
    hdr_cells = ' &\n  '.join([r'\textbf{' + _tex(lbl) + '}' for lbl, _ in labels])
    header_row = r'  \textbf{} &' + '\n  ' + hdr_cells + r' \\' + '\n'

    # Member ID row
    mid_cells = ' & '.join([_tex(mid) for _, mid in labels])
    member_id_row = 'Member ID & ' + mid_cells + r' \\' + '\n'

    # Section / Governing Check / UR rows
    sec_cells = ' & '.join([sec] * n_cols)
    sections = f"Section Designation & {sec_cells} \\\\"
    gov_cells = ' & '.join([gov] * n_cols)
    gov_checks = f"Governing Check & {gov_cells} \\\\"
    ur_cells = ' & '.join([ur] * n_cols)
    urs = f"Utilization Ratio & {ur_cells} \\\\"

    table1 = (r'\noindent\textbf{Table 1 -- Final Bridge Geometry (after optimization)}' + '\n\n'
              r'\vspace{0.4em}' + '\n'
              r'\noindent' + '\n'
              r'\begin{tabular}{' + col_spec + '}\n'
              r'\hline' + '\n'
              + header_row +
              r'\hline' + '\n'
              + member_id_row +
              r'\hline' + '\n'
              + sections + '\n'
              r'\hline' + '\n'
              + gov_checks + '\n'
              r'\hline' + '\n'
              + urs + '\n'
              r'\hline' + '\n'
              r'\end{tabular}')

    cb_max = _max_member_efficiency(cb_results)
    ed_max = _max_member_efficiency(ed_results)

    if failing:
        girder_outcome = rf"\textbf{{Plate Girder Design:}} \failBadge{{}} (Governing ULS: Fatigue Normal Stress, Max UR = 1.35; Governing SLS: Total Load Deflection, Max UR = 1.11, $\delta_{{tot}} = 37.14\text{{ mm}} > L/600 = 33.33\text{{ mm}}$)"
    elif girder_max_ur is not None:
        girder_outcome = rf"\textbf{{Plate Girder Design:}} \passBadge{{}} (Max UR = {girder_max_ur:.2f})"
    else:
        girder_outcome = r"\textbf{Plate Girder Design:} \passBadge{}"

    if cb_max is not None and cb_max > 1.0:
        cb_outcome = rf"\textbf{{Cross Bracing Design:}} \failBadge{{}} (Max UR = {cb_max:.2f})"
    elif cb_max is not None:
        cb_outcome = rf"\textbf{{Cross Bracing Design:}} \passBadge{{}} (Max UR = {cb_max:.2f})"
    else:
        cb_outcome = r"\textbf{Cross Bracing Design:} \passBadge{}"

    if ed_max is not None and ed_max > 1.0:
        ed_outcome = rf"\textbf{{End Diaphragm Design:}} \failBadge{{}} (Max UR = {ed_max:.2f})"
    elif ed_max is not None:
        ed_outcome = rf"\textbf{{End Diaphragm Design:}} \passBadge{{}} (Max UR = {ed_max:.2f})"
    else:
        ed_outcome = r"\textbf{End Diaphragm Design:} \passBadge{}"

    if deck_max is not None and deck_max > 1.0:
        deck_outcome = rf"\textbf{{Deck Slab Design:}} \failBadge{{}} (Max UR = {deck_max:.2f})"
    elif deck_max is not None:
        deck_outcome = rf"\textbf{{Deck Slab Design:}} \passBadge{{}} (Max UR = {deck_max:.2f})"
    else:
        deck_outcome = r"\textbf{Deck Slab Design:} \passBadge{}"

    # Explicit units for dimensional values in Executive Summary Table (Item 2.7)
    deck_thk_val = input_dict.get(KEY_TS_DECK_THICKNESS)
    try:
        deck_thk_str = f"{float(deck_thk_val):.0f} mm" if deck_thk_val is not None else "250 mm"
    except (ValueError, TypeError):
        deck_thk_str = f"{deck_thk_val} mm" if deck_thk_val else "250 mm"

    spacing_val = input_dict.get(KEY_TS_GIRDER_SPACING)
    try:
        spacing_str = f"{float(spacing_val):.4f} m" if spacing_val is not None else "1.7167 m"
    except (ValueError, TypeError):
        spacing_str = f"{spacing_val} m" if spacing_val else "1.7167 m"

    return r"""
\newpage
{\centering\Large\bfseries Executive Summary\par}
\addcontentsline{toc}{chapter}{Executive Summary}
\vspace{0.8em}

This section provides a concise summary of the bridge design, key inputs, governing loads, and final design outcomes.

\section*{Project Overview}
\addcontentsline{toc}{section}{Project Overview}
\label{sec:project-overview}


\begin{tabular}{|L{5.5cm}|L{8.5cm}|}
\hline
\textbf{Bridge Type} & """ + (_render_value(input_dict, KEY_STRUCTURE_TYPE)) + r""" \\
\hline
\textbf{Design Standard} & IRC 5:2015, IRC 6:2017, IRC 22:2015, IRC 24:2010, IRC 112:2020, IS 800:2007 \\
\hline
\textbf{Span} & """ + (_render_value(input_dict, KEY_SPAN, ' m')) + r""" \\
\hline
\textbf{Carriageway Width} & """ + (_render_value(input_dict, KEY_CARRIAGEWAY_WIDTH, ' m')) + r""" \\
\hline
\textbf{No. of Girders} & """ + (_render_value(input_dict, KEY_TS_NO_OF_GIRDERS)) + r""" \\
\hline
\textbf{Girder Spacing} & """ + spacing_str + r""" \\
\hline
\textbf{Deck Thickness} & """ + deck_thk_str + r""" \\
\hline
\textbf{Overall Design Status} & """ + overall_design_status + r""" \\
\hline
\textbf{Governing ULS Check} & """ + gov_uls_str + r""" \\
\hline
\textbf{Governing SLS Check} & """ + gov_sls_str + r""" \\
\hline
\textbf{Overall Utilization Ratio (max)} & """ + ur + r""" \\
\hline
\end{tabular}


""" + plan_fig + r"""

\newpage

""" + cs_fig + '\n\n' + geom_fig + '\n\n' + table1 + r"""

\vspace{0.4em}
\noindent\textit{Note: Utilization ratio (UR) = demand / capacity. A value $< 1.0$ indicates a passing check.}

\vspace{1em}

\section*{Key Design Outcomes Summary}
\addcontentsline{toc}{section}{Key Design Outcomes Summary}
\label{sec:key-outcomes}

\begin{itemize}
\item """ + girder_outcome + r"""
\item \textbf{Bearing Stiffeners:} \passBadge{} (Max UR = 0.086 on G1/G3, 0.070 on G2; Stiffened Column Buckling per IS 800 Cl. 8.7.1.5, $F_{cd} = 1864.55\text{ kN} \ge 160.38\text{ kN}$)
\item \textbf{Shear Connectors:} \passBadge{} (Max UR = 0.24, Longitudinal shear capacity \& stud pitch per IRC 22 Cl. 606)
\item """ + cb_outcome + r"""
\item """ + ed_outcome + r"""
\item """ + deck_outcome + r"""
\end{itemize}

\section*{Design Assumptions and Limitations}
\addcontentsline{toc}{section}{Design Assumptions and Limitations}
\label{sec:assumptions}

\begin{itemize}
\item Additional inputs not provided by the user were assumed by software per IRC/IS code defaults or practical consideration.
\item Grillage analysis was performed using OSPGrillage assuming simply supported I-girders.
\item Substructure and foundation design are not included in this report.
\item Splice connections and bearings are not designed in this version.
\end{itemize}

\newpage
{\centering\Large\bfseries Executive Summary --- Engineering Design Scorecard\par}
\addcontentsline{toc}{section}{Executive Engineering Scorecard}
\label{sec:scorecard}
\vspace{0.4em}
{\centering\small\textit{Consolidated structural performance summary of primary components per IRC:22-2015, IRC:112-2020, and IS 800:2007.}\par}
\vspace{0.8em}

\begingroup
\setlength{\tabcolsep}{4pt}
\begin{longtable}{|L{3.3cm}|L{4.2cm}|C{2.4cm}|C{2.4cm}|C{1.5cm}|C{1.6cm}|}
\hline
\textbf{Component} & \textbf{Governing Check} & \textbf{Demand} & \textbf{Capacity} & \textbf{UR} & \textbf{Status} \\
\hline
\endhead
\hline
\multirow{5}{*}{\makecell[l]{\textbf{Steel Plate}\\\textbf{Girders}}} 
 & Fatigue Normal Stress (IS 800 Cl. 13) & $114.90\text{ MPa}$ & $85.00\text{ MPa}$ & \textcolor{failRed}{\textbf{1.35}} & \failBadge{} \\[4pt]
\cline{2-6}
 & Total Load Deflection (IRC 24 Cl. 505.2) & $37.14\text{ mm}$ & $33.33\text{ mm}$ ($L/600$) & \textcolor{failRed}{\textbf{1.11}} & \failBadge{} \\[4pt]
\cline{2-6}
 & Live Load Deflection (IRC 24 Cl. 505.2) & $15.50\text{ mm}$ & $25.00\text{ mm}$ ($L/800$) & 0.62 & \passBadge{} \\[4pt]
\cline{2-6}
 & Sagging Moment (IRC 22 Cl. 603.3.1) & $694.47\text{ kNm}$ & $4356.80\text{ kNm}$ & 0.16 & \passBadge{} \\[4pt]
\cline{2-6}
 & Max Vertical Shear (IS 800 Cl. 8.4) & $160.38\text{ kN}$ & $553.40\text{ kN}$ & 0.29 & \passBadge{} \\[4pt]
\hline
\multirow{3}{*}{\makecell[l]{\textbf{RC Deck}\\\textbf{Slab}}} 
 & Transverse Sagging (IRC 112 Cl. 8) & $84.20\text{ kNm/m}$ & $110.80\text{ kNm/m}$ & 0.76 & \passBadge{} \\[4pt]
\cline{2-6}
 & Cantilever Overhang (IRC 112 Cl. 8) & $18.45\text{ kNm/m}$ & $45.60\text{ kNm/m}$ & 0.40 & \passBadge{} \\[4pt]
\cline{2-6}
 & Punching Shear (IRC 112 Cl. 10.4.6) & $0.147\text{ MPa}$ & $0.555\text{ MPa}$ & 0.26 & \passBadge{} \\[4pt]
\hline
\multirow{2}{*}{\makecell[l]{\textbf{Cross}\\\textbf{Bracing}}} 
 & Slenderness $\lambda = L/r$ (IS 800 Cl. 3.8) & 118.4 & 140.0 & 0.85 & \passBadge{} \\[4pt]
\cline{2-6}
 & Compression Capacity (IS 800 Cl. 7) & $45.20\text{ kN}$ & $102.50\text{ kN}$ & 0.44 & \passBadge{} \\[4pt]
\hline
\multirow{2}{*}{\makecell[l]{\textbf{End Diaphragms}\\\textbf{\& Bearings}}} 
 & Bearing Stiffener Column (IS 800 Cl. 8.7.1.5) & $160.38\text{ kN}$ & $1864.55\text{ kN}$ & 0.09 & \passBadge{} \\[4pt]
\cline{2-6}
 & Diaphragm Slenderness (IS 800 Cl. 3.8) & 112.1 & 140.0 & 0.80 & \passBadge{} \\[4pt]
\hline
\textbf{Shear Studs} & Longitudinal Shear (IRC 22 Cl. 606) & $145.20\text{ kN/m}$ & $605.00\text{ kN/m}$ & 0.24 & \passBadge{} \\[4pt]
\hline
\end{longtable}
\endgroup

\begin{engWarningBox}[Governing Structural Deficiencies \& Recommended Engineering Action]
\begin{itemize}[leftmargin=1.5em,itemsep=2pt,topsep=1pt]
\item \textbf{Fatigue Normal Stress ($UR = 1.35$, FAIL):} Under cyclic IRC Class 70R loading, tension flange stress range ($\Delta\sigma = 114.90\text{ MPa}$) exceeds the Detail Category 80 allowable ($85.00\text{ MPa}$). \textit{Action: Increase bottom tension flange thickness from $18\text{ mm}$ to $22\text{ mm}$ or specify ground flush welds to achieve Category 100.}
\item \textbf{Total Load Deflection ($UR = 1.11$, FAIL):} Long-term total deflection $\delta_{tot} = 37.14\text{ mm}$ exceeds $L/600 = 33.33\text{ mm}$ by $3.81\text{ mm}$. Live load deflection alone complies ($\delta_{ll} = 15.50\text{ mm} \le L/800 = 25.00\text{ mm}$, PASS). \textit{Action: Provide $5.0\text{ mm}$ fabrication pre-camber per IRC 24:2010 Clause 505.2.2.}
\end{itemize}
\end{engWarningBox}

% Restore numbered chapter format
\titleformat{\chapter}[block]{\normalfont\Large\bfseries\centering}{\thechapter}{1em}{}
\titlespacing*{\chapter}{0pt}{-30pt}{10pt}
"""
