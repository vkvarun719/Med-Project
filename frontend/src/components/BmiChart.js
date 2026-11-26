// frontend/src/components/BmiChart.js
import React, { useState } from "react";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} from "chart.js";
import { Line } from "react-chartjs-2";

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

function BmiChart({ measurements }) {
  const [metric, setMetric] = useState("bmi"); // 'bmi', 'weight', 'height'

  if (!measurements || measurements.length === 0) {
    return <div className="chart-empty">No historical measurement records found for this patient.</div>;
  }

  // Measurements are passed desc, reverse for chronological chart
  const chronological = [...measurements].reverse();

  const labels = chronological.map((m) =>
    new Date(m.timestamp).toLocaleDateString([], { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" })
  );

  let datasetConfig = {};
  if (metric === "bmi") {
    datasetConfig = {
      label: "BMI (kg/m²)",
      data: chronological.map((m) => m.bmi),
      borderColor: "#0284c7",
      backgroundColor: "rgba(2, 132, 199, 0.15)",
      fill: true,
      tension: 0.3,
    };
  } else if (metric === "weight") {
    datasetConfig = {
      label: "Weight (kg)",
      data: chronological.map((m) => m.weight),
      borderColor: "#10b981",
      backgroundColor: "rgba(16, 185, 129, 0.15)",
      fill: true,
      tension: 0.3,
    };
  } else {
    datasetConfig = {
      label: "Height (cm)",
      data: chronological.map((m) => m.height),
      borderColor: "#8b5cf6",
      backgroundColor: "rgba(139, 92, 246, 0.15)",
      fill: true,
      tension: 0.3,
    };
  }

  const chartData = {
    labels,
    datasets: [
      {
        ...datasetConfig,
        pointRadius: 5,
        pointHoverRadius: 7,
        borderWidth: 2,
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: true,
        position: "top",
      },
      tooltip: {
        callbacks: {
          label: (context) => `${context.dataset.label}: ${context.raw}`,
        },
      },
    },
    scales: {
      y: {
        beginAtZero: false,
        grid: { color: "rgba(226, 232, 240, 0.6)" },
      },
      x: {
        grid: { display: false },
      },
    },
  };

  return (
    <div className="chart-container-box">
      <div className="chart-tabs">
        <button
          className={`tab-btn ${metric === "bmi" ? "active" : ""}`}
          onClick={() => setMetric("bmi")}
        >
          BMI Trend
        </button>
        <button
          className={`tab-btn ${metric === "weight" ? "active" : ""}`}
          onClick={() => setMetric("weight")}
        >
          Weight Trend
        </button>
        <button
          className={`tab-btn ${metric === "height" ? "active" : ""}`}
          onClick={() => setMetric("height")}
        >
          Height Trend
        </button>
      </div>

      <div style={{ height: "260px" }}>
        <Line data={chartData} options={chartOptions} />
      </div>
    </div>
  );
}

export default BmiChart;
