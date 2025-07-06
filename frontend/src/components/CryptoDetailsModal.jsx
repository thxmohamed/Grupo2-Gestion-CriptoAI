import React, { useEffect } from 'react';
import { createPortal } from 'react-dom';

const CryptoDetailsModal = ({ coin, isOpen, onClose }) => {
  // Manejar escape y prevenir scroll del body
  useEffect(() => {
    const handleEscape = (e) => {
      if (e.key === 'Escape' && isOpen) {
        onClose();
      }
    };

    if (isOpen) {
      document.addEventListener('keydown', handleEscape);
      // Prevenir scroll del body cuando el modal está abierto
      document.body.style.overflow = 'hidden';
    }

    return () => {
      document.removeEventListener('keydown', handleEscape);
      document.body.style.overflow = 'unset';
    };
  }, [isOpen, onClose]);

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
          icon: "⚠️"
        };
      case "high":
        return {
          background: "linear-gradient(135deg, #ef4444 0%, #dc2626 100%)",
          color: "white",
          icon: "🚨"
        };
      default:
        return {
          background: "linear-gradient(135deg, #6b7280 0%, #4b5563 100%)",
          color: "white",
          icon: "❓"
        };
    }
  };

  const getPriceChangeStyle = (change) => {
    if (change > 0) {
      return {
        color: "#10b981",
        background: "rgba(16, 185, 129, 0.1)",
        icon: "📈"
      };
    } else if (change < 0) {
      return {
        color: "#ef4444",
        background: "rgba(239, 68, 68, 0.1)",
        icon: "📉"
      };
    }
    return {
      color: "var(--text-secondary)",
      background: "rgba(255, 255, 255, 0.05)",
      icon: "➖"
    };
  };

  if (!isOpen || !coin) return null;

  const riskStyle = getRiskBadgeStyle(coin.risk_level);
  const priceStyle = getPriceChangeStyle(coin.price_change_24h);

  const ModalContent = () => (
    <div
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        background: 'rgba(0, 0, 0, 0.85)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        zIndex: 99999,
        padding: '20px',
        backdropFilter: 'blur(15px)',
        animation: 'fadeIn 0.3s ease-out'
      }}
      onClick={onClose}
    >
      <div
        style={{
          background: 'var(--bg-card)',
          border: `2px solid ${riskStyle.background.includes('gradient') ? 'rgba(102, 126, 234, 0.5)' : 'var(--border-primary)'}`,
          borderRadius: '20px',
          boxShadow: '0 20px 60px rgba(0, 0, 0, 0.6)',
          padding: '40px',
          maxWidth: '800px',
          width: '100%',
          maxHeight: '90vh',
          overflowY: 'auto',
          position: 'relative',
          animation: 'slideIn 0.4s ease-out'
        }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Botón de cerrar */}
        <button
          onClick={onClose}
          style={{
            position: 'absolute',
            top: '20px',
            right: '20px',
            width: '40px',
            height: '40px',
            border: 'none',
            background: 'rgba(255, 255, 255, 0.1)',
            borderRadius: '50%',
            color: 'var(--text-secondary)',
            fontSize: '18px',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            transition: 'var(--transition-smooth)'
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.background = 'rgba(255, 255, 255, 0.2)';
            e.currentTarget.style.color = 'var(--text-primary)';
            e.currentTarget.style.transform = 'scale(1.1)';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.background = 'rgba(255, 255, 255, 0.1)';
            e.currentTarget.style.color = 'var(--text-secondary)';
            e.currentTarget.style.transform = 'scale(1)';
          }}
        >
          ✕
        </button>

        {/* Header de la crypto */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '24px',
          marginBottom: '32px',
          paddingBottom: '24px',
          borderBottom: '1px solid var(--border-primary)'
        }}>
          <div style={{
            width: '80px',
            height: '80px',
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            borderRadius: '20px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: '32px',
            fontWeight: '900',
            color: 'white',
            boxShadow: '0 12px 32px rgba(102, 126, 234, 0.4)',
            position: 'relative'
          }}>
            {coin.symbol?.charAt(0) || '₿'}
            <div style={{
              position: 'absolute',
              top: '-8px',
              right: '-8px',
              background: 'linear-gradient(135deg, #ff6b6b 0%, #ffd93d 100%)',
              borderRadius: '50%',
              width: '24px',
              height: '24px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '12px',
              fontWeight: '700',
              color: 'white',
              boxShadow: '0 4px 12px rgba(255, 107, 107, 0.4)'
            }}>
              #1
            </div>
          </div>
          
          <div style={{ flex: 1 }}>
            <h1 style={{
              fontSize: '36px',
              fontWeight: '900',
              color: 'var(--text-primary)',
              margin: '0 0 8px 0',
              lineHeight: '1.2'
            }}>
              {coin.name}
            </h1>
            <div style={{ display: 'flex', alignItems: 'center', gap: '16px', flexWrap: 'wrap' }}>
              <p style={{
                fontSize: '18px',
                color: 'var(--text-tertiary)',
                margin: 0,
                fontWeight: '600',
                textTransform: 'uppercase',
                letterSpacing: '1px'
              }}>
                {coin.symbol}
              </p>
              <div
                style={{
                  background: riskStyle.background,
                  color: riskStyle.color,
                  padding: '8px 16px',
                  borderRadius: '20px',
                  fontSize: '14px',
                  fontWeight: '700',
                  textTransform: 'uppercase',
                  letterSpacing: '0.5px',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                  boxShadow: '0 4px 12px rgba(0, 0, 0, 0.3)'
                }}
              >
                <span style={{ fontSize: '16px' }}>{riskStyle.icon}</span>
                Riesgo {coin.risk_level}
              </div>
            </div>
          </div>
        </div>

        {/* Métricas principales destacadas */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
          gap: '20px',
          marginBottom: '32px'
        }}>
          <div style={{
            padding: '24px',
            background: 'linear-gradient(135deg, rgba(139, 92, 246, 0.15) 0%, rgba(139, 92, 246, 0.05) 100%)',
            border: '2px solid rgba(139, 92, 246, 0.3)',
            borderRadius: '16px',
            textAlign: 'center',
            position: 'relative',
            overflow: 'hidden'
          }}>
            <div style={{
              position: 'absolute',
              top: 0,
              left: 0,
              right: 0,
              height: '4px',
              background: 'linear-gradient(90deg, #8b5cf6, #7c3aed, #8b5cf6)',
              animation: 'shimmer 3s infinite'
            }} />
            <p style={{
              fontSize: '14px',
              color: 'var(--text-tertiary)',
              margin: '0 0 12px 0',
              fontWeight: '600',
              textTransform: 'uppercase',
              letterSpacing: '1px'
            }}>
              💰 Precio Actual
            </p>
            <p style={{
              fontSize: '32px',
              fontWeight: '900',
              color: 'var(--text-primary)',
              margin: 0,
              background: 'linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              backgroundClip: 'text'
            }}>
              ${coin.current_price?.toLocaleString() || '0'}
            </p>
          </div>

          <div style={{
            padding: '24px',
            background: priceStyle.background,
            border: `2px solid ${priceStyle.color}60`,
            borderRadius: '16px',
            textAlign: 'center',
            position: 'relative',
            overflow: 'hidden'
          }}>
            <div style={{
              position: 'absolute',
              top: 0,
              left: 0,
              right: 0,
              height: '4px',
              background: `linear-gradient(90deg, ${priceStyle.color}, ${priceStyle.color}80, ${priceStyle.color})`,
              animation: 'shimmer 3s infinite'
            }} />
            <p style={{
              fontSize: '14px',
              color: 'var(--text-tertiary)',
              margin: '0 0 12px 0',
              fontWeight: '600',
              textTransform: 'uppercase',
              letterSpacing: '1px'
            }}>
              {priceStyle.icon} Cambio 24h
            </p>
            <p style={{
              fontSize: '28px',
              fontWeight: '900',
              color: priceStyle.color,
              margin: 0
            }}>
              {coin.price_change_24h?.toFixed(2) || '0'}%
            </p>
          </div>

          <div style={{
            padding: '24px',
            background: 'linear-gradient(135deg, rgba(16, 185, 129, 0.15) 0%, rgba(16, 185, 129, 0.05) 100%)',
            border: '2px solid rgba(16, 185, 129, 0.3)',
            borderRadius: '16px',
            textAlign: 'center',
            position: 'relative',
            overflow: 'hidden'
          }}>
            <div style={{
              position: 'absolute',
              top: 0,
              left: 0,
              right: 0,
              height: '4px',
              background: 'linear-gradient(90deg, #10b981, #059669, #10b981)',
              animation: 'shimmer 3s infinite'
            }} />
            <p style={{
              fontSize: '14px',
              color: 'var(--text-tertiary)',
              margin: '0 0 12px 0',
              fontWeight: '600',
              textTransform: 'uppercase',
              letterSpacing: '1px'
            }}>
              🏦 Cap. Mercado
            </p>
            <p style={{
              fontSize: '24px',
              fontWeight: '800',
              color: 'var(--text-primary)',
              margin: 0
            }}>
              ${coin.market_cap?.toLocaleString() || '0'}
            </p>
          </div>
        </div>

        {/* Análisis detallado */}
        <div style={{
          background: 'linear-gradient(135deg, rgba(255, 255, 255, 0.05) 0%, rgba(255, 255, 255, 0.02) 100%)',
          border: '1px solid var(--border-primary)',
          borderRadius: '16px',
          padding: '32px',
          marginBottom: '24px'
        }}>
          <h2 style={{
            fontSize: '24px',
            fontWeight: '700',
            color: 'var(--text-primary)',
            marginBottom: '24px',
            textAlign: 'center',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '12px'
          }}>
            <span style={{ fontSize: '28px' }}>📊</span>
            Análisis Completo
          </h2>

          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
            gap: '20px'
          }}>
            <div style={{
              padding: '20px',
              background: 'linear-gradient(135deg, rgba(59, 130, 246, 0.1) 0%, rgba(59, 130, 246, 0.05) 100%)',
              border: '1px solid rgba(59, 130, 246, 0.3)',
              borderRadius: '12px',
              textAlign: 'center'
            }}>
              <div style={{ fontSize: '24px', marginBottom: '8px' }}>🎯</div>
              <p style={{ fontSize: '14px', color: 'var(--text-tertiary)', margin: '0 0 8px 0', fontWeight: '600' }}>
                Retorno Esperado
              </p>
              <p style={{ fontSize: '20px', fontWeight: '700', color: '#3b82f6', margin: 0 }}>
                {coin.expected_return}%
              </p>
            </div>

            <div style={{
              padding: '20px',
              background: 'linear-gradient(135deg, rgba(239, 68, 68, 0.1) 0%, rgba(239, 68, 68, 0.05) 100%)',
              border: '1px solid rgba(239, 68, 68, 0.3)',
              borderRadius: '12px',
              textAlign: 'center'
            }}>
              <div style={{ fontSize: '24px', marginBottom: '8px' }}>📊</div>
              <p style={{ fontSize: '14px', color: 'var(--text-tertiary)', margin: '0 0 8px 0', fontWeight: '600' }}>
                Volatilidad
              </p>
              <p style={{ fontSize: '20px', fontWeight: '700', color: '#ef4444', margin: 0 }}>
                {coin.volatility}%
              </p>
            </div>

            <div style={{
              padding: '20px',
              background: 'linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(16, 185, 129, 0.05) 100%)',
              border: '1px solid rgba(16, 185, 129, 0.3)',
              borderRadius: '12px',
              textAlign: 'center'
            }}>
              <div style={{ fontSize: '24px', marginBottom: '8px' }}>⭐</div>
              <p style={{ fontSize: '14px', color: 'var(--text-tertiary)', margin: '0 0 8px 0', fontWeight: '600' }}>
                Score Inversión
              </p>
              <p style={{ fontSize: '20px', fontWeight: '700', color: '#10b981', margin: 0 }}>
                {coin.investment_score}/100
              </p>
            </div>

            <div style={{
              padding: '20px',
              background: 'linear-gradient(135deg, rgba(245, 158, 11, 0.1) 0%, rgba(245, 158, 11, 0.05) 100%)',
              border: '1px solid rgba(245, 158, 11, 0.3)',
              borderRadius: '12px',
              textAlign: 'center'
            }}>
              <div style={{ fontSize: '24px', marginBottom: '8px' }}>⚠️</div>
              <p style={{ fontSize: '14px', color: 'var(--text-tertiary)', margin: '0 0 8px 0', fontWeight: '600' }}>
                Score Riesgo
              </p>
              <p style={{ fontSize: '20px', fontWeight: '700', color: '#f59e0b', margin: 0 }}>
                {coin.risk_score}/100 
              </p>
            </div>

            <div style={{
              padding: '20px',
              background: 'linear-gradient(135deg, rgba(139, 92, 246, 0.1) 0%, rgba(139, 92, 246, 0.05) 100%)',
              border: '1px solid rgba(139, 92, 246, 0.3)',
              borderRadius: '12px',
              textAlign: 'center'
            }}>
              <div style={{ fontSize: '24px', marginBottom: '8px' }}>💧</div>
              <p style={{ fontSize: '14px', color: 'var(--text-tertiary)', margin: '0 0 8px 0', fontWeight: '600' }}>
                Liquidez
              </p>
              <p style={{ fontSize: '20px', fontWeight: '700', color: '#8b5cf6', margin: 0 }}>
                {coin.liquidity_ratio}
              </p>
            </div>

            <div style={{
              padding: '20px',
              background: 'linear-gradient(135deg, rgba(236, 72, 153, 0.1) 0%, rgba(236, 72, 153, 0.05) 100%)',
              border: '1px solid rgba(236, 72, 153, 0.3)',
              borderRadius: '12px',
              textAlign: 'center'
            }}>
              <div style={{ fontSize: '24px', marginBottom: '8px' }}>🎭</div>
              <p style={{ fontSize: '14px', color: 'var(--text-tertiary)', margin: '0 0 8px 0', fontWeight: '600' }}>
                Sentimiento
              </p>
              <p style={{ fontSize: '20px', fontWeight: '700', color: '#ec4899', margin: 0 }}>
                {coin.market_sentiment}
              </p>
            </div>
          </div>
        </div>

        {/* Estabilidad destacada */}
        <div style={{
          padding: '32px',
          background: 'linear-gradient(135deg, rgba(100, 255, 218, 0.15) 0%, rgba(100, 255, 218, 0.05) 100%)',
          border: '2px solid rgba(100, 255, 218, 0.3)',
          borderRadius: '16px',
          textAlign: 'center',
          position: 'relative',
          overflow: 'hidden'
        }}>
          <div style={{
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            height: '4px',
            background: 'linear-gradient(90deg, #64ffda, #00bfa5, #64ffda)',
            animation: 'shimmer 3s infinite'
          }} />
          <div style={{
            fontSize: '48px',
            marginBottom: '16px',
            animation: 'pulse 2s infinite'
          }}>
            🛡️
          </div>
          <p style={{
            fontSize: '18px',
            color: 'var(--text-tertiary)',
            margin: '0 0 12px 0',
            fontWeight: '600',
            textTransform: 'uppercase',
            letterSpacing: '1px'
          }}>
            Estabilidad General
          </p>
          <p style={{
            fontSize: '36px',
            fontWeight: '900',
            color: 'var(--text-accent)',
            margin: 0,
            background: 'linear-gradient(135deg, #64ffda 0%, #00bfa5 100%)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            backgroundClip: 'text'
          }}>
            {coin.stability_score}/100
          </p>
        </div>
      </div>
    </div>
  );

  return createPortal(<ModalContent />, document.body);
};

// Agregar estilos CSS globales
if (typeof document !== 'undefined' && !document.getElementById('crypto-modal-styles')) {
  const style = document.createElement('style');
  style.id = 'crypto-modal-styles';
  style.textContent = `
    @keyframes fadeIn {
      from {
        opacity: 0;
      }
      to {
        opacity: 1;
      }
    }
    
    @keyframes slideIn {
      from {
        opacity: 0;
        transform: scale(0.9) translateY(20px);
      }
      to {
        opacity: 1;
        transform: scale(1) translateY(0);
      }
    }
    
    @keyframes shimmer {
      0% {
        background-position: -200px 0;
      }
      100% {
        background-position: 200px 0;
      }
    }
    
    @keyframes pulse {
      0%, 100% {
        transform: scale(1);
      }
      50% {
        transform: scale(1.05);
      }
    }
  `;
  document.head.appendChild(style);
}

export default CryptoDetailsModal;
