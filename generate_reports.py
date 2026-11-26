import os
import subprocess

REPORTS_DIR = r"E:\Med-Project\reports"
EDGE_PATH = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

COMMON_CSS = """
<style>
    @page {
        size: A4;
        margin: 14mm 14mm 16mm 14mm;
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
        line-height: 1.5;
        font-size: 9.5pt;
        margin: 0;
        padding: 0;
    }
    .header-banner {
        background: linear-gradient(135deg, #064e3b 0%, #047857 50%, #10b981 100%);
        color: #ffffff;
        padding: 22px;
        border-radius: 8px;
        margin-bottom: 18px;
    }
    .header-banner.blue-theme {
        background: linear-gradient(135deg, #1e3a8a 0%, #2563eb 50%, #38bdf8 100%);
    }
    .header-banner h1 {
        margin: 0 0 6px 0;
        font-size: 20pt;
        font-weight: 800;
        letter-spacing: -0.5px;
    }
    .header-banner .subtitle {
        font-size: 10.5pt;
        color: #d1fae5;
        font-weight: 600;
        margin-bottom: 12px;
    }
    .header-banner.blue-theme .subtitle {
        color: #e0f2fe;
    }
    .meta-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 10px;
        background: rgba(255, 255, 255, 0.15);
        padding: 10px 14px;
        border-radius: 6px;
        font-size: 8.5pt;
    }
    .meta-item strong {
        color: #a7f3d0;
        display: block;
        text-transform: uppercase;
        font-size: 7.5pt;
        letter-spacing: 0.5px;
    }
    .header-banner.blue-theme .meta-item strong {
        color: #bae6fd;
    }
    h2 {
        color: #064e3b;
        font-size: 13pt;
        font-weight: 700;
        border-bottom: 2px solid #e2e8f0;
        padding-bottom: 5px;
        margin-top: 20px;
        margin-bottom: 10px;
        page-break-after: avoid;
    }
    .blue-theme-text h2 {
        color: #1e3a8a;
    }
    h3 {
        color: #0f766e;
        font-size: 10.5pt;
        font-weight: 600;
        margin-top: 14px;
        margin-bottom: 6px;
        page-break-after: avoid;
    }
    .blue-theme-text h3 {
        color: #1d4ed8;
    }
    p {
        margin: 0 0 8px 0;
    }
    .callout {
        border-left: 4px solid #059669;
        background-color: #ecfdf5;
        padding: 10px 14px;
        border-radius: 0 6px 6px 0;
        margin: 12px 0;
    }
    .callout.danger {
        border-left-color: #dc2626;
        background-color: #fef2f2;
    }
    .callout.warning {
        border-left-color: #d97706;
        background-color: #fffbeb;
    }
    .callout.info {
        border-left-color: #2563eb;
        background-color: #eff6ff;
    }
    .callout-title {
        font-weight: 700;
        font-size: 9pt;
        margin-bottom: 4px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .callout.danger .callout-title { color: #b91c1c; }
    .callout.warning .callout-title { color: #b45309; }
    .callout.info .callout-title { color: #1d4ed8; }
    .callout.default .callout-title { color: #047857; }

    table {
        width: 100%;
        border-collapse: collapse;
        margin: 10px 0 14px 0;
        font-size: 8.5pt;
    }
    th, td {
        padding: 7px 9px;
        text-align: left;
        border-bottom: 1px solid #e2e8f0;
        vertical-align: top;
    }
    th {
        background-color: #f1f5f9;
        color: #334155;
        font-weight: 700;
        text-transform: uppercase;
        font-size: 7.5pt;
        letter-spacing: 0.5px;
    }
    tr:nth-child(even) td {
        background-color: #f8fafc;
    }
    .badge {
        display: inline-block;
        padding: 2px 7px;
        border-radius: 10px;
        font-size: 7.5pt;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.3px;
        white-space: nowrap;
    }
    .badge-done { background-color: #d1fae5; color: #065f46; border: 1px solid #a7f3d0; }
    .badge-partial { background-color: #fef3c7; color: #92400e; border: 1px solid #fde68a; }
    .badge-missing { background-color: #fee2e2; color: #991b1b; border: 1px solid #fecaca; }
    .badge-critical { background-color: #7f1d1d; color: #ffffff; }

    .code-box {
        background-color: #0f172a;
        color: #e2e8f0;
        font-family: "Courier New", Courier, monospace;
        font-size: 7.8pt;
        padding: 10px 14px;
        border-radius: 6px;
        margin: 8px 0;
        white-space: pre-wrap;
        word-break: break-all;
    }
    .diagram-img {
        width: 100%;
        max-height: 340px;
        object-fit: contain;
        border: 1px solid #cbd5e1;
        border-radius: 6px;
        margin: 10px 0;
        background-color: #000000;
    }
    .progress-bar-container {
        background-color: #e2e8f0;
        border-radius: 6px;
        height: 10px;
        width: 100%;
        overflow: hidden;
        margin: 4px 0;
    }
    .progress-bar {
        background-color: #10b981;
        height: 100%;
    }
    .grid-2 {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 14px;
        margin: 10px 0;
    }
    .metric-card {
        border: 1px solid #e2e8f0;
        border-radius: 6px;
        padding: 12px;
        background-color: #ffffff;
    }
    .metric-card .num {
        font-size: 18pt;
        font-weight: 800;
        color: #0f766e;
    }
    .metric-card .label {
        font-size: 8pt;
        text-transform: uppercase;
        color: #64748b;
        font-weight: 600;
    }
    .page-break {
        page-break-before: always;
    }
    ul, ol {
        margin: 4px 0 8px 18px;
        padding: 0;
    }
    li {
        margin-bottom: 4px;
    }
    .footer-note {
        margin-top: 18px;
        padding-top: 8px;
        border-top: 1px solid #e2e8f0;
        font-size: 7.5pt;
        color: #94a3b8;
        display: flex;
        justify-content: space-between;
    }
</style>
"""

