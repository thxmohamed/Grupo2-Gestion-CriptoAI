import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import apiClient from "../http-common";

export default function CryptoDashboard({ user }) {
  const navigate = useNavigate();
  const [metrics, setMetrics] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [rateLimitExceeded, setRateLimitExceeded] = useState(false);
  const [expandedIndex, setExpandedIndex] = useState(null);
  const [sortBy, setSortBy] = useState("market_cap");
  const [filterRisk, setFilterRisk] = useState("all");
  const [currentPage, setCurrentPage] = useState(0);
  const [itemsPerPage, setItemsPerPage] = useState(3); // Número de criptos por página del carrusel
  const [autoPlay, setAutoPlay] = useState(false);
  
  // Estados para el depósito de dinero
  const [depositAmount, setDepositAmount] = useState("");
  const [depositLoading, setDepositLoading] = useState(false);
  const [depositError, setDepositError] = useState(null);
  const [depositSuccess, setDepositSuccess] = useState(false);
  const [currentUser, setCurrentUser] = useState(user);
  const [balanceLoading, setBalanceLoading] = useState(false);
  const [refreshTrigger, setRefreshTrigger] = useState(0);
  const [displayBalance, setDisplayBalance] = useState(user?.wallet_balance || 0);

  // Redirect to login if user is not authenticated
  useEffect(() => {
    if (!user) {
      navigate('/login');
      return;
    }
    // Sincronizar el estado local con las props del usuario
    setCurrentUser(user);
    setDisplayBalance(user?.wallet_balance || 0);
  }, [user, navigate]);

  // Función nuclear para forzar actualización del balance
  const forceBalanceUpdate = (newBalance) => {
    console.log("🚨 FORZANDO ACTUALIZACIÓN NUCLEAR DEL BALANCE:", newBalance);
    
    // Actualizar todos los estados posibles
    setDisplayBalance(newBalance);
    setCurrentUser(prevUser => ({
      ...prevUser,
      wallet_balance: newBalance
    }));
    setRefreshTrigger(prev => prev + 10); // Gran salto para asegurar cambio
    
    // Múltiples actualizaciones con delay
    [50, 100, 200, 500].forEach(delay => {
      setTimeout(() => {
        setDisplayBalance(newBalance);
        setRefreshTrigger(prev => prev + 1);
      }, delay);
    });
  };

  // Función para obtener el balance actualizado del usuario
  const fetchUserBalance = async () => {
    const userId = currentUser?.user_id || user?.user_id;
    if (!userId) return;
    
    setBalanceLoading(true);
    try {
      const response = await apiClient.get(`/api/wallet/balance/${userId}`);
      const updatedBalance = response.data.balance;
      
      console.log("Fetch balance response:", {
        userId,
        balanceAnterior: displayBalance,
        balanceNuevo: updatedBalance,
        timestamp: new Date().toISOString()
      });
      
      // USAR LA FUNCIÓN NUCLEAR
      forceBalanceUpdate(updatedBalance);
      
      return updatedBalance;
    } catch (err) {
      console.error("Error al obtener balance:", err);
      throw err;
    } finally {
      setBalanceLoading(false);
    }
  };

  // Cargar balance al montar el componente
  useEffect(() => {
    if (user?.user_id) {
      fetchUserBalance();
    }
  }, [user?.user_id]); // Solo cuando cambie el user_id del prop, no del estado local

  // Observer para cambios en el balance del usuario
  useEffect(() => {
    console.log("Balance actualizado en UI:", {
      balance: currentUser?.wallet_balance,
      displayBalance: displayBalance,
      formatted: formatBalance(displayBalance),
      timestamp: new Date().toISOString()
    });
  }, [currentUser?.wallet_balance, displayBalance]);

  // Sincronizar displayBalance con currentUser
  useEffect(() => {
    if (currentUser?.wallet_balance !== undefined) {
      setDisplayBalance(currentUser.wallet_balance);
    }
  }, [currentUser?.wallet_balance]);

  useEffect(() => {
    apiClient.get(`/api/economic-metrics/`)
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
  }, []);

  // If user is not authenticated, don't render anything (will redirect)
  if (!user) {
    return null;
  }

  const getGreeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return "Buenos días";
    if (hour < 18) return "Buenas tardes";
    return "Buenas noches";
  };

  const formatBalance = (balance) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2
    }).format(balance);
  };

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

  const toggleExpand = (localIndex) => {
    // Convertir índice local del carrusel a índice global
    const globalIndex = currentPage * itemsPerPage + localIndex;
    setExpandedIndex(expandedIndex === globalIndex ? null : globalIndex);
  };

  const filteredMetrics = metrics.filter(coin => 
    filterRisk === "all" || coin.risk_level === filterRisk
  );

  const sortedMetrics = [...filteredMetrics].sort((a, b) => {
    switch(sortBy) {
      case "market_cap":
        return b.market_cap - a.market_cap;
      case "price":
        return b.current_price - a.current_price;
      case "change":
        return b.price_change_24h - a.price_change_24h;
      case "investment_score":
        return b.investment_score - a.investment_score;
      default:
        return 0;
    }
  });

  // Cálculos para el carrusel
  const totalPages = Math.ceil(sortedMetrics.length / itemsPerPage);
  const currentItems = sortedMetrics.slice(
    currentPage * itemsPerPage,
    (currentPage + 1) * itemsPerPage
  );

  const nextPage = () => {
    setCurrentPage((prev) => (prev + 1) % totalPages);
    setExpandedIndex(null); // Cerrar cualquier tarjeta expandida al cambiar página
  };

  const prevPage = () => {
    setCurrentPage((prev) => (prev - 1 + totalPages) % totalPages);
    setExpandedIndex(null); // Cerrar cualquier tarjeta expandida al cambiar página
  };

  const goToPage = (page) => {
    setCurrentPage(page);
    setExpandedIndex(null);
  };

  // Controles de teclado para el carrusel
  useEffect(() => {
    const handleKeyPress = (event) => {
      const pages = Math.ceil(sortedMetrics.length / itemsPerPage);
      if (pages <= 1) return;
      
      if (event.key === 'ArrowLeft') {
        setCurrentPage((prev) => (prev - 1 + pages) % pages);
        setExpandedIndex(null);
      } else if (event.key === 'ArrowRight') {
        setCurrentPage((prev) => (prev + 1) % pages);
        setExpandedIndex(null);
      }
    };

    window.addEventListener('keydown', handleKeyPress);
    return () => {
      window.removeEventListener('keydown', handleKeyPress);
    };
  }, [sortedMetrics.length, itemsPerPage]);

  // Reset página cuando cambian los filtros
  useEffect(() => {
    setCurrentPage(0);
    setExpandedIndex(null);
  }, [sortBy, filterRisk, itemsPerPage]);

  // Función para manejar el depósito de dinero
  const handleDeposit = async () => {
    if (!currentUser) {
      setDepositError("Debe estar logueado para realizar un depósito");
      return;
    }

    const amount = parseFloat(depositAmount);
    
    // Validaciones
    if (isNaN(amount) || amount <= 0) {
      setDepositError("Por favor ingrese un monto válido mayor a 0");
      return;
    }

    if (amount > 10000) {
      setDepositError("El monto máximo permitido es $10,000");
      return;
    }

    const newBalance = (displayBalance || 0) + amount;
    if (newBalance > 10000) {
      setDepositError(`El depósito excedería el límite máximo. Balance actual: ${formatBalance(displayBalance || 0)}`);
      return;
    }

    setDepositLoading(true);
    setDepositError(null);
    setDepositSuccess(false);

    try {
      const response = await apiClient.post(`/api/wallet/deposit/${currentUser.user_id}`, {
        amount: amount
      });

      // Actualizar inmediatamente con el nuevo balance de la respuesta
      const newBalance = response.data.new_balance;
      if (newBalance !== undefined) {
        console.log("Actualizando balance:", {
          anterior: displayBalance,
          nuevo: newBalance,
          timestamp: new Date().toISOString()
        });
        
        // USAR LA FUNCIÓN NUCLEAR
        forceBalanceUpdate(newBalance);
      }
      
      // También obtener el balance actualizado desde la API como respaldo
      try {
        // Esperar un poco antes de refrescar para asegurar que el backend esté actualizado
        setTimeout(async () => {
          await fetchUserBalance();
        }, 500);
      } catch (balanceError) {
        console.warn("Error al refrescar balance después del depósito:", balanceError);
        // Si falla el refresh, seguimos con el balance de la respuesta del depósito
      }
      
      // Limpiar el formulario
      setDepositAmount("");
      setDepositSuccess(true);
      
      // Ocultar mensaje de éxito después de 3 segundos
      setTimeout(() => {
        setDepositSuccess(false);
      }, 3000);

    } catch (err) {
      console.error("Error al realizar depósito:", err);
      if (err.response?.data?.detail) {
        setDepositError(err.response.data.detail);
      } else {
        setDepositError("Error al procesar el depósito. Intente nuevamente.");
      }
    } finally {
      setDepositLoading(false);
    }
  };

  // Auto-play del carrusel
  useEffect(() => {
    const pages = Math.ceil(sortedMetrics.length / itemsPerPage);
    if (!autoPlay || pages <= 1) return;
    
    const interval = setInterval(() => {
      setCurrentPage((prev) => (prev + 1) % pages);
      setExpandedIndex(null);
    }, 5000); // Cambiar cada 5 segundos

    return () => clearInterval(interval);
  }, [autoPlay, sortedMetrics.length, itemsPerPage]);

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
            Cargando datos del mercado...
          </p>
        </div>
      </div>
    );
  }

  if (rateLimitExceeded) {
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
          maxWidth: '500px',
          background: 'rgba(239, 68, 68, 0.1)',
          border: '1px solid rgba(239, 68, 68, 0.2)'
        }}>
          <div style={{ fontSize: '64px', marginBottom: '20px' }}>⚠️</div>
          <h2 style={{ color: '#ef4444', marginBottom: '16px' }}>
            Límite de API alcanzado
          </h2>
          <p style={{ color: 'var(--text-secondary)' }}>
            Hemos alcanzado el límite de peticiones a CoinGecko. 
            Por favor, intenta nuevamente más tarde.
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
          <p style={{ color: 'var(--text-secondary)' }}>{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div style={{
      minHeight: '100vh',
      paddingTop: '100px',
      paddingBottom: '40px',
      background: 'var(--bg-primary)'
    }}>
      <div className="container">
        {/* Personalized Welcome Section */}
        <div className="card" style={{
          padding: '32px',
          marginBottom: '40px',
          background: 'linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(139, 92, 246, 0.1) 100%)',
          border: '1px solid rgba(102, 126, 234, 0.2)',
          position: 'relative',
          overflow: 'hidden'
        }}>
          {/* Decorative elements */}
          <div style={{
            position: 'absolute',
            top: '-50px',
            right: '-50px',
            width: '100px',
            height: '100px',
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            borderRadius: '50%',
            opacity: 0.1,
            filter: 'blur(30px)'
          }} />
          
          <div className="animate-fadeInUp" style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            gap: '24px',
            flexWrap: 'wrap'
          }}>
            <div>
              <h1 style={{
                fontSize: 'clamp(1.8rem, 4vw, 2.5rem)',
                fontWeight: '700',
                color: 'var(--text-primary)',
                marginBottom: '8px',
                display: 'flex',
                alignItems: 'center',
                gap: '12px'
              }}>
                <span>👋</span>
                {getGreeting()}, {currentUser.nombre}!
              </h1>
              <p style={{
                color: 'var(--text-secondary)',
                fontSize: '16px',
                marginBottom: '16px'
              }}>
                Bienvenido a tu dashboard personalizado de CriptoAI. Aquí tienes las mejores oportunidades del mercado.
              </p>
              <div style={{
                display: 'flex',
                gap: '24px',
                flexWrap: 'wrap'
              }}>
                <div 
                  key={`balance-display-${refreshTrigger}`}
                  style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                  padding: '8px 16px',
                  background: 'var(--bg-card)',
                  borderRadius: '8px',
                  border: '1px solid var(--border-primary)'
                }}>
                  <span style={{ fontSize: '16px' }}>💰</span>
                  <span style={{ color: 'var(--text-secondary)', fontSize: '14px' }}>Balance:</span>
                  {balanceLoading ? (
                    <div style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '8px'
                    }}>
                      <div style={{
                        width: '12px',
                        height: '12px',
                        border: '2px solid rgba(16, 185, 129, 0.3)',
                        borderTop: '2px solid #10b981',
                        borderRadius: '50%',
                        animation: 'spin 1s linear infinite'
                      }} />
                      <span style={{ color: 'var(--text-tertiary)', fontSize: '12px' }}>
                        Actualizando...
                      </span>
                    </div>
                  ) : (
                    <span style={{ color: 'var(--text-accent)', fontWeight: '600' }}>
                      {formatBalance(displayBalance)}
                    </span>
                  )}
                  <button
                    onClick={fetchUserBalance}
                    disabled={balanceLoading}
                    style={{
                      width: '20px',
                      height: '20px',
                      border: 'none',
                      background: 'transparent',
                      cursor: balanceLoading ? 'not-allowed' : 'pointer',
                      fontSize: '12px',
                      color: 'var(--text-secondary)',
                      opacity: balanceLoading ? 0.5 : 0.7,
                      transition: 'var(--transition-smooth)',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center'
                    }}
                    onMouseEnter={(e) => {
                      if (!balanceLoading) {
                        e.currentTarget.style.opacity = '1';
                        e.currentTarget.style.transform = 'scale(1.1)';
                      }
                    }}
                    onMouseLeave={(e) => {
                      if (!balanceLoading) {
                        e.currentTarget.style.opacity = '0.7';
                        e.currentTarget.style.transform = 'scale(1)';
                      }
                    }}
                    title="Actualizar balance"
                  >
                    🔄
                  </button>
                  
                  {/* DEBUG BUTTON - TEMPORAL */}
                  <button
                    onClick={() => {
                      console.log("🔧 ESTADO DEBUG:", {
                        currentUser: currentUser?.wallet_balance,
                        displayBalance: displayBalance,
                        refreshTrigger: refreshTrigger
                      });
                      forceBalanceUpdate(displayBalance);
                    }}
                    style={{
                      padding: '4px 8px',
                      fontSize: '10px',
                      background: 'rgba(255, 255, 0, 0.2)',
                      border: '1px solid rgba(255, 255, 0, 0.5)',
                      borderRadius: '4px',
                      color: '#ffeb3b',
                      cursor: 'pointer'
                    }}
                    title="Debug: Forzar actualización"
                  >
                    🔧
                  </button>
                </div>
                <div style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                  padding: '8px 16px',
                  background: 'var(--bg-card)',
                  borderRadius: '8px',
                  border: '1px solid var(--border-primary)'
                }}>
                  <span style={{ fontSize: '16px' }}>🆔</span>
                  <span style={{ color: 'var(--text-secondary)', fontSize: '14px' }}>ID:</span>
                  <span style={{ color: 'var(--text-primary)', fontWeight: '600' }}>
                    {currentUser.user_id}
                  </span>
                </div>
              </div>
            </div>
            
            <div style={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              gap: '12px'
            }}>
              <div style={{
                width: '80px',
                height: '80px',
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                borderRadius: '50%',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '32px',
                color: 'white',
                boxShadow: '0 8px 32px rgba(102, 126, 234, 0.3)'
              }}>
                {currentUser.nombre ? currentUser.nombre.charAt(0).toUpperCase() : '👤'}
              </div>
              <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                padding: '4px 12px',
                background: 'rgba(16, 185, 129, 0.1)',
                border: '1px solid rgba(16, 185, 129, 0.3)',
                borderRadius: '20px',
                fontSize: '12px',
                fontWeight: '600',
                color: '#10b981'
              }}>
                <div style={{
                  width: '6px',
                  height: '6px',
                  background: '#10b981',
                  borderRadius: '50%',
                  animation: 'pulse 2s infinite'
                }} />
                ACTIVO
              </div>
            </div>
          </div>
        </div>

        {/* Wallet Deposit Section */}
        {currentUser && (
          <div className="card animate-fadeInUp" style={{
            padding: '32px',
            marginBottom: '40px',
            background: 'linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(5, 150, 105, 0.1) 100%)',
            border: '1px solid rgba(16, 185, 129, 0.2)',
            position: 'relative',
            overflow: 'hidden'
          }}>
            {/* Decorative elements */}
            <div style={{
              position: 'absolute',
              top: '-30px',
              left: '-30px',
              width: '80px',
              height: '80px',
              background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
              borderRadius: '50%',
              opacity: 0.1,
              filter: 'blur(20px)'
            }} />
            
            <div style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'flex-start',
              gap: '32px',
              flexWrap: 'wrap'
            }}>
              <div style={{ flex: '1', minWidth: '300px' }}>
                <h2 style={{
                  fontSize: 'clamp(1.5rem, 3vw, 2rem)',
                  fontWeight: '700',
                  color: 'var(--text-primary)',
                  marginBottom: '12px',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '12px'
                }}>
                  <span>💰</span>
                  Cargar Dinero a tu Wallet
                </h2>
                <p style={{
                  color: 'var(--text-secondary)',
                  fontSize: '16px',
                  marginBottom: '24px',
                  lineHeight: '1.5'
                }}>
                  Añade fondos a tu wallet para empezar a invertir en criptomonedas. 
                  Límite máximo: <strong style={{ color: 'var(--text-accent)' }}>$10,000</strong>
                </p>

                {/* Deposit Form */}
                <div style={{
                  display: 'flex',
                  gap: '16px',
                  alignItems: 'flex-end',
                  flexWrap: 'wrap',
                  marginBottom: '20px'
                }}>
                  <div style={{ flex: '1', minWidth: '200px' }}>
                    <label style={{
                      display: 'block',
                      fontSize: '14px',
                      fontWeight: '600',
                      color: 'var(--text-secondary)',
                      marginBottom: '8px'
                    }}>
                      Monto a depositar (USD)
                    </label>
                    <input
                      type="number"
                      min="0"
                      max="10000"
                      step="0.01"
                      value={depositAmount}
                      onChange={(e) => {
                        setDepositAmount(e.target.value);
                        setDepositError(null);
                        setDepositSuccess(false);
                      }}
                      placeholder="Ingrese el monto..."
                      disabled={depositLoading}
                      style={{
                        width: '100%',
                        padding: '16px 20px',
                        background: 'var(--bg-card)',
                        border: '1px solid var(--border-primary)',
                        borderRadius: 'var(--radius-md)',
                        color: 'var(--text-primary)',
                        fontSize: '16px',
                        outline: 'none',
                        transition: 'var(--transition-smooth)',
                        backdropFilter: 'blur(10px)'
                      }}
                      onFocus={(e) => {
                        e.currentTarget.style.borderColor = 'rgba(16, 185, 129, 0.5)';
                        e.currentTarget.style.boxShadow = '0 0 0 3px rgba(16, 185, 129, 0.1)';
                      }}
                      onBlur={(e) => {
                        e.currentTarget.style.borderColor = 'var(--border-primary)';
                        e.currentTarget.style.boxShadow = 'none';
                      }}
                    />
                  </div>

                  <button
                    onClick={handleDeposit}
                    disabled={depositLoading || !depositAmount || parseFloat(depositAmount) <= 0}
                    style={{
                      padding: '16px 32px',
                      background: depositLoading || !depositAmount || parseFloat(depositAmount) <= 0
                        ? 'rgba(255, 255, 255, 0.1)'
                        : 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
                      border: 'none',
                      borderRadius: 'var(--radius-md)',
                      color: depositLoading || !depositAmount || parseFloat(depositAmount) <= 0
                        ? 'var(--text-tertiary)'
                        : 'white',
                      fontSize: '16px',
                      fontWeight: '600',
                      cursor: depositLoading || !depositAmount || parseFloat(depositAmount) <= 0
                        ? 'not-allowed'
                        : 'pointer',
                      transition: 'var(--transition-smooth)',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '8px',
                      boxShadow: depositLoading || !depositAmount || parseFloat(depositAmount) <= 0
                        ? 'none'
                        : '0 4px 12px rgba(16, 185, 129, 0.3)',
                      minWidth: '140px',
                      justifyContent: 'center'
                    }}
                    onMouseEnter={(e) => {
                      if (!depositLoading && depositAmount && parseFloat(depositAmount) > 0) {
                        e.currentTarget.style.transform = 'translateY(-2px)';
                        e.currentTarget.style.boxShadow = '0 6px 20px rgba(16, 185, 129, 0.4)';
                      }
                    }}
                    onMouseLeave={(e) => {
                      if (!depositLoading && depositAmount && parseFloat(depositAmount) > 0) {
                        e.currentTarget.style.transform = 'translateY(0)';
                        e.currentTarget.style.boxShadow = '0 4px 12px rgba(16, 185, 129, 0.3)';
                      }
                    }}
                  >
                    {depositLoading ? (
                      <>
                        <div style={{
                          width: '16px',
                          height: '16px',
                          border: '2px solid transparent',
                          borderTop: '2px solid currentColor',
                          borderRadius: '50%',
                          animation: 'spin 1s linear infinite'
                        }} />
                        Procesando...
                      </>
                    ) : (
                      <>
                        💳 Depositar
                      </>
                    )}
                  </button>
                </div>

                {/* Quick Amount Buttons */}
                <div style={{
                  display: 'flex',
                  gap: '12px',
                  flexWrap: 'wrap',
                  marginBottom: '20px'
                }}>
                  <span style={{
                    fontSize: '14px',
                    color: 'var(--text-secondary)',
                    fontWeight: '600',
                    alignSelf: 'center'
                  }}>
                    Montos rápidos:
                  </span>
                  {[100, 500, 1000, 5000].map(amount => (
                    <button
                      key={amount}
                      onClick={() => {
                        setDepositAmount(amount.toString());
                        setDepositError(null);
                        setDepositSuccess(false);
                      }}
                      disabled={depositLoading}
                      style={{
                        padding: '8px 16px',
                        background: 'rgba(16, 185, 129, 0.1)',
                        border: '1px solid rgba(16, 185, 129, 0.3)',
                        borderRadius: '20px',
                        color: '#10b981',
                        fontSize: '12px',
                        fontWeight: '600',
                        cursor: depositLoading ? 'not-allowed' : 'pointer',
                        transition: 'var(--transition-smooth)',
                        opacity: depositLoading ? 0.5 : 1
                      }}
                      onMouseEnter={(e) => {
                        if (!depositLoading) {
                          e.currentTarget.style.background = 'rgba(16, 185, 129, 0.2)';
                          e.currentTarget.style.transform = 'scale(1.05)';
                        }
                      }}
                      onMouseLeave={(e) => {
                        if (!depositLoading) {
                          e.currentTarget.style.background = 'rgba(16, 185, 129, 0.1)';
                          e.currentTarget.style.transform = 'scale(1)';
                        }
                      }}
                    >
                      ${amount.toLocaleString()}
                    </button>
                  ))}
                </div>

                {/* Status Messages */}
                {depositError && (
                  <div style={{
                    padding: '12px 16px',
                    background: 'rgba(239, 68, 68, 0.1)',
                    border: '1px solid rgba(239, 68, 68, 0.3)',
                    borderRadius: 'var(--radius-md)',
                    color: '#ef4444',
                    fontSize: '14px',
                    fontWeight: '600',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '8px',
                    marginBottom: '12px'
                  }}>
                    <span>⚠️</span>
                    {depositError}
                  </div>
                )}

                {depositSuccess && (
                  <div style={{
                    padding: '12px 16px',
                    background: 'rgba(16, 185, 129, 0.1)',
                    border: '1px solid rgba(16, 185, 129, 0.3)',
                    borderRadius: 'var(--radius-md)',
                    color: '#10b981',
                    fontSize: '14px',
                    fontWeight: '600',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '8px',
                    marginBottom: '12px'
                  }}>
                    <span>✅</span>
                    ¡Depósito realizado exitosamente! Tu balance ha sido actualizado.
                  </div>
                )}
              </div>

              {/* Balance Display */}
              <div style={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                gap: '16px',
                minWidth: '200px'
              }}>
                <div style={{
                  width: '120px',
                  height: '120px',
                  background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
                  borderRadius: '50%',
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  justifyContent: 'center',
                  boxShadow: '0 8px 32px rgba(16, 185, 129, 0.3)',
                  position: 'relative',
                  overflow: 'hidden'
                }}>
                  <div style={{
                    position: 'absolute',
                    top: '-10px',
                    right: '-10px',
                    width: '40px',
                    height: '40px',
                    background: 'rgba(255, 255, 255, 0.2)',
                    borderRadius: '50%',
                    filter: 'blur(15px)'
                  }} />
                  <span style={{
                    fontSize: '32px',
                    marginBottom: '4px'
                  }}>💰</span>
                  <span style={{
                    color: 'white',
                    fontSize: '12px',
                    fontWeight: '600',
                    textTransform: 'uppercase',
                    letterSpacing: '0.5px'
                  }}>
                    Balance
                  </span>
                </div>
                
                <div 
                  key={`balance-big-display-${refreshTrigger}`}
                  style={{
                  textAlign: 'center',
                  padding: '16px 24px',
                  background: 'var(--bg-card)',
                  borderRadius: 'var(--radius-lg)',
                  border: '1px solid var(--border-primary)',
                  backdropFilter: 'blur(10px)'
                }}>
                  {balanceLoading ? (
                    <div style={{
                      display: 'flex',
                      flexDirection: 'column',
                      alignItems: 'center',
                      gap: '12px'
                    }}>
                      <div style={{
                        width: '24px',
                        height: '24px',
                        border: '3px solid rgba(16, 185, 129, 0.3)',
                        borderTop: '3px solid #10b981',
                        borderRadius: '50%',
                        animation: 'spin 1s linear infinite'
                      }} />
                      <p style={{
                        fontSize: '14px',
                        color: 'var(--text-tertiary)',
                        margin: 0
                      }}>
                        Actualizando balance...
                      </p>
                    </div>
                  ) : (
                    <>
                      <p style={{
                        fontSize: '28px',
                        fontWeight: '900',
                        color: 'var(--text-accent)',
                        margin: '0 0 4px 0',
                        background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
                        WebkitBackgroundClip: 'text',
                        WebkitTextFillColor: 'transparent',
                        backgroundClip: 'text'
                      }}>
                        {formatBalance(displayBalance)}
                      </p>
                      <p style={{
                        fontSize: '12px',
                        color: 'var(--text-tertiary)',
                        margin: 0,
                        textTransform: 'uppercase',
                        letterSpacing: '0.5px'
                      }}>
                        Disponible para invertir
                      </p>
                    </>
                  )}
                </div>

                <div style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                  padding: '8px 16px',
                  background: 'rgba(245, 158, 11, 0.1)',
                  border: '1px solid rgba(245, 158, 11, 0.3)',
                  borderRadius: '20px',
                  fontSize: '12px',
                  fontWeight: '600',
                  color: '#f59e0b'
                }}>
                  <span>⚠️</span>
                  Límite: $10,000
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Hero Section */}
        <div style={{
          textAlign: 'center',
          padding: '40px 0'
        }}>
          <h1 
            className="animate-fadeInUp crypto-glow"
            style={{
              fontSize: 'clamp(2.5rem, 6vw, 4rem)',
              fontWeight: '900',
              marginBottom: '20px',
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              backgroundClip: 'text',
              letterSpacing: '-2px'
            }}
          >
            Top 20 Criptomonedas
          </h1>
          <p style={{
            fontSize: '18px',
            color: 'var(--text-secondary)',
            maxWidth: '600px',
            margin: '0 auto 40px',
            lineHeight: '1.6'
          }}>
            Análisis completo del mercado cripto con métricas avanzadas, 
            evaluación de riesgos y recomendaciones de inversión en tiempo real.
          </p>


        </div>

        {/* Controls */}
        <div style={{
          display: 'flex',
          gap: '20px',
          marginBottom: '40px',
          flexWrap: 'wrap',
          alignItems: 'center',
          justifyContent: 'space-between'
        }}>
          <div style={{
            display: 'flex',
            gap: '16px',
            alignItems: 'center',
            flexWrap: 'wrap'
          }}>
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              style={{
                padding: '16px 20px',
                background: 'var(--bg-card)',
                border: '1px solid var(--border-primary)',
                borderRadius: 'var(--radius-md)',
                color: 'var(--text-primary)',
                fontSize: '14px',
                backdropFilter: 'blur(10px)',
                cursor: 'pointer',
                outline: 'none',
                minWidth: '200px'
              }}
            >
              <option value="market_cap">Cap. de Mercado</option>
              <option value="price">Precio</option>
              <option value="change">Cambio 24h</option>
              <option value="investment_score">Score Inversión</option>
            </select>

            <select
              value={filterRisk}
              onChange={(e) => setFilterRisk(e.target.value)}
              style={{
                padding: '16px 20px',
                background: 'var(--bg-card)',
                border: '1px solid var(--border-primary)',
                borderRadius: 'var(--radius-md)',
                color: 'var(--text-primary)',
                fontSize: '14px',
                backdropFilter: 'blur(10px)',
                cursor: 'pointer',
                outline: 'none',
                minWidth: '180px'
              }}
            >
              <option value="all">Todos los riesgos</option>
              <option value="low">Riesgo bajo</option>
              <option value="medium">Riesgo medio</option>
              <option value="high">Riesgo alto</option>
            </select>

            <select
              value={itemsPerPage}
              onChange={(e) => setItemsPerPage(parseInt(e.target.value))}
              style={{
                padding: '16px 20px',
                background: 'var(--bg-card)',
                border: '1px solid var(--border-primary)',
                borderRadius: 'var(--radius-md)',
                color: 'var(--text-primary)',
                fontSize: '14px',
                backdropFilter: 'blur(10px)',
                cursor: 'pointer',
                outline: 'none',
                minWidth: '140px'
              }}
            >
              <option value={1}>1 por página</option>
              <option value={2}>2 por página</option>
              <option value={3}>3 por página</option>
              <option value={4}>4 por página</option>
            </select>
          </div>

          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '16px'
          }}>
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              padding: '8px 16px',
              background: 'rgba(16, 185, 129, 0.1)',
              border: '1px solid rgba(16, 185, 129, 0.3)',
              borderRadius: '20px',
              fontSize: '12px',
              fontWeight: '600',
              color: '#10b981',
            }}>
              <div
                style={{
                  width: '8px',
                  height: '8px',
                  background: '#10b981',
                  borderRadius: '50%',
                  boxShadow: '0 0 8px #10b981',
                }}
                className="animate-pulse"
              />
              DATOS EN VIVO
            </div>

            {totalPages > 1 && (
              <>
                <div style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                  padding: '8px 16px',
                  background: 'rgba(102, 126, 234, 0.1)',
                  border: '1px solid rgba(102, 126, 234, 0.3)',
                  borderRadius: '20px',
                  fontSize: '12px',
                  fontWeight: '600',
                  color: '#667eea',
                }}>
                  ⌨️ Use ← → para navegar
                </div>
                
                <button
                  onClick={() => setAutoPlay(!autoPlay)}
                  style={{
                    padding: '8px 16px',
                    background: autoPlay 
                      ? 'rgba(239, 68, 68, 0.1)' 
                      : 'rgba(16, 185, 129, 0.1)',
                    border: autoPlay 
                      ? '1px solid rgba(239, 68, 68, 0.3)' 
                      : '1px solid rgba(16, 185, 129, 0.3)',
                    borderRadius: '20px',
                    fontSize: '12px',
                    fontWeight: '600',
                    color: autoPlay ? '#ef4444' : '#10b981',
                    cursor: 'pointer',
                    transition: 'var(--transition-smooth)',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '6px'
                  }}
                >
                  {autoPlay ? '⏸️ Pausar' : '▶️ Auto'}
                </button>
              </>
            )}
          </div>
        </div>

        {/* Crypto Carousel */}
        <div style={{ 
          position: 'relative',
          marginBottom: '40px'
        }}>
          {/* Carousel Header */}
          <div style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            marginBottom: '32px',
            flexWrap: 'wrap',
            gap: '16px'
          }}>
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '16px'
            }}>
              <h2 style={{
                fontSize: '24px',
                fontWeight: '700',
                color: 'var(--text-primary)',
                margin: 0
              }}>
                📊 Análisis de Criptomonedas
              </h2>
              <div style={{
                fontSize: '14px',
                color: 'var(--text-tertiary)',
                padding: '6px 12px',
                background: 'rgba(255, 255, 255, 0.1)',
                borderRadius: '12px',
                border: '1px solid var(--border-secondary)'
              }}>
                {currentPage + 1} de {totalPages} páginas
              </div>
            </div>

            {/* Navigation Controls */}
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '12px'
            }}>
              <button
                onClick={prevPage}
                disabled={totalPages <= 1}
                style={{
                  padding: '12px 16px',
                  background: totalPages <= 1 
                    ? 'rgba(255, 255, 255, 0.1)' 
                    : 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                  border: 'none',
                  borderRadius: 'var(--radius-md)',
                  color: totalPages <= 1 ? 'var(--text-tertiary)' : 'white',
                  fontSize: '14px',
                  fontWeight: '600',
                  cursor: totalPages <= 1 ? 'not-allowed' : 'pointer',
                  transition: 'var(--transition-smooth)',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                  opacity: totalPages <= 1 ? 0.5 : 1
                }}
                onMouseEnter={(e) => {
                  if (totalPages > 1) {
                    e.currentTarget.style.transform = 'scale(1.05)';
                  }
                }}
                onMouseLeave={(e) => {
                  if (totalPages > 1) {
                    e.currentTarget.style.transform = 'scale(1)';
                  }
                }}
              >
                ← Anterior
              </button>

              {/* Page Indicators */}
              <div style={{
                display: 'flex',
                gap: '6px',
                alignItems: 'center'
              }}>
                {Array.from({ length: totalPages }, (_, i) => (
                  <button
                    key={i}
                    onClick={() => goToPage(i)}
                    style={{
                      width: '10px',
                      height: '10px',
                      borderRadius: '50%',
                      border: 'none',
                      background: i === currentPage 
                        ? 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
                        : 'rgba(255, 255, 255, 0.3)',
                      cursor: 'pointer',
                      transition: 'var(--transition-smooth)',
                      boxShadow: i === currentPage 
                        ? '0 0 12px rgba(102, 126, 234, 0.5)'
                        : 'none'
                    }}
                    onMouseEnter={(e) => {
                      if (i !== currentPage) {
                        e.currentTarget.style.background = 'rgba(255, 255, 255, 0.5)';
                      }
                    }}
                    onMouseLeave={(e) => {
                      if (i !== currentPage) {
                        e.currentTarget.style.background = 'rgba(255, 255, 255, 0.3)';
                      }
                    }}
                  />
                ))}
              </div>

              <button
                onClick={nextPage}
                disabled={totalPages <= 1}
                style={{
                  padding: '12px 16px',
                  background: totalPages <= 1 
                    ? 'rgba(255, 255, 255, 0.1)' 
                    : 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                  border: 'none',
                  borderRadius: 'var(--radius-md)',
                  color: totalPages <= 1 ? 'var(--text-tertiary)' : 'white',
                  fontSize: '14px',
                  fontWeight: '600',
                  cursor: totalPages <= 1 ? 'not-allowed' : 'pointer',
                  transition: 'var(--transition-smooth)',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                  opacity: totalPages <= 1 ? 0.5 : 1
                }}
                onMouseEnter={(e) => {
                  if (totalPages > 1) {
                    e.currentTarget.style.transform = 'scale(1.05)';
                  }
                }}
                onMouseLeave={(e) => {
                  if (totalPages > 1) {
                    e.currentTarget.style.transform = 'scale(1)';
                  }
                }}
              >
                Siguiente →
              </button>
            </div>
          </div>

          {/* Carousel Container */}
          <div style={{
            position: 'relative',
            overflow: 'hidden',
            borderRadius: 'var(--radius-lg)',
            padding: '20px',
            background: 'rgba(255, 255, 255, 0.02)',
            border: '1px solid var(--border-secondary)',
            backdropFilter: 'blur(10px)'
          }}>
            <div 
              className="carousel-grid"
              style={{
                display: 'grid',
                gridTemplateColumns: itemsPerPage === 1 ? '1fr' : 
                                     itemsPerPage === 2 ? 'repeat(2, 1fr)' : 
                                     'repeat(auto-fit, minmax(350px, 1fr))',
                gap: '24px',
                transition: 'all 0.5s ease-in-out'
              }}>
              {currentItems.map((coin, index) => {
            const riskStyle = getRiskBadgeStyle(coin.risk_level);
            const priceStyle = getPriceChangeStyle(coin.price_change_24h);
            const globalIndex = currentPage * itemsPerPage + index;
            const isExpanded = expandedIndex === globalIndex;

            return (
              <div
                key={`${currentPage}-${index}`} // Key único para forzar re-render con animación
                className="card animate-fadeInUp carousel-item"
                style={{
                  padding: '32px',
                  position: 'relative',
                  overflow: 'hidden',
                  background: 'var(--bg-card)',
                  border: '1px solid var(--border-primary)',
                  borderRadius: 'var(--radius-lg)',
                  backdropFilter: 'blur(20px)',
                  transition: 'var(--transition-smooth)',
                  animationDelay: `${index * 0.1}s`
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.transform = 'translateY(-4px)';
                  e.currentTarget.style.boxShadow = '0 20px 40px rgba(0, 0, 0, 0.3)';
                  e.currentTarget.style.borderColor = 'rgba(100, 255, 218, 0.3)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.transform = 'translateY(0)';
                  e.currentTarget.style.boxShadow = '0 4px 12px rgba(0, 0, 0, 0.15)';
                  e.currentTarget.style.borderColor = 'var(--border-primary)';
                }}
              >
                {/* Background Pattern */}
                <div style={{
                  position: 'absolute',
                  top: 0,
                  right: 0,
                  width: '150px',
                  height: '150px',
                  background: `radial-gradient(circle, ${riskStyle.background.includes('gradient') ? 'rgba(102, 126, 234, 0.05)' : 'rgba(255, 255, 255, 0.02)'} 0%, transparent 70%)`,
                  borderRadius: '50%',
                  transform: 'translate(50px, -50px)'
                }} />

                {/* Header */}
                <div style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'flex-start',
                  marginBottom: '24px',
                  flexWrap: 'wrap',
                  gap: '16px'
                }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
                    {/* Coin Icon */}
                    <div style={{
                      width: '60px',
                      height: '60px',
                      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                      borderRadius: '16px',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      fontSize: '24px',
                      fontWeight: '900',
                      color: 'white',
                      boxShadow: '0 8px 24px rgba(102, 126, 234, 0.3)',
                      position: 'relative',
                      overflow: 'hidden'
                    }}>
                      {coin.symbol?.charAt(0) || '₿'}
                      <div style={{
                        position: 'absolute',
                        top: '-2px',
                        right: '-2px',
                        fontSize: '12px'
                      }}>
                        #{index + 1}
                      </div>
                    </div>

                    <div>
                      <h2 style={{
                        fontSize: '28px',
                        fontWeight: '800',
                        color: 'var(--text-primary)',
                        margin: 0,
                        lineHeight: '1.2'
                      }}>
                        {coin.name}
                      </h2>
                      <p style={{
                        fontSize: '16px',
                        color: 'var(--text-tertiary)',
                        margin: 0,
                        fontWeight: '600',
                        textTransform: 'uppercase',
                        letterSpacing: '1px'
                      }}>
                        {coin.symbol}
                      </p>
                    </div>
                  </div>

                  <div style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '12px'
                  }}>
                    {/* Risk Badge */}
                    <div
                      className="badge"
                      style={{
                        background: riskStyle.background,
                        color: riskStyle.color,
                        padding: '8px 16px',
                        borderRadius: '20px',
                        fontSize: '12px',
                        fontWeight: '700',
                        textTransform: 'uppercase',
                        letterSpacing: '0.5px',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '6px',
                        boxShadow: '0 4px 12px rgba(0, 0, 0, 0.2)'
                      }}
                    >
                      <span>{riskStyle.icon}</span>
                      {coin.risk_level}
                    </div>

                    {/* Expand Button */}
                    <button
                      onClick={() => toggleExpand(index)}
                      style={{
                        padding: '12px 20px',
                        background: isExpanded 
                          ? 'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)' 
                          : 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                        border: 'none',
                        borderRadius: 'var(--radius-md)',
                        color: 'white',
                        fontSize: '14px',
                        fontWeight: '600',
                        cursor: 'pointer',
                        transition: 'var(--transition-smooth)',
                        textTransform: 'uppercase',
                        letterSpacing: '0.5px',
                        boxShadow: '0 4px 12px rgba(0, 0, 0, 0.2)'
                      }}
                      onMouseEnter={(e) => {
                        e.currentTarget.style.transform = 'scale(1.05)';
                      }}
                      onMouseLeave={(e) => {
                        e.currentTarget.style.transform = 'scale(1)';
                      }}
                    >
                      {isExpanded ? 'Ocultar' : 'Ver más'}
                    </button>
                  </div>
                </div>

                {/* Main Metrics */}
                <div className="grid grid-auto" style={{ marginBottom: '24px' }}>
                  <div style={{
                    padding: '20px',
                    background: 'rgba(139, 92, 246, 0.1)',
                    border: '1px solid rgba(139, 92, 246, 0.2)',
                    borderRadius: 'var(--radius-md)',
                    textAlign: 'center'
                  }}>
                    <p style={{ 
                      fontSize: '14px', 
                      color: 'var(--text-tertiary)', 
                      margin: '0 0 8px 0',
                      fontWeight: '600',
                      textTransform: 'uppercase',
                      letterSpacing: '0.5px'
                    }}>
                      Precio Actual
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
                    padding: '20px',
                    background: 'rgba(16, 185, 129, 0.1)',
                    border: '1px solid rgba(16, 185, 129, 0.2)',
                    borderRadius: 'var(--radius-md)',
                    textAlign: 'center'
                  }}>
                    <p style={{ 
                      fontSize: '14px', 
                      color: 'var(--text-tertiary)', 
                      margin: '0 0 8px 0',
                      fontWeight: '600',
                      textTransform: 'uppercase',
                      letterSpacing: '0.5px'
                    }}>
                      Cap. Mercado
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

                  <div style={{
                    padding: '20px',
                    background: priceStyle.background,
                    border: `1px solid ${priceStyle.color}40`,
                    borderRadius: 'var(--radius-md)',
                    textAlign: 'center'
                  }}>
                    <p style={{ 
                      fontSize: '14px', 
                      color: 'var(--text-tertiary)', 
                      margin: '0 0 8px 0',
                      fontWeight: '600',
                      textTransform: 'uppercase',
                      letterSpacing: '0.5px'
                    }}>
                      Cambio 24h
                    </p>
                    <div style={{
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      gap: '8px'
                    }}>
                      <span style={{ fontSize: '20px' }}>{priceStyle.icon}</span>
                      <p style={{ 
                        fontSize: '24px', 
                        fontWeight: '800', 
                        color: priceStyle.color, 
                        margin: 0 
                      }}>
                        {coin.price_change_24h?.toFixed(2) || '0'}%
                      </p>
                    </div>
                  </div>
                </div>

                {/* Extended Metrics */}
                {isExpanded && (
                  <div 
                    className="animate-fadeInUp"
                    style={{
                      padding: '24px',
                      background: 'rgba(255, 255, 255, 0.02)',
                      border: '1px solid var(--border-secondary)',
                      borderRadius: 'var(--radius-md)',
                      marginTop: '24px'
                    }}
                  >
                    <h3 style={{
                      fontSize: '20px',
                      fontWeight: '700',
                      color: 'var(--text-primary)',
                      marginBottom: '24px',
                      textAlign: 'center'
                    }}>
                      📊 Análisis Detallado
                    </h3>

                    <div className="grid grid-2" style={{ gap: '20px' }}>
                      <div style={{
                        padding: '16px',
                        background: 'rgba(59, 130, 246, 0.1)',
                        border: '1px solid rgba(59, 130, 246, 0.2)',
                        borderRadius: 'var(--radius-sm)',
                      }}>
                        <p style={{ fontSize: '14px', color: 'var(--text-tertiary)', margin: '0 0 4px 0' }}>
                          <strong>🎯 Retorno Esperado:</strong>
                        </p>
                        <p style={{ fontSize: '18px', fontWeight: '700', color: '#3b82f6', margin: 0 }}>
                          {coin.expected_return}%
                        </p>
                      </div>

                      <div style={{
                        padding: '16px',
                        background: 'rgba(239, 68, 68, 0.1)',
                        border: '1px solid rgba(239, 68, 68, 0.2)',
                        borderRadius: 'var(--radius-sm)',
                      }}>
                        <p style={{ fontSize: '14px', color: 'var(--text-tertiary)', margin: '0 0 4px 0' }}>
                          <strong>📊 Volatilidad:</strong>
                        </p>
                        <p style={{ fontSize: '18px', fontWeight: '700', color: '#ef4444', margin: 0 }}>
                          {coin.volatility}%
                        </p>
                      </div>

                      <div style={{
                        padding: '16px',
                        background: 'rgba(16, 185, 129, 0.1)',
                        border: '1px solid rgba(16, 185, 129, 0.2)',
                        borderRadius: 'var(--radius-sm)',
                      }}>
                        <p style={{ fontSize: '14px', color: 'var(--text-tertiary)', margin: '0 0 4px 0' }}>
                          <strong>⭐ Score Inversión:</strong>
                        </p>
                        <p style={{ fontSize: '18px', fontWeight: '700', color: '#10b981', margin: 0 }}>
                          {coin.investment_score}/10
                        </p>
                      </div>

                      <div style={{
                        padding: '16px',
                        background: 'rgba(245, 158, 11, 0.1)',
                        border: '1px solid rgba(245, 158, 11, 0.2)',
                        borderRadius: 'var(--radius-sm)',
                      }}>
                        <p style={{ fontSize: '14px', color: 'var(--text-tertiary)', margin: '0 0 4px 0' }}>
                          <strong>⚠️ Score Riesgo:</strong>
                        </p>
                        <p style={{ fontSize: '18px', fontWeight: '700', color: '#f59e0b', margin: 0 }}>
                          {coin.risk_score}/10
                        </p>
                      </div>

                      <div style={{
                        padding: '16px',
                        background: 'rgba(139, 92, 246, 0.1)',
                        border: '1px solid rgba(139, 92, 246, 0.2)',
                        borderRadius: 'var(--radius-sm)',
                      }}>
                        <p style={{ fontSize: '14px', color: 'var(--text-tertiary)', margin: '0 0 4px 0' }}>
                          <strong>💧 Liquidez:</strong>
                        </p>
                        <p style={{ fontSize: '18px', fontWeight: '700', color: '#8b5cf6', margin: 0 }}>
                          {coin.liquidity_ratio}
                        </p>
                      </div>

                      <div style={{
                        padding: '16px',
                        background: 'rgba(236, 72, 153, 0.1)',
                        border: '1px solid rgba(236, 72, 153, 0.2)',
                        borderRadius: 'var(--radius-sm)',
                      }}>
                        <p style={{ fontSize: '14px', color: 'var(--text-tertiary)', margin: '0 0 4px 0' }}>
                          <strong>🎭 Sentimiento:</strong>
                        </p>
                        <p style={{ fontSize: '18px', fontWeight: '700', color: '#ec4899', margin: 0 }}>
                          {coin.market_sentiment}
                        </p>
                      </div>
                    </div>

                    <div style={{
                      marginTop: '20px',
                      padding: '20px',
                      background: 'linear-gradient(135deg, rgba(100, 255, 218, 0.1) 0%, rgba(100, 255, 218, 0.05) 100%)',
                      border: '1px solid rgba(100, 255, 218, 0.2)',
                      borderRadius: 'var(--radius-md)',
                      textAlign: 'center'
                    }}>
                      <p style={{ fontSize: '14px', color: 'var(--text-tertiary)', margin: '0 0 8px 0' }}>
                        <strong>🛡️ Estabilidad General:</strong>
                      </p>
                      <p style={{ fontSize: '24px', fontWeight: '900', color: 'var(--text-accent)', margin: 0 }}>
                        {coin.stability_score}/10
                      </p>
                    </div>
                  </div>
                )}
              </div>
                );
              })}
            </div>
          </div>
        </div>

        {/* Empty State */}
        {sortedMetrics.length === 0 && (
          <div style={{
            textAlign: 'center',
            padding: '80px 20px',
            color: 'var(--text-tertiary)'
          }}>
            <div style={{ 
              fontSize: '64px', 
              marginBottom: '24px',
              opacity: '0.5'
            }}>
              📊
            </div>
            <h3 style={{ 
              fontSize: '24px', 
              marginBottom: '12px',
              color: 'var(--text-secondary)'
            }}>
              No hay datos disponibles
            </h3>
            <p>Intenta ajustar los filtros o recargar la página</p>
          </div>
        )}
      </div>

      <style jsx>{`
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
        
        @keyframes slideIn {
          from {
            opacity: 0;
            transform: translateY(20px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
        
        .carousel-item {
          animation: slideIn 0.5s ease-out;
        }
        
        @media (max-width: 768px) {
          .carousel-grid {
            grid-template-columns: 1fr !important;
          }
        }
      `}</style>
    </div>
  );
}
