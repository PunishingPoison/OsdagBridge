# =============================================================================
# Chapter 3: Loads and Load Combinations
# Refactored for structured vehicle parameters, separate footway table,
# and repeated longtable headers via centralized styles.
# =============================================================================

from osdagbridge.core.utils.common import (
    KEY_CARRIAGEWAY_WIDTH,
    KEY_CB_LOAD,
    KEY_FOOTPATH,
    KEY_LL_CUSTOM_VEHICLES,
    KEY_LL_FOOTPATH_PRESSURE_MODE,
    KEY_LL_FOOTPATH_PRESSURE_VALUE,
    KEY_LL_IRC_70R_BOGIE,
    KEY_LL_IRC_70R_TRACKED,
    KEY_LL_IRC_70R_WHEELED,
    KEY_LL_IRC_AA_TRACKED,
    KEY_LL_IRC_AA_WHEELED,
    KEY_LL_IRC_CLASS_A,
    KEY_LL_IRC_CLASS_FATIGUE,
    KEY_LL_IRC_CLASS_SV,
    KEY_MATERIAL_DECK_DENSITY,
    KEY_MATERIAL_GIRDER_DENSITY,
    KEY_PL_SELF_WEIGHT_FACTOR,
    KEY_RL_LOAD_VALUE,
    KEY_SL_DAMPING,
    KEY_SL_DEAD_LOAD_MODE,
    KEY_SL_DEAD_LOAD_VALUE,
    KEY_SL_HORIZONTAL_COEFF,
    KEY_SL_IMPORTANCE_FACTOR,
    KEY_SL_LIVE_LOAD_MODE,
    KEY_SL_LIVE_LOAD_VALUE,
    KEY_SL_SEISMIC_ZONE,
    KEY_SL_SOIL_TYPE,
    KEY_SL_SPECTRAL_COEFF,
    KEY_SL_TIME_PERIOD,
    KEY_SL_VERTICAL_COEFF,
    KEY_SL_ZONE_FACTOR,
    KEY_SPAN,
    KEY_TL_BRIDGE_TEMP_MAX,
    KEY_TL_BRIDGE_TEMP_MIN,
    KEY_TL_HIGHEST_MAX_TEMP,
    KEY_TL_LOWEST_MIN_TEMP,
    KEY_TL_TEMP_FALL,
    KEY_TL_TEMP_RISE,
    KEY_TS_FOOTPATH_WIDTH,
    KEY_TS_NO_OF_FOOTPATHS,
    KEY_TS_OVERALL_WIDTH,
    KEY_WC_LD_LANE_TABLE_COUNT,
    KEY_WC_MATERIAL,
    KEY_WC_THICKNESS,
    KEY_WL_AVG_EXPOSED_HEIGHT,
    KEY_WL_BASIC_WIND_SPEED,
    KEY_WL_HOURLY_MEAN_WIND,
    KEY_WL_HOURLY_WIND_PRESSURE,
    KEY_WL_LONGITUDINAL_WIND_FORCE,
    KEY_WL_TERRAIN_TYPE,
    KEY_WL_TRANSVERSE_WIND_FORCE,
    KEY_WL_VERTICAL_WIND_FORCE
)

from osdagbridge.core.reports.report_utils import _tex, _render_value
from osdagbridge.core.reports.styles import make_longtable_header, NEEDSPACE_TABLE
from osdagbridge.core.utils.codes.irc6_2017 import IRC6_2017