# HTML 1: Work Done
html_audit = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>Clinic Patient Measurement System - Work Done & Audit Report</title>
""" + COMMON_CSS + """
</head>
<body>

<div class="header-banner">
    <h1>Clinic Patient Measurement System</h1>
    <div class="subtitle">AUDIT REPORT & PREVIOUS WORK EVALUATION (DELIVERABLE 1)</div>
    <div class="meta-grid">
        <div class="meta-item"><strong>Project Stage</strong> Handover / Audit</div>
        <div class="meta-item"><strong>Date</strong> November 2026</div>
        <div class="meta-item"><strong>Lead Role</strong> Senior Full-Stack + IoT Engineer</div>
        <div class="meta-item"><strong>Overall Progress</strong> ~22% Complete</div>
    </div>
</div>

<h2>1. Executive Summary & Root Architecture Findings</h2>
<p>
An exhaustive line-by-line audit of both source repositories left by the previous senior developer was conducted:
</p>
<ul>
    <li><strong>Frontend Repository:</strong> <code>https://github.com/Giridhar257/Weighing_front</code></li>
    <li><strong>Hardware/Automation Repository:</strong> <code>https://github.com/Giridhar257/Weighing_automation</code></li>
</ul>

<div class="callout danger">
    <div class="callout-title">Critical Architectural Inversion Identified</div>
    <strong>The Raspberry Pi embedded automation code was never implemented.</strong> The repository named <code>Weighing_automation</code> is in reality a <strong>FastAPI backend</strong> with a 30-line standard input (<code>sys.stdin</code>) scanner reader script. There is <strong>zero GPIO code, zero load cell/HX711 integration, zero ultrasonic height code, no stability filter, and no systemd daemon</strong>. The physical measurement layer on the Raspberry Pi—which is the heart of the clinic station—must be engineered completely from the ground up.
</div>

<div class="grid-2">
    <div class="metric-card">
        <div class="label">Repository Progress Breakdown</div>
        <div style="margin-top: 8px;">
            <div style="display:flex; justify-content:space-between; font-size:8pt; margin-bottom:2px;">
                <span>React Frontend</span><strong>35%</strong>
            </div>
            <div class="progress-bar-container"><div class="progress-bar" style="width: 35%;"></div></div>
            
            <div style="display:flex; justify-content:space-between; font-size:8pt; margin-bottom:2px; margin-top:6px;">
                <span>FastAPI Backend</span><strong>40%</strong>
            </div>
            <div class="progress-bar-container"><div class="progress-bar" style="width: 40%; background-color:#3b82f6;"></div></div>
            
            <div style="display:flex; justify-content:space-between; font-size:8pt; margin-bottom:2px; margin-top:6px;">
                <span>Raspberry Pi IoT Station</span><strong>5%</strong>
            </div>
            <div class="progress-bar-container"><div class="progress-bar" style="width: 5%; background-color:#ef4444;"></div></div>

            <div style="display:flex; justify-content:space-between; font-size:8pt; margin-bottom:2px; margin-top:6px;">
                <span>Docker & Cloud Deploy</span><strong>0%</strong>
            </div>
            <div class="progress-bar-container"><div class="progress-bar" style="width: 0%; background-color:#64748b;"></div></div>
        </div>
    </div>
    
    <div class="metric-card">
        <div class="label">Critical Security & Integrity Vulnerabilities</div>
        <ul style="font-size:8pt; color:#991b1b; margin-top:6px;">
            <li><strong>Hardcoded Neon DB credentials:</strong> Live production Postgres URI with cleartext username & password found committed in <code>database.py</code>.</li>
            <li><strong>Hardcoded LAN IPs:</strong> Backend generates barcode URLs referencing local private IP <code>10.65.139.44</code>.</li>
            <li><strong>Unauthenticated API:</strong> Scanner script and frontend communicate with zero API Key authentication.</li>
            <li><strong>Polled Live-Weight:</strong> Frontend polls every 300ms, causing high network traffic and lockups.</li>
        </ul>
    </div>
