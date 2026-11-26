import os
import subprocess

REPORTS_DIR = r"E:\Med-Project\reports"
EDGE_PATH = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

html_content = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>Lab Equipment Requisition Form - Clinic Patient Measurement System</title>
<style>
    @page {
        size: A4;
        margin: 14mm 16mm 14mm 16mm;
    }
    * {
        box-sizing: border-box;
        -webkit-print-color-adjust: exact !important;
        print-color-adjust: exact !important;
    }
    body {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        color: #1e293b;
        background-color: #ffffff;
        line-height: 1.45;
        font-size: 9pt;
        margin: 0;
        padding: 0;
    }
    .requisition-header {
        border-bottom: 2px solid #064e3b;
        padding-bottom: 12px;
        margin-bottom: 16px;
        display: flex;
        justify-content: space-between;
        align-items: flex-end;
    }
    .requisition-header h1 {
        margin: 0 0 4px 0;
        font-size: 16pt;
        color: #064e3b;
        font-weight: 800;
        letter-spacing: -0.5px;
    }
    .requisition-header .sub {
        font-size: 9.5pt;
        color: #0f766e;
        font-weight: 600;
    }
    .date-badge {
        font-size: 8.5pt;
        color: #64748b;
        text-align: right;
    }
    .meta-box {
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 6px;
        padding: 10px 14px;
        margin-bottom: 16px;
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 8px 16px;
        font-size: 8.5pt;
    }
    .meta-box div span {
        color: #64748b;
        font-weight: 600;
        text-transform: uppercase;
        font-size: 7.5pt;
        display: block;
    }
    .meta-box div strong {
        color: #0f172a;
        font-size: 9pt;
    }
    h2 {
        color: #064e3b;
        font-size: 11pt;
        font-weight: 700;
        margin-top: 14px;
        margin-bottom: 8px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    table {
        width: 100%;
        border-collapse: collapse;
        margin-bottom: 16px;
        font-size: 8.5pt;
    }
    th, td {
        padding: 7px 9px;
        text-align: left;
        border: 1px solid #cbd5e1;
        vertical-align: middle;
    }
    th {
        background-color: #064e3b;
        color: #ffffff;
        font-weight: 700;
        text-transform: uppercase;
        font-size: 7.5pt;
        letter-spacing: 0.5px;
    }
    tr:nth-child(even) td {
        background-color: #f8fafc;
    }
    .highlight-row td {
        background-color: #ecfdf5 !important;
        font-weight: 600;
    }
    .badge {
        display: inline-block;
        padding: 2px 6px;
        border-radius: 4px;
        font-size: 7pt;
        font-weight: 700;
        text-transform: uppercase;
    }
    .badge-primary { background-color: #d1fae5; color: #065f46; border: 1px solid #a7f3d0; }
    .badge-secondary { background-color: #e0f2fe; color: #0369a1; border: 1px solid #bae6fd; }

    .note-box {
        border-left: 3.5px solid #059669;
        background-color: #ecfdf5;
        padding: 8px 12px;
        border-radius: 0 4px 4px 0;
        margin: 14px 0;
        font-size: 8.5pt;
    }
    .note-box strong {
        color: #065f46;
        display: block;
        margin-bottom: 2px;
        text-transform: uppercase;
        font-size: 7.5pt;
    }
    .signature-section {
        margin-top: 32px;
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 20px;
        text-align: center;
        padding-top: 10px;
    }
    .sig-box {
        border-top: 1px solid #94a3b8;
        padding-top: 6px;
        font-size: 8pt;
        color: #475569;
    }
    .sig-box strong {
        display: block;
        color: #0f172a;
        font-size: 8.5pt;
    }
</style>
</head>
<body>

<div class="requisition-header">
    <div>
        <h1>DEPARTMENT LAB EQUIPMENT REQUISITION FORM</h1>
        <div class="sub">Project: Clinic Patient Measurement System (IoT Vitals Station)</div>
    </div>
    <div class="date-badge">
        <strong>Date:</strong> November 2026<br>
        <strong>Academic Year:</strong> 2026–2027
    </div>
</div>

<div class="meta-box">
    <div>
        <span>Project Title</span>
        <strong>Smart Clinic Patient Measurement &amp; BMI Tracking System</strong>
    </div>
    <div>
        <span>Hardware Architecture</span>
        <strong>Raspberry Pi 4 Edge Client + Cloud IoT Backend</strong>
    </div>
    <div>
        <span>Repository / Work Done</span>
        <strong>https://github.com/vkvarun719/Med-Project</strong>
    </div>
    <div>
        <span>Current Status</span>
        <strong>Backend &amp; UI Ready &bull; Awaiting Physical Station Assembly</strong>
    </div>
</div>

<h2>Requested Hardware &amp; Laboratory Components</h2>
<p style="font-size: 8.5pt; color: #475569; margin-bottom: 8px;">
Please issue the following equipment required for assembling and demonstrating the physical clinic measurement station:
</p>

<table>
    <thead>
        <tr>
            <th style="width: 5%;">#</th>
            <th style="width: 28%;">Equipment / Item Description</th>
            <th style="width: 14%;">Qty / Spec</th>
            <th style="width: 15%;">Category</th>
            <th>Technical Purpose / Subsystem</th>
        </tr>
    </thead>
    <tbody>
        <tr class="highlight-row">
            <td><strong>1</strong></td>
            <td><strong>Lab Modified Weighing Scale</strong><br><small style="color: #047857;">(Customized digital scale available with Faculty)</small></td>
            <td><strong>1 Unit</strong></td>
            <td><span class="badge badge-primary">Lab Customized</span></td>
            <td><strong>Weight Measurement:</strong> Embedded sensor platform with modified load cells / ESP32 interface to stream live patient weight.</td>
        </tr>
        <tr>
            <td><strong>2</strong></td>
            <td><strong>Raspberry Pi Board</strong><br><small>Raspberry Pi 4 Model B (or Pi 3B+)</small></td>
            <td>1 Unit</td>
            <td><span class="badge badge-secondary">Controller</span></td>
            <td><strong>Central Station Edge Controller:</strong> Runs stability algorithms, state machine, and offline SQLite resilience daemon.</td>
        </tr>
        <tr>
            <td><strong>3</strong></td>
            <td><strong>Raspberry Pi Power Adapter</strong><br><small>5V / 3A Type-C Adapter</small></td>
            <td>1 Unit</td>
            <td><span class="badge badge-secondary">Power</span></td>
            <td>Stable power supply for the Raspberry Pi board and connected peripherals.</td>
        </tr>
        <tr>
            <td><strong>4</strong></td>
            <td><strong>MicroSD Card</strong><br><small>16GB or 32GB Class 10</small></td>
            <td>1 Unit</td>
            <td><span class="badge badge-secondary">Storage</span></td>
            <td>Hosts Raspberry Pi OS (64-bit Lite) and the clinic station software.</td>
        </tr>
        <tr>
            <td><strong>5</strong></td>
            <td><strong>HC-SR04 Ultrasonic Sensor</strong><br><small>5V Ultrasonic Ranging Module</small></td>
            <td>1 Unit</td>
            <td><span class="badge badge-secondary">Sensor</span></td>
            <td><strong>Height Measurement:</strong> Overhead stadiometer distance sensor to calculate height (Ceiling &minus; Head Distance).</td>
        </tr>
        <tr>
            <td><strong>6</strong></td>
            <td><strong>USB Handheld Barcode Scanner</strong><br><small>Standard USB HID Keyboard Gun</small></td>
            <td>1 Unit</td>
            <td><span class="badge badge-secondary">Input Device</span></td>
            <td><strong>Patient Identification:</strong> Scans the unique 8-character Code128 patient barcode cards to unlock measurement session.</td>
        </tr>
        <tr>
            <td><strong>7</strong></td>
            <td><strong>Voltage Divider Resistors</strong><br><small>1&times; 1k&Omega; and 1&times; 2k&Omega; (or 1k&Omega; + 2.2k&Omega;)</small></td>
            <td>1 Pair</td>
            <td><span class="badge badge-secondary">Safety Circuit</span></td>
            <td>Steps down HC-SR04 Echo pin 5V signal to 3.3V to protect Raspberry Pi GPIO pin from electrical damage.</td>
        </tr>
        <tr>
            <td><strong>8</strong></td>
            <td><strong>Breadboard &amp; Jumper Wires</strong><br><small>Mini Breadboard + 15 M-F / F-F wires</small></td>
            <td>1 Set</td>
            <td><span class="badge badge-secondary">Prototyping</span></td>
            <td>Connecting sensors to the Raspberry Pi GPIO pins and voltage divider.</td>
        </tr>
        <tr>
            <td><strong>9</strong></td>
            <td><strong>HX711 24-bit ADC Module</strong><br><small>Load Cell Amplifier Board</small></td>
            <td>1 Unit (Backup)</td>
            <td><span class="badge badge-secondary">Amplifier</span></td>
            <td>Used if the modified weighing machine requires external ADC amplification to the Pi.</td>
        </tr>
    </tbody>
</table>

<div class="note-box">
    <strong>Technical Readiness Note</strong>
    All cloud backend services, Neon PostgreSQL database schemas, and React dashboards are <strong>100% completed and verified</strong>. A hardware simulation mode (<code>python main.py --mock</code>) has also been implemented so that software testing and review can proceed immediately while the hardware components are being issued.
</div>

<div class="signature-section">
    <div class="sig-box">
        <strong>Student / Applicant</strong>
        Signature &amp; Date
    </div>
    <div class="sig-box">
        <strong>Project Guide / Faculty (Ma'am)</strong>
        Recommendation &amp; Signature
    </div>
    <div class="sig-box">
        <strong>Lab In-Charge / HOD</strong>
        Approval &amp; Issue Sign-off
    </div>
</div>

</body>
</html>
"""

html_path = os.path.join(REPORTS_DIR, "lab_requisition.html")
pdf_path = os.path.join(REPORTS_DIR, "Clinic_System_Lab_Equipment_Requisition.pdf")

with open(html_path, "w", encoding="utf-8") as f:
    f.write(html_content)

cmd = [
    EDGE_PATH,
    "--headless",
    "--disable-gpu",
    "--no-pdf-header-footer",
    f"--print-to-pdf={pdf_path}",
    html_path
]

res = subprocess.run(cmd, capture_output=True, text=True)
if res.returncode == 0 and os.path.exists(pdf_path):
    print(f"SUCCESS: Generated {pdf_path} ({os.path.getsize(pdf_path)} bytes)")
else:
    print(f"Error compiling PDF: {res.stderr}")
