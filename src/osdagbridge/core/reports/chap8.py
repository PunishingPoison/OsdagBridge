from typing import List

from osdagbridge.core.utils.common import (
    KEY_DESIGN_MODE
)


def ch8_design_log(log_entries: List[str], input_dict: dict) -> str:
    """Render Chapter 8 using real log_entries, matching Osdag color convention."""

    lines_tex = []
    if log_entries:
        for entry in log_entries:
            for raw_line in entry.split('\n'):
                line = raw_line.strip()
                if not line:
                    continue
                escaped = (line
                    .replace('_', r'\_')
                    .replace('%', r'\%')
                    .replace('&', r'\&')
                    .replace('#', r'\#'))
                upper = line.upper()
                if 'WARNING' in upper:
                    lines_tex.append(
                        rf'\textcolor{{blue}}{{{escaped}}}\\')
                elif 'ERROR' in upper:
                    lines_tex.append(
                        rf'\textcolor{{red}}{{{escaped}}}\\')
                elif 'INFO' in upper:
                    lines_tex.append(
                        rf'\textcolor{{osdagGreen}}{{{escaped}}}\\')
                else:
                    continue  # skip lines without a known level — Osdag patter

    mode = str(input_dict.get(KEY_DESIGN_MODE, 'Optimized')).strip().lower()
    is_custom = mode in {'custom', 'customized'}
    return _ch8_assumptions(is_custom)


