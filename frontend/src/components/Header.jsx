import React, { useState, useEffect } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import apiClient from "../http-common";

export function Header({ user, onLogout }) {
  const location = useLocation();
  const navigate = useNavigate();
  const [isScrolled, setIsScrolled] = useState(false);
  const [showUserMenu, setShowUserMenu] = useState(false);
  const [currentBalance, setCurrentBalance] = useState(Number(user?.wallet_balance) || 0);
  const [balanceLoading, setBalanceLoading] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 20);
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  // Función para obtener el balance actualizado
  const fetchUserBalance = async () => {
    if (!user?.user_id) return;
    
    setBalanceLoading(true);
    try {
      const response = await apiClient.get(`/api/wallet/balance/${user.user_id}`);
      
      // Intentar diferentes campos posibles
      const updatedBalance = response.data.balance || 
                           response.data.wallet_balance || 
                           response.data.new_balance || 
                           0;
      
      setCurrentBalance(updatedBalance);
    } catch (err) {
      console.error("Error al obtener balance en Header:", err);
      // En caso de error, mantener el balance actual del usuario
      if (user?.wallet_balance !== undefined) {
        setCurrentBalance(user.wallet_balance);
      }
    } finally {
      setBalanceLoading(false);
    }
  };

  // Sincronizar balance inicial cuando cambie el usuario
  useEffect(() => {
    if (user?.wallet_balance !== undefined) {
      const balance = Number(user.wallet_balance) || 0;
      setCurrentBalance(balance);
    }
  }, [user?.wallet_balance]);

  // Obtener balance actualizado periódicamente y cuando el usuario cambie
  useEffect(() => {
    if (user?.user_id) {
      // Obtener balance inmediatamente
      fetchUserBalance();
      
      // Configurar intervalo para actualizar cada 500ms (súper rápido)
      const interval = setInterval(fetchUserBalance, 500);
      
      return () => clearInterval(interval);
    }
  }, [user?.user_id]);

  // Escuchar eventos de actualización del balance desde otras partes de la app
  useEffect(() => {
    const handleBalanceUpdate = (event) => {
      if (event.detail && event.detail.userId === user?.user_id) {
        setCurrentBalance(event.detail.balance);
      }
    };

    window.addEventListener('balanceUpdated', handleBalanceUpdate);
    return () => window.removeEventListener('balanceUpdated', handleBalanceUpdate);
  }, [user?.user_id]);

  const isActive = (path) => location.pathname === path;

  const navItems = [
    { path: "/", label: "Inicio", icon: "🏠" },
    { path: "/dashboard", label: "Dashboard", icon: "📊", requireAuth: true },
    { path: "/portfolio", label: "Portafolio", icon: "💼", requireAuth: true },
  ];

  const handleLogout = () => {
    onLogout();
    setShowUserMenu(false);
    navigate('/');
  };

  const formatBalance = (balance) => {
    // Asegurar que balance sea un número válido
    const numBalance = Number(balance) || 0;
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2
    }).format(numBalance);
  };

  return (
    <header 
      className={`header ${isScrolled ? 'header-scrolled' : ''}`}
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        zIndex: 1000,
        background: isScrolled 
          ? 'rgba(15, 15, 35, 0.95)' 
          : 'rgba(15, 15, 35, 0.8)',
        backdropFilter: 'blur(20px)',
        borderBottom: `1px solid ${isScrolled ? 'rgba(255, 255, 255, 0.1)' : 'transparent'}`,
        transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
        boxShadow: isScrolled 
          ? '0 8px 32px rgba(0, 0, 0, 0.3)' 
          : '0 4px 16px rgba(0, 0, 0, 0.1)',
      }}
    >
      <div className="container">
        <div 
          style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            padding: '16px 0',
            minHeight: '70px',
          }}
        >
          {/* Logo */}
          <Link 
            to="/" 
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '12px',
              textDecoration: 'none',
              transition: 'all 0.3s ease',
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.transform = 'scale(1.05)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.transform = 'scale(1)';
            }}
          >
            <div
              style={{
                width: '40px',
                height: '40px',
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                borderRadius: '12px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '20px',
                boxShadow: '0 4px 16px rgba(102, 126, 234, 0.3)',
              }}
            >
              ₿
            </div>
            <div>
              <h1 
                style={{ 
                  fontSize: '24px', 
                  fontWeight: '800', 
                  background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                  WebkitBackgroundClip: 'text',
                  WebkitTextFillColor: 'transparent',
                  backgroundClip: 'text',
                  margin: 0,
                  letterSpacing: '-0.5px',
                }}
                className="crypto-glow"
              >
                CriptoAI
              </h1>
              <span 
                style={{ 
                  fontSize: '11px', 
                  color: 'var(--text-tertiary)',
                  fontWeight: '500',
                  textTransform: 'uppercase',
                  letterSpacing: '1px',
                }}
              >
                Smart Trading
              </span>
            </div>
          </Link>

          {/* Navigation */}
          <nav style={{ display: 'flex', gap: '8px' }}>
            {navItems
              .filter(item => !item.requireAuth || user)
              .map((item) => (
              <Link
                key={item.path}
                to={item.path}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                  padding: '12px 20px',
                  borderRadius: '12px',
                  fontSize: '14px',
                  fontWeight: '600',
                  textDecoration: 'none',
                  position: 'relative',
                  overflow: 'hidden',
                  transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                  background: isActive(item.path) 
                    ? 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' 
                    : 'transparent',
                  color: isActive(item.path) 
                    ? 'white' 
                    : 'var(--text-secondary)',
                  border: isActive(item.path) 
                    ? 'none' 
                    : '1px solid transparent',
                  boxShadow: isActive(item.path) 
                    ? '0 4px 16px rgba(102, 126, 234, 0.3)' 
                    : 'none',
                }}
                onMouseEnter={(e) => {
                  if (!isActive(item.path)) {
                    e.currentTarget.style.background = 'rgba(255, 255, 255, 0.05)';
                    e.currentTarget.style.borderColor = 'rgba(255, 255, 255, 0.1)';
                    e.currentTarget.style.color = 'var(--text-primary)';
                    e.currentTarget.style.transform = 'translateY(-2px)';
                  }
                }}
                onMouseLeave={(e) => {
                  if (!isActive(item.path)) {
                    e.currentTarget.style.background = 'transparent';
                    e.currentTarget.style.borderColor = 'transparent';
                    e.currentTarget.style.color = 'var(--text-secondary)';
                    e.currentTarget.style.transform = 'translateY(0)';
                  }
                }}
              >
                <span style={{ fontSize: '16px' }}>{item.icon}</span>
                {item.label}
                {isActive(item.path) && (
                  <div
                    style={{
                      position: 'absolute',
                      bottom: '-1px',
                      left: '50%',
                      transform: 'translateX(-50%)',
                      width: '4px',
                      height: '4px',
                      background: 'white',
                      borderRadius: '50%',
                      boxShadow: '0 0 8px rgba(255, 255, 255, 0.8)',
                    }}
                  />
                )}
              </Link>
            ))}
          </nav>

          {/* Right side - User info or Auth buttons */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
            {/* Live Market Indicator */}
            <div 
              style={{
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
              }}
            >
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
              LIVE
            </div>

            {/* User Menu or Auth Buttons */}
            {user ? (
              <div style={{ position: 'relative' }}>
                <button
                  onClick={() => setShowUserMenu(!showUserMenu)}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '12px',
                    padding: '12px 16px',
                    background: 'var(--bg-card)',
                    border: '1px solid var(--border-primary)',
                    borderRadius: '12px',
                    color: 'var(--text-primary)',
                    cursor: 'pointer',
                    transition: 'var(--transition-smooth)',
                    backdropFilter: 'blur(10px)'
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.background = 'var(--bg-card-hover)';
                    e.currentTarget.style.borderColor = 'var(--text-accent)';
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.background = 'var(--bg-card)';
                    e.currentTarget.style.borderColor = 'var(--border-primary)';
                  }}
                >
                  <div style={{
                    width: '32px',
                    height: '32px',
                    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                    borderRadius: '50%',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    color: 'white',
                    fontSize: '14px',
                    fontWeight: '600'
                  }}>
                    {user.nombre ? user.nombre.charAt(0).toUpperCase() : '👤'}
                  </div>
                  <div style={{ textAlign: 'left' }}>
                    <div style={{ fontSize: '14px', fontWeight: '600', color: 'var(--text-primary)' }}>
                      ¡Hola, {user.nombre}!
                    </div>
                    <div style={{ 
                      fontSize: '12px', 
                      color: 'var(--text-accent)',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '4px'
                    }}>
                      {formatBalance(currentBalance)}
                      {balanceLoading && (
                        <div style={{
                          width: '6px',
                          height: '6px',
                          border: '1px solid var(--text-accent)',
                          borderTop: '1px solid transparent',
                          borderRadius: '50%',
                          animation: 'spin 0.8s linear infinite',
                          opacity: 0.7
                        }} />
                      )}
                    </div>
                  </div>
                  <span style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>
                    {showUserMenu ? '▲' : '▼'}
                  </span>
                </button>

                {/* User Dropdown Menu */}
                {showUserMenu && (
                  <div style={{
                    position: 'absolute',
                    top: '100%',
                    right: 0,
                    marginTop: '8px',
                    width: '200px',
                    background: 'var(--bg-card)',
                    border: '1px solid var(--border-primary)',
                    borderRadius: '12px',
                    backdropFilter: 'blur(20px)',
                    boxShadow: 'var(--shadow-xl)',
                    overflow: 'hidden',
                    zIndex: 1000
                  }}>
                    <div style={{
                      padding: '16px',
                      borderBottom: '1px solid var(--border-primary)'
                    }}>
                      <div style={{ fontSize: '14px', fontWeight: '600', color: 'var(--text-primary)' }}>
                        {user.nombre}
                      </div>
                      <div style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>
                        ID: {user.user_id}
                      </div>
                    </div>
                    
                    <Link
                      to="/dashboard"
                      onClick={() => setShowUserMenu(false)}
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '8px',
                        padding: '12px 16px',
                        color: 'var(--text-secondary)',
                        textDecoration: 'none',
                        fontSize: '14px',
                        transition: 'var(--transition-smooth)'
                      }}
                      onMouseEnter={(e) => {
                        e.currentTarget.style.background = 'var(--bg-card-hover)';
                        e.currentTarget.style.color = 'var(--text-primary)';
                      }}
                      onMouseLeave={(e) => {
                        e.currentTarget.style.background = 'transparent';
                        e.currentTarget.style.color = 'var(--text-secondary)';
                      }}
                    >
                      📊 Dashboard
                    </Link>

                    <Link
                      to="/portfolio"
                      onClick={() => setShowUserMenu(false)}
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '8px',
                        padding: '12px 16px',
                        color: 'var(--text-secondary)',
                        textDecoration: 'none',
                        fontSize: '14px',
                        transition: 'var(--transition-smooth)'
                      }}
                      onMouseEnter={(e) => {
                        e.currentTarget.style.background = 'var(--bg-card-hover)';
                        e.currentTarget.style.color = 'var(--text-primary)';
                      }}
                      onMouseLeave={(e) => {
                        e.currentTarget.style.background = 'transparent';
                        e.currentTarget.style.color = 'var(--text-secondary)';
                      }}
                    >
                      💼 Mi Portafolio
                    </Link>

                    <div style={{ borderTop: '1px solid var(--border-primary)' }}>
                      <button
                        onClick={handleLogout}
                        style={{
                          width: '100%',
                          display: 'flex',
                          alignItems: 'center',
                          gap: '8px',
                          padding: '12px 16px',
                          background: 'transparent',
                          border: 'none',
                          color: '#ef4444',
                          fontSize: '14px',
                          cursor: 'pointer',
                          transition: 'var(--transition-smooth)'
                        }}
                        onMouseEnter={(e) => {
                          e.currentTarget.style.background = 'rgba(239, 68, 68, 0.1)';
                        }}
                        onMouseLeave={(e) => {
                          e.currentTarget.style.background = 'transparent';
                        }}
                      >
                        🚪 Cerrar Sesión
                      </button>
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div style={{ display: 'flex', gap: '8px' }}>
                <Link
                  to="/login"
                  className="btn btn-ghost"
                  style={{
                    padding: '10px 20px',
                    fontSize: '14px'
                  }}
                >
                  Iniciar Sesión
                </Link>
                <Link
                  to="/register"
                  className="btn btn-primary"
                  style={{
                    padding: '10px 20px',
                    fontSize: '14px'
                  }}
                >
                  Registrarse
                </Link>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Click outside to close menu */}
      {showUserMenu && (
        <div
          style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            zIndex: 999
          }}
          onClick={() => setShowUserMenu(false)}
        />
      )}
    </header>
  );
}

export default Header;