</div>

<h2>2. End-to-End Target Architecture Diagram</h2>
<p>The system is designed for an automated clinic station interacting seamlessly with cloud infrastructure:</p>
<img class="diagram-img" src="architecture_diagram.jpg" alt="Clinic System Architecture Diagram">

<div class="page-break"></div>

<h2>3. Detailed Repository Audit</h2>

<h3>3.1 Frontend Repository (<code>Weighing_front</code>)</h3>
<p><strong>Stack:</strong> React 19.2.5, React Scripts 5.0.1, Chart.js 4.5.1, React-Chartjs-2 5.3.1, Axios 1.15.2.</p>
<table>
    <thead>
        <tr>
            <th style="width: 25%;">Component / File</th>
            <th style="width: 15%;">Status</th>
            <th>Observed Behavior & Code Findings</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td><code>src/App.js</code> (Registration)</td>
            <td><span class="badge badge-partial">Partial</span></td>
            <td>Collects Name, Age, Gender, Phone. Submits to <code>POST /register</code>. Lacks phone format validation, empty check guards, and loading feedback.</td>
        </tr>
        <tr>
            <td><code>src/App.js</code> (Barcode Card)</td>
            <td><span class="badge badge-partial">Partial</span></td>
            <td>Renders barcode string and an <code>&lt;img&gt;</code> pointing to <code>http://10.65.139.44:8000/barcodes/...</code>. Fails when IP changes. No printable sticker layout.</td>
        </tr>
        <tr>
            <td><code>src/App.js</code> (Live Polling)</td>
            <td><span class="badge badge-missing">Defective</span></td>
            <td>Runs a <code>setInterval</code> every 300ms to <code>GET /live-weight</code>. Lacks WebSocket or debounce; causes high memory churn and unneeded server load.</td>
        </tr>
        <tr>
            <td><code>src/App.js</code> (Chart & History)</td>
            <td><span class="badge badge-partial">Partial</span></td>
            <td>Renders a Line chart of historical weights. <strong>Hardcoded filter:</strong> Drops any weight below 20 kg (<code>w.weight > 20</code>), breaking pediatric usability. Height and BMI are completely absent.</td>
        </tr>
        <tr>
            <td><code>src/App.js</code> (Environment Config)</td>
            <td><span class="badge badge-critical">Hardcoded</span></td>
            <td>Line 43: <code>const API = "https://weighingautomation-production.up.railway.app";</code>. No <code>.env</code> file or <code>process.env.REACT_APP_API_BASE_URL</code> used.</td>
        </tr>
    </tbody>
</table>

<h3>3.2 Automation Repository (<code>Weighing_automation</code>)</h3>
<p><strong>Stack:</strong> Python 3.12, FastAPI 0.110.0, SQLAlchemy 2.0.49, psycopg2-binary 2.9.12, python-barcode 0.16.1, Pillow 11.3.0, Pydantic 2.6.4.</p>
<table>
    <thead>
        <tr>
            <th style="width: 25%;">File</th>
            <th style="width: 15%;">Status</th>
            <th>Observed Functionality & Vulnerabilities</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td><code>database.py</code></td>
            <td><span class="badge badge-critical">Leak</span></td>
            <td>Contains plaintext Neon PostgreSQL password: <code>npg_vkGDa7Uj0uIN</code> and commented local password <code>Qwert585</code>. No environment variable fallback.</td>
        </tr>
        <tr>
            <td><code>models.py</code></td>
            <td><span class="badge badge-partial">Partial</span></td>
            <td>Defines <code>Patient</code> and <code>Weight</code>. Missing height column, BMI column, and proper timestamps. Spec requires <code>measurements</code> table.</td>
        </tr>
        <tr>
            <td><code>main.py</code></td>
            <td><span class="badge badge-partial">Partial</span></td>
            <td>FastAPI routes for <code>/register</code>, <code>/scan</code>, <code>/patient/{barcode}</code>, <code>/weight</code>, <code>/live-weight</code>. Has global in-memory state variables which are non-thread-safe and fail in multi-worker deployments.</td>
        </tr>
        <tr>
            <td><code>barcode_generator.py</code></td>
            <td><span class="badge badge-partial">Partial</span></td>
            <td>Generates Code128 barcodes using <code>uuid.uuid4()[:8]</code>. Does not verify whether the 8-character string collides with an existing patient barcode in database.</td>
        </tr>
        <tr>
            <td><code>scanner_to_api.py</code></td>
            <td><span class="badge badge-missing">Crude</span></td>
            <td>32-line loop reading <code>sys.stdin</code> and posting to Railway URL. No reconnection logic, no buffering, no session handling, and no hardware detection.</td>
        </tr>
        <tr>
            <td><code>patients.db</code></td>
            <td><span class="badge badge-critical">Pollution</span></td>
            <td>A 24KB SQLite test database checked directly into git repository history.</td>
        </tr>
        <tr>
            <td><code>openmrs_service.py</code></td>
            <td><span class="badge badge-missing">Empty</span></td>
            <td>Completely empty 0-byte file abandoned by the senior.</td>
        </tr>
    </tbody>