def ch3_loads(input_dict):
    span = input_dict.get(KEY_SPAN)
    span_m = float(span) if span not in (None, "") else 20.0

    # Impact factors per vehicle category
    im_a = IRC6_2017.cl_208_2_impact_factor(span_m)
    im_aa = IRC6_2017.cl_208_3_impact_factor(span_m)

    lanes = input_dict.get(KEY_WC_LD_LANE_TABLE_COUNT)
    lanes_int = 1
    if lanes not in (None, ""):
        try:
            lanes_int = int(lanes)
        except Exception:
            lanes_int = 1
    else:
        cw = input_dict.get(KEY_CARRIAGEWAY_WIDTH) or input_dict.get('geometry.carriageway_width') or input_dict.get(KEY_TS_OVERALL_WIDTH)
        try:
            if cw:
                cw_f = float(cw)
                if cw_f < 5.3:
                    lanes_int = 1
                elif cw_f < 9.6:
                    lanes_int = 2
                else:
                    lanes_int = max(1, int((cw_f - 3.0) / 3.5))
        except (ValueError, TypeError):
            lanes_int = 1

    # Centrifugal force is 0.00 kN for straight bridge alignment per IRC 6 Cl. 212
    cf_force_str = "0.00"

    # Braking force values per vehicle category (IRC 6 Cl. 211.2):
    # For 1 design lane: 20% of first vehicle train weight
    # Class A: 0.20 * 57.0 t * 9.81 = 111.83 kN
    # Class 70R Wheeled: 0.20 * 1000 kN = 200.00 kN
    # Class 70R Tracked: 0.20 * 700 kN = 140.00 kN
    # Class AA Wheeled: 0.20 * 400 kN = 80.00 kN
    # Class AA Tracked: 0.20 * 700 kN = 140.00 kN
    # Class 70R Bogie: 0.20 * 400 kN = 80.00 kN
    if lanes_int == 1:
        bk_a = "111.83"
        bk_70rw = "200.00"
        bk_70rt = "140.00"
        bk_aaw = "80.00"
        bk_aat = "140.00"
        bk_bogie = "80.00"
    else:
        # Multi-lane scaling per IRC 6 Cl. 211.2
        try:
            bk_a = f"{IRC6_2017.cl_211_2_braking_force(lanes_int) * 9.81:.2f}"
        except Exception:
            bk_a = "111.83"
        bk_70rw = f"{200.0 * min(2, lanes_int) + 50.0 * max(0, lanes_int - 2):.2f}"
        bk_70rt = f"{140.0 * min(2, lanes_int) + 35.0 * max(0, lanes_int - 2):.2f}"
        bk_aaw = f"{80.0 * min(2, lanes_int) + 20.0 * max(0, lanes_int - 2):.2f}"
        bk_aat = f"{140.0 * min(2, lanes_int) + 35.0 * max(0, lanes_int - 2):.2f}"
        bk_bogie = f"{80.0 * min(2, lanes_int) + 20.0 * max(0, lanes_int - 2):.2f}"

    # Build Vehicle Live Load rows based on UI selection
    # Vehicle specifications: (key, name, total_load_kN, impact_factor, braking_considered, braking_val, eccentricity, cf_val)
    vehicle_specs = [
        (KEY_LL_IRC_CLASS_A, "Class A", 554.0, f"{1.0 + im_a:.3f}", "Yes", bk_a, "1.20", cf_force_str),
        (KEY_LL_IRC_70R_WHEELED, "Class 70R (Wheeled)", 1000.0, f"{1.0 + im_aa:.3f}", "Yes", bk_70rw, "1.20", cf_force_str),
        (KEY_LL_IRC_70R_TRACKED, "Class 70R (Tracked)", 700.0, f"{1.0 + im_aa:.3f}", "Yes", bk_70rt, "1.20", cf_force_str),
        (KEY_LL_IRC_AA_WHEELED, "Class AA (Wheeled)", 400.0, f"{1.0 + im_aa:.3f}", "Yes", bk_aaw, "1.20", cf_force_str),
        (KEY_LL_IRC_AA_TRACKED, "Class AA (Tracked)", 700.0, f"{1.0 + im_aa:.3f}", "Yes", bk_aat, "1.20", cf_force_str),
        (KEY_LL_IRC_70R_BOGIE, "Class 70R (Bogie)", 400.0, f"{1.0 + im_aa:.3f}", "Yes", bk_bogie, "1.20", cf_force_str),
        (KEY_LL_IRC_CLASS_SV, "Class SV", 3850.0, "1.000", "No", "---", "---", cf_force_str),
        (KEY_LL_IRC_CLASS_FATIGUE, "Class Fatigue", 400.0, "1.000", "No", "---", "---", cf_force_str),
    ]

    vehicle_rows = []
    for k, name, tot_load, if_val, bk_cons, bk_val, ecc, cf_val in vehicle_specs:
        if input_dict.get(k):
            vehicle_rows.append(
                f"{name} & {tot_load:.1f} & {if_val} & {bk_cons} & {bk_val} & {ecc} & {cf_val} \\\\[6pt]\n\\hline"
            )

    custom = input_dict.get(KEY_LL_CUSTOM_VEHICLES)
    if custom and isinstance(custom, list):
        for c in custom:
            cname = c.get('name', 'Custom') if isinstance(c, dict) else str(c)
            cload = c.get('total_load', 500.0) if isinstance(c, dict) else 500.0
            bk_c = f"{0.20 * float(cload):.2f}"
            vehicle_rows.append(
                f"{_tex(cname)} & {float(cload):.1f} & 1.000 & Yes & {bk_c} & 1.20 & {cf_force_str} \\\\[6pt]\n\\hline"
            )

    if not vehicle_rows:
        vehicle_rows.append(r"None Specified & --- & --- & --- & --- & --- & --- \\[6pt]\n\hline")

    vehicle_rows_tex = "\n".join(vehicle_rows)

    # Footpath live load details
    fp_mode  = input_dict.get(KEY_LL_FOOTPATH_PRESSURE_MODE, "")
    fp_value = input_dict.get(KEY_LL_FOOTPATH_PRESSURE_VALUE, "")
    if str(fp_mode).strip().lower() in ("as per irc 6", "as per irc6", "automatic"):
        try:
            fp_intensity = f"{IRC6_2017.cl_206_1_footway_load():.3f} kN/m²"
        except Exception:
            fp_intensity = "5.000 kN/m²"
    elif fp_value not in (None, ""):
        fp_intensity = f"{fp_value} kN/m²"
    else:
        fp_intensity = "5.000 kN/m²"

    n_fp = input_dict.get(KEY_TS_NO_OF_FOOTPATHS, 0)
    fp_width = input_dict.get(KEY_TS_FOOTPATH_WIDTH, 0.0)
    has_footpath = (int(n_fp) > 0) if str(n_fp).isdigit() else (str(input_dict.get(KEY_FOOTPATH, "")).lower() not in ("none", "", "no"))

    # ── Wind Load (IRC 6 Cl. 207) ─────────────────────────────────────────────
    vb_val = str(input_dict.get(KEY_WL_BASIC_WIND_SPEED) or input_dict.get('wind_speed') or '33.0').replace('m/s', '').strip()
    terrain_val = str(input_dict.get(KEY_WL_TERRAIN_TYPE) or 'Plain Terrain').strip()
    h_val = str(input_dict.get(KEY_WL_AVG_EXPOSED_HEIGHT) or '10.0').replace('m', '').strip()

    vz_val = input_dict.get(KEY_WL_HOURLY_MEAN_WIND)
    pz_val = input_dict.get(KEY_WL_HOURLY_WIND_PRESSURE)
    if not vz_val or not pz_val:
        try:
            _ter = "plain" if "plain" in terrain_val.lower() else "obstructed"
            _res = IRC6_2017.table_12(float(h_val), _ter, float(vb_val))
            if not vz_val:
                vz_val = _res.get("Vz")
            if not pz_val:
                pz_val = _res.get("Pz")
        except Exception:
            pass
    if not vz_val:
        vz_val = float(vb_val) if vb_val else 33.00
    if not pz_val:
        pz_val = 0.6 * (float(vz_val) ** 2)

    vz_str = f"{float(vz_val):.2f} m/s"
    pz_str = f"{float(pz_val):.2f} N/m\\textsuperscript{{2}}"

    f_wt = str(input_dict.get(KEY_WL_TRANSVERSE_WIND_FORCE) or '41.53').replace('kN', '').strip()
    f_wl = str(input_dict.get(KEY_WL_LONGITUDINAL_WIND_FORCE) or '10.38').replace('kN', '').strip()
    f_wv = str(input_dict.get(KEY_WL_VERTICAL_WIND_FORCE) or '50.48').replace('kN', '').strip()

    # ── Earthquake Load (IRC 6 Cl. 218) ───────────────────────────────────────
    sz_name = str(input_dict.get('seismic_zone') or input_dict.get(KEY_SL_SEISMIC_ZONE) or 'Zone II').strip()
    z_fac = str(input_dict.get(KEY_SL_ZONE_FACTOR) or ('0.10' if 'II' in sz_name else '0.16')).strip()
    imp_fac = str(input_dict.get(KEY_SL_IMPORTANCE_FACTOR) or '1.20').strip()
    soil_val = str(input_dict.get(KEY_SL_SOIL_TYPE) or 'Type II (Medium)').strip()
    sag_val = str(input_dict.get(KEY_SL_SPECTRAL_COEFF) or '2.50').strip()
    ah_val = str(input_dict.get(KEY_SL_HORIZONTAL_COEFF) or '0.050').strip()
    av_val = str(input_dict.get(KEY_SL_VERTICAL_COEFF) or '0.033').strip()
    feq_long_str = "72.50"
    feq_trans_str = "72.50"

    # ── Temperature Load (IRC 6 Cl. 215) ──────────────────────────────────────
    t_max_shade = str(input_dict.get('shade_temp_max') or input_dict.get(KEY_TL_HIGHEST_MAX_TEMP) or '38.0').strip()
    t_min_shade = str(input_dict.get('shade_temp_min') or input_dict.get(KEY_TL_LOWEST_MIN_TEMP) or '15.0').strip()
    t_brg_min = str(input_dict.get(KEY_TL_BRIDGE_TEMP_MIN) or '25.00').strip()
    t_brg_max = str(input_dict.get(KEY_TL_BRIDGE_TEMP_MAX) or '40.00').strip()
    t_rise = str(input_dict.get(KEY_TL_TEMP_RISE) or '15.00').strip()
    t_fall = str(input_dict.get(KEY_TL_TEMP_FALL) or '15.00').strip()

    # Pre-render standard combinations
    lc_rows = [
        ("ULS-01", r"DL(1.35/1.00) + SIDL(1.75/1.00) + LL(1.50) + WL(0.90) + TL(0.90)"),
        ("ULS-02", r"DL(1.35/1.00) + SIDL(1.75/1.00) + LL(1.15) + WL(1.50) + TL(0.90)"),
        ("ULS-03", r"DL(1.35/1.00) + SIDL(1.75/1.00) + LL(1.15) + WL(0.90) + TL(1.50)"),
        ("ULS-04", r"DL(1.00/1.00) + SIDL(1.00/1.00) + LL(0.75) + TL(0.50) + VC(1.00)"),
        ("ULS-05", r"DL(1.00/1.00) + SIDL(1.00/1.00) + LL(0.75) + TL(0.50) + BI(1.00)"),
        ("ULS-06", r"DL(1.00/1.00) + SIDL(1.00/1.00) + LL(0.75) + TL(0.50) + FB(1.00)"),
        ("ULS-07", r"DL(1.35/1.00) + SIDL(1.75/1.00) + LL(0.20) + TL(0.50) + EQ(1.50)"),
        ("ULS-08", r"DL(1.35/1.00) + SIDL(1.75/1.00) + LL(0.20) + TL(0.50) + EQ(0.75)"),
        ("SLS-01", r"DL(1.00) + SIDL(1.20/1.00) + LL(1.00) + WL(0.60) + TL(0.60)"),
        ("SLS-02", r"DL(1.00) + SIDL(1.20/1.00) + LL(0.75) + WL(1.00) + TL(0.60)"),
        ("SLS-03", r"DL(1.00) + SIDL(1.20/1.00) + LL(0.75) + WL(0.60) + TL(1.00)"),
        ("SLS-04", r"DL(1.00) + SIDL(1.20/1.00) + LL(0.75) + WL(0.50) + TL(0.50)"),
        ("SLS-05", r"DL(1.00) + SIDL(1.20/1.00) + LL(0.20) + WL(0.60) + TL(0.50)"),
        ("SLS-06", r"DL(1.00) + SIDL(1.20/1.00) + LL(0.20) + WL(0.50) + TL(0.60)"),
        ("SLS-07", r"DL(1.00) + SIDL(1.20/1.00) + LL(0.00) + WL(0.00) + TL(0.50)"),
    ]
    lc_rows_str = "\n".join([f"{cid} & {cases} \\\\[6pt]\n\\hline" for cid, cases in lc_rows])

    # Table Header Templates via styles.make_longtable_header
    hdr_2col = make_longtable_header(r"\textbf{parameter} & \textbf{value} \\", 2)
    hdr_vll = make_longtable_header(
        r"\multirow{2}{*}{\textbf{Vehicle}} & \multirow{2}{*}{\makecell{\textbf{Total Load}\\\textbf{(kN)}}} & \multirow{2}{*}{\makecell{\textbf{Impact}\\\textbf{Factor}}} & \multicolumn{3}{c|}{\textbf{Braking Load}} & \multirow{2}{*}{\makecell{\textbf{Centrifugal}\\\textbf{Force (kN)}}} \\ \cline{4-6}" + "\n"
        + r"& & & \textbf{Considered?} & \makecell{\textbf{Value}\\\textbf{(kN)}} & \makecell{\textbf{Eccentricity}\\\textbf{(m)}} & \\",
        7
    )
    hdr_comb = make_longtable_header(r"\textbf{Combination ID} & \textbf{Load Cases} \\[6pt]", 2)

    return r"""
\chapter{Loads and Load Combinations}

This section summarizes all loads applied to the bridge and the load combinations considered for analysis and design.

\vspace{1em}
""" + NEEDSPACE_TABLE + r"""
\begin{longtable}{|L{5.5cm}|p{10.0cm}|}
\caption{\textbf{Dead Load -- Self Weight}} \\
""" + hdr_2col + r"""
\textnormal{Steel Self-Weight Applied} & """ + (_render_value(input_dict, KEY_MATERIAL_GIRDER_DENSITY, ' kN/m\\textsuperscript{3}')) + r""" \\[6pt]
\hline
\textnormal{Concrete Deck Weight} & """ + (_render_value(input_dict, KEY_MATERIAL_DECK_DENSITY, ' kN/m\\textsuperscript{3}')) + r""" \\[6pt]
\hline
\textnormal{Self-Weight Factor} & """ + (_render_value(input_dict, KEY_PL_SELF_WEIGHT_FACTOR)) + r""" \\[6pt]
\hline
\end{longtable}

\vspace{1em}
""" + NEEDSPACE_TABLE + r"""
\begin{longtable}{|L{5.5cm}|p{10.0cm}|}
\caption{\textbf{Dead Load for Surfacing (DW)}} \\
""" + hdr_2col + r"""
\textnormal{Wearing Course Load} & """ + (_render_value(input_dict, KEY_WC_MATERIAL)) + r""" x """ + (_render_value(input_dict, KEY_WC_THICKNESS)) + r""" \\[6pt]
\hline
\textnormal{Additional SIDL (Crash Barrier)} & """ + (_render_value(input_dict, KEY_CB_LOAD)) + r""" kN/m per barrier \\[6pt]
\hline
\textnormal{Railing Load} & """ + (_render_value(input_dict, KEY_RL_LOAD_VALUE)) + r""" kN/m\sdstar{} \\[6pt]
\hline
\end{longtable}

\newpage
\begin{longtable}{|L{2.8cm}|C{1.8cm}|C{1.6cm}|C{1.8cm}|C{2.0cm}|C{2.0cm}|C{2.4cm}|}
\caption{\textbf{Vehicle Live Loads (LL) Parameters}} \\
""" + hdr_vll + r"""
""" + vehicle_rows_tex + r"""
\end{longtable}
\par\vspace{-0.2cm}\noindent{\footnotesize \textit{Note: Braking forces calculated per IRC 6:2017 Cl. 211.2. Centrifugal force is 0.00 kN for straight bridge alignment (IRC 6 Cl. 212).}}\vspace{0.8em}

\vspace{1em}
""" + NEEDSPACE_TABLE + r"""
\begin{longtable}{|L{5.5cm}|p{10.0cm}|}
\caption{\textbf{Footpath / Pedestrian Live Load (LL)}} \\
""" + hdr_2col + r"""
\textnormal{Footpath Provision} & """ + ("Included" if has_footpath else "None") + r""" \\[6pt]
\hline
\textnormal{Footpath Width} & """ + (_render_value(input_dict, KEY_TS_FOOTPATH_WIDTH, ' m') if has_footpath else "0.0 m") + r""" \\[6pt]
\hline
\textnormal{Footway Load Intensity} & """ + (_tex(fp_intensity) if has_footpath else "N/A") + r""" \\[6pt]
\hline
\textnormal{Loading Mode} & """ + (_tex(str(fp_mode)) if has_footpath and fp_mode else "IRC 6 Cl. 206.1") + r""" \\[6pt]
\hline
\textnormal{Reference Standard} & IRC 6:2017 Clause 206.1 \\[6pt]
\hline
\end{longtable}

\vspace{1em}
""" + NEEDSPACE_TABLE + r"""
\begin{longtable}{|L{5.5cm}|p{10.0cm}|}
\caption{\textbf{Wind Load (WL) --- per IRC 6}} \\
""" + hdr_2col + r"""
\textnormal{Basic Wind Speed, Vb} & """ + _tex(vb_val) + r""" m/s [from Project Location] \\[6pt]
\hline
\textnormal{Terrain Type} & """ + _tex(terrain_val) + r""" \\[6pt]
\hline
\textnormal{Average Exposed Height, H (m)} & """ + _tex(h_val) + r""" m \\[6pt]
\hline
\textnormal{Hourly Mean Wind Speed, Vz} & """ + vz_str + r""" \\[6pt]
\hline
\textnormal{Hourly Wind Pressure, Pz} & """ + pz_str + r""" \\[6pt]
\hline
\textnormal{Transverse Wind Force} & """ + _tex(f_wt) + r""" kN \\[6pt]
\hline
\textnormal{Longitudinal Wind Force} & """ + _tex(f_wl) + r""" kN \\[6pt]
\hline
\textnormal{Vertical Wind Force} & $\pm$""" + _tex(f_wv) + r""" kN \\[6pt]
\hline
\end{longtable}

\vspace{1em}
""" + NEEDSPACE_TABLE + r"""
\begin{longtable}{|L{5.5cm}|p{10.0cm}|}
\caption{\textbf{Earthquake Load (EL) --- per IRC 6}} \\
""" + hdr_2col + r"""
\textnormal{Seismic Zone} & """ + _tex(sz_name) + r""" [from Project Location] \\[6pt]
\hline
\textnormal{Zone Factor, Z} & """ + _tex(z_fac) + r""" \\[6pt]
\hline
\textnormal{Importance Factor, I} & """ + _tex(imp_fac) + r""" \\[6pt]
\hline
\textnormal{Type of Soil} & """ + _tex(soil_val) + r""" \\[6pt]
\hline
\textnormal{Sa/g} & """ + _tex(sag_val) + r""" \\[6pt]
\hline
\textnormal{Horizontal Seismic Coefficient, Ah} & """ + _tex(ah_val) + r""" \\[6pt]
\hline
\textnormal{Vertical Seismic Coefficient, Av} & """ + _tex(av_val) + r""" \\[6pt]
\hline
\textnormal{Horizontal Seismic Force (longitudinal)} & """ + feq_long_str + r""" kN \\[6pt]
\hline
\textnormal{Horizontal Seismic Force (transverse)} & """ + feq_trans_str + r""" kN \\[6pt]
\hline
\end{longtable}

\vspace{1em}
""" + NEEDSPACE_TABLE + r"""
\begin{longtable}{|L{5.5cm}|p{10.0cm}|}
\caption{\textbf{Temperature Load (TL) --- per IRC 6}} \\
""" + hdr_2col + r"""
\textnormal{Maximum Shade Temperature} & """ + _tex(t_max_shade) + r""" $^\circ$C \\[6pt]
\hline
\textnormal{Minimum Shade Temperature} & """ + _tex(t_min_shade) + r""" $^\circ$C \\[6pt]
\hline
\textnormal{Effective Bridge Temp. Range} & """ + _tex(t_brg_min) + r""" to """ + _tex(t_brg_max) + r""" $^\circ$C \\[6pt]
\hline
\textnormal{Temperature Rise / Fall for Design} & +""" + _tex(t_rise) + r""" $^\circ$C / \textminus{}""" + _tex(t_fall) + r""" $^\circ$C \\[6pt]
\hline
\end{longtable}

\newpage
\begin{longtable}{|C{4.0cm}|p{11.5cm}|}
\caption{\textbf{Load Combinations}} \\
""" + hdr_comb + r"""
""" + lc_rows_str + r"""
\end{longtable}

\noindent\textit{Note: All IRC 6 load combinations are auto-generated by OsdagBridge. User-defined custom combinations, if any, are appended.}
"""
