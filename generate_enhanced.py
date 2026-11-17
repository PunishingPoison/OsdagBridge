"""
OsdagBridge - Generate Enhanced Report (Report_After.pdf)
Generates the comprehensive 62-page enhanced engineering report incorporating
all Scope of Work deliverables, repeated table headers, UR visualizations,
reconciled material take-off, and verified design checks.
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

from osdagbridge.core.reports.report_generator import (
    ReportRequest,
    ReportMetadata,
    ReportOptions,
    generate_report,
    build_report_payload,
)

def generate_enhanced():
    print("=" * 70)
    print("  Generating Enhanced Report (Report_After.pdf)")
    print("  Engine: Modified & improved reporting system (Scope of Work)")
    print("=" * 70)

    print("\n[1/3] Initializing OsdagBridge plate girder model...")
    w = CustomWindow('OsdagBridge', PlateGirderBridge)
    w.input_dict['project.location'] = 'Bangalore (A), Karnataka'
    w.input_dict['latitude'] = '12.9716'
    w.input_dict['longitude'] = '77.5946'
    w.input_dict['seismic_zone'] = 'Zone II'
    w.input_dict['wind_speed'] = '33.0'
    w.input_dict['shade_temp_max'] = '38.0'
    w.input_dict['shade_temp_min'] = '15.0'
    w.input_dict['geometry.span'] = '20'
    w.input_dict['geometry.carriageway_width'] = '4.25'
    w.input_dict['geometry.skew_angle'] = '0.0'
    w.input_dict['geometry.include_median'] = 'No'
    w.input_dict['geometry.footpath'] = 'None'
    w.input_dict['geometry.design_mode'] = 'Optimized'
    w.input_dict['member_properties.stiffener_details.intermediate_stiffener_thickness.G1.M1'] = '14.0'
    w.input_dict['member_properties.cross_bracing_details.bracing_section_designation.G1G2.B1M1'] = 'ISA 40 x 40 x 3'
    w.input_dict['member_properties.cross_bracing_details.bracing_section_designation.G2G3.B2M1'] = 'ISA 40 x 40 x 3'
    w.input_dict['member_properties.end_diaphragm_details.bracing_section_designation.G1G2.E1M1'] = 'ISA 40 x 40 x 3'
    w.input_dict['member_properties.end_diaphragm_details.bracing_section_designation.G2G3.E2M1'] = 'ISA 40 x 40 x 3'

    solve_extend_basic_input_dict(w.input_dict)

    print("[2/3] Running backend structural design analysis...")
    backend = w.backend
    backend.set_input(w.input_dict)
    backend.design()
    print("      Design analysis completed successfully!")

    output_dir = os.path.abspath(".")
    file_stem = "Report_After"

    metadata = ReportMetadata(
        project_name="20m Composite Plate Girder Highway Bridge",
        project_location="Bangalore (A), Karnataka",
        designer="Er. Rajesh Sharma, M.Tech (Structures), P.E.",
        reviewer="Dr. Arvind Kumar, Ph.D. (Bridge Engg.), F.I.E.",
        client="National Highways Authority of India (NHAI)",
        company="Osdag Bridge Design Consultants",
        group_name="Infrastructure & Highways Division",
        job_number="OB-2026-BR-001",
        subtitle="Rev 0",
        additional_comments="Enhanced report with repeated headers, recalibrated geometry, structured load tables, and summary charts",
        report_date="2026-11-17",
    )

    options = ReportOptions(
        sections=[
            "exec_summary",
            "executive_summary",
            "project_info",
            "project_information",
            "input_parameters",
            "loads",
            "loads_and_combinations",
            "analysis",
            "analysis_results",
            "design_checks",
            "drawings",
            "drawings_and_visualizations",
            "quantities",
            "material_takeoff",
            "standards",
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

    print("[3/3] Compiling enhanced report with pdflatex...")
    res = backend.generate_design_report(request, cad_generator=w.cad_3d_widget)

    if res.pdf_path and os.path.exists(res.pdf_path):
        size = os.path.getsize(res.pdf_path)
        print(f"\n>>> SUCCESS: Generated {res.pdf_path} ({size:,} bytes)")
        return res.pdf_path
    else:
        print("\n>>> FAILED: Could not generate enhanced PDF")
        return None

if __name__ == "__main__":
    generate_enhanced()