</table>

<div class="page-break"></div>

<h2>4. Raspberry Pi Hardware Reality Check</h2>
<table>
    <thead>
        <tr>
            <th style="width: 28%;">Specification Area</th>
            <th style="width: 32%;">Found in Senior's Code</th>
            <th>Required Engineering Specification</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td><strong>Pi Hardware Model</strong></td>
            <td>None specified (Code ran on laptop/cloud).</td>
            <td><strong>Raspberry Pi 4 Model B (2GB/4GB)</strong> or Pi 3B+.</td>
        </tr>
        <tr>
            <td><strong>Operating System</strong></td>
            <td>None. Railway Linux container in runtime.txt.</td>
            <td><strong>Raspberry Pi OS (64-bit Lite, Debian Bookworm)</strong>.</td>
        </tr>
        <tr>
            <td><strong>GPIO / Sensor Drivers</strong></td>
            <td>0 lines of code. No GPIO libraries imported.</td>
            <td><code>RPi.GPIO</code> / <code>gpiozero</code>, <code>hx711</code>, <code>pyserial</code>.</td>
        </tr>
        <tr>
            <td><strong>Weight Sensor</strong></td>
            <td>None (comment mentions <code>NO barcode from ESP</code>).</td>
            <td><strong>HX711 24-bit ADC + 4-cell Wheatstone Bridge Load Cells</strong>.</td>
        </tr>
        <tr>
            <td><strong>Height Sensor</strong></td>
            <td>Zero mention in entire codebase.</td>
            <td><strong>HC-SR04 Ultrasonic</strong> (or VL53L0X Time-of-Flight Laser Sensor).</td>
        </tr>
        <tr>
            <td><strong>Barcode Scanner</strong></td>
            <td>Commented USB HID VID:PID (1504:4608) / <code>sys.stdin</code>.</td>
            <td><strong>USB HID Keyboard emulation</strong> with evdev/stdin stream.</td>
        </tr>
        <tr>
            <td><strong>Stability Verification</strong></td>
            <td>None on device (crude simulated boolean in backend).</td>
            <td><strong>Rolling window filter:</strong> N consecutive values within tolerance.</td>
        </tr>
        <tr>
            <td><strong>Network Fault Tolerance</strong></td>
            <td>1-shot synchronous request with 5s timeout.</td>
            <td><strong>SQLite offline buffer queue (<code>buffer.db</code>)</strong> with background sync.</td>
        </tr>
        <tr>
            <td><strong>Boot & Process Control</strong></td>
            <td>Manual command line run.</td>
            <td><strong>Linux Systemd unit (<code>clinic-station.service</code>)</strong> with auto-restart.</td>
        </tr>
        <tr>
            <td><strong>Development Mocking</strong></td>
            <td>None.</td>
            <td><strong>Dual Mode:</strong> <code>MOCK_MODE=true</code> flag for laptop testing.</td>
        </tr>
    </tbody>
</table>

