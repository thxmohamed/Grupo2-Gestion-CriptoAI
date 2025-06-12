import React from "react";
import { BarChart2, TrendingUp, Activity, PieChart } from "lucide-react";

export function Dashboard() {
  const monedas = [
    { nombre: "Bitcoin", rentabilidad: "+8.5%", riesgo: "Moderado" },
    { nombre: "Ethereum", rentabilidad: "+6.2%", riesgo: "Alto" },
    { nombre: "Solana", rentabilidad: "+12.1%", riesgo: "Alto" },
    { nombre: "Cardano", rentabilidad: "+3.4%", riesgo: "Bajo" },
  ];

  const metricas = [
    { nombre: "Sharpe Ratio", valor: "1.87", icon: <TrendingUp color="green" size={24} /> },
    { nombre: "Rentabilidad esperada", valor: "7.4%", icon: <BarChart2 color="blue" size={24} /> },
    { nombre: "Volatilidad", valor: "2.3%", icon: <Activity color="orange" size={24} /> },
  ];

  const cardStyle = {
    backgroundColor: "#fff",
    padding: "16px",
    marginBottom: "16px",
    borderRadius: "8px",
    boxShadow: "0 2px 8px rgba(0, 0, 0, 0.1)",
    textAlign: "left",
  };

  return (
    <div style={{ minHeight: "100vh", padding: "24px", background: "#f3f4f6" }}>
      <h1 style={{ fontSize: "28px", fontWeight: "bold", marginBottom: "24px", textAlign: "center" }}>
        Tu Panel Diario
      </h1>

      <div style={cardStyle}>
        <h2 style={{ fontSize: "20px", fontWeight: "600", marginBottom: "8px" }}>
          Recomendación de Hoy
        </h2>
        <p style={{ color: "#4b5563" }}>
          Hoy te recomendamos distribuir tu portafolio en estas 4 monedas clave según tu perfil de riesgo.
        </p>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(250px, 1fr))", gap: "16px", marginBottom: "24px" }}>
        {monedas.map((m, i) => (
          <div key={i} style={cardStyle}>
            <h3 style={{ fontSize: "18px", fontWeight: "600", color: "#4338ca" }}>{m.nombre}</h3>
            <p style={{ fontSize: "14px", color: "#6b7280" }}>Rentabilidad: {m.rentabilidad}</p>
            <p style={{ fontSize: "14px", color: "#6b7280" }}>Riesgo: {m.riesgo}</p>
          </div>
        ))}
      </div>

      <div style={{
        width: "100%",
        maxWidth: "600px",
        height: "200px",
        margin: "0 auto 24px auto",
        border: "2px dashed #d1d5db",
        borderRadius: "12px",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        color: "#9ca3af"
      }}>
        <PieChart size={24} style={{ marginRight: "8px" }} />
        <span>Gráfico de portafolio próximamente</span>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))", gap: "16px" }}>
        {metricas.map((m, i) => (
          <div key={i} style={{ ...cardStyle, textAlign: "center" }}>
            {m.icon}
            <h4 style={{ fontWeight: "600", marginTop: "8px" }}>{m.nombre}</h4>
            <p style={{ fontSize: "14px", color: "#6b7280" }}>{m.valor}</p>
          </div>
        ))}
      </div>
    </div>
  );
}

export default Dashboard;
