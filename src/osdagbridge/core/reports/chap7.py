from osdagbridge.core.reports.styles import make_longtable_header, NEEDSPACE_TABLE
from osdagbridge.core.reports.report_utils import _fig_or_placeholder

def ch7_quantities(input_dict, fig_paths=None):
    fig_paths = fig_paths or {}
    
    headers = r"\textbf{S.N.} & \textbf{Item Description} & \textbf{Volume} & \textbf{Quantity} & \textbf{Total Volume} & \textbf{Weight (MT)} & \textbf{Total Weight (MT)} \\"
    table_headers = make_longtable_header(headers, 7)

    steel_fig = fig_paths.get("steel_breakdown")
    rebar_fig = fig_paths.get("concrete_rebar")

    fig_markup = ""
    if steel_fig or rebar_fig:
        fig_markup = r"""
\newpage
\noindent\textbf{Material Quantity Summary Visualizations}

\begin{figure}[H]
\centering
"""
        if steel_fig and rebar_fig:
            fig_markup += r"""
\begin{subfigure}[b]{0.48\textwidth}
    \centering
    \includegraphics[width=\textwidth]{""" + steel_fig + r"""}
    \caption{Structural Steel Tonnage Breakdown}
\end{subfigure}
\hfill
\begin{subfigure}[b]{0.48\textwidth}
    \centering
    \includegraphics[width=\textwidth]{""" + rebar_fig + r"""}
    \caption{Concrete Volume vs. Rebar Weight}
\end{subfigure}
\caption{\textbf{Material Quantity Distributions}}
"""
        elif steel_fig:
            fig_markup += r"""
\includegraphics[width=0.75\textwidth]{""" + steel_fig + r"""}
\caption{\textbf{Structural Steel Tonnage Breakdown by Component}}
"""
        elif rebar_fig:
            fig_markup += r"""
\includegraphics[width=0.75\textwidth]{""" + rebar_fig + r"""}
\caption{\textbf{Concrete Volume vs. Reinforcement Steel Weight}}
"""
        fig_markup += r"""
\label{fig:material_takeoff}
\end{figure}
"""

    return r"""
\chapter{Material Take-off \& Quantity Summary}
\label{ch:material-takeoff}

This chapter summarizes the Bill of Materials (BOM) including the quantities, total volumes, and weights of structural steel, concrete, reinforcement, and accessories.

\vspace{0.8em}
\begingroup
\setlength{\tabcolsep}{3.5pt}
\begin{longtable}{|C{1.0cm}|L{3.8cm}|C{2.6cm}|C{1.8cm}|C{1.8cm}|C{1.8cm}|C{1.8cm}|}
\caption{\textbf{Bill of Materials (Steel, Concrete, and Reinforcement Quantities)}} \\
""" + table_headers + r"""
1 & Structural Steel (IS 2062) for Girders & """ + str(input_dict.get("steel_girders_vol_formula", "N.A.")) + r""" & """ + str(input_dict.get("steel_girders_qty", "N.A.")) + r""" & """ + str(input_dict.get("steel_girders_vol_total", "N.A.")) + r""" & """ + str(input_dict.get("steel_girders_wt_single", "N.A.")) + r""" & """ + str(input_dict.get("steel_girders_wt_total", "N.A.")) + r""" \\
\hline
2(a) & Cross Bracing - Top Chord & """ + str(input_dict.get("bracing_top_vol_formula", "N.A.")) + r""" & """ + str(input_dict.get("bracing_top_qty", "N.A.")) + r""" & """ + str(input_dict.get("bracing_top_vol_total", "N.A.")) + r""" & """ + str(input_dict.get("bracing_top_wt_single", "N.A.")) + r""" & """ + str(input_dict.get("bracing_top_wt_total", "N.A.")) + r""" \\
\hline
2(b) & Cross Bracing - Bottom Chord & """ + str(input_dict.get("bracing_bot_vol_formula", "N.A.")) + r""" & """ + str(input_dict.get("bracing_bot_qty", "N.A.")) + r""" & """ + str(input_dict.get("bracing_bot_vol_total", "N.A.")) + r""" & """ + str(input_dict.get("bracing_bot_wt_single", "N.A.")) + r""" & """ + str(input_dict.get("bracing_bot_wt_total", "N.A.")) + r""" \\
\hline
2(c) & Cross Bracing - Diagonal Chord & """ + str(input_dict.get("bracing_diag_vol_formula", "N.A.")) + r""" & """ + str(input_dict.get("bracing_diag_qty", "N.A.")) + r""" & """ + str(input_dict.get("bracing_diag_vol_total", "N.A.")) + r""" & """ + str(input_dict.get("bracing_diag_wt_single", "N.A.")) + r""" & """ + str(input_dict.get("bracing_diag_wt_total", "N.A.")) + r""" \\
\hline
3(a) & End Diaphragm - Top Chord & """ + str(input_dict.get("diaphragm_top_vol_formula", "N.A.")) + r""" & """ + str(input_dict.get("diaphragm_top_qty", "N.A.")) + r""" & """ + str(input_dict.get("diaphragm_top_vol_total", "N.A.")) + r""" & """ + str(input_dict.get("diaphragm_top_wt_single", "N.A.")) + r""" & """ + str(input_dict.get("diaphragm_top_wt_total", "N.A.")) + r""" \\
\hline
3(b) & End Diaphragm - Bottom Chord & """ + str(input_dict.get("diaphragm_bot_vol_formula", "N.A.")) + r""" & """ + str(input_dict.get("diaphragm_bot_qty", "N.A.")) + r""" & """ + str(input_dict.get("diaphragm_bot_vol_total", "N.A.")) + r""" & """ + str(input_dict.get("diaphragm_bot_wt_single", "N.A.")) + r""" & """ + str(input_dict.get("diaphragm_bot_wt_total", "N.A.")) + r""" \\
\hline
3(c) & End Diaphragm - Diagonal Chord & """ + str(input_dict.get("diaphragm_diag_vol_formula", "N.A.")) + r""" & """ + str(input_dict.get("diaphragm_diag_qty", "N.A.")) + r""" & """ + str(input_dict.get("diaphragm_diag_vol_total", "N.A.")) + r""" & """ + str(input_dict.get("diaphragm_diag_wt_single", "N.A.")) + r""" & """ + str(input_dict.get("diaphragm_diag_wt_total", "N.A.")) + r""" \\
\hline
4 & Concrete (M40) for Deck Slab & """ + str(input_dict.get("concrete_deck_vol_formula", "N.A.")) + r""" & """ + str(input_dict.get("concrete_deck_qty", "N.A.")) + r""" & """ + str(input_dict.get("concrete_deck_vol_total", "N.A.")) + r""" & """ + str(input_dict.get("concrete_deck_wt_single", "N.A.")) + r""" & """ + str(input_dict.get("concrete_deck_wt_total", "N.A.")) + r""" \\
\hline
5 & Reinforcement Steel (Fe 500) & """ + str(input_dict.get("rebar_deck_vol_formula", "N.A.")) + r""" & """ + str(input_dict.get("rebar_deck_qty", "N.A.")) + r""" & """ + str(input_dict.get("rebar_deck_vol_total", "N.A.")) + r""" & """ + str(input_dict.get("rebar_deck_wt_single", "N.A.")) + r""" & """ + str(input_dict.get("rebar_deck_wt_total", "N.A.")) + r""" \\
\hline
6 & Shear Stud Connectors & """ + str(input_dict.get("shear_studs_vol_formula", "N.A.")) + r""" & """ + str(input_dict.get("shear_studs_qty", "N.A.")) + r""" & """ + str(input_dict.get("shear_studs_vol_total", "N.A.")) + r""" & """ + str(input_dict.get("shear_studs_wt_single", "N.A.")) + r""" & """ + str(input_dict.get("shear_studs_wt_total", "N.A.")) + r""" \\
\hline
7 & Crash Barrier & """ + str(input_dict.get("crash_barrier_vol_formula", "N.A.")) + r""" & """ + str(input_dict.get("crash_barrier_qty", "N.A.")) + r""" & """ + str(input_dict.get("crash_barrier_vol_total", "N.A.")) + r""" & """ + str(input_dict.get("crash_barrier_wt_single", "N.A.")) + r""" & """ + str(input_dict.get("crash_barrier_wt_total", "N.A.")) + r""" \\
\hline
\end{longtable}
\endgroup
""" + fig_markup + r"""
"""
