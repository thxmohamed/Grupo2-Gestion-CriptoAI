import React from "react";
import { useNavigate } from "react-router-dom";

export default function Portfolio() {
  const navigate = useNavigate();

  return (
    <div style={{
      minHeight: '100vh',
      paddingTop: '100px',
      paddingBottom: '40px',
      background: 'var(--bg-primary)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center'
    }}>
      <div className="container" style={{ textAlign: 'center' }}>
        <div className="card" style={{
          padding: '60px 40px',
          background: 'var(--bg-card)',
          border: '1px solid var(--border-primary)',
          borderRadius: 'var(--radius-xl)',
          maxWidth: '600px',
          margin: '0 auto',
          position: 'relative',
          overflow: 'hidden'
        }}>
          {/* Background Effect */}
          <div style={{
            position: 'absolute',
            top: '-50%',
            left: '-50%',
            width: '200%',
            height: '200%',
            background: 'radial-gradient(circle, rgba(102, 126, 234, 0.1) 0%, transparent 50%)',
            borderRadius: '50%'
          }} />

          <div style={{ position: 'relative', zIndex: 2 }}>
            <div style={{
              width: '100px',
              height: '100px',
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              borderRadius: '24px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '48px',
              margin: '0 auto 32px',
              boxShadow: '0 20px 40px rgba(102, 126, 234, 0.3)'
            }}>
              💼
            </div>

            <h1 style={{
              fontSize: 'clamp(2rem, 5vw, 3rem)',
              fontWeight: '800',
              marginBottom: '24px',
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              backgroundClip: 'text'
            }}>
              Portfolio en Desarrollo
            </h1>

            <p style={{
              fontSize: '18px',
              color: 'var(--text-secondary)',
              marginBottom: '32px',
              lineHeight: '1.6'
            }}>
              Esta funcionalidad está siendo desarrollada. Pronto podrás gestionar tu portafolio de criptomonedas con análisis avanzados de IA.
            </p>

            <div style={{
              display: 'flex',
              gap: '16px',
              justifyContent: 'center',
              flexWrap: 'wrap'
            }}>
              <button
                onClick={() => navigate('/dashboard')}
                style={{
                  padding: '16px 24px',
                  background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                  border: 'none',
                  borderRadius: 'var(--radius-lg)',
                  color: 'white',
                  fontSize: '16px',
                  fontWeight: '600',
                  cursor: 'pointer',
                  transition: 'var(--transition-smooth)',
                  boxShadow: '0 8px 24px rgba(102, 126, 234, 0.3)'
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.transform = 'translateY(-2px)';
                  e.currentTarget.style.boxShadow = '0 12px 32px rgba(102, 126, 234, 0.4)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.transform = 'translateY(0)';
                  e.currentTarget.style.boxShadow = '0 8px 24px rgba(102, 126, 234, 0.3)';
                }}
              >
                📊 Ver Dashboard
              </button>

              <button
                onClick={() => navigate('/')}
                style={{
                  padding: '16px 24px',
                  background: 'transparent',
                  border: '2px solid rgba(102, 126, 234, 0.3)',
                  borderRadius: 'var(--radius-lg)',
                  color: 'var(--text-primary)',
                  fontSize: '16px',
                  fontWeight: '600',
                  cursor: 'pointer',
                  transition: 'var(--transition-smooth)',
                  backdropFilter: 'blur(10px)'
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.background = 'rgba(102, 126, 234, 0.1)';
                  e.currentTarget.style.borderColor = 'rgba(102, 126, 234, 0.5)';
                  e.currentTarget.style.transform = 'translateY(-2px)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.background = 'transparent';
                  e.currentTarget.style.borderColor = 'rgba(102, 126, 234, 0.3)';
                  e.currentTarget.style.transform = 'translateY(0)';
                }}
              >
                🏠 Volver al Inicio
              </button>
            </div>
          </div>
        </div>

        {/* Coming Soon Features */}
        <div style={{
          marginTop: '60px',
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
          gap: '24px'
        }}>
          {[
            {
              icon: "📈",
              title: "Análisis de Rendimiento",
              description: "Seguimiento detallado de ganancias y pérdidas"
            },
            {
              icon: "🎯",
              title: "Rebalanceo Automático",
              description: "Optimización inteligente de tu portafolio"
            },
            {
              icon: "🔔",
              title: "Alertas Personalizadas",
              description: "Notificaciones sobre oportunidades de mercado"
            }
          ].map((feature, index) => (
            <div
              key={index}
              className="card"
              style={{
                padding: '24px',
                background: 'var(--bg-card)',
                border: '1px solid var(--border-primary)',
                borderRadius: 'var(--radius-lg)',
                textAlign: 'center',
                opacity: 0.7,
                transition: 'var(--transition-smooth)'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.opacity = '1';
                e.currentTarget.style.transform = 'translateY(-4px)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.opacity = '0.7';
                e.currentTarget.style.transform = 'translateY(0)';
              }}
            >
              <div style={{
                fontSize: '32px',
                marginBottom: '16px'
              }}>
                {feature.icon}
              </div>
              <h3 style={{
                fontSize: '18px',
                fontWeight: '700',
                color: 'var(--text-primary)',
                marginBottom: '12px'
              }}>
                {feature.title}
              </h3>
              <p style={{
                fontSize: '14px',
                color: 'var(--text-secondary)',
                margin: 0
              }}>
                {feature.description}
              </p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