<h2>5. Target 10-Step Clinic Workflow: Audit Scorecard</h2>
<table>
    <thead>
        <tr>
            <th style="width: 6%;">Step</th>
            <th style="width: 30%;">Workflow Requirement</th>
            <th style="width: 14%;">Audit Status</th>
            <th>Gap Analysis & Remediation Needed</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td><strong>1</strong></td>
            <td><strong>Patient Registration (React UI)</strong></td>
            <td><span class="badge badge-partial">Partial (50%)</span></td>
            <td>Form exists. Needs form validation, clear user feedback, and responsive layout.</td>
        </tr>
        <tr>
            <td><strong>2</strong></td>
            <td><strong>Barcode Generation</strong></td>
            <td><span class="badge badge-partial">Partial (60%)</span></td>
            <td>Code128 generation works. Needs DB collision check and printable CSS card in UI.</td>
        </tr>
        <tr>
            <td><strong>3</strong></td>
            <td><strong>Barcode Scan (on Pi)</strong></td>
            <td><span class="badge badge-missing">Missing (10%)</span></td>
            <td>Only raw stdin script exists. Needs modular scanner driver with session binding.</td>
        </tr>
        <tr>
            <td><strong>4</strong></td>
            <td><strong>Live Measurement (on Pi)</strong></td>
            <td><span class="badge badge-missing">Missing (0%)</span></td>
            <td>Zero sensor drivers exist. Must write HX711 and HC-SR04 drivers + mock generators.</td>
        </tr>
        <tr>
            <td><strong>5</strong></td>
            <td><strong>Stability Check (on Pi)</strong></td>
            <td><span class="badge badge-missing">Missing (0%)</span></td>
            <td>Must implement on the Pi: buffers N readings within tolerance before transmitting.</td>
        </tr>
        <tr>
            <td><strong>6</strong></td>
            <td><strong>Data Transmission & Offline Buffer</strong></td>
            <td><span class="badge badge-missing">Missing (5%)</span></td>
            <td>Must implement local SQLite queue (<code>buffer.db</code>) with backoff retry worker.</td>
        </tr>
        <tr>
            <td><strong>7</strong></td>
            <td><strong>Backend Processing (FastAPI)</strong></td>
            <td><span class="badge badge-partial">Partial (50%)</span></td>
            <td>FastAPI routes exist. Must add height, calculate BMI, add validation, and API key auth.</td>
        </tr>
        <tr>
            <td><strong>8</strong></td>
            <td><strong>Database (Neon PostgreSQL)</strong></td>
            <td><span class="badge badge-partial">Partial (40%)</span></td>
            <td>Connected to Neon. Must update schema to <code>measurements</code> (with BMI) and use <code>.env</code>.</td>
        </tr>
        <tr>
            <td><strong>9</strong></td>
            <td><strong>Complete & Reset (State Machine)</strong></td>
            <td><span class="badge badge-missing">Missing (0%)</span></td>
            <td>Must build state machine: <code>IDLE -> SCANNED -> MEASURING -> STABLE -> SENT -> RESET</code>.</td>
        </tr>
        <tr>
            <td><strong>10</strong></td>
            <td><strong>History & Dashboard (React)</strong></td>
            <td><span class="badge badge-partial">Partial (30%)</span></td>
            <td>Weight chart exists. Must add Height, BMI tracking, BMI classification, and table view.</td>
        </tr>
    </tbody>
</table>

<div class="callout default" style="margin-top:16px;">
    <div class="callout-title">Conclusion & Recommendation</div>
    The previous senior left a working proof-of-concept for the database connection and basic React form, but completely neglected the Raspberry Pi hardware integration and architectural modularity. We will <strong>reuse and refactor</strong> the existing database models, barcode logic, and React components, while <strong>properly structuring</strong> the backend into a clean service and <strong>building the Raspberry Pi embedded client from scratch</strong>.
</div>

<div class="footer-note">
    <span>Clinic Patient Measurement System — Audit Report</span>
    <span>CONFIDENTIAL & PROPRIETARY</span>
</div>

