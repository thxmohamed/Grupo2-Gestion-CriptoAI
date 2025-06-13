import React, { useEffect, useState } from "react";
import axios from "axios";
import { useParams, Link, useLocation } from "react-router-dom";
import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  Legend,
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid
} from "recharts";
import ReactMarkdown from "react-markdown";
import '/src/index.css';


export default function UserMetricsPage() {
  const { userId } = useParams();
  const location = useLocation();
  const [portfolio, setPortfolio] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [aiReport, setAiReport] = useState(null);

  const nombre = location.state?.nombre;
  const apellido = location.state?.apellido;

  useEffect(() => {
    setLoading(true);
    axios.post(`http://localhost:8000/api/optimize-portfolio`, { id: userId })
      .then(response => {
        setPortfolio(response.data);
        return axios.post("http://127.0.0.1:8000/api/generate-portfolio-report", { id: userId });
      })
      .then(reportResponse => {
        setAiReport(reportResponse.data.ai_report);
        setLoading(false);
      })
      .catch(err => {
        console.error("Error al obtener datos:", err);
        setError("No se pudo cargar el portafolio o el reporte.");
        setLoading(false);
      });
  }, [userId]);

  const getRiskBadgeColor = (riskLevel) => {
    switch (riskLevel) {
      case "low": return "#4CAF50";
      case "medium": return "#FFC107";
      case "high": return "#F44336";
      default: return "#757575";
    }
  };

  if (loading) return <p style={{ textAlign: "center" }}>Cargando portafolio...</p>;
  if (error) return <p style={{ color: "red", textAlign: "center" }}>{error}</p>;

  const { user_profile, portfolio_optimization, portfolio_metrics } = portfolio;

  const chartData = portfolio_optimization.top_4_coins.map(coin => ({
    name: coin.name,
    value: coin.allocation_percentage
  }));

  const COLORS = ["#4CAF50", "#2196F3", "#FFC107", "#F44336"];

  return (
    <div style={{ padding: "32px", fontFamily: "Segoe UI, sans-serif", backgroundColor: "#f4f6f8" }}>
      <h1 style={{ fontSize: "28px", fontWeight: "bold", marginBottom: "16px", textAlign: "center" }}>
        Portafolio de {nombre ?? user_profile.nombre ?? 'Usuario'} {apellido ?? user_profile.apellido ?? ''}
      </h1>
      <div style={{ marginBottom: "24px", textAlign: "center" }}>
        <p><strong>Perfil de riesgo:</strong> {user_profile.risk_tolerance} | <strong>Horizonte de inversión:</strong> {user_profile.investment_horizon}</p>
        <p><strong>Monto total invertido:</strong> ${user_profile.investment_amount}</p>
      </div>

      <div style={{ marginBottom: "32px", backgroundColor: "#fff", padding: "16px", borderRadius: "8px", boxShadow: "0 2px 6px rgba(0,0,0,0.1)" }}>
        <h3>Métricas generales del Portafolio</h3>
        <p><strong>Retorno esperado (promedio ponderado):</strong> {portfolio_metrics.expected_return}%</p>
        <p><strong>Índice de riesgo global:</strong> {portfolio_metrics.risk_score}/100</p>
        <p><strong>Nivel de confianza en la recomendación:</strong> {portfolio_metrics.confidence_level}%</p>
      </div>

      <div style={{ backgroundColor: "#fff", padding: "20px", borderRadius: "8px", marginBottom: "32px", boxShadow: "0 2px 6px rgba(0,0,0,0.1)" }}>
        <h2 style={{ textAlign: "center", marginBottom: "20px" }}>
          Distribución recomendada del monto invertido por criptomoneda
        </h2>
        <ResponsiveContainer width="100%" height={300}>
          <PieChart>
            <Pie data={chartData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={100}>
              {chartData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip formatter={(value) => `${value}% del total`} />
            <Legend />
          </PieChart>
        </ResponsiveContainer>
      </div>

      <div style={{ backgroundColor: "#fff", padding: "20px", borderRadius: "8px", marginBottom: "32px", boxShadow: "0 2px 6px rgba(0,0,0,0.1)" }}>
        <h2 style={{ textAlign: "center", marginBottom: "20px" }}>
          Relación entre retorno esperado y volatilidad por criptomoneda
        </h2>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={portfolio_optimization.top_4_coins}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="symbol" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Bar dataKey="expected_return" fill="#8884d8" name="Retorno esperado (%)" />
            <Bar dataKey="volatility" fill="#82ca9d" name="Volatilidad (%)" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      <h2 style={{ marginBottom: "16px", textAlign: "center" }}>Detalle por criptomoneda recomendada</h2>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(300px, 1fr))", gap: "20px" }}>
        {portfolio_optimization.top_4_coins.map((coin, index) => (
          <div key={index} style={{
            backgroundColor: "#fff",
            borderRadius: "8px",
            padding: "20px",
            borderLeft: `6px solid ${getRiskBadgeColor(coin.risk_level)}`,
            boxShadow: "0 2px 6px rgba(0,0,0,0.1)"
          }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "10px" }}>
              <h2 style={{ margin: 0, fontSize: "20px" }}>{coin.name} ({coin.symbol})</h2>
              <span style={{
                backgroundColor: getRiskBadgeColor(coin.risk_level),
                color: "white",
                padding: "4px 10px",
                borderRadius: "14px",
                fontSize: "12px",
                fontWeight: "bold"
              }}>
                {coin.risk_level.toUpperCase()}
              </span>
            </div>
            <p><strong>% Recomendado:</strong> {coin.allocation_percentage}%</p>
            <p><strong>Monto sugerido:</strong> ${portfolio_optimization.investment_amounts[coin.symbol]}</p>
            <p><strong>Retorno esperado:</strong> {coin.expected_return}%</p>
            <p><strong>Volatilidad:</strong> {coin.volatility}%</p>
            <p><strong>Estabilidad:</strong> {coin.stability_score}</p>
            <p><strong>Sentimiento de mercado:</strong> {coin.market_sentiment}</p>
          </div>
        ))}
      </div>

      {aiReport && (
        <div style={{ backgroundColor: "#fff", padding: "24px", borderRadius: "8px", marginTop: "32px", boxShadow: "0 2px 6px rgba(0,0,0,0.1)" }}>
          <div className="markdown-report">
            <ReactMarkdown>{aiReport}</ReactMarkdown>
          </div>

        </div>
      )}

    </div>
  );
}
