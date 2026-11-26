# Clinic Patient Measurement System 🏥
### End-to-End Automated Patient Vitals (Weight, Height & BMI) Tracking Station

[![FastAPI](https://img.shields.io/badge/FastAPI-0.110.0-009688.svg?logo=fastapi)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-19.2.5-61DAFB.svg?logo=react)](https://react.dev)
[![Raspberry Pi](https://img.shields.io/badge/Raspberry%20Pi-4B-C51A4A.svg?logo=raspberrypi)](https://www.raspberrypi.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Neon%20Cloud-336791.svg?logo=postgresql)](https://neon.tech)
[![Docker](https://img.shields.io/badge/Docker-EC2%20Compose-2496ED.svg?logo=docker)](https://www.docker.com/)
[![Tests](https://img.shields.io/badge/Tests-16%20Passed-brightgreen.svg)]()

---

## 1. System Architecture

```text
+-------------------------------------------------------------------------------+
|                        CLINIC STATION (Raspberry Pi 4)                       |
|                                                                               |
|   +-------------------+    +--------------------+    +--------------------+   |
|   | Weight Sensor     |    | Height Sensor      |    | USB Barcode        |   |
|   | (HX711 ADC Bridge)|    | (HC-SR04 Ultrasonic|    | Scanner (HID/evdev)|   |
|   +---------+---------+    +---------+----------+    +---------+----------+   |
|             |                        |                         |              |
|             +-------------------> [GPIO / BCM] <---------------+              |
|                                      |                                        |
|                          +-----------v-----------+                            |
|                          | Finite State Machine  | (IDLE -> SCANNED ->        |
|                          | (session.py)          |  MEASURING -> STABLE ->    |
|                          +-----------+-----------+  SENT -> RESET)            |
|                                      |                                        |
|                          +-----------v-----------+                            |
|                          | Rolling Stability     | (N=5 samples within        |
|                          | Filter (stability.py) |  0.2kg & 0.5cm tolerance)  |
|                          +-----------+-----------+                            |
|                                      |                                        |
|                     +----------------v----------------+                       |
|                     | Offline Buffer Queue (SQLite)   |                       |
|                     | Auto-sync with backoff on retry |                       |
|                     +----------------+----------------+                       |
+--------------------------------------|----------------------------------------+
                                       |
                   Wi-Fi / HTTPS (with X-API-Key Header)
                                       |
                                       v
+-------------------------------------------------------------------------------+
|                       AWS EC2 SERVER (Docker Compose)                         |
|                                                                               |
|   +---------------------------------------+    +--------------------------+   |
|   | FastAPI Backend (:8000)               |    | React Frontend (:80)     |   |
|   | - Range validation (1-350kg, 30-250cm)|    | - Patient Registration   |   |
|   | - BMI = weight / (height_m ^ 2)       |    | - Thermal Barcode Card   |   |
|   | - Station API Key authentication      |    | - Real-time Gauge Feed   |   |
|   | - Collision-free Code128 generator    |    | - Multi-metric Charts    |   |
|   +-------------------+-------------------+    +--------------------------+   |
|                       |                                                       |
+-----------------------|-------------------------------------------------------+
                        |
            SQLAlchemy Pool (SSL Mode)
                        |
                        v
+-------------------------------------------------------------------------------+
|                       NEON POSTGRESQL CLOUD DATABASE                          |
|                                                                               |
|   - patients: id, name, age, gender, phone, barcode UNIQUE, created_at        |
|   - measurements: id, patient_id FK, weight, height, bmi, timestamp           |
+-------------------------------------------------------------------------------+
```

---

## 2. Raspberry Pi Hardware Wiring & Pinout

### Physical Pin Connections (Raspberry Pi 4 Model B)

| Subsystem | Sensor Pin | Raspberry Pi Physical Pin | BCM GPIO Pin | Electrical & Wiring Instructions |
| :--- | :--- | :--- | :--- | :--- |
| **Weight (HX711)** | VCC | Pin 2 | 5V Power | Connect to 5V rail |
| | GND | Pin 6 | Ground | Common system ground |
| | DT (Data) | Pin 29 | GPIO 5 | 24-bit ADC serial output |
| | SCK (Clock) | Pin 31 | GPIO 6 | Serial clock input |
| **Height (HC-SR04)**| VCC | Pin 4 | 5V Power | Sensor requires 5V supply |
| | GND | Pin 14 | Ground | Common ground |
| | TRIG | Pin 16 | GPIO 23 | 10µs trigger pulse from Pi |
| | ECHO | Pin 18 | GPIO 24 | **CRITICAL: Use Voltage Divider (1kΩ / 2kΩ)** to step 5V down to 3.3V safe for Pi |
| **Barcode Scanner** | USB Type-A | USB 2.0/3.0 Port | USB HID | Plugs directly into any USB port |
| **Status Buzzer** | Positive (+) | Pin 12 | GPIO 18 | Optional 5V active piezo buzzer |

> ⚠️ **IMPORTANT ELECTRICAL SAFETY NOTE:** The `ECHO` pin of the HC-SR04 outputs 5V logic. Connecting this directly to the Raspberry Pi GPIO (3.3V maximum) will permanently damage the Pi SoC. Always connect a resistor voltage divider: `ECHO` -> `1kΩ resistor` -> `GPIO 24` -> `2kΩ resistor` -> `GND`.

---

## 3. Raspberry Pi Station Setup (On the Pi)

### 3.1 OS Installation & Dependencies
1. Flash **Raspberry Pi OS (64-bit Lite, Debian Bookworm)** using Raspberry Pi Imager.
2. Connect to clinic Wi-Fi and open a terminal:
```bash
sudo apt-get update && sudo apt-get install -y python3-pip python3-venv git
cd /home/pi
git clone https://github.com/vkvarun719/Med-Project.git clinic-system
cd clinic-system/automation

# Create virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install RPi.GPIO
```

### 3.2 Sensor Calibration
Zero the scale and calibrate your load cells and stadiometer height:
```bash
# 1. Zero the scale platform (Tare)
python main.py --tare

# 2. Place a known calibration weight (e.g., 20 kg) and calibrate
python main.py --calibrate-weight 420.0

# 3. Calibrate total stadiometer ceiling distance in cm (e.g., 220.0 cm)
python main.py --calibrate-height 220.0
```

### 3.3 Production Systemd Autostart on Boot
Enable the daemon to automatically start on boot and restart if it ever crashes:
```bash
sudo cp clinic-station.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable clinic-station
sudo systemctl start clinic-station

# Monitor live station logs
sudo journalctl -u clinic-station -f
```

### 3.4 Laptop / Development Simulation Mode
To run and test the complete system on a PC or laptop without physical sensors:
```bash
cd automation
python main.py --mock
```

---

## 4. Cloud Server Deployment (AWS EC2 + Docker)

### 4.1 Prerequisites
* An AWS EC2 instance (Ubuntu 22.04 LTS or 24.04 LTS, `t3.small` or `t3.medium`).
* Docker and Docker Compose installed:
```bash
sudo apt-get update && sudo apt-get install -y docker.io docker-compose
sudo usermod -aG docker $USER
```

### 4.2 Configuration
1. Clone the repository on your EC2 instance:
```bash
git clone https://github.com/vkvarun719/Med-Project.git
cd Med-Project
```
2. Create your `.env` file based on `.env.example`:
```bash
cp .env.example .env
nano .env
```
Provide your **Neon PostgreSQL database connection string** and configure your `STATION_API_KEY`.

### 4.3 Launch Containers
```bash
docker-compose up -d --build
```
* **Frontend Web App:** `http://<YOUR_EC2_PUBLIC_IP>/`
* **FastAPI Swagger API Docs:** `http://<YOUR_EC2_PUBLIC_IP>:8000/docs`
* **Health Check:** `http://<YOUR_EC2_PUBLIC_IP>:8000/health`

---

## 5. Local Development Quickstart

### Backend (FastAPI)
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Frontend (React)
```bash
cd frontend
npm install --legacy-peer-deps
npm start
```

### Run Automated Tests
```bash
pytest tests -v
```

---

## 6. End-to-End Clinic Workflow (10 Steps)

1. **Patient Registration (React UI):** Receptionist captures Name, Age, Gender, and Phone Number.
2. **Barcode Generation:** Backend produces an 8-character collision-checked Code128 barcode and base64 printable card.
3. **Printable Card:** Print thermal label sticker or patient card directly from browser (`window.print()`).
4. **Barcode Scan (Raspberry Pi):** Patient presents barcode at measurement station. USB scanner reads code and locks session.
5. **Live Measurement:** HX711 reads load cells; HC-SR04 measures head distance.
6. **Stability Verification:** Rolling filter verifies $N=5$ consecutive readings within $\pm 0.2\text{ kg}$ and $\pm 0.5\text{ cm}$.
7. **Resilient Data Transmission:** Pi transmits reading to cloud with `X-API-Key`. If Wi-Fi is down, reading is saved to `buffer.db` and flushed automatically when connection restores.
8. **Backend Processing:** Computes $\text{BMI} = \frac{\text{weight(kg)}}{(\text{height(m)})^2}$ and validates ranges.
9. **Database Persistence:** Saves measurement record to Neon PostgreSQL.
10. **Reset & Dashboard:** Station emits double confirmation beep and resets to `IDLE` for next patient. History table and Chart.js graphs refresh automatically!

---

## 7. Reports & Documentation

Detailed project handover documents generated during the audit phase are located in `/reports`:
* [Clinic System Audit & Work Done Report (PDF)](reports/Clinic_System_Work_Done_Audit.pdf)
* [Clinic System Execution Plan & Roadmap (PDF)](reports/Clinic_System_Execution_Plan.pdf)

---

## 8. License
Proprietary & Confidential — Smart Clinic Measurement System 2026.
