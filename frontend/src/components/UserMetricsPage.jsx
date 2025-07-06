import React, { useEffect, useState } from "react";
import apiClient from "../http-common";
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
    apiClient.post(`/api/optimize-portfolio`, { id: userId })
      .then(response => {
        setPortfolio(response.data);
        return apiClient.post("/api/generate-portfolio-report", { id: userId });
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

  const getRiskBadgeStyle = (riskLevel) => {
    switch (riskLevel) {
      case "low":
        return {
          background: "linear-gradient(135deg, #10b981 0%, #059669 100%)",
          color: "white",
          icon: "🛡️"
        };
      case "medium":
        return {
          background: "linear-gradient(135deg, #f59e0b 0%, #d97706 100%)",
          color: "white",
          icon: "⚖️"
        };
      case "high":
        return {
          background: "linear-gradient(135deg, #ef4444 0%, #dc2626 100%)",
          color: "white",
          icon: "⚡"
        };
      default:
        return {
          background: "var(--bg-card)",
          color: "var(--text-secondary)",
          icon: "❓"
        };
    }
  };

  const COLORS = [
    '#667eea', '#764ba2', '#f093fb', '#f5576c', 
    '#4facfe', '#00f2fe', '#43e97b', '#38f9d7'
  ];

  if (loading) {
    return (
      <div style={{ 
        minHeight: '100vh', 
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: 'center',
        paddingTop: '80px',
        background: 'var(--bg-primary)'
      }}>
        <div style={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          gap: '20px'
        }}>
          <div className="loading-spinner" style={{
            width: '60px',
            height: '60px',
            border: '4px solid var(--border-primary)',
            borderTop: '4px solid var(--text-accent)',
            borderRadius: '50%',
            animation: 'spin 1s linear infinite'
          }} />
          <p style={{ color: 'var(--text-secondary)', fontSize: '16px' }}>
            Optimizando portafolio...
          </p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        paddingTop: '80px',
        background: 'var(--bg-primary)'
      }}>
        <div className="card" style={{
          padding: '40px',
          textAlign: 'center',
          maxWidth: '500px'
        }}>
          <div style={{ fontSize: '64px', marginBottom: '20px' }}>❌</div>
          <h2 style={{ color: 'var(--text-primary)', marginBottom: '16px' }}>
            Error al cargar datos
          </h2>
          <p style={{ color: 'var(--text-secondary)', marginBottom: '24px' }}>{error}</p>
          <Link 
            to="/"
            className="btn btn-primary"
            style={{ textDecoration: 'none' }}
          >
            Volver al inicio
          </Link>
        </div>
      </div>
    );
  }

  if (!portfolio || !portfolio.portfolio_optimization) {
    return (
      <div style={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        paddingTop: '80px',
        background: 'var(--bg-primary)'
      }}>
        <div className="card" style={{
          padding: '40px',
          textAlign: 'center',
          maxWidth: '500px'
        }}>
          <div style={{ fontSize: '64px', marginBottom: '20px' }}>📊</div>
          <h2 style={{ color: 'var(--text-primary)', marginBottom: '16px' }}>
            Sin datos de portafolio
          </h2>
          <p style={{ color: 'var(--text-secondary)' }}>
            No se encontraron datos de optimización para este usuario.
          </p>
        </div>
      </div>
    );
  }

  const { portfolio_optimization, user_profile, portfolio_metrics } = portfolio;

  return (
    <div style={{
      minHeight: '100vh',
      paddingTop: '100px',
      paddingBottom: '40px',
      background: 'var(--bg-primary)'
    }}>
      <div className="container">
        {/* Back Button */}
        <Link 
          to="/"
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '8px',
            padding: '12px 20px',
            background: 'var(--bg-card)',
            border: '1px solid var(--border-primary)',
            borderRadius: 'var(--radius-md)',
            color: 'var(--text-secondary)',
            textDecoration: 'none',
            fontSize: '14px',
            fontWeight: '600',
            marginBottom: '40px',
            transition: 'var(--transition-smooth)',
            backdropFilter: 'blur(10px)'
          }}
        >
          ← Volver
        </Link>

        <h1 
          className="animate-fadeInUp crypto-glow"
          style={{
            fontSize: 'clamp(2rem, 5vw, 3.5rem)',
            fontWeight: '900',
            marginBottom: '20px',
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            backgroundClip: 'text',
            letterSpacing: '-2px',
            textAlign: 'center'
          }}
        >
          Portafolio de {nombre || user_profile?.nombre || 'Usuario'} {apellido || user_profile?.apellido || ''}
        </h1>

        {user_profile && (
          <div style={{
            display: 'flex',
            justifyContent: 'center',
            gap: '24px',
            flexWrap: 'wrap',
            marginBottom: '60px'
          }}>
            <div className="badge badge-success">
              🎯 {user_profile.risk_tolerance}
            </div>
            <div className="badge badge-info">
              ⏱️ {user_profile.investment_horizon}
            </div>
            <div className="badge" style={{ background: 'var(--primary-gradient)' }}>
              💰 ${user_profile.wallet_balance?.toLocaleString()}
            </div>
          </div>
        )}

        {/* Charts */}
        <div className="grid grid-2" style={{ marginBottom: '60px' }}>
          <div className="card" style={{ padding: '32px' }}>
            <h2 style={{ textAlign: 'center', marginBottom: '24px', color: 'var(--text-primary)' }}>
              🥧 Distribución del Portafolio
            </h2>
            <ResponsiveContainer width="100%" height={350}>
              <PieChart>
                <Pie
                  data={portfolio_optimization.top_4_coins}
                  cx="50%"
                  cy="50%"
                  outerRadius={120}
                  innerRadius={60}
                  dataKey="allocation_percentage"
                  label={({ name, value }) => `${name}: ${value}%`}
                >
                  {portfolio_optimization.top_4_coins.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </div>

          <div className="card" style={{ padding: '32px' }}>
            <h2 style={{ textAlign: 'center', marginBottom: '24px', color: 'var(--text-primary)' }}>
              📊 Retorno vs Volatilidad
            </h2>
            <ResponsiveContainer width="100%" height={350}>
              <BarChart data={portfolio_optimization.top_4_coins}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="symbol" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="expected_return" fill="#10b981" name="Retorno (%)" />
                <Bar dataKey="volatility" fill="#ef4444" name="Volatilidad (%)" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Crypto Cards */}
        <div className="grid grid-2" style={{ marginBottom: '60px' }}>
          {portfolio_optimization.top_4_coins.map((coin, index) => {
            const riskStyle = getRiskBadgeStyle(coin.risk_level);
            const investmentAmount = portfolio_optimization.investment_amounts?.[coin.symbol] || 0;

            return (
              <div key={index} className="card" style={{ padding: '32px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
                  <h3 style={{ color: 'var(--text-primary)', fontSize: '24px', fontWeight: '800' }}>
                    {coin.name} ({coin.symbol})
                  </h3>
                  <div className="badge" style={{
                    background: riskStyle.background,
                    color: riskStyle.color
                  }}>
                    {riskStyle.icon} {coin.risk_level}
                  </div>
                </div>

                <div style={{
                  padding: '20px',
                  background: 'var(--primary-gradient)',
                  borderRadius: 'var(--radius-md)',
                  textAlign: 'center',
                  marginBottom: '20px'
                }}>
                  <p style={{ color: 'white', fontSize: '14px', margin: 0, opacity: 0.9 }}>
                    Asignación Recomendada
                  </p>
                  <p style={{ color: 'white', fontSize: '32px', fontWeight: '900', margin: '8px 0' }}>
                    {coin.allocation_percentage}%
                  </p>
                  <p style={{ color: 'white', fontSize: '18px', fontWeight: '700', margin: 0 }}>
                    ${investmentAmount?.toLocaleString() || '0'}
                  </p>
                </div>

                <div className="grid" style={{ gridTemplateColumns: 'repeat(2, 1fr)', gap: '12px' }}>
                  <div style={{ textAlign: 'center', padding: '12px', background: 'rgba(16, 185, 129, 0.1)', borderRadius: '8px' }}>
                    <p style={{ fontSize: '12px', color: 'var(--text-tertiary)', margin: 0 }}>RETORNO</p>
                    <p style={{ fontSize: '18px', fontWeight: '700', color: '#10b981', margin: 0 }}>
                      {coin.expected_return}%
                    </p>
                  </div>
                  <div style={{ textAlign: 'center', padding: '12px', background: 'rgba(239, 68, 68, 0.1)', borderRadius: '8px' }}>
                    <p style={{ fontSize: '12px', color: 'var(--text-tertiary)', margin: 0 }}>VOLATILIDAD</p>
                    <p style={{ fontSize: '18px', fontWeight: '700', color: '#ef4444', margin: 0 }}>
                      {coin.volatility}%
                    </p>
                  </div>
                  <div style={{ textAlign: 'center', padding: '12px', background: 'rgba(59, 130, 246, 0.1)', borderRadius: '8px' }}>
                    <p style={{ fontSize: '12px', color: 'var(--text-tertiary)', margin: 0 }}>ESTABILIDAD</p>
                    <p style={{ fontSize: '18px', fontWeight: '700', color: '#3b82f6', margin: 0 }}>
                      {coin.stability_score}/100
                    </p>
                  </div>
                  <div style={{ textAlign: 'center', padding: '12px', background: 'rgba(245, 158, 11, 0.1)', borderRadius: '8px' }}>
                    <p style={{ fontSize: '12px', color: 'var(--text-tertiary)', margin: 0 }}>SENTIMIENTO</p>
                    <p style={{ fontSize: '14px', fontWeight: '700', color: '#f59e0b', margin: 0 }}>
                      {coin.market_sentiment}
                    </p>
                  </div>
                </div>
              </div>
            );
          })}
        </div>

        {/* AI Report */}
        {aiReport && (
          <div className="card" style={{ padding: '40px' }}>
            <h2 style={{
              fontSize: '32px',
              fontWeight: '800',
              color: 'var(--text-primary)',
              marginBottom: '30px',
              textAlign: 'center',
              background: 'var(--primary-gradient)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent'
            }}>
              🤖 Reporte IA Personalizado
            </h2>
            <div className="markdown-report">
              <ReactMarkdown>{aiReport}</ReactMarkdown>
            </div>
          </div>
        )}
      </div>

      <style jsx>{`
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
}