def _ch8_assumptions(is_custom: bool) -> str:
    assumptions = [
        r"""
\chapter{Standards \& Assumptions}
\label{ch:Design Standards}

This section provides references to standards used to calibrate the OsdagBridge
design modules, and notes the limitations of the current software version.

\section{Design Standards}
\label{sec:design_standards}

The following Indian Road Congress (IRC) codes and Indian Standards (IS) 
form the basis of all design calculations in this software.

\vspace{0.5cm}

\begingroup
\setlength{\tabcolsep}{3.5pt}
\begin{table}[H]
\caption{\textbf{IRC Codes}}
\begin{tabular}{|c|c|p{13cm}|}
\hline
\textbf{Code} & \textbf{Year} & \textbf{Title / Scope} \\ 
\hline
IRC 5 & 2015 & General Features of Design - carriageway widths, kerb, footpath dimensions \\ 
\hline
IRC 6 & 2017 & Loads and Load Combinations - dead load, live load, impact, wind, temperature, etc. \\ 
\hline
IRC 22 & 2015 & Composite Construction (LS) - Composite section properties, ULS/SLS design, shear connectors \\ 
\hline
IRC 24 & 2010 & Steel Road Bridges (LS) - Stiffener design, skew angle limits, diaphragm requirements \\ 
\hline
IRC 112 & 2020 & Concrete Road Bridges - Deck slab flexure, shear, crack width, reinforcement \\ 
\hline
IRC SP 114 & 2018 & Seismic Design of Road Bridges \\ 
\hline
\end{tabular}
\end{table}

\begingroup
\setlength{\tabcolsep}{3.5pt}
\begin{table}[H]
\caption{\textbf{IS Codes}}
\begin{tabular}{|c|c|p{13cm}|}
\hline
\textbf{Code} & \textbf{Year} & \textbf{Scope} \\
\hline
IS 800 & 2007 & Steel construction - tension, compression, bending, shear, LTB, stiffeners, combined checks \\
\hline
IS 456 & 2000 & Concrete - simplified stress-block for deck moment capacity \\
\hline
IS 1786 & 2008 & Reinforcement steel properties \\
\hline
IS 1893 (Part 3) & 2014 & Earthquake resistant design \\
\hline
IS 2062 & 2011 & Structural steel - yield and ultimate strength by grade \\
\hline
\end{tabular}
\end{table}

\clearpage
\section{Analysis and Design Assumptions of This Version}
\label{sec:assumptions}

This section details the primary engineering assumptions adopted in the structural analysis and design models of OsdagBridge, providing their technical justifications, affected design checks, sensitivity evaluations, and verification thresholds per IRC and IS bridge codes.

\subsection{1. Simply Supported Boundary Conditions}
\begin{itemize}
    \item \textbf{Technical Justification:} Standard medium-span composite highway bridges (up to 30~m) in India are conventionally configured as simply supported spans resting on elastomeric or POT/PTFE bearings. This prevents moment transfer across pier supports, accommodates thermal breathing without inducing secondary stresses, and simplifies substructure design.
    \item \textbf{Design Checks Affected:} Maximum positive bending moment at midspan ($M_u$), end support reactions and vertical shear ($V_u$), and midspan deflections ($\delta_{live}$, $\delta_{total}$).
    \item \textbf{Sensitivity:} Moderate to high. Rotational restraint at bearings (e.g., seized bearings) would induce negative hogging moments at ends and reduce midspan sagging moments.
    \item \textbf{Verification Recommendations:} For continuous spans, integral abutments, or spans with elastomeric bearings providing partial rotational stiffness, a continuous grillage or 3D FEM should be utilized.
\end{itemize}

\subsection{2. Construction Stage Sequence and Long-Term Creep/Shrinkage}
\begin{itemize}
    \item \textbf{Technical Justification:} Prior to the concrete deck curing and achieving its 28-day design compressive strength ($f_{ck}$), the bare steel girder must independently support its self-weight, the wet concrete deck, formwork, and construction loads. After hardening, all subsequent dead loads (wearing course, crash barriers) and live loads act on the composite section. Creep is accounted for using an effective modular ratio ($m = 2n$ or $3n$) per IRC 22:2015 Cl.~604.2.
    \item \textbf{Design Checks Affected:} Lateral torsional buckling of bare steel girder (IS 800 Cl.~8.2.2 / IRC 24 Cl.~509.4), construction stage stresses, SLS long-term deflection (L/600 limit per IRC 22 Cl.~604.3.2), and SLS concrete/steel stress limitations (IRC 22 Cl.~604.3.1).
    \item \textbf{Sensitivity:} High. The long-term total deflection is particularly sensitive to the creep coefficient ($\phi = 2.0$--$2.5$) and casting sequence (unpropped vs. propped construction).
    \item \textbf{Verification Recommendations:} Detailed time-dependent staged erection analysis is recommended for spans $\ge 25$~m or when staged deck slab casting is specified in the construction sequence.
\end{itemize}

\subsection{3. Full Shear Connection Assumption at ULS}
\begin{itemize}
    \item \textbf{Technical Justification:} IRC 22:2015 Cl.~606.3 mandates that highway bridge girders provide full shear connection between the steel top flange and concrete slab so that the plastic or elastic flexural capacity of the composite girder can be fully mobilized without interfacial slip. Headed stud shear connectors are provided at pitches satisfying both interface shear capacity and maximum spacing limits ($s \le 3 t_{slab} \le 600$~mm).
    \item \textbf{Design Checks Affected:} Composite moment capacity ($M_d$), neutral axis depth ($x_u$), longitudinal shear at the steel-concrete interface, and flexural stiffness governing deflections.
    \item \textbf{Sensitivity:} Low for flexure as long as stud pitch is rigorously checked ($UR \le 1.0$), but high for fatigue and serviceability slip if studs are under-designed.
    \item \textbf{Verification Recommendations:} Partial shear connection is prohibited for bridge structures per IRC 22. In-situ push-out tests or FE interface modelling should be considered only when non-standard connector configurations are employed.
\end{itemize}

\subsection{4. Bearing Stiffness Idealization ($k = 10^6\text{ kN/m}$ vs $100\text{ kN/m}$)}
\begin{itemize}
    \item \textbf{Technical Justification:} Fixed bearings are idealized with high translation stiffness ($k_x = 10^6\text{ kN/m}$) to represent restrained longitudinal/transverse movement, while expansion (free) bearings are modelled with nominal stiffness ($k = 100\text{ kN/m}$) to avoid numerical singularity in grillage analysis while allowing uninhibited thermal expansion and contraction.
    \item \textbf{Design Checks Affected:} Longitudinal horizontal braking forces (IRC 6 Cl.~211), seismic inertial base shear distribution (IRC SP 114), and temperature-induced expansion reactions.
    \item \textbf{Sensitivity:} Low for vertical girder design; moderate for substructure and bearing selection.
    \item \textbf{Verification Recommendations:} Exact bearing stiffness matrices (incorporating elastomer shear modulus $G$ and shape factor $S$) should be verified during bearing design per IRC 83 (Part II/Part III).
\end{itemize}

\subsection{5. Transverse Member Forces via 2D Frame Analogy}
\begin{itemize}
    \item \textbf{Technical Justification:} In grillage analysis, transverse deck elements represent tributary strips of the concrete slab and intermediate cross frames. The 2D transverse frame analogy isolates transverse slices of the superstructure under wheel loads, kerb loads, and wind/seismic overturning to estimate transverse bending moments, shear forces, and cross-bracing axial forces.
    \item \textbf{Design Checks Affected:} Deck slab sagging and hogging flexure, slab shear capacity, cross-bracing diagonal and chord axial forces, and end diaphragm reaction transfer.
    \item \textbf{Sensitivity:} Moderate for straight, right-angled bridges with uniform girder spacing; high for bridges with skew angles $> 15^\circ$ or curved alignments.
    \item \textbf{Verification Recommendations:} For skew angles $> 15^\circ$, bifurcated structures, or highly asymmetric carriageways, full 3D plate-and-shell finite element analysis (FEA) must be carried out per IRC 24 Cl.~504.8.
\end{itemize}
"""
    ]

    if not is_custom:
        assumptions.append(r"""
\textbf{Material Properties (IRC 22:2015 Annex III)}

\begin{itemize}
\item Steel: $E_s = 200{,}000 \, \text{MPa}, \ G_s = 80{,}000 \, \text{MPa}, \ \nu = 0.30, \ \alpha = 11.7 \times 10^{-6}/^\circ\mathrm{C}$ (grade-independent).
\item Minimum structural concrete grade: M25.
\item Default reinforcement grade: Fe500.
\end{itemize}

\textbf{Partial Safety Factors (IRC 22:2015 Cl.601.4)}

\begin{itemize}
\item $\gamma_{m0}$ (steel yield, ULS) = 1.10
\item $\gamma_{m1}$ (steel ultimate, ULS) = 1.25
\item Reinforcement (ULS) = 1.15
\item Welds -- shop: 1.25; field: 1.50
\item Fatigue ($\gamma_{mft}$) = 1.35
\end{itemize}

\textbf{Loading}

\begin{itemize}
\item Dead load densities per IRC 6:2017 Cl.203: structural steel $78.5 \ \text{kN/m}^3$, concrete $25.0 \ \text{kN/m}^3$, bituminous wearing course $24.0 \ \text{kN/m}^3$.
\item Multi-lane live load reduction factors per IRC 6:2017 Cl.204.4 Table 6A: 1st lane = 1.0, 2nd lane = 0.8, 3rd lane onwards = 0.4.
\item Impact factor (dynamic load allowance) computed from span per IRC 6:2017 Cl.208.2/208.3.
\item Wind load applied as transverse, longitudinal, and vertical components per IRC 6:2017 Cl.209.3.3--209.3.5.
\end{itemize}

\textbf{Serviceability Limits}

\begin{itemize}
\item Deflection limits (IRC 22:2015 Cl.604.3.2): live load + impact $\leq L/800$; total $\leq L/600$.
\item SLS stress limits: concrete $\sigma_c \leq 0.48 f_{ck}$; rebar $\sigma_s \leq 0.80 f_{yk}$; steel $f_e \leq 0.9 f_y$.
\item Permissible crack width: $w_k \leq 0.3 \ \text{mm}$ (bridge deck, exposure class XS2/XD2 per IRC 112:2020 Cl.12.3.2).
\end{itemize}

\textbf{Fatigue}

\begin{itemize}
\item Reference fatigue life: $N_{sc} = 2 \times 10^6$ cycles (IRC 22:2015 Cl.605).
\item Constant stress range is assumed. A thickness correction factor $\mu_r$ is applied for plate thickness $> 25 \ \text{mm}$.
\end{itemize}

\textbf{Stiffener Design}

\begin{itemize}
\item Intermediate transverse stiffener and bearing stiffener design follows IS 800:2007 Cl.8.7.2/8.7.3 and IRC 24:2010 Cl.509.7.2/509.7.3.
\end{itemize}
""")

    assumptions.append(r"""
\section{Known Limitations of This Version}
\label{sec:limitations}

\begin{itemize}
\item Substructure (piers, pile caps, foundations) and bearing design are not included.
\item Splice connection design is not implemented.
\item Skew angle $>$ 15 degrees requires independent manual analysis (IRC 24 Cl. 504.8).
\item Construction stage sequence analysis is approximate; detailed staged analysis
  should be performed for long-term deflection checks.
\item The grillage analysis assumes simply supported boundary conditions;
  continuous spans are not currently supported.
\end{itemize}
""")

    return "\n".join(assumptions)


