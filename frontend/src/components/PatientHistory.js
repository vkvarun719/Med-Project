// frontend/src/components/PatientHistory.js
import React, { useState, useEffect, useCallback } from "react";
import api from "../api";
import BmiChart from "./BmiChart";

function PatientHistory({ searchCode }) {
  const [barcodeInput, setBarcodeInput] = useState("");
  const [patient, setPatient] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const fetchPatientData = useCallback(async (code) => {
    if (!code) return;
    setLoading(true);
    setError("");
    try {
      const res = await api.get(`/patient/${code.trim().toUpperCase()}`);
      setPatient(res.data);
    } catch (err) {
      setPatient(null);
      setError(err.response?.data?.detail || `Patient with barcode "${code}" not found.`);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (searchCode) {
      setBarcodeInput(searchCode);
      fetchPatientData(searchCode);
    }
  }, [searchCode, fetchPatientData]);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    if (barcodeInput.trim()) {
      fetchPatientData(barcodeInput);
    }
  };

  const getBmiBadge = (bmi) => {
    if (bmi < 18.5) return <span className="badge badge-underweight">Underweight ({bmi})</span>;
    if (bmi < 25.0) return <span className="badge badge-normal">Normal ({bmi})</span>;
    if (bmi < 30.0) return <span className="badge badge-overweight">Overweight ({bmi})</span>;
    return <span className="badge badge-obese">Obese ({bmi})</span>;
  };

  const latestMeasurement = patient?.measurements?.[0];

  return (
    <div className="card history-card">
      <div className="card-header">
        <h2>📊 Patient History & Analytics</h2>
        <span className="card-subtitle">Lookup patient measurements, BMI history, and trend graphs</span>
      </div>

      <form onSubmit={handleSearchSubmit} className="search-bar-row">
        <input
          type="text"
          placeholder="Enter or scan 8-character barcode (e.g. 3A7F9B12)..."
          value={barcodeInput}
          onChange={(e) => setBarcodeInput(e.target.value)}
          autoFocus
        />
        <button type="submit" className="btn-primary" disabled={loading}>
          {loading ? "Searching..." : "🔍 Search"}
        </button>
      </form>

      {error && <div className="alert-error" style={{ marginTop: "12px" }}>{error}</div>}

      {patient && (
        <div className="patient-profile-section">
          <div className="patient-meta-banner">
            <div>
              <h3>{patient.name}</h3>
              <p className="patient-demographics">
                <span><strong>Age:</strong> {patient.age} yrs</span> &bull;{" "}
                <span><strong>Gender:</strong> {patient.gender || "N/A"}</span> &bull;{" "}
                <span><strong>Phone:</strong> {patient.phone || "N/A"}</span> &bull;{" "}
                <span><strong>Barcode:</strong> <code>{patient.barcode}</code></span>
              </p>
            </div>
            {latestMeasurement && (
              <div className="latest-vitals-box">
                <div className="vitals-title">Latest Measurement</div>
                <div className="vitals-values">
                  <span>{latestMeasurement.weight} kg</span> &bull;{" "}
                  <span>{latestMeasurement.height} cm</span> &bull;{" "}
                  {getBmiBadge(latestMeasurement.bmi)}
                </div>
              </div>
            )}
          </div>

          <div style={{ marginTop: "18px" }}>
            <h4>📈 Measurement Trends</h4>
            <BmiChart measurements={patient.measurements} />
          </div>

          <div style={{ marginTop: "20px" }}>
            <h4>📋 Historical Records ({patient.measurements.length})</h4>
            <div className="table-responsive">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Date & Time</th>
                    <th>Weight</th>
                    <th>Height</th>
                    <th>BMI</th>
                    <th>Clinical Status</th>
                  </tr>
                </thead>
                <tbody>
                  {patient.measurements.map((m) => (
                    <tr key={m.id}>
                      <td>{new Date(m.timestamp).toLocaleString()}</td>
                      <td><strong>{m.weight}</strong> kg</td>
                      <td><strong>{m.height}</strong> cm</td>
                      <td>{m.bmi}</td>
                      <td>{getBmiBadge(m.bmi)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default PatientHistory;
