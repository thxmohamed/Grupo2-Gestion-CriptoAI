import React from "react";
import { Link } from "react-router-dom";

export function HomePage() {
  return (
    <div className="homepage">
      <h1>Tu asesor cripto con IA</h1>
      <p className="subtitle">
        CryptoAdvisor analiza el mercado por ti, optimiza tu portafolio y te envía
        recomendaciones personalizadas por WhatsApp. Todo con inteligencia artificial, 24/7.
      </p>

      <div className="features">
        <div className="feature-card">
          <h3>Análisis Automático</h3>
          <p>Recolectamos y procesamos datos del mercado en tiempo real.</p>
        </div>
        <div className="feature-card">
          <h3>Recomendaciones Personalizadas</h3>
          <p>Adaptadas a tu perfil de riesgo y objetivos financieros.</p>
        </div>
        <div className="feature-card">
          <h3>IA 24/7</h3>
          <p>Siempre activa para detectar oportunidades y alertarte.</p>
        </div>
      </div>

      <div className="cta-buttons">
        <Link to="/dashboard">
          <button className="primary-btn">Ir al Dashboard</button>
        </Link>
        <Link to="/historial">
          <button className="secondary-btn">Ver Historial</button>
        </Link>
      </div>

      <div className="placeholder-box">
        <p>Gráfica de rendimiento / Demo próximamente</p>
      </div>
    </div>
  );
}
export default HomePage;