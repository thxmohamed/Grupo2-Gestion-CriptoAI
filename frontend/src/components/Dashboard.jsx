import React, { useEffect, useState } from "react";
import axios from "axios";
import { useParams, Link } from "react-router-dom";

export default function AdminMetricsPage() {
  const { userId } = useParams();
  const [metrics, setMetrics] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [rateLimitExceeded, setRateLimitExceeded] = useState(false);
  const [expandedIndex, setExpandedIndex] = useState(null);

  useEffect(() => {
    axios.get(`http://localhost:8000/api/economic-metrics/`)
      .then(response => {
        setMetrics(response.data.metrics);
        setLoading(false);
      })
      .catch(err => {
        console.error("Error al obtener métricas:", err);
        if (err.response && err.response.status === 429) {
          setRateLimitExceeded(true);
        } else {
          setError("No se pudieron cargar las métricas.");
        }
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

  const toggleExpand = (index) => {
    setExpandedIndex(expandedIndex === index ? null : index);
  };

  if (loading) return <p style={{ textAlign: "center" }}>Cargando métricas...</p>;
  if (rateLimitExceeded) return <p style={{ color: "red", textAlign: "center" }}>⚠️ Límite de peticiones a CoinGecko alcanzado. Intenta nuevamente más tarde.</p>;
  if (error) return <p style={{ textAlign: "center" }}>{error}</p>;

  return (
    <div style={{ padding: "32px", fontFamily: "Segoe UI, sans-serif", backgroundColor: "#f4f6f8" }}>
      <h1 style={{ fontSize: "28px", fontWeight: "bold", marginBottom: "32px", textAlign: "center" }}>
        Dashboard de Métricas ({userId})
      </h1>

      <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
        {metrics.map((coin, index) => (
          <div key={index} style={{ backgroundColor: "#fff", padding: "16px", borderRadius: "8px", boxShadow: "0 2px 4px rgba(0,0,0,0.1)" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <h2 style={{ margin: 0 }}>
                {coin.name} ({coin.symbol})
                <span style={{
                  backgroundColor: getRiskBadgeColor(coin.risk_level),
                  color: "white",
                  padding: "4px 10px",
                  borderRadius: "14px",
                  fontSize: "12px",
                  fontWeight: "bold",
                  marginLeft: "12px"
                }}>
                  {coin.risk_level.toUpperCase()}
                </span>
              </h2>
              <button onClick={() => toggleExpand(index)} style={{ padding: "6px 12px", border: "none", backgroundColor: "#007BFF", color: "white", borderRadius: "6px", cursor: "pointer" }}>
                {expandedIndex === index ? "Ocultar" : "Ver más"}
              </button>
            </div>

            {expandedIndex === index && (
              <div style={{ marginTop: "12px", fontSize: "14px", lineHeight: "1.6" }}>
                <p><strong>Precio actual:</strong> ${coin.current_price}</p>
                <p><strong>Cap. de mercado:</strong> ${coin.market_cap.toLocaleString()}</p>
                <p><strong>Cambio 24h:</strong> {coin.price_change_24h}%</p>
                <p><strong>Retorno esperado:</strong> {coin.expected_return}%</p>
                <p><strong>Volatilidad:</strong> {coin.volatility}%</p>
                <p><strong>Score inversión:</strong> {coin.investment_score}</p>
                <p><strong>Score riesgo:</strong> {coin.risk_score}</p>
                <p><strong>Ratio de liquidez:</strong> {coin.liquidity_ratio}</p>
                <p><strong>Sentimiento del mercado:</strong> {coin.market_sentiment}</p>
                <p><strong>Estabilidad:</strong> {coin.stability_score}</p>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
