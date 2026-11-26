// frontend/src/App.js
import React, { useState } from "react";
import "./App.css";
import PatientRegistration from "./components/PatientRegistration";
import LiveStationStatus from "./components/LiveStationStatus";
import PatientHistory from "./components/PatientHistory";

function App() {
  const [activeTab, setActiveTab] = useState("dashboard"); // 'register', 'dashboard', 'live'
  const [selectedBarcode, setSelectedBarcode] = useState("");
  const [notification, setNotification] = useState("");

  const handlePatientRegistered = (newPatient) => {
    setSelectedBarcode(newPatient.barcode);
    setNotification(`Patient registered: ${newPatient.name} (Barcode: ${newPatient.barcode})`);
    setTimeout(() => setNotification(""), 6000);
  };

  const handleMeasurementCompleted = (barcode) => {
    setSelectedBarcode(barcode);
    setNotification(`New measurement received for patient ${barcode}! Updated records.`);
    setTimeout(() => setNotification(""), 6000);
  };

  return (
    <div className="app-container">
      {/* Top Clinic Header */}
      <header className="app-header no-print">
        <div className="header-brand">
          <span className="brand-icon">🏥</span>
          <div>
            <h1>Smart Clinic Measurement Station</h1>
            <span className="brand-tagline">Automated IoT Weight, Height & BMI Tracking System</span>
          </div>
        </div>

        <nav className="header-nav">
          <button
            className={`nav-btn ${activeTab === "dashboard" ? "active" : ""}`}
            onClick={() => setActiveTab("dashboard")}
          >
            📊 Patient History
          </button>
          <button
            className={`nav-btn ${activeTab === "register" ? "active" : ""}`}
            onClick={() => setActiveTab("register")}
          >
            ➕ Register Patient
          </button>
          <button
            className={`nav-btn ${activeTab === "live" ? "active" : ""}`}
            onClick={() => setActiveTab("live")}
          >
            📟 Station Monitor
          </button>
        </nav>
      </header>

      {/* Global Notification Banner */}
      {notification && (
        <div className="notification-banner no-print">
          <span>🔔 {notification}</span>
          <button onClick={() => setNotification("")} className="close-btn">&times;</button>
        </div>
      )}

      {/* Main Content Area */}
      <main className="main-content">
        {/* Always display Live Station Status at the top of the monitor view */}
        <div className="no-print" style={{ marginBottom: "20px" }}>
          <LiveStationStatus onMeasurementCompleted={handleMeasurementCompleted} />
        </div>

        {activeTab === "register" && (
          <div className="tab-pane">
            <PatientRegistration onPatientRegistered={handlePatientRegistered} />
          </div>
        )}

        {activeTab === "dashboard" && (
          <div className="tab-pane">
            <PatientHistory searchCode={selectedBarcode} />
          </div>
        )}

        {activeTab === "live" && (
          <div className="tab-pane">
            <div className="card">
              <h2>Station Operations Guide</h2>
              <ol className="guide-list">
                <li>Register patient to obtain a unique 8-character printable barcode.</li>
                <li>Patient steps up to the clinic station equipped with Raspberry Pi 4.</li>
                <li>Scan barcode with USB HID scanner to unlock active patient session.</li>
                <li>Weight and height are sampled at 5Hz until consecutive readings stabilize.</li>
                <li>Measurements automatically sync to Neon Cloud DB, and records refresh live!</li>
              </ol>
            </div>
          </div>
        )}
      </main>

      <footer className="app-footer no-print">
        <p>Clinic Patient Measurement System &bull; Raspberry Pi + FastAPI + Neon PostgreSQL &bull; Production v1.0</p>
      </footer>
    </div>
  );
}

export default App;