</body>
</html>
"""

# HTML 2: Execution Plan
html_plan = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>Clinic Patient Measurement System - Execution Plan</title>
""" + COMMON_CSS + """
</head>
<body class="blue-theme-text">

<div class="header-banner blue-theme">
    <h1>Clinic Patient Measurement System</h1>
    <div class="subtitle">ENGINEERING EXECUTION PLAN & IMPLEMENTATION ROADMAP (DELIVERABLE 2)</div>
    <div class="meta-grid">
        <div class="meta-item"><strong>Target Architecture</strong> 3-Tier IoT / Cloud</div>
        <div class="meta-item"><strong>Deployment</strong> AWS EC2 + Docker</div>
        <div class="meta-item"><strong>Database</strong> Neon PostgreSQL</div>
        <div class="meta-item"><strong>Edge Client</strong> Raspberry Pi 4 (Python)</div>
    </div>
</div>

<h2>1. Target Architecture & Project Structure</h2>
<p>
To resolve the senior's architectural confusion, the repository will be structured cleanly into three independent, decoupled modules:
</p>

<div class="code-box">clinic-system/
|-- backend/                   # FastAPI Backend (Runs in Docker on EC2)
|   |-- app/
|   |   |-- main.py            # FastAPI Application entrypoint & routes
|   |   |-- config.py          # Pydantic Settings (.env loader)
|   |   |-- database.py        # SQLAlchemy engine & Neon session manager
|   |   |-- models.py          # Patient and Measurement DB models
|   |   |-- schemas.py         # Request/Response Pydantic schemas (Validation)
|   |   |-- crud.py            # Database query operations
|   |   |-- auth.py            # X-API-Key security header dependency
|   |   `-- barcode_utils.py   # Barcode generator with collision checking
|   |-- requirements.txt
|   |-- Dockerfile
|   `-- .env.example
|-- automation/                # Raspberry Pi Clinic Station Client (Runs on Pi)
|   |-- sensors/
|   |   |-- __init__.py
|   |   |-- weight.py          # HX711 Load Cell driver + Calibration + Mock
|   |   `-- height.py          # HC-SR04 Ultrasonic driver + Calibration + Mock
|   |-- scanner.py             # USB HID / Serial Barcode Scanner driver
|   |-- stability.py           # Configurable rolling-window stability filter
|   |-- api_client.py          # HTTP client with retry backoff & SQLite queue
|   |-- session.py             # State machine (IDLE -> SCANNED -> MEASURING -> STABLE -> SENT)
|   |-- main.py                # Station CLI daemon entrypoint (Supports --mock)
|   |-- config.json            # Hardware pins, offsets & stability parameters
|   |-- clinic-station.service # Systemd service unit for autostart on boot
|   |-- requirements.txt       # Embedded libraries (RPi.GPIO, hx711, requests)
|   `-- .env.example
|-- frontend/                  # React Single Page App (Runs in Docker on EC2)
|   |-- src/
|   |   |-- components/        # Registration, BarcodeCard, LiveFeed, HistoryTable, Charts
|   |   |-- App.js             # Main Dashboard container
|   |   |-- App.css            # Medical UI styling & Print styles
|   |   `-- api.js             # Axios client with env baseUrl
|   |-- Dockerfile
|   |-- nginx.conf
|   `-- .env.example
`-- docker-compose.yml         # Multi-container EC2 orchestration (Frontend + Backend)</div>

<div class="page-break"></div>

<h2>2. Phase-by-Phase Implementation Roadmap</h2>

<h3>Phase 1: Backend Clean Architecture & Neon Database</h3>
<div class="callout default">
    <div class="callout-title">Phase 1 Objectives & Deliverables</div>
    Refactor senior's backend code out of <code>automation/</code> into <code>/clinic-system/backend</code>. Secure all credentials via <code>.env</code>, implement Pydantic v2 validation, and support height & BMI calculations.
</div>
<ul>
    <li><strong>Database Migration:</strong> Create target tables in Neon PostgreSQL:
        <ul>
            <li><code>patients</code> (id, name, age, gender, phone, barcode UNIQUE, created_at)</li>
            <li><code>measurements</code> (id, patient_id FK, weight, height, bmi, timestamp)</li>
        </ul>
    </li>
    <li><strong>BMI Formula Implementation:</strong>
        <p style="font-family:monospace; background:#f1f5f9; padding:4px 8px; border-radius:4px; display:inline-block;">
            height_m = height_cm / 100.0; bmi = round(weight_kg / (height_m ** 2), 2)
        </p>
    </li>
    <li><strong>Validation Rules:</strong> Weight: 1.0 kg to 350.0 kg; Height: 30.0 cm to 250.0 cm; Phone: 10 digits regex.</li>
    <li><strong>Station Authentication:</strong> Protect <code>POST /measurements</code> using an API Key header (<code>X-API-Key: {STATION_API_KEY}</code>).</li>
    <li><strong>Collision-Safe Barcodes:</strong> Update <code>barcode_generator.py</code> to query the DB in a loop to ensure 100% collision-free 8-char codes.</li>
</ul>

<h3>Phase 2: Raspberry Pi Autonomous Clinic Station</h3>
<div class="callout warning">
    <div class="callout-title">Phase 2 Objectives & Deliverables (Heart of Project)</div>
    Build a production-grade, modular Python daemon running natively on the Raspberry Pi with hardware drivers, stability algorithms, and offline resilience.
</div>

<div class="grid-2">
    <div>
        <strong>Finite State Machine (session.py):</strong>
        <ol style="font-size:8.5pt; margin-top:4px;">
            <li><code>IDLE</code>: Waiting for patient barcode scan.</li>
            <li><code>SCANNED</code>: Active patient locked; tare scale if empty.</li>
            <li><code>MEASURING</code>: Continuous streaming of Weight & Height.</li>
            <li><code>STABLE</code>: N consecutive values within tolerance delta.</li>
            <li><code>SENT</code>: Transmitted to backend (or buffered in SQLite).</li>
            <li><code>RESET</code>: Audio feedback (beep) & return to <code>IDLE</code>.</li>
        </ol>
    </div>
    <div>
        <strong>Resilient Offline Buffering (api_client.py):</strong>
        <p style="font-size:8.5pt;">
            When Wi-Fi drops, the Pi does <strong>not crash or drop data</strong>. Unsent readings are persisted in a local SQLite file (<code>buffer.db</code>). A background worker thread checks Wi-Fi connectivity and flushes the queue via exponential backoff.
        </p>
    </div>
</div>

<h4>Stability Check Algorithm Specification (stability.py)</h4>
<p>
The stability filter maintains two rolling FIFO queues of size N (default N = 5 samples, at 5 Hz = 1.0 second window). A reading is declared stable if and only if:
</p>
<div class="code-box">max(weight_buffer) - min(weight_buffer) <= weight_tolerance (e.g. 0.2 kg)
AND
max(height_buffer) - min(height_buffer) <= height_tolerance (e.g. 0.5 cm)
AND
average(weight_buffer) >= min_patient_weight (e.g. 5.0 kg)</div>

<h4>Raspberry Pi GPIO Pinout & Wiring Table</h4>
<table>
    <thead>
        <tr>
            <th>Subsystem</th>
            <th>Sensor Pin</th>
            <th>Raspberry Pi Physical Pin</th>
            <th>BCM GPIO</th>
            <th>Electrical Notes</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td rowspan="4"><strong>Weight Sensor (HX711)</strong></td>
            <td>VCC</td>
            <td>Pin 2 (or Pin 4)</td>
            <td>5V Power</td>
            <td>Connect to 5V rail of Pi</td>
        </tr>
        <tr>
            <td>GND</td>
            <td>Pin 6 (or Pin 9)</td>
            <td>Ground</td>
            <td>Common ground</td>
        </tr>
        <tr>
            <td>DT (Data)</td>
            <td>Pin 29</td>
            <td>GPIO 5</td>
            <td>24-bit ADC serial output</td>
        </tr>
        <tr>
            <td>SCK (Clock)</td>
            <td>Pin 31</td>
            <td>GPIO 6</td>
            <td>Serial clock input (50Hz)</td>
        </tr>
        <tr>
            <td rowspan="4"><strong>Height Sensor (HC-SR04)</strong></td>
            <td>VCC</td>
            <td>Pin 4</td>
            <td>5V Power</td>
            <td>Sensor requires 5V supply</td>
        </tr>
        <tr>
            <td>GND</td>
            <td>Pin 14 (or Pin 20)</td>
            <td>Ground</td>
            <td>Common ground</td>
        </tr>
        <tr>
            <td>TRIG</td>
            <td>Pin 16</td>
            <td>GPIO 23</td>
            <td>10us trigger pulse from Pi</td>
        </tr>
        <tr>
            <td>ECHO</td>
            <td>Pin 18</td>
            <td>GPIO 24</td>
            <td><strong>Must use Voltage Divider (1k / 2k ohm)</strong> to step 5V down to 3.3V</td>
        </tr>
        <tr>
            <td><strong>Barcode Scanner</strong></td>
            <td>USB Type-A</td>
            <td>USB 3.0 / 2.0 Port</td>
            <td>USB HID</td>
            <td>Standard keyboard HID mode</td>
        </tr>
    </tbody>
</table>

<div class="page-break"></div>

<h3>Phase 3: React Frontend Redesign & Print System</h3>
<div class="callout default">
    <div class="callout-title">Phase 3 Objectives & Deliverables</div>
    Elevate the user experience from an unstyled prototype to a clean, clinic-ready dashboard with live measurement streaming and printable patient cards.
</div>
<ul>
    <li><strong>Printable Patient Card:</strong> Barcode sticker printable directly on standard thermal label printers (or standard A4) with patient name, age, phone, barcode graphic, and generation date.</li>
    <li><strong>Real-time Station Status Card:</strong> Visual gauge displaying live station state (<code>IDLE</code>, <code>MEASURING...</code>, <code>STABLE</code>) without locking the UI.</li>
    <li><strong>Multi-Metric Analytics Dashboard:</strong>
        <ul>
            <li>Weight, Height, and BMI trend line charts using Chart.js.</li>
            <li>Color-coded clinical BMI badges:
                <span class="badge" style="background:#bfdbfe; color:#1e40af;">Underweight (&lt; 18.5)</span>
                <span class="badge badge-done">Normal (18.5 - 24.9)</span>
                <span class="badge badge-partial">Overweight (25.0 - 29.9)</span>
                <span class="badge badge-missing">Obese (&ge; 30.0)</span>
            </li>
            <li>Tabular historical log with date/time stamps and delta changes.</li>
        </ul>
    </li>
    <li><strong>Clean Environment Variable Injection:</strong> All endpoints read dynamically from <code>REACT_APP_API_BASE_URL</code>.</li>
</ul>

<h3>Phase 4: Docker & AWS EC2 Cloud Deployment</h3>
<ul>
    <li><strong>Backend Container:</strong> Multi-stage Python 3.12-slim Dockerfile running Uvicorn with auto-restart.</li>
    <li><strong>Frontend Container:</strong> Node.js multi-stage build creating static assets served by an optimized Nginx Alpine web server.</li>
    <li><strong>Docker Compose:</strong> Single file deployment on AWS EC2 with restart policies, bridged internal networking, and health checks.</li>
    <li><strong>Security Hardening:</strong> All secrets isolated in <code>.env</code>, with comprehensive <code>.env.example</code> and root <code>.gitignore</code> preventing credential leaks.</li>
</ul>

<h3>Phase 5: Automated Testing Suite & Documentation</h3>
<table>
    <thead>
        <tr>
            <th style="width: 25%;">Test Domain</th>
            <th style="width: 35%;">Test Cases</th>
            <th>Verification Tool</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td><strong>BMI Calculation</strong></td>
            <td>Standard values, boundary values, zero/negative guards.</td>
            <td><code>pytest tests/test_bmi.py</code></td>
        </tr>
        <tr>
            <td><strong>Stability Filter</strong></td>
            <td>Oscillating noise, sudden jumps, step-off before N threshold.</td>
            <td><code>pytest tests/test_stability.py</code></td>
        </tr>
        <tr>
            <td><strong>Offline Buffer Queue</strong></td>
            <td>Network disconnection, local SQLite queue, automatic sync on reconnect.</td>
            <td><code>pytest tests/test_offline_queue.py</code></td>
        </tr>
        <tr>
            <td><strong>FastAPI Endpoints</strong></td>
            <td>Patient CRUD, Barcode search, Measurement posting, Auth validation.</td>
            <td><code>pytest tests/test_api.py</code> (TestClient)</td>
        </tr>
    </tbody>
</table>

<div class="callout info" style="margin-top:20px;">
    <div class="callout-title">Ready for Execution</div>
    With this approved execution plan, implementation begins immediately on <strong>Phase 1 (Backend & Database)</strong>, followed sequentially by <strong>Phase 2 (Raspberry Pi Station)</strong>, <strong>Phase 3 (Frontend)</strong>, <strong>Phase 4 (Docker EC2)</strong>, and <strong>Phase 5 (Testing & Documentation)</strong>.
</div>

<div class="footer-note">
    <span>Clinic Patient Measurement System — Execution Plan</span>
    <span>CONFIDENTIAL & PROPRIETARY</span>
</div>

</body>
</html>
"""

