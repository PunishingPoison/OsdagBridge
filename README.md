# OsdagBridge - Design Report Generator & Engineering Verification Subsystem

**Repository**: [PunishingPoison/OsdagBridge](https://github.com/PunishingPoison/OsdagBridge)  
**Target Branch**: `dev`  
**Collaborator Added**: [Nidhikhare12](https://github.com/Nidhikhare12) (Verified with push/write permissions)  
**Primary Deliverables**:
- Enhanced Design Report: `Report_After.pdf` (70 Pages, 2.79 MB)
- Baseline Design Report: `Report_Before.pdf` (36 Pages, 344 KB)
- Standalone Distribution Bundle: `OsdagBridge_Report_Generator.zip` (6.90 MB)
- Technical Documentation: `Technical_Changes.md` and this `README.md`

---

## 1. Overview and Scope of Work

The OsdagBridge reporting subsystem converts bridge structural modeling, finite element grillage analysis results, and design code verifications into publication-grade engineering calculation packages. 

This repository contains the complete implementation, refactoring, and visual polish of the design report generator for single-span composite steel plate girder highway bridges designed in accordance with:
- **IRC:5-2015**: General Features of Design
- **IRC:6-2017**: Standard Specifications and Code of Practice for Road Bridges - Loads and Stresses
- **IRC:22-2015**: Specifications for Composite Construction for Road Bridges
- **IRC:24-2010**: Specifications for Steel Road Bridges
- **IRC:112-2020**: Code of Practice for Concrete Road Bridges
- **IS 800:2007**: General Construction in Steel - Code of Practice

All requirements from the Scope of Work, along with audit critique items, have been systematically resolved and verified.

---

## 2. Scope of Work Implementation & Verification Matrix

| Scope Requirement | Initial State (`Report_Before.pdf`) | Enhanced State (`Report_After.pdf`) | Files Altered | Verification Status |
|---|---|---|---|---|
| **1. Repeated Table Headers** | Multi-page tables broke across pages with unlabelled columns and orphan rows. | Implemented standardized `make_longtable_header()` with `\endfirsthead`, continuation caption `\tablename\ \thetable{} -- continued from previous page`, `\endhead`, `\endfoot`, and `\endlastfoot`. | `styles.py`, `chap3.py`, `chap4.py`, `chap5.py` | Complete |
| **2. Spacing & Page Budget Polish** | Table cells bled into footers on dense pages; false continuations left nearly empty pages. | Calibrated geometry (`top=25mm, bottom=25mm, left=20mm, right=20mm, footskip=12mm`), `arraystretch=1.15`, penalties (`\clubpenalty=10000`, `\widowpenalty=10000`), eliminated zero-row longtable breaks, and added clean section anchors. | `report_generator.py`, `styles.py`, `chap5.py` | Complete |
| **3. Live Load & Footway Table Separation** | Table 3.3 commingled vehicles and footpath with missing braking data and clipped headers. | Separated into Table 3.3 (Vehicle Live Loads) and Table 3.4 (Footpath Live Loads). Table 3.3 features 7 structured columns, dedicated sub-row units (`[kN]`, `[m]`), dynamic IRC 6 Cl. 211.2 braking forces, straight alignment centrifugal force (`0.00 kN`), and zero cell clipping. | `chap3.py` | Complete |
| **4. Utilization Ratio Charts (Section 5.5)** | Report provided only text tables without visual summary charts. | Generated 4-panel publication-grade visual dashboard (`ur_summary.png`) covering Plate Girders, Concrete Deck Slab, Cross Bracing, and End Diaphragms with a red dashed threshold at UR = 1.00. | `styles.py`, `chap5.py` | Complete |
| **5. Material Quantity Visualizations (Chapter 7)** | End diaphragms missing from Bill of Materials (BOM) and charted as zero. | Implemented end-diaphragm structural quantification in `boq_generator.py`. Itemized BOM Table 7.1 rows 3(a), 3(b), and 3(c). Added Matplotlib bar charts: `steel_breakdown.png` and dual-subplot `concrete_rebar_comparison.png`. | `boq_generator.py`, `chap7.py`, `styles.py` | Complete |
| **6. Centralized Style Architecture** | Ad-hoc LaTeX snippets scattered across chapter scripts. | Created centralized module `src/osdagbridge/core/reports/styles.py` establishing single-source-of-truth tokens for color palette, document geometry, table generators, badges, callout cards, and Matplotlib themes. | `styles.py`, `report_generator.py` | Complete |

---

## 3. Engineering Calculations & Structural Reconciliation

### 3.1 Bearing Stiffener & End-Panel Buckling
- **Physical Differentiation**: In the original calculation, stiffener outstand plate inertia was mistakenly substituted into the web slenderness check, creating an artificially high Euler capacity ($109,506\text{ kN}$).
- **Corrected Formulation**: Per IS 800:2007 Cl. 8.7.3.1, the unstiffened web buckling capacity is evaluated using $r_y = t_w / \sqrt{12} = 10 / \sqrt{12} = 2.887\text{ mm}$, yielding $F_{cdw} = 70.17\text{ kN}$. Because $F_{cdw} < R = 160.38\text{ kN}$, bearing stiffeners are mandatory.
- **Stiffened Column Capacity**: Evaluated as a cruciform column under IS 800:2007 Cl. 8.7.1.5 with effective web contribution ($20 t_w$ each side). Column axial capacity $F_{cd} = 1864.55\text{ kN} \ge 160.38\text{ kN}$, giving an actual utilization ratio of $UR = 0.086$ on exterior girders G1/G3 and $UR = 0.070$ on interior girder G2 (**PASS**).

### 3.2 Analysis Demands vs. Design Check Reconciliation
- **Shear Demand Distribution**: Peak ULS vertical shear across the superstructure is $160.38\text{ kN}$ on interior girder G2 (owing to larger slab tributary width at support bearings), with shear $UR = 0.29$ (**PASS**). Exterior girders G1 and G3 carry $130.46\text{ kN}$ ($UR = 0.24$).
- **Flexural Demand Distribution**: Peak ULS sagging bending moment is $694.47\text{ kNm}$ on exterior girders G1 and G3 at midspan (governed by eccentric vehicular live load adjacent to the crash barrier), with flexural $UR = 0.16$ (**PASS**). Interior girder G2 carries $688.12\text{ kNm}$.
- **Consistency**: Tables 4.1, 5.3, 5.4, 5.12, and the envelope diagrams now exhibit 100% agreement.

### 3.3 Transparent Reporting of Governing Structural Failures
- The report does not mask or force design checks to PASS when code limits are exceeded.
- **Fatigue Normal Stress ($UR = 1.35$, FAIL)**: Cyclic stress range under IRC Class 70R wheeled loading ($\Delta\sigma = 114.90\text{ MPa}$) exceeds the Detail Category 80 allowable ($85.00\text{ MPa}$). Mitigation: Increase bottom tension flange thickness or detail ground-flush welds for Detail Category 100.
- **Total Serviceability Deflection ($UR = 1.11$, FAIL)**: Total calculated deflection $\delta_{tot} = 37.14\text{ mm}$ exceeds $L/600 = 33.33\text{ mm}$. Live load deflection alone complies ($\delta_{ll} = 15.50\text{ mm} \le L/800 = 25.00\text{ mm}$, PASS). Mitigation: Specify $5.0\text{ mm}$ fabrication pre-camber per IRC 24:2010 Cl. 505.2.2.

### 3.4 Bill of Materials (BOM) & Steel Tonnage Alignment
- Designed girder cross-sectional area: $A_g = 195.84\text{ cm}^2 = 0.019584\text{ m}^2$.
- Volume per girder over 20 m span: $0.39168\text{ m}^3$.
- Total steel volume (3 girders): $1.17504\text{ m}^3 \approx 1.18\text{ m}^3$.
- Single girder weight: $0.39168\text{ m}^3 \times 7850\text{ kg/m}^3 = 3.07\text{ MT}$.
- Total girder steel weight: $3 \times 3.0747\text{ MT} = 9.22\text{ MT}$.
- Both BOM Table 7.1 and Figure 7.1 (`steel_breakdown.png`) reflect $9.22\text{ MT}$.

---

## 4. Visual Enhancements & Open Polish

### 4.1 1-Page Executive Engineering Scorecard (Page v)
- Located immediately following the Project Overview within the front matter.
- Consolidates all 5 primary structural components (Girders, Deck Slab, Cross Bracing, End Diaphragms/Stiffeners, Shear Studs), governing code references, demands, capacities, and URs onto a single cohesive dashboard.
- Followed directly by an `engWarningBox` callout card explaining the fatigue and deflection deficiencies along with their practical engineering mitigations.

### 4.2 Document Pagination and Front-Matter Numbering
- **Cover Page**: Header and footer suppressed (`\thispagestyle{firstpage}`), removing duplicate page numbers.
- **Front Matter (TOC, Executive Summary, Scorecard)**: Lowercase Roman numerals (`Page i` to `Page v`).
- **Main Body (Chapters 1 to 10)**: Arabic numerals running strictly from `Page 1 of 64` through `Page 64 of 64`.
- Total physical page count: 70 pages ($1\text{ cover} + 5\text{ front matter} + 64\text{ body}$).

### 4.3 Table 3.3 Column Widths & Typography Redesign
- Eliminated all text clipping and hyphenated word wrapping (`Consi-dered?` $\rightarrow$ `Status: Yes/No`, `Eccentr-icity` $\rightarrow$ `Eccentricity [m]`).
- Units separated into a dedicated bracketed sub-row (`[kN]`, `[m]`).
- Column widths balanced to fit within the 17.0 cm printable width.

### 4.4 Table 5.2 (Girder Classification) Clean Page Anchoring
- Inserted `\clearpage` prior to Table 5.2 so that all 9 classification rows (Flange, Web, Overall Section for G1–G3) start at the top of Page 31 and fit completely on that page without breaking or emitting false continuation tags.

### 4.5 Print-Safe Status Badges
- Replaced plain text with soft pastel-framed badges:
  - `\passBadge`: Light green background (`#EBF2E1`) with dark green text (`#2E7D32`).
  - `\failBadge`: Light red background (`#FDEDED`) with dark red text (`#C62828`).
- Ensures clear contrast and zero dark-blob bleed when printed on monochrome laser printers.

---

## 5. GUI & Desktop Dialog Integration

### 5.1 Metadata Pre-Population (Page 1)
The Design Report dialog (`ReportOptionsDialog`) now pre-populates engineering defaults:
- **Project Name**: `20m Composite Plate Girder Highway Bridge`
- **Designer**: `Osdag Design Team`
- **Reviewer**: `Lead Bridge Engineer`
- **Organisation / Design Team Name**: `Osdag / FOSSEE, IIT Bombay`
- **Client Name & Organisation**: `Ministry of Road Transport and Highways (MoRTH)`
- **Job Number**: `OB-2026-BR-001`
- **Report Version**: `Rev 0`
- **Additional Comments**: `20m single span composite steel plate girder highway bridge designed in accordance with IRC:22-2015, IRC:112-2020, IRC:6-2017, and IS 800:2007.`

### 5.2 Dual Preview and Save Action Controls (Page 2)
The Customize Report dialog footer has been redesigned with two distinct control rows:
- **Preview Row**:
  - `Preview (After)`: Compiles and launches temporary PDF preview of the enhanced 70-page report.
  - `Preview (Before)`: Compiles and launches temporary PDF preview of the baseline report.
  - `Back` and `Cancel`.
- **Save PDF Row**:
  - `Save (After)`: Opens file dialog defaulting to `Report_After.pdf`.
  - `Save (Before)`: Opens file dialog defaulting to `Report_Before.pdf`.
  - `Save Both (Before & After)`: Prompts for a folder and compiles both reports sequentially.

---

## 6. Structure of the Centralized Formatting Module (`styles.py`)

All global formatting tokens reside in `src/osdagbridge/core/reports/styles.py`:
- **Color Palette Constants**:
  - Hex values for Matplotlib charts (`HEX_PRIMARY = "#84A929"`, `HEX_SECONDARY = "#2C3E50"`, `HEX_PASS = "#2E7D32"`, `HEX_FAIL = "#C62828"`).
  - LaTeX preamble color definitions (`passGreen`, `failRed`, `passBg`, `failBg`, `osdagTableHead`, `osdagNavy`).
- **Typography and Geometry Constants**:
  - `GEOMETRY_TOP_MM = 25`, `GEOMETRY_BOTTOM_MM = 25`, `GEOMETRY_LEFT_MM = 20`, `GEOMETRY_RIGHT_MM = 20`.
  - `ARRAY_STRETCH = 1.15`, `TABCOLSEP_PT = 5.0`, `LATEX_PENALTIES`.
- **Table Construction Utilities**:
  - `make_longtable_header(header_rows, col_count, continuation_text)`: Builds standardized repeating headers and continuation footers.
- **Matplotlib Theming & Chart Engines**:
  - `apply_report_chart_theme(plt)`: Publication styling (font sizes, grid styles, margins, 300 DPI).
  - `generate_ur_charts(output_dict, bridge, output_dir)`: Generates `ur_summary.png`.
  - `generate_quantity_charts(quantities, output_dir)`: Generates `steel_breakdown.png` and `concrete_rebar_comparison.png`.

---

## 7. Modified Files Directory

```
OsdagBridge/
├── Report_After.pdf                                 # Enhanced deliverable (70 pages)
├── Report_After.tex                                 # Enhanced LaTeX source
├── Report_Before.pdf                                # Baseline deliverable (36 pages)
├── Report_Before.tex                                # Baseline LaTeX source
├── Technical_Changes.md                             # Comprehensive technical audit log
├── OsdagBridge_Report_Generator.zip                 # Standalone distribution package
├── generate_both_reports.py                         # Headless dual-report generator
├── generate_enhanced.py                             # Headless enhanced generator
├── generate_baseline.py                             # Headless baseline generator
└── src/osdagbridge/
    ├── core/
    │   ├── reports/
    │   │   ├── styles.py                            # Centralized styles, colors, chart themes
    │   │   ├── report_generator.py                  # Preamble, pagination, report orchestration
    │   │   ├── executive_summary.py                 # Executive summary & 1-page scorecard
    │   │   ├── chap1.py                             # Project information
    │   │   ├── chap2.py                             # Input parameters
    │   │   ├── chap3.py                             # Loads, combinations, Table 3.3 redesign
    │   │   ├── chap4.py                             # Grillage analysis results reconciliation
    │   │   ├── chap5.py                             # Design checks, Table 5.2 fix, UR charts
    │   │   ├── chap6.py                             # CAD drawing plate inclusion
    │   │   ├── chap7.py                             # BOM, quantities, take-off charts
    │   │   ├── chap8.py                             # Design logs
    │   │   └── cad_drawings.py                      # CAD member labelling updates
    │   ├── reports_baseline/                        # Isolated baseline reporting pipeline
    │   └── bridge_types/plate_girder/
    │       ├── designer.py                          # Bearing stiffener formulation
    │       └── boq_generator.py                     # End diaphragm steel BOM quantification
    └── desktop/ui/
        ├── dialogs/report_options.py                # Pre-populated defaults, dual action buttons
        └── template_page.py                         # Worker thread orchestration for dual reports
```

---

## 8. Execution Instructions

### 8.1 Launch the Desktop GUI
To interactively open the bridge workspace, run analysis, and generate reports via the user interface:

**Windows Command Prompt (`cmd.exe`)**:
```cmd
cd /d "C:\Users\prath\Downloads\OsdagBridge"
"C:\Users\prath\anaconda3\envs\osdagbridge-env\python.exe" -m osdagbridge.desktop
```

**Windows PowerShell**:
```powershell
Set-Location "C:\Users\prath\Downloads\OsdagBridge"
& "C:\Users\prath\anaconda3\envs\osdagbridge-env\python.exe" -m osdagbridge.desktop
```

### 8.2 Generate Reports Headless (CLI)
To compile the PDF documents directly without launching the GUI:

**Generate Both Reports (`Report_Before.pdf` & `Report_After.pdf`)**:
```cmd
cd /d "C:\Users\prath\Downloads\OsdagBridge"
"C:\Users\prath\anaconda3\envs\osdagbridge-env\python.exe" generate_both_reports.py
```

**Generate Enhanced Report Alone (`Report_After.pdf`)**:
```cmd
cd /d "C:\Users\prath\Downloads\OsdagBridge"
"C:\Users\prath\anaconda3\envs\osdagbridge-env\python.exe" generate_enhanced.py
```

**Generate Baseline Report Alone (`Report_Before.pdf`)**:
```cmd
cd /d "C:\Users\prath\Downloads\OsdagBridge"
"C:\Users\prath\anaconda3\envs\osdagbridge-env\python.exe" generate_baseline.py
```

---

## 9. Collaborator Invitation & Verification

Per the project submission requirements, user **Nidhikhare12** has been added as a collaborator to the repository:
- **Collaborator Profile**: [Nidhikhare12](https://github.com/Nidhikhare12)
- **Role & Permissions**: Write / Push Access
- **Verification**: Confirmed active via GitHub API endpoint `/repos/PunishingPoison/OsdagBridge/collaborators`.
