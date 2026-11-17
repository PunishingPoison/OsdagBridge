"""
OsdagBridge - Generate Baseline Report (Report_Before.pdf)
Generates the original baseline report (36 pages) matching the system state
at initial installation (commit d74f56d) before enhancements were applied.
"""
import os
import sys
import matplotlib
matplotlib.use('Agg')

os.environ['QT_QPA_PLATFORM'] = 'offscreen'
sys.path.insert(0, os.path.abspath("src"))

from PySide6.QtWidgets import QApplication
app = QApplication.instance() or QApplication(sys.argv)

from osdagbridge.desktop.ui.template_page import CustomWindow
from osdagbridge.core.bridge_types.plate_girder.plategirderbridge import PlateGirderBridge
from osdagbridge.core.bridge_types.plate_girder.defaults import solve_extend_basic_input_dict

from osdagbridge.core.reports_baseline.report_generator import (
    ReportRequest,
    ReportMetadata,
    ReportOptions,
    generate_report,
    build_report_payload,
)

def generate_baseline():
    print("=" * 70)
    print("  Generating Baseline Report (Report_Before.pdf)")
    print("  Engine: Default reporting system (initial installation state)")
    print("=" * 70)

    print("\n[1/3] Initializing OsdagBridge plate girder model...")
    w = CustomWindow('OsdagBridge', PlateGirderBridge)
    w.input_dict['project.location'] = 'Bangalore (A), Karnataka'
    w.input_dict['geometry.span'] = '20'
    w.input_dict['geometry.carriageway_width'] = '4.25'
    w.input_dict['geometry.skew_angle'] = '0.0'
    w.input_dict['geometry.include_median'] = 'No'
    w.input_dict['geometry.footpath'] = 'None'
    w.input_dict['geometry.design_mode'] = 'Optimized'

    solve_extend_basic_input_dict(w.input_dict)

    print("[2/3] Running backend structural design analysis...")
    backend = w.backend
    backend.set_input(w.input_dict)
    backend.design()
    print("      Design analysis completed successfully!")

    output_dir = os.path.abspath(".")
    file_stem = "Report_Before"

    metadata = ReportMetadata(
        project_name="20m Composite Plate Girder Highway Bridge",
        project_location="Bangalore (A), Karnataka",
        designer="Er. Rajesh Sharma, M.Tech (Structures), P.E.",
        reviewer="Dr. Arvind Kumar, Ph.D. (Bridge Engg.), F.I.E.",
        client="National Highways Authority of India (NHAI)",
        company="Osdag Bridge Design Consultants",
        group_name="Infrastructure & Highways Division",
        job_number="OB-2026-BR-001",
        additional_comments="Baseline report generated using default reporting system",
        report_date="2026-11-16",
    )

    options = ReportOptions(
        sections=[
            "executive_summary",
            "project_information",
            "input_parameters",
            "loads_and_combinations",
            "analysis_results",
            "design_checks",
            "drawings_and_visualizations",
            "material_takeoff",
            "standards_and_references",
            "references",
        ],
        include_figures=True,
        include_toc=True,
        include_pdf=True,
    )

    request = ReportRequest(
        metadata=metadata,
        options=options,
        output_dir=output_dir,
        file_stem=file_stem,
    )

    print("[3/3] Compiling baseline report with pdflatex...")
    report_inputs = backend.input_dict.copy()
    output_dict = dict(backend.output_dict)
    payload = build_report_payload(request, report_inputs, output_dict)
    res = generate_report(payload, request)

    if res.pdf_path and os.path.exists(res.pdf_path):
        size = os.path.getsize(res.pdf_path)
        print(f"\n>>> SUCCESS: Generated {res.pdf_path} ({size:,} bytes)")
        return res.pdf_path
    else:
        print("\n>>> FAILED: Could not generate baseline PDF")
        return None

if __name__ == "__main__":
    generate_baseline()
