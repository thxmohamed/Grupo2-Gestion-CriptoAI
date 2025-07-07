import React, { useState, useEffect } from 'react';
import { createPortal } from 'react-dom';
import apiClient from '../http-common';

export default function TelegramSubscription({ user }) {
  const [showModal, setShowModal] = useState(false);
  const [showConfirmModal, setShowConfirmModal] = useState(false);
  const [isSubscribed, setIsSubscribed] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [userProfile, setUserProfile] = useState(null);

  // Manejar escape y prevenir scroll del body
  useEffect(() => {
    const handleEscape = (e) => {
      if (e.key === 'Escape' && (showModal || showConfirmModal)) {
        setShowModal(false);
        setShowConfirmModal(false);
      }
    };

    if (showModal || showConfirmModal) {
      document.addEventListener('keydown', handleEscape);
      // Prevenir scroll del body cuando el modal está abierto
      document.body.style.overflow = 'hidden';
    }

    return () => {
      document.removeEventListener('keydown', handleEscape);
      document.body.style.overflow = 'unset';
    };
  }, [showModal, showConfirmModal]);

  // Verificar estado de suscripción al cargar el componente
  useEffect(() => {
    const checkSubscriptionStatus = async () => {
      try {
        const userData = JSON.parse(localStorage.getItem('userData'));
        if (userData && userData.user_id) {
          const response = await apiClient.get(`/api/user-profiles/by-id/${userData.user_id}`);
          setIsSubscribed(response.data.is_subscribed);
        }
      } catch (error) {
        console.error('Error checking subscription status:', error);
      }
    };

    checkSubscriptionStatus();
  }, []);

  const handleSubscribe = () => {
    setShowConfirmModal(true);
  };

  const handleCloseModal = () => {
    setShowModal(false);
  };

  const handleCloseConfirmModal = () => {
    setShowConfirmModal(false);
  };

  const handleOpenTelegram = () => {
    // Abrir el enlace de Telegram en una nueva ventana
    window.open('https://t.me/cryptoadvisorGrupo2_bot', '_blank');
  };

  const handleConfirmSubscription = async () => {
    setLoading(true);
    setError(null);

    try {
      // Obtener userData del localStorage
      const userData = JSON.parse(localStorage.getItem('userData'));
      if (!userData || !userData.user_id) {
        throw new Error('No se encontró información del usuario. Por favor, inicia sesión nuevamente.');
      }

      // Obtener los datos del usuario desde la API
      const userResponse = await apiClient.get(`/api/user-profiles/by-id/${userData.user_id}`);
      const userProfileData = userResponse.data;
      setUserProfile(userProfileData);

      // Preparar los datos para la suscripción
      const subscriptionData = {
        user_id: userProfileData.user_id,
        email: userProfileData.email,
        phone: userProfileData.telefono || '',
        notification_type: "email",
        frequency: "daily",
        risk_tolerance: userProfileData.risk_tolerance || "moderate",
        investment_amount: userProfileData.investment_amount || 1000,
        investment_horizon: userProfileData.investment_horizon || "medium",
        preferred_sectors: []
      };

      // Llamar a la API de suscripción
      const subscriptionResponse = await apiClient.post('/api/subscribe', subscriptionData);
      
      if (subscriptionResponse.data.success) {
        // Actualizar el estado de suscripción en el backend
        await apiClient.put(`/api/user-profiles/by-id/${userData.user_id}`, {
          ...userProfileData,
          is_subscribed: true
        });
        
        setIsSubscribed(true);
        setShowConfirmModal(false);
        setShowModal(true); // Mostrar el modal de instrucciones de Telegram
      } else {
        throw new Error(subscriptionResponse.data.message || 'Error al procesar la suscripción');
      }

    } catch (error) {
      console.error('Error en suscripción:', error);
      setError(error.response?.data?.detail || error.message || 'Error al procesar la suscripción');
    } finally {
      setLoading(false);
    }
  };

  const handleFinalConfirmation = () => {
    setShowModal(false);
  };

  return (
    <>
      {/* Botón de suscripción */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        gap: '8px',
        padding: '8px 16px',
        background: isSubscribed ? 'var(--bg-success)' : 'var(--bg-card)',
        borderRadius: '8px',
        border: `1px solid ${isSubscribed ? 'var(--border-success)' : 'var(--border-primary)'}`
      }}>
        <span style={{ fontSize: '16px' }}>
          {isSubscribed ? '✅' : '📱'}
        </span>
        <span style={{ color: 'var(--text-secondary)', fontSize: '14px' }}>
          {isSubscribed ? 'Suscrito a' : 'Suscribirse a'} Telegram:
        </span>
        <button
          onClick={isSubscribed ? null : handleSubscribe}
          disabled={isSubscribed}
          style={{
            background: isSubscribed ? 'transparent' : 'linear-gradient(135deg, #0088cc 0%, #0066aa 100%)',
            color: isSubscribed ? 'var(--text-success)' : 'white',
            border: 'none',
            padding: '6px 12px',
            borderRadius: '6px',
            fontSize: '12px',
            fontWeight: '600',
            cursor: isSubscribed ? 'not-allowed' : 'pointer',
            opacity: isSubscribed ? 0.7 : 1,
            transition: 'var(--transition-smooth)',
            textDecoration: 'none'
          }}
          onMouseEnter={(e) => {
            if (!isSubscribed) {
              e.currentTarget.style.transform = 'scale(1.05)';
              e.currentTarget.style.boxShadow = '0 4px 12px rgba(0, 136, 204, 0.3)';
            }
          }}
          onMouseLeave={(e) => {
            if (!isSubscribed) {
              e.currentTarget.style.transform = 'scale(1)';
              e.currentTarget.style.boxShadow = 'none';
            }
          }}
        >
          {isSubscribed ? 'Suscrito' : 'Suscribirse'}
        </button>
      </div>

      {/* Modal de confirmación */}
      {showConfirmModal && createPortal(
        <div 
          style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: 'rgba(0, 0, 0, 0.8)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 10000,
            backdropFilter: 'blur(8px)'
          }}
          onClick={handleCloseConfirmModal}
        >
          <div 
            style={{
              background: 'linear-gradient(135deg, var(--bg-card) 0%, var(--bg-primary) 100%)',
              borderRadius: '20px',
              padding: '40px',
              maxWidth: '500px',
              width: '90%',
              maxHeight: '90vh',
              overflowY: 'auto',
              position: 'relative',
              border: '2px solid var(--border-primary)',
              boxShadow: '0 20px 60px rgba(0, 0, 0, 0.3)',
              backdropFilter: 'blur(20px)'
            }}
            onClick={(e) => e.stopPropagation()}
          >
            {/* Botón de cerrar */}
            <button
              onClick={handleCloseConfirmModal}
              style={{
                position: 'absolute',
                top: '20px',
                right: '20px',
                background: 'transparent',
                border: 'none',
                color: 'var(--text-secondary)',
                fontSize: '24px',
                cursor: 'pointer',
                padding: '8px',
                borderRadius: '50%',
                transition: 'var(--transition-smooth)',
                zIndex: 1
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.background = 'rgba(255, 255, 255, 0.1)';
                e.currentTarget.style.transform = 'scale(1.1)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.background = 'transparent';
                e.currentTarget.style.transform = 'scale(1)';
              }}
            >
              ×
            </button>

            {/* Contenido del modal */}
            <div style={{ textAlign: 'center', marginBottom: '32px' }}>
              <div style={{ fontSize: '48px', marginBottom: '16px' }}>🤔</div>
              <h2 style={{
                fontSize: '24px',
                fontWeight: '800',
                marginBottom: '12px',
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                backgroundClip: 'text'
              }}>
                Confirmar Suscripción
              </h2>
              <p style={{
                color: 'var(--text-secondary)',
                fontSize: '16px',
                lineHeight: '1.6',
                marginBottom: '24px'
              }}>
                ¿Estás seguro que te quieres suscribir a las notificaciones de Telegram?
                <br />
                Recibirás reportes diarios sobre el mercado de criptomonedas.
              </p>
            </div>

            {/* Mostrar error si existe */}
            {error && (
              <div style={{
                background: 'rgba(239, 68, 68, 0.1)',
                border: '1px solid #ef4444',
                borderRadius: '12px',
                padding: '16px',
                marginBottom: '24px',
                color: '#ef4444',
                fontSize: '14px',
                textAlign: 'center'
              }}>
                {error}
              </div>
            )}

            {/* Botones de acción */}
            <div style={{
              display: 'flex',
              gap: '16px',
              justifyContent: 'center',
              flexWrap: 'wrap'
            }}>
              <button
                onClick={handleCloseConfirmModal}
                disabled={loading}
                style={{
                  background: 'transparent',
                  color: 'var(--text-secondary)',
                  border: '2px solid var(--border-primary)',
                  padding: '12px 24px',
                  borderRadius: '12px',
                  fontSize: '16px',
                  fontWeight: '600',
                  cursor: loading ? 'not-allowed' : 'pointer',
                  opacity: loading ? 0.5 : 1,
                  transition: 'var(--transition-smooth)',
                  minWidth: '120px'
                }}
                onMouseEnter={(e) => {
                  if (!loading) {
                    e.currentTarget.style.background = 'rgba(255, 255, 255, 0.1)';
                    e.currentTarget.style.transform = 'scale(1.02)';
                  }
                }}
                onMouseLeave={(e) => {
                  if (!loading) {
                    e.currentTarget.style.background = 'transparent';
                    e.currentTarget.style.transform = 'scale(1)';
                  }
                }}
              >
                No, cancelar
              </button>

              <button
                onClick={handleConfirmSubscription}
                disabled={loading}
                style={{
                  background: loading ? 'var(--bg-secondary)' : 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
                  color: 'white',
                  border: 'none',
                  padding: '12px 24px',
                  borderRadius: '12px',
                  fontSize: '16px',
                  fontWeight: '700',
                  cursor: loading ? 'not-allowed' : 'pointer',
                  opacity: loading ? 0.7 : 1,
                  transition: 'var(--transition-smooth)',
                  minWidth: '120px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: '8px'
                }}
                onMouseEnter={(e) => {
                  if (!loading) {
                    e.currentTarget.style.transform = 'scale(1.05)';
                    e.currentTarget.style.boxShadow = '0 8px 24px rgba(16, 185, 129, 0.4)';
                  }
                }}
                onMouseLeave={(e) => {
                  if (!loading) {
                    e.currentTarget.style.transform = 'scale(1)';
                    e.currentTarget.style.boxShadow = 'none';
                  }
                }}
              >
                {loading ? (
                  <>
                    <div style={{
                      width: '16px',
                      height: '16px',
                      border: '2px solid transparent',
                      borderTop: '2px solid white',
                      borderRadius: '50%',
                      animation: 'spin 1s linear infinite'
                    }} />
                    Procesando...
                  </>
                ) : (
                  <>
                    <span>✅</span>
                    Sí, deseo continuar
                  </>
                )}
              </button>
            </div>
          </div>
        </div>,
        document.body
      )}

      {/* Modal de suscripción usando Portal */}
      {showModal && createPortal(
        <div 
          style={{
            position: 'fixed',
            top: 0,
            left: 0,
            width: '100vw',
            height: '100vh',
            background: 'rgba(0, 0, 0, 0.8)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 99999,
            backdropFilter: 'blur(10px)',
            padding: '20px',
            boxSizing: 'border-box'
          }}
          onClick={handleCloseModal}
        >
          <div 
            style={{
              background: 'var(--bg-card)',
              borderRadius: '16px',
              padding: '32px',
              maxWidth: '500px',
              width: '100%',
              maxHeight: '90vh',
              overflow: 'auto',
              boxShadow: '0 20px 60px rgba(0, 0, 0, 0.5)',
              border: '1px solid var(--border-primary)',
              position: 'relative',
              animation: 'modalAppear 0.3s ease-out'
            }}
            onClick={(e) => e.stopPropagation()}
          >
            {/* Botón de cerrar */}
            <button
              onClick={handleCloseModal}
              style={{
                position: 'absolute',
                top: '16px',
                right: '16px',
                background: 'none',
                border: 'none',
                fontSize: '24px',
                cursor: 'pointer',
                color: 'var(--text-secondary)',
                padding: '4px',
                borderRadius: '50%',
                width: '32px',
                height: '32px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                transition: 'var(--transition-smooth)'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.background = 'var(--bg-secondary)';
                e.currentTarget.style.color = 'var(--text-primary)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.background = 'none';
                e.currentTarget.style.color = 'var(--text-secondary)';
              }}
            >
              ×
            </button>

            {/* Contenido del modal */}
            <div style={{ textAlign: 'center' }}>
              <div style={{
                fontSize: '64px',
                marginBottom: '24px',
                animation: 'bounce 2s ease-in-out infinite',
                background: 'linear-gradient(135deg, #ff6b6b 0%, #ffd93d 100%)',
                borderRadius: '50%',
                width: '100px',
                height: '100px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                margin: '0 auto 24px',
                boxShadow: '0 12px 40px rgba(255, 215, 0, 0.4)'
              }}>
                ⚠️
              </div>
              
              <h2 style={{
                fontSize: '32px',
                fontWeight: '900',
                color: 'var(--text-primary)',
                marginBottom: '24px',
                textTransform: 'uppercase',
                letterSpacing: '2px',
                background: 'linear-gradient(135deg, #ff6b6b 0%, #ffd93d 100%)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                backgroundClip: 'text'
              }}>
                ¡IMPORTANTE!
              </h2>
              
              <div style={{
                background: 'linear-gradient(135deg, rgba(255, 193, 7, 0.1) 0%, rgba(255, 152, 0, 0.1) 100%)',
                border: '2px solid rgba(255, 193, 7, 0.4)',
                borderRadius: '16px',
                padding: '24px',
                marginBottom: '32px',
                textAlign: 'left',
                position: 'relative',
                overflow: 'hidden'
              }}>
                <div style={{
                  position: 'absolute',
                  top: 0,
                  left: 0,
                  right: 0,
                  height: '4px',
                  background: 'linear-gradient(90deg, #ffd93d, #ff6b6b, #ffd93d)',
                  animation: 'shimmer 2s infinite'
                }} />
                
                <h3 style={{
                  fontSize: '20px',
                  fontWeight: '700',
                  color: 'var(--text-primary)',
                  marginBottom: '16px',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '12px'
                }}>
                  📋 Para suscribirse al bot de Telegram:
                </h3>
                
                <p style={{
                  color: 'var(--text-secondary)',
                  fontSize: '16px',
                  lineHeight: '1.6',
                  marginBottom: '20px'
                }}>
                  Necesitas enviar el siguiente comando al bot de Telegram:
                </p>
                
                <div style={{
                  background: 'rgba(0, 0, 0, 0.6)',
                  padding: '16px 20px',
                  borderRadius: '12px',
                  marginBottom: '20px',
                  fontFamily: 'monospace',
                  fontSize: '18px',
                  color: '#00ff88',
                  border: '2px solid rgba(0, 255, 136, 0.3)',
                  boxShadow: '0 0 20px rgba(0, 255, 136, 0.2)',
                  position: 'relative',
                  textAlign: 'center'
                }}>
                  <div style={{
                    position: 'absolute',
                    top: '8px',
                    left: '12px',
                    fontSize: '12px',
                    color: 'rgba(255, 255, 255, 0.7)',
                    textTransform: 'uppercase',
                    letterSpacing: '1px'
                  }}>
                    Comando:
                  </div>
                  <div style={{
                    marginTop: '8px',
                    fontSize: '20px',
                    fontWeight: '700',
                    letterSpacing: '1px'
                  }}>
                    /start {userProfile?.user_id}
                  </div>
                </div>
                
                <div style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '12px',
                  padding: '12px 16px',
                  background: 'rgba(0, 136, 204, 0.1)',
                  border: '1px solid rgba(0, 136, 204, 0.3)',
                  borderRadius: '8px',
                  marginBottom: '20px'
                }}>
                  <span style={{ fontSize: '24px' }}>🔗</span>
                  <div>
                    <p style={{ 
                      margin: 0, 
                      fontSize: '14px', 
                      color: 'var(--text-secondary)',
                      fontWeight: '600'
                    }}>
                      Bot oficial de Telegram:
                    </p>
                    <p style={{ 
                      margin: 0, 
                      fontSize: '16px', 
                      color: '#0088cc',
                      fontWeight: '700'
                    }}>
                      t.me/cryptoadvisorGrupo2_bot
                    </p>
                  </div>
                </div>
              </div>

              <div style={{
                display: 'flex',
                gap: '16px',
                justifyContent: 'center',
                flexWrap: 'wrap',
                marginBottom: '24px'
              }}>
                <button
                  onClick={handleOpenTelegram}
                  style={{
                    background: 'linear-gradient(135deg, #0088cc 0%, #0066aa 100%)',
                    color: 'white',
                    border: 'none',
                    padding: '16px 32px',
                    borderRadius: '12px',
                    fontSize: '16px',
                    fontWeight: '700',
                    cursor: 'pointer',
                    transition: 'var(--transition-smooth)',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '12px',
                    boxShadow: '0 8px 24px rgba(0, 136, 204, 0.4)',
                    textTransform: 'uppercase',
                    letterSpacing: '1px'
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.transform = 'scale(1.05) translateY(-2px)';
                    e.currentTarget.style.boxShadow = '0 12px 32px rgba(0, 136, 204, 0.5)';
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.transform = 'scale(1) translateY(0)';
                    e.currentTarget.style.boxShadow = '0 8px 24px rgba(0, 136, 204, 0.4)';
                  }}
                >
                  <span style={{ fontSize: '20px' }}>📱</span>
                  Abrir Bot de Telegram
                </button>
                
                <button
                  onClick={handleFinalConfirmation}
                  style={{
                    background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
                    color: 'white',
                    border: 'none',
                    padding: '16px 32px',
                    borderRadius: '12px',
                    fontSize: '16px',
                    fontWeight: '700',
                    cursor: 'pointer',
                    transition: 'var(--transition-smooth)',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '12px',
                    boxShadow: '0 8px 24px rgba(16, 185, 129, 0.4)',
                    textTransform: 'uppercase',
                    letterSpacing: '1px'
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.transform = 'scale(1.05) translateY(-2px)';
                    e.currentTarget.style.boxShadow = '0 12px 32px rgba(16, 185, 129, 0.5)';
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.transform = 'scale(1) translateY(0)';
                    e.currentTarget.style.boxShadow = '0 8px 24px rgba(16, 185, 129, 0.4)';
                  }}
                >
                  <span style={{ fontSize: '20px' }}>✅</span>
                  Confirmar Suscripción
                </button>
              </div>
              
              <div style={{
                padding: '16px 20px',
                background: 'rgba(16, 185, 129, 0.1)',
                border: '1px solid rgba(16, 185, 129, 0.3)',
                borderRadius: '12px',
                marginBottom: '20px'
              }}>
                <p style={{
                  fontSize: '14px',
                  color: '#10b981',
                  margin: 0,
                  fontWeight: '600',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: '8px',
                  lineHeight: '1.4'
                }}>
                  <span style={{ fontSize: '16px' }}>💡</span>
                  Después de enviar el comando, recibirás notificaciones personalizadas sobre el mercado cripto
                </p>
              </div>
            </div>
          </div>
        </div>,
        document.body
      )}

      <style jsx>{`
        @keyframes modalAppear {
          from {
            opacity: 0;
            transform: scale(0.9) translateY(-20px);
          }
          to {
            opacity: 1;
            transform: scale(1) translateY(0);
          }
        }
        
        @keyframes bounce {
          0%, 20%, 50%, 80%, 100% {
            transform: translateY(0);
          }
          40% {
            transform: translateY(-10px);
          }
          60% {
            transform: translateY(-5px);
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
        
        @keyframes spin {
          0% {
            transform: rotate(0deg);
          }
          100% {
            transform: rotate(360deg);
          }
        }
      `}</style>
    </>
  );
}
