// frontend/src/components/LiveStationStatus.js
import React, { useState, useEffect } from "react";
import api from "../api";

function LiveStationStatus({ onMeasurementCompleted }) {
  const [stationFeed, setStationFeed] = useState({
    active_barcode: null,
    live_weight: 0.0,
    live_height: 0.0,
    stable: false,
    state: "IDLE",
  });
  const [lastCompletedBarcode, setLastCompletedBarcode] = useState(null);

  useEffect(() => {
    // Poll station status every 1200ms
    const interval = setInterval(async () => {
      try {
        const res = await api.get("/station/live");
        setStationFeed(res.data);

        // Notify parent when measurement completes
        if (res.data.state === "SENT" && res.data.active_barcode !== lastCompletedBarcode) {
          setLastCompletedBarcode(res.data.active_barcode);
          if (onMeasurementCompleted) {
            onMeasurementCompleted(res.data.active_barcode);
          }
        }
      } catch (err) {
        // Station offline or unreachable
      }
    }, 1200);

    return () => clearInterval(interval);
  }, [lastCompletedBarcode, onMeasurementCompleted]);

  const handleReset = async () => {
    try {
      await api.post("/station/reset");
      setStationFeed((prev) => ({ ...prev, state: "IDLE", active_barcode: null, live_weight: 0, live_height: 0, stable: false }));
    } catch (err) {
      console.error("Reset failed", err);
    }
  };

  const getStateBadge = (state) => {
    switch (state) {
      case "IDLE":
        return <span className="pill pill-idle">🟢 Station Idle (Ready)</span>;
      case "SCANNED":
        return <span className="pill pill-scanned">🟡 Patient Scanned</span>;
      case "MEASURING":
        return <span className="pill pill-measuring">⏳ Measuring...</span>;
      case "STABLE":
        return <span className="pill pill-stable">✅ Stable Reading</span>;
      case "SENT":
        return <span className="pill pill-sent">🚀 Saved to Cloud</span>;
      default:
        return <span className="pill">{state}</span>;
    }
  };

  return (
    <div className="card station-card">
      <div className="card-header station-header">
        <div>
          <h2>📟 Station Live Monitor</h2>
          <span className="card-subtitle">Raspberry Pi Clinic Station (Real-time Feed)</span>
        </div>
        {getStateBadge(stationFeed.state)}
      </div>

      <div className="gauge-grid">
        <div className="gauge-box">
          <span className="gauge-label">Weight</span>
          <div className="gauge-value">
            {stationFeed.live_weight.toFixed(1)} <span className="gauge-unit">kg</span>
          </div>
        </div>

        <div className="gauge-box">
          <span className="gauge-label">Height</span>
          <div className="gauge-value">
            {stationFeed.live_height.toFixed(1)} <span className="gauge-unit">cm</span>
          </div>
        </div>
      </div>

      <div className="station-meta-row">
        <span><strong>Active Patient:</strong> {stationFeed.active_barcode || "None (Waiting for scan)"}</span>
        <button className="btn-secondary btn-sm" onClick={handleReset}>🔄 Reset Station</button>
      </div>
    </div>
  );
}

export default LiveStationStatus;
