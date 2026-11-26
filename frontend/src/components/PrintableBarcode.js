// frontend/src/components/PrintableBarcode.js
import React from "react";

function PrintableBarcode({ patient }) {
  if (!patient || !patient.barcode) return null;

  const handlePrint = () => {
    window.print();
  };

  return (
    <div className="printable-card-wrapper">
      <div className="printable-badge" id="patient-print-card">
        <div className="badge-header">
          <h3>CLINIC PATIENT CARD</h3>
          <span className="badge-clinic-id">ID: {patient.barcode}</span>
        </div>
        
        <div className="badge-body">
          <p><strong>Name:</strong> {patient.name}</p>
          <div className="badge-inline-meta">
            <span><strong>Age:</strong> {patient.age} yrs</span>
            <span><strong>Gender:</strong> {patient.gender || "N/A"}</span>
            <span><strong>Phone:</strong> {patient.phone || "N/A"}</span>
          </div>
          
          <div className="badge-barcode-visual">
            <img src={patient.barcode_image_url} alt={`Barcode ${patient.barcode}`} />
            <div className="barcode-code-text">{patient.barcode}</div>
          </div>
        </div>

        <div className="badge-footer">
          <small>Present this barcode at the measurement station</small>
        </div>
      </div>

      <div className="no-print" style={{ marginTop: "12px", display: "flex", gap: "10px", justifyContent: "center" }}>
        <button className="btn-primary" onClick={handlePrint}>🖨️ Print Barcode Card</button>
        {patient.barcode_image_url && (
          <a href={patient.barcode_image_url} download={`patient_${patient.barcode}.png`}>
            <button className="btn-secondary">⬇️ Save Image</button>
          </a>
        )}
      </div>
    </div>
  );
}

export default PrintableBarcode;
