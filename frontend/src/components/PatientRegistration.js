// frontend/src/components/PatientRegistration.js
import React, { useState } from "react";
import api from "../api";
import PrintableBarcode from "./PrintableBarcode";

function PatientRegistration({ onPatientRegistered }) {
  const [name, setName] = useState("");
  const [age, setAge] = useState("");
  const [gender, setGender] = useState("");
  const [phone, setPhone] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [registeredPatient, setRegisteredPatient] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    if (!name.trim()) {
      setError("Please enter the patient's full name.");
      return;
    }
    const parsedAge = parseInt(age, 10);
    if (isNaN(parsedAge) || parsedAge < 0 || parsedAge > 130) {
      setError("Please enter a valid age between 0 and 130.");
      return;
    }

    setLoading(true);
    try {
      const response = await api.post("/register", {
        name: name.trim(),
        age: parsedAge,
        gender: gender || null,
        phone: phone.trim() || null,
      });

      setRegisteredPatient(response.data);
      if (onPatientRegistered) {
        onPatientRegistered(response.data);
      }

      // Reset form fields
      setName("");
      setAge("");
      setGender("");
      setPhone("");
    } catch (err) {
      setError(err.response?.data?.detail || "Registration failed. Please check network connection.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card registration-card">
      <div className="card-header">
        <h2>➕ Patient Registration</h2>
        <span className="card-subtitle">Generate an 8-character medical barcode</span>
      </div>

      <form onSubmit={handleSubmit} className="form-layout">
        {error && <div className="alert-error">{error}</div>}

        <div className="form-group">
          <label>Full Name *</label>
          <input
            type="text"
            placeholder="e.g. John Doe"
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
          />
        </div>

        <div className="form-row">
          <div className="form-group">
            <label>Age (years) *</label>
            <input
              type="number"
              placeholder="e.g. 35"
              value={age}
              min="0"
              max="130"
              onChange={(e) => setAge(e.target.value)}
              required
            />
          </div>

          <div className="form-group">
            <label>Gender</label>
            <select value={gender} onChange={(e) => setGender(e.target.value)}>
              <option value="">Select Gender</option>
              <option value="M">Male</option>
              <option value="F">Female</option>
              <option value="O">Other</option>
            </select>
          </div>
        </div>

        <div className="form-group">
          <label>Phone Number</label>
          <input
            type="tel"
            placeholder="e.g. +1 555-0199"
            value={phone}
            onChange={(e) => setPhone(e.target.value)}
          />
        </div>

        <button type="submit" className="btn-primary btn-block" disabled={loading}>
          {loading ? "Generating Barcode..." : "Register Patient"}
        </button>
      </form>

      {registeredPatient && (
        <div style={{ marginTop: "20px" }}>
          <PrintableBarcode patient={registeredPatient} />
        </div>
      )}
    </div>
  );
}

export default PatientRegistration;