audit_html_path = os.path.join(REPORTS_DIR, "audit_work_done.html")
plan_html_path = os.path.join(REPORTS_DIR, "execution_plan.html")

with open(audit_html_path, "w", encoding="utf-8") as f:
    f.write(html_audit)

with open(plan_html_path, "w", encoding="utf-8") as f:
    f.write(html_plan)

print("HTML files generated successfully.")

audit_pdf_path = os.path.join(REPORTS_DIR, "Clinic_System_Work_Done_Audit.pdf")
plan_pdf_path = os.path.join(REPORTS_DIR, "Clinic_System_Execution_Plan.pdf")

def html_to_pdf(html_path, pdf_path):
    cmd = [
        EDGE_PATH,
        "--headless",
        "--disable-gpu",
        "--no-pdf-header-footer",
        f"--print-to-pdf={pdf_path}",
        html_path
    ]
    print(f"Generating PDF: {pdf_path}...")
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode == 0 and os.path.exists(pdf_path):
        print(f"Success! Generated {pdf_path} ({os.path.getsize(pdf_path)} bytes)")
    else:
        print(f"Error compiling {pdf_path}: {res.stderr}")

html_to_pdf(audit_html_path, audit_pdf_path)
html_to_pdf(plan_html_path, plan_pdf_path)
