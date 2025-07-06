import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import apiClient from "../http-common";

export default function HomePage() {
  const [topCryptos, setTopCryptos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [currentSlide, setCurrentSlide] = useState(0);
  const navigate = useNavigate();

  useEffect(() => {
    apiClient.post('/api/economic-metrics/', {})
      .then(response => {
        // La respuesta ahora tiene una estructura diferente
        const metricsData = response.data.metrics;
        // Convertir el objeto de métricas a un array para mantener compatibilidad
        const metricsArray = Object.values(metricsData);
        const top5 = metricsArray
          .sort((a, b) => b.market_cap - a.market_cap)
          .slice(0, 5);
        setTopCryptos(top5);
        setLoading(false);
      })
      .catch(err => {
        console.error("Error al obtener datos:", err);
        setError("No se pudieron cargar los datos");
        setLoading(false);
      });
  }, []);

  // Auto-cambio de slides cada 5 segundos
  useEffect(() => {
    if (topCryptos.length === 0) return;
    
    const interval = setInterval(() => {
      setCurrentSlide((prev) => (prev + 1) % topCryptos.length);
    }, 5000);

    return () => clearInterval(interval);
  }, [topCryptos.length]);

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

  const getRiskColor = (riskLevel) => {
    switch (riskLevel) {
      case "low": return "#10b981";
      case "medium": return "#f59e0b";
      case "high": return "#ef4444";
      default: return "#6b7280";
    }
  };

  if (loading) {
    return (
      <div style={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
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
          <p style={{ color: 'var(--text-secondary)' }}>Cargando datos del mercado...</p>
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
        background: 'var(--bg-primary)'
      }}>
        <div className="card" style={{ padding: '40px', textAlign: 'center' }}>
          <div style={{ fontSize: '64px', marginBottom: '20px' }}>❌</div>
          <h2 style={{ color: 'var(--text-primary)', marginBottom: '16px' }}>
            Error al cargar datos
          </h2>
          <p style={{ color: 'var(--text-secondary)' }}>{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div style={{
      minHeight: '100vh',
      background: 'var(--bg-primary)',
      paddingTop: '80px'
    }}>
      {/* Hero Section */}
      <section style={{
        padding: '80px 0 120px',
        position: 'relative',
        overflow: 'hidden'
      }}>
        {/* Background Effects */}
        <div style={{
          position: 'absolute',
          top: '20%',
          left: '10%',
          width: '300px',
          height: '300px',
          background: 'radial-gradient(circle, rgba(102, 126, 234, 0.1) 0%, transparent 70%)',
          borderRadius: '50%',
          filter: 'blur(60px)',
          animation: 'float 6s ease-in-out infinite'
        }} />
        
        <div style={{
          position: 'absolute',
          bottom: '20%',
          right: '10%',
          width: '200px',
          height: '200px',
          background: 'radial-gradient(circle, rgba(139, 92, 246, 0.1) 0%, transparent 70%)',
          borderRadius: '50%',
          filter: 'blur(40px)',
          animation: 'float 8s ease-in-out infinite reverse'
        }} />

        <div className="container" style={{
          textAlign: 'center',
          position: 'relative',
          zIndex: 2
        }}>
          <h1 style={{
            fontSize: 'clamp(3rem, 8vw, 6rem)',
            fontWeight: '900',
            marginBottom: '24px',
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            backgroundClip: 'text',
            letterSpacing: '-3px',
            lineHeight: '1.1'
          }}>
            CriptoAI
          </h1>
          
          <p style={{
            fontSize: 'clamp(1.2rem, 3vw, 1.8rem)',
            color: 'var(--text-secondary)',
            marginBottom: '16px',
            fontWeight: '300',
            maxWidth: '800px',
            margin: '0 auto 16px'
          }}>
            Inteligencia artificial avanzada para inversiones cripto inteligentes
          </p>
          
          <p style={{
            fontSize: 'clamp(1rem, 2vw, 1.2rem)',
            color: 'var(--text-tertiary)',
            marginBottom: '48px',
            maxWidth: '600px',
            margin: '0 auto 48px',
            lineHeight: '1.6'
          }}>
            Analiza el mercado en tiempo real, gestiona tu portafolio y toma decisiones basadas en datos con nuestra IA especializada en criptomonedas.
          </p>

          <div style={{
            display: 'flex',
            gap: '20px',
            justifyContent: 'center',
            flexWrap: 'wrap'
          }}>
            <button
              onClick={() => navigate('/dashboard')}
              style={{
                padding: '16px 32px',
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                border: 'none',
                borderRadius: 'var(--radius-lg)',
                color: 'white',
                fontSize: '16px',
                fontWeight: '600',
                cursor: 'pointer',
                transition: 'var(--transition-smooth)',
                boxShadow: '0 8px 24px rgba(102, 126, 234, 0.3)',
                textTransform: 'uppercase',
                letterSpacing: '0.5px'
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
              onClick={() => navigate('/portfolio')}
              style={{
                padding: '16px 32px',
                background: 'transparent',
                border: '2px solid rgba(102, 126, 234, 0.3)',
                borderRadius: 'var(--radius-lg)',
                color: 'var(--text-primary)',
                fontSize: '16px',
                fontWeight: '600',
                cursor: 'pointer',
                transition: 'var(--transition-smooth)',
                backdropFilter: 'blur(10px)',
                textTransform: 'uppercase',
                letterSpacing: '0.5px'
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
              💼 Mi Portfolio
            </button>
          </div>
        </div>
      </section>

      {/* Top 5 Cryptocurrencies Showcase */}
      <section style={{
        padding: '80px 0',
        background: 'rgba(255, 255, 255, 0.02)',
        borderTop: '1px solid var(--border-secondary)',
        borderBottom: '1px solid var(--border-secondary)'
      }}>
        <div className="container">
          <div style={{ textAlign: 'center', marginBottom: '60px' }}>
            <h2 style={{
              fontSize: 'clamp(2rem, 5vw, 3rem)',
              fontWeight: '800',
              marginBottom: '20px',
              background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              backgroundClip: 'text'
            }}>
              🏆 Top 5 Criptomonedas
            </h2>
            <p style={{
              fontSize: '18px',
              color: 'var(--text-secondary)',
              maxWidth: '600px',
              margin: '0 auto'
            }}>
              Las criptomonedas más importantes del mercado con análisis en tiempo real
            </p>
          </div>

          {/* Featured Crypto Slider */}
          {topCryptos.length > 0 && (
            <div style={{
              position: 'relative',
              marginBottom: '60px',
              borderRadius: 'var(--radius-xl)',
              overflow: 'hidden',
              background: 'var(--bg-card)',
              border: '1px solid var(--border-primary)',
              boxShadow: '0 20px 40px rgba(0, 0, 0, 0.2)'
            }}>
              <div style={{
                padding: '60px 40px',
                background: `linear-gradient(135deg, ${getRiskColor(topCryptos[currentSlide]?.risk_level)}15 0%, transparent 100%)`,
                position: 'relative',
                overflow: 'hidden'
              }}>
                {/* Background Pattern */}
                <div style={{
                  position: 'absolute',
                  top: '-20%',
                  right: '-10%',
                  width: '400px',
                  height: '400px',
                  background: `radial-gradient(circle, ${getRiskColor(topCryptos[currentSlide]?.risk_level)}08 0%, transparent 70%)`,
                  borderRadius: '50%'
                }} />

                <div style={{
                  display: 'grid',
                  gridTemplateColumns: '1fr 2fr',
                  gap: '60px',
                  alignItems: 'center',
                  position: 'relative',
                  zIndex: 2
                }}>
                  {/* Crypto Info */}
                  <div>
                    <div style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '20px',
                      marginBottom: '24px'
                    }}>
                      <div style={{
                        width: '80px',
                        height: '80px',
                        background: `linear-gradient(135deg, ${getRiskColor(topCryptos[currentSlide]?.risk_level)} 0%, ${getRiskColor(topCryptos[currentSlide]?.risk_level)}80 100%)`,
                        borderRadius: '20px',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        fontSize: '32px',
                        fontWeight: '900',
                        color: 'white',
                        boxShadow: `0 12px 28px ${getRiskColor(topCryptos[currentSlide]?.risk_level)}40`
                      }}>
                        {topCryptos[currentSlide]?.symbol?.charAt(0) || '₿'}
                      </div>
                      <div>
                        <h3 style={{
                          fontSize: '32px',
                          fontWeight: '900',
                          color: 'var(--text-primary)',
                          margin: 0,
                          lineHeight: '1.2'
                        }}>
                          {topCryptos[currentSlide]?.name}
                        </h3>
                        <p style={{
                          fontSize: '18px',
                          color: 'var(--text-tertiary)',
                          margin: 0,
                          fontWeight: '600',
                          textTransform: 'uppercase'
                        }}>
                          {topCryptos[currentSlide]?.symbol}
                        </p>
                      </div>
                    </div>

                    <div style={{
                      display: 'grid',
                      gridTemplateColumns: 'repeat(2, 1fr)',
                      gap: '16px',
                      marginBottom: '32px'
                    }}>
                      <div style={{
                        padding: '20px',
                        background: 'rgba(255, 255, 255, 0.05)',
                        borderRadius: 'var(--radius-md)',
                        border: '1px solid var(--border-secondary)'
                      }}>
                        <p style={{
                          fontSize: '14px',
                          color: 'var(--text-tertiary)',
                          margin: '0 0 8px 0',
                          fontWeight: '600'
                        }}>
                          Precio
                        </p>
                        <p style={{
                          fontSize: '24px',
                          fontWeight: '900',
                          color: 'var(--text-primary)',
                          margin: 0
                        }}>
                          ${topCryptos[currentSlide]?.current_price?.toLocaleString()}
                        </p>
                      </div>

                      <div style={{
                        padding: '20px',
                        background: getPriceChangeStyle(topCryptos[currentSlide]?.price_change_24h).background,
                        borderRadius: 'var(--radius-md)',
                        border: `1px solid ${getPriceChangeStyle(topCryptos[currentSlide]?.price_change_24h).color}40`
                      }}>
                        <p style={{
                          fontSize: '14px',
                          color: 'var(--text-tertiary)',
                          margin: '0 0 8px 0',
                          fontWeight: '600'
                        }}>
                          24h
                        </p>
                        <div style={{
                          display: 'flex',
                          alignItems: 'center',
                          gap: '8px'
                        }}>
                          <span style={{ fontSize: '16px' }}>
                            {getPriceChangeStyle(topCryptos[currentSlide]?.price_change_24h).icon}
                          </span>
                          <p style={{
                            fontSize: '20px',
                            fontWeight: '800',
                            color: getPriceChangeStyle(topCryptos[currentSlide]?.price_change_24h).color,
                            margin: 0
                          }}>
                            {topCryptos[currentSlide]?.price_change_24h?.toFixed(2)}%
                          </p>
                        </div>
                      </div>
                    </div>

                    {/* Investment Score */}
                    <div style={{
                      padding: '24px',
                      background: 'linear-gradient(135deg, rgba(100, 255, 218, 0.1) 0%, rgba(100, 255, 218, 0.05) 100%)',
                      border: '1px solid rgba(100, 255, 218, 0.2)',
                      borderRadius: 'var(--radius-lg)',
                      textAlign: 'center'
                    }}>
                      <p style={{
                        fontSize: '16px',
                        color: 'var(--text-tertiary)',
                        margin: '0 0 12px 0',
                        fontWeight: '600'
                      }}>
                        Score de Inversión IA
                      </p>
                      <p style={{
                        fontSize: '36px',
                        fontWeight: '900',
                        color: 'var(--text-accent)',
                        margin: 0
                      }}>
                        {topCryptos[currentSlide]?.investment_score}/100
                      </p>
                    </div>
                  </div>

                  {/* Visual Chart Area */}
                  <div style={{
                    position: 'relative',
                    height: '300px',
                    background: 'rgba(255, 255, 255, 0.02)',
                    borderRadius: 'var(--radius-lg)',
                    border: '1px solid var(--border-secondary)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    overflow: 'hidden'
                  }}>
                    {/* Simulated Chart */}
                    <div style={{
                      position: 'relative',
                      width: '100%',
                      height: '200px',
                      display: 'flex',
                      alignItems: 'end',
                      justifyContent: 'space-around',
                      padding: '0 20px'
                    }}>
                      {[...Array(12)].map((_, i) => {
                        const height = Math.random() * 150 + 50;
                        const isPositive = Math.random() > 0.5;
                        return (
                          <div
                            key={i}
                            style={{
                              width: '8px',
                              height: `${height}px`,
                              background: isPositive 
                                ? 'linear-gradient(0deg, #10b981 0%, #059669 100%)'
                                : 'linear-gradient(0deg, #ef4444 0%, #dc2626 100%)',
                              borderRadius: '4px',
                              opacity: 0.8,
                              animation: `grow 1s ease-out ${i * 0.1}s both`
                            }}
                          />
                        );
                      })}
                    </div>
                    
                    <div style={{
                      position: 'absolute',
                      top: '50%',
                      left: '50%',
                      transform: 'translate(-50%, -50%)',
                      fontSize: '48px',
                      opacity: 0.1
                    }}>
                      📈
                    </div>
                  </div>
                </div>
              </div>

              {/* Slide Indicators */}
              <div style={{
                position: 'absolute',
                bottom: '20px',
                left: '50%',
                transform: 'translateX(-50%)',
                display: 'flex',
                gap: '8px'
              }}>
                {topCryptos.map((_, i) => (
                  <button
                    key={i}
                    onClick={() => setCurrentSlide(i)}
                    style={{
                      width: '12px',
                      height: '12px',
                      borderRadius: '50%',
                      border: 'none',
                      background: i === currentSlide 
                        ? 'var(--text-accent)'
                        : 'rgba(255, 255, 255, 0.3)',
                      cursor: 'pointer',
                      transition: 'var(--transition-smooth)',
                      boxShadow: i === currentSlide 
                        ? '0 0 12px var(--text-accent)'
                        : 'none'
                    }}
                  />
                ))}
              </div>
            </div>
          )}

          {/* Quick Stats Grid */}
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
            gap: '24px'
          }}>
            {topCryptos.map((crypto, index) => (
              <div
                key={crypto.symbol}
                className="card"
                style={{
                  padding: '24px',
                  textAlign: 'center',
                  background: 'var(--bg-card)',
                  border: '1px solid var(--border-primary)',
                  borderRadius: 'var(--radius-lg)',
                  transition: 'var(--transition-smooth)',
                  cursor: 'pointer',
                  position: 'relative',
                  overflow: 'hidden'
                }}
                onClick={() => setCurrentSlide(index)}
                onMouseEnter={(e) => {
                  e.currentTarget.style.transform = 'translateY(-4px)';
                  e.currentTarget.style.boxShadow = '0 12px 28px rgba(0, 0, 0, 0.2)';
                  e.currentTarget.style.borderColor = getRiskColor(crypto.risk_level);
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.transform = 'translateY(0)';
                  e.currentTarget.style.boxShadow = '0 4px 12px rgba(0, 0, 0, 0.1)';
                  e.currentTarget.style.borderColor = 'var(--border-primary)';
                }}
              >
                {/* Background Effect */}
                <div style={{
                  position: 'absolute',
                  top: '-50%',
                  right: '-50%',
                  width: '100%',
                  height: '100%',
                  background: `radial-gradient(circle, ${getRiskColor(crypto.risk_level)}08 0%, transparent 70%)`,
                  borderRadius: '50%'
                }} />

                <div style={{
                  position: 'relative',
                  zIndex: 2
                }}>
                  <div style={{
                    width: '50px',
                    height: '50px',
                    background: `linear-gradient(135deg, ${getRiskColor(crypto.risk_level)} 0%, ${getRiskColor(crypto.risk_level)}80 100%)`,
                    borderRadius: '12px',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontSize: '20px',
                    fontWeight: '900',
                    color: 'white',
                    margin: '0 auto 16px',
                    boxShadow: `0 8px 20px ${getRiskColor(crypto.risk_level)}30`
                  }}>
                    #{index + 1}
                  </div>

                  <h4 style={{
                    fontSize: '18px',
                    fontWeight: '700',
                    color: 'var(--text-primary)',
                    margin: '0 0 8px 0'
                  }}>
                    {crypto.name}
                  </h4>

                  <p style={{
                    fontSize: '14px',
                    color: 'var(--text-tertiary)',
                    margin: '0 0 16px 0',
                    fontWeight: '600'
                  }}>
                    {crypto.symbol}
                  </p>

                  <p style={{
                    fontSize: '20px',
                    fontWeight: '800',
                    color: 'var(--text-primary)',
                    margin: 0
                  }}>
                    ${crypto.current_price?.toLocaleString()}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section style={{ padding: '80px 0' }}>
        <div className="container">
          <div style={{ textAlign: 'center', marginBottom: '60px' }}>
            <h2 style={{
              fontSize: 'clamp(2rem, 5vw, 3rem)',
              fontWeight: '800',
              marginBottom: '20px',
              background: 'linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              backgroundClip: 'text'
            }}>
              ⚡ Funcionalidades Avanzadas
            </h2>
          </div>

          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
            gap: '40px'
          }}>
            {[
              {
                icon: "🤖",
                title: "Análisis con IA",
                description: "Algoritmos avanzados analizan el mercado 24/7 para identificar las mejores oportunidades de inversión.",
                color: "#667eea"
              },
              {
                icon: "📊",
                title: "Dashboard Interactivo",
                description: "Visualiza todas tus inversiones y métricas del mercado en un panel elegante y fácil de usar.",
                color: "#10b981"
              },
              {
                icon: "🎯",
                title: "Gestión de Riesgos",
                description: "Evalúa automáticamente el riesgo de cada inversión y optimiza tu portafolio para máxima rentabilidad.",
                color: "#f59e0b"
              },
              {
                icon: "⚡",
                title: "Datos en Tiempo Real",
                description: "Información actualizada al instante desde las principales exchanges del mundo.",
                color: "#ef4444"
              },
              {
                icon: "🔒",
                title: "Seguridad Total",
                description: "Tus datos están protegidos con encriptación de grado militar y autenticación avanzada.",
                color: "#8b5cf6"
              },
              {
                icon: "📱",
                title: "Multiplataforma",
                description: "Accede desde cualquier dispositivo con una experiencia fluida y responsiva.",
                color: "#06b6d4"
              }
            ].map((feature, index) => (
              <div
                key={index}
                className="card"
                style={{
                  padding: '40px',
                  background: 'var(--bg-card)',
                  border: '1px solid var(--border-primary)',
                  borderRadius: 'var(--radius-xl)',
                  transition: 'var(--transition-smooth)',
                  position: 'relative',
                  overflow: 'hidden'
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.transform = 'translateY(-8px)';
                  e.currentTarget.style.boxShadow = `0 20px 40px ${feature.color}20`;
                  e.currentTarget.style.borderColor = `${feature.color}40`;
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.transform = 'translateY(0)';
                  e.currentTarget.style.boxShadow = '0 4px 12px rgba(0, 0, 0, 0.1)';
                  e.currentTarget.style.borderColor = 'var(--border-primary)';
                }}
              >
                {/* Background Gradient */}
                <div style={{
                  position: 'absolute',
                  top: '-50%',
                  right: '-50%',
                  width: '150%',
                  height: '150%',
                  background: `radial-gradient(circle, ${feature.color}08 0%, transparent 50%)`,
                  borderRadius: '50%'
                }} />

                <div style={{ position: 'relative', zIndex: 2 }}>
                  <div style={{
                    width: '70px',
                    height: '70px',
                    background: `linear-gradient(135deg, ${feature.color} 0%, ${feature.color}80 100%)`,
                    borderRadius: '18px',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontSize: '28px',
                    marginBottom: '24px',
                    boxShadow: `0 12px 28px ${feature.color}30`
                  }}>
                    {feature.icon}
                  </div>

                  <h3 style={{
                    fontSize: '24px',
                    fontWeight: '700',
                    color: 'var(--text-primary)',
                    marginBottom: '16px'
                  }}>
                    {feature.title}
                  </h3>

                  <p style={{
                    fontSize: '16px',
                    color: 'var(--text-secondary)',
                    lineHeight: '1.6',
                    margin: 0
                  }}>
                    {feature.description}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Call to Action */}
      <section style={{
        padding: '80px 0',
        background: 'linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(139, 92, 246, 0.1) 100%)',
        borderTop: '1px solid var(--border-secondary)'
      }}>
        <div className="container" style={{ textAlign: 'center' }}>
          <h2 style={{
            fontSize: 'clamp(2rem, 5vw, 3rem)',
            fontWeight: '800',
            marginBottom: '24px',
            color: 'var(--text-primary)'
          }}>
            🚀 Comienza tu Journey Cripto
          </h2>
          
          <p style={{
            fontSize: '20px',
            color: 'var(--text-secondary)',
            marginBottom: '40px',
            maxWidth: '600px',
            margin: '0 auto 40px'
          }}>
            Únete a miles de inversores que ya están maximizando sus ganancias con nuestra IA
          </p>

          <button
            onClick={() => navigate('/dashboard')}
            style={{
              padding: '20px 40px',
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              border: 'none',
              borderRadius: 'var(--radius-xl)',
              color: 'white',
              fontSize: '18px',
              fontWeight: '700',
              cursor: 'pointer',
              transition: 'var(--transition-smooth)',
              boxShadow: '0 12px 32px rgba(102, 126, 234, 0.3)',
              textTransform: 'uppercase',
              letterSpacing: '1px'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.transform = 'translateY(-4px) scale(1.05)';
              e.currentTarget.style.boxShadow = '0 20px 40px rgba(102, 126, 234, 0.4)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.transform = 'translateY(0) scale(1)';
              e.currentTarget.style.boxShadow = '0 12px 32px rgba(102, 126, 234, 0.3)';
            }}
          >
            Explorar Dashboard
          </button>
        </div>
      </section>

      <style jsx>{`
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }

        @keyframes float {
          0%, 100% { transform: translateY(0px); }
          50% { transform: translateY(-20px); }
        }

        @keyframes grow {
          from {
            height: 0;
            opacity: 0;
          }
          to {
            opacity: 1;
          }
        }

        @media (max-width: 768px) {
          .grid-2 {
            grid-template-columns: 1fr !important;
          }
        }
      `}</style>
    </div>
  );
}
