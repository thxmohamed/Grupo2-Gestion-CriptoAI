import React, { useEffect, useState } from "react";
import apiClient from "../http-common";
import { useNavigate } from "react-router-dom";

export default function AdminPage() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const [sortBy, setSortBy] = useState("name");
  const navigate = useNavigate();

  useEffect(() => {
    apiClient.get("/api/user-profiles/")
      .then(response => {
        setUsers(response.data);
        setLoading(false);
      })
      .catch(error => {
        console.error("Error al obtener usuarios:", error);
        setLoading(false);
      });
  }, []);

  const handleUserClick = (user) => {
    navigate(`/admin/user/${user.id}`, { 
      state: { nombre: user.nombre, apellido: user.apellido } 
    });
  };

  const filteredUsers = users.filter(user =>
    `${user.nombre} ${user.apellido}`.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const sortedUsers = [...filteredUsers].sort((a, b) => {
    switch(sortBy) {
      case "investment":
        return b.investment_amount - a.investment_amount;
      case "name":
        return `${a.nombre} ${a.apellido}`.localeCompare(`${b.nombre} ${b.apellido}`);
      case "subscription":
        return b.is_subscribed - a.is_subscribed;
      default:
        return 0;
    }
  });

  const totalInvestment = users.reduce((sum, user) => sum + (user.investment_amount || 0), 0);
  const subscribedUsers = users.filter(user => user.is_subscribed).length;

  if (loading) {
    return (
      <div style={{ 
        minHeight: '100vh', 
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: 'center',
        paddingTop: '80px'
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
            Cargando usuarios...
          </p>
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
        {/* Hero Section */}
        <div style={{
          textAlign: 'center',
          marginBottom: '60px',
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
            Panel de Administración
          </h1>
          <p style={{
            fontSize: '18px',
            color: 'var(--text-secondary)',
            maxWidth: '600px',
            margin: '0 auto 40px',
            lineHeight: '1.6'
          }}>
            Gestiona todos los usuarios de la plataforma CryptoAI. 
            Visualiza métricas, inversiones y estados de suscripción.
          </p>

          {/* Stats Cards */}
          <div className="grid grid-3" style={{ marginBottom: '40px' }}>
            <div className="card animate-fadeInUp" style={{
              padding: '30px',
              textAlign: 'center',
              background: 'linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(5, 150, 105, 0.05) 100%)',
              border: '1px solid rgba(16, 185, 129, 0.2)'
            }}>
              <div style={{
                fontSize: '48px',
                fontWeight: '900',
                background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                backgroundClip: 'text',
                marginBottom: '12px'
              }}>
                {users.length}
              </div>
              <h3 style={{ color: 'var(--text-primary)', marginBottom: '8px' }}>
                Total Usuarios
              </h3>
              <p style={{ color: 'var(--text-tertiary)', fontSize: '14px' }}>
                Usuarios registrados
              </p>
            </div>

            <div className="card animate-fadeInUp" style={{
              padding: '30px',
              textAlign: 'center',
              background: 'linear-gradient(135deg, rgba(59, 130, 246, 0.1) 0%, rgba(37, 99, 235, 0.05) 100%)',
              border: '1px solid rgba(59, 130, 246, 0.2)',
              animationDelay: '0.1s'
            }}>
              <div style={{
                fontSize: '48px',
                fontWeight: '900',
                background: 'linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                backgroundClip: 'text',
                marginBottom: '12px'
              }}>
                {subscribedUsers}
              </div>
              <h3 style={{ color: 'var(--text-primary)', marginBottom: '8px' }}>
                Suscriptores
              </h3>
              <p style={{ color: 'var(--text-tertiary)', fontSize: '14px' }}>
                Usuarios premium
              </p>
            </div>

            <div className="card animate-fadeInUp" style={{
              padding: '30px',
              textAlign: 'center',
              background: 'linear-gradient(135deg, rgba(139, 92, 246, 0.1) 0%, rgba(124, 58, 237, 0.05) 100%)',
              border: '1px solid rgba(139, 92, 246, 0.2)',
              animationDelay: '0.2s'
            }}>
              <div style={{
                fontSize: '32px',
                fontWeight: '900',
                background: 'linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                backgroundClip: 'text',
                marginBottom: '12px'
              }}>
                ${totalInvestment.toLocaleString()}
              </div>
              <h3 style={{ color: 'var(--text-primary)', marginBottom: '8px' }}>
                Inversión Total
              </h3>
              <p style={{ color: 'var(--text-tertiary)', fontSize: '14px' }}>
                Capital gestionado
              </p>
            </div>
          </div>
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
            flex: 1,
            minWidth: '300px'
          }}>
            <div style={{ position: 'relative', flex: 1, maxWidth: '400px' }}>
              <input
                type="text"
                placeholder="Buscar usuarios..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                style={{
                  width: '100%',
                  padding: '16px 20px 16px 50px',
                  background: 'var(--bg-card)',
                  border: '1px solid var(--border-primary)',
                  borderRadius: 'var(--radius-md)',
                  color: 'var(--text-primary)',
                  fontSize: '14px',
                  backdropFilter: 'blur(10px)',
                  transition: 'var(--transition-smooth)',
                  outline: 'none'
                }}
                onFocus={(e) => {
                  e.target.style.borderColor = 'var(--text-accent)';
                  e.target.style.boxShadow = '0 0 0 3px rgba(100, 255, 218, 0.1)';
                }}
                onBlur={(e) => {
                  e.target.style.borderColor = 'var(--border-primary)';
                  e.target.style.boxShadow = 'none';
                }}
              />
              <div style={{
                position: 'absolute',
                left: '18px',
                top: '50%',
                transform: 'translateY(-50%)',
                fontSize: '18px',
                color: 'var(--text-tertiary)'
              }}>
                🔍
              </div>
            </div>
          </div>

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
            <option value="name">Ordenar por nombre</option>
            <option value="investment">Ordenar por inversión</option>
            <option value="subscription">Ordenar por suscripción</option>
          </select>
        </div>

        {/* Users Grid */}
        <div className="grid grid-auto">
          {sortedUsers.map((user, index) => (
            <div
              key={user.id}
              className="card animate-fadeInUp"
              onClick={() => handleUserClick(user)}
              style={{
                padding: '32px',
                cursor: 'pointer',
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
                e.currentTarget.style.transform = 'translateY(-8px) scale(1.02)';
                e.currentTarget.style.boxShadow = '0 20px 40px rgba(0, 0, 0, 0.4)';
                e.currentTarget.style.borderColor = 'rgba(100, 255, 218, 0.3)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.transform = 'translateY(0) scale(1)';
                e.currentTarget.style.boxShadow = '0 4px 12px rgba(0, 0, 0, 0.15)';
                e.currentTarget.style.borderColor = 'var(--border-primary)';
              }}
            >
              {/* Background Pattern */}
              <div style={{
                position: 'absolute',
                top: 0,
                right: 0,
                width: '100px',
                height: '100px',
                background: 'linear-gradient(135deg, rgba(100, 255, 218, 0.1) 0%, transparent 70%)',
                borderRadius: '50%',
                transform: 'translate(30px, -30px)'
              }} />

              {/* User Avatar */}
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
                marginBottom: '24px',
                boxShadow: '0 8px 24px rgba(102, 126, 234, 0.3)',
                position: 'relative',
                overflow: 'hidden'
              }}>
                {user.nombre.charAt(0).toUpperCase()}
                {user.apellido.charAt(0).toUpperCase()}
                
                {/* Subscription Badge */}
                {user.is_subscribed && (
                  <div style={{
                    position: 'absolute',
                    top: '-4px',
                    right: '-4px',
                    width: '24px',
                    height: '24px',
                    background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
                    borderRadius: '50%',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontSize: '12px',
                    boxShadow: '0 4px 12px rgba(16, 185, 129, 0.4)'
                  }}>
                    ✓
                  </div>
                )}
              </div>

              {/* User Info */}
              <h2 style={{
                fontSize: '24px',
                fontWeight: '700',
                color: 'var(--text-primary)',
                marginBottom: '8px',
                lineHeight: '1.2'
              }}>
                {user.nombre} {user.apellido}
              </h2>

              <div style={{
                display: 'flex',
                flexDirection: 'column',
                gap: '16px',
                marginBottom: '24px'
              }}>
                <div style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '12px',
                  padding: '12px 16px',
                  background: 'rgba(139, 92, 246, 0.1)',
                  border: '1px solid rgba(139, 92, 246, 0.2)',
                  borderRadius: 'var(--radius-md)',
                }}>
                  <span style={{ fontSize: '20px' }}>💰</span>
                  <div>
                    <p style={{ 
                      fontSize: '14px', 
                      color: 'var(--text-tertiary)', 
                      margin: 0,
                      fontWeight: '500'
                    }}>
                      Inversión
                    </p>
                    <p style={{ 
                      fontSize: '18px', 
                      fontWeight: '700', 
                      color: 'var(--text-primary)', 
                      margin: 0 
                    }}>
                      ${user.investment_amount?.toLocaleString() || '0'}
                    </p>
                  </div>
                </div>

                <div style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '12px',
                  padding: '12px 16px',
                  background: user.is_subscribed 
                    ? 'rgba(16, 185, 129, 0.1)' 
                    : 'rgba(239, 68, 68, 0.1)',
                  border: user.is_subscribed 
                    ? '1px solid rgba(16, 185, 129, 0.2)' 
                    : '1px solid rgba(239, 68, 68, 0.2)',
                  borderRadius: 'var(--radius-md)',
                }}>
                  <span style={{ fontSize: '20px' }}>
                    {user.is_subscribed ? '👑' : '👤'}
                  </span>
                  <div>
                    <p style={{ 
                      fontSize: '14px', 
                      color: 'var(--text-tertiary)', 
                      margin: 0,
                      fontWeight: '500'
                    }}>
                      Estado
                    </p>
                    <p style={{ 
                      fontSize: '16px', 
                      fontWeight: '600', 
                      color: user.is_subscribed ? '#10b981' : '#ef4444', 
                      margin: 0 
                    }}>
                      {user.is_subscribed ? 'Premium' : 'Básico'}
                    </p>
                  </div>
                </div>
              </div>

              {/* Action Button */}
              <button
                style={{
                  width: '100%',
                  padding: '16px',
                  background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                  border: 'none',
                  borderRadius: 'var(--radius-md)',
                  color: 'white',
                  fontSize: '14px',
                  fontWeight: '600',
                  cursor: 'pointer',
                  transition: 'var(--transition-smooth)',
                  textTransform: 'uppercase',
                  letterSpacing: '0.5px',
                  position: 'relative',
                  overflow: 'hidden'
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.transform = 'scale(1.05)';
                  e.currentTarget.style.boxShadow = '0 8px 24px rgba(102, 126, 234, 0.4)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.transform = 'scale(1)';
                  e.currentTarget.style.boxShadow = 'none';
                }}
              >
                Ver Detalles
                <span style={{ marginLeft: '8px' }}>→</span>
              </button>
            </div>
          ))}
        </div>

        {/* Empty State */}
        {sortedUsers.length === 0 && (
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
              🔍
            </div>
            <h3 style={{ 
              fontSize: '24px', 
              marginBottom: '12px',
              color: 'var(--text-secondary)'
            }}>
              No se encontraron usuarios
            </h3>
            <p>Intenta ajustar los filtros de búsqueda</p>
          </div>
        )}
      </div>

      {/* Floating Action Button */}
      <div style={{
        position: 'fixed',
        bottom: '30px',
        right: '30px',
        zIndex: 100
      }}>
        <button
          style={{
            width: '60px',
            height: '60px',
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            border: 'none',
            borderRadius: '50%',
            color: 'white',
            fontSize: '24px',
            cursor: 'pointer',
            boxShadow: '0 8px 24px rgba(102, 126, 234, 0.4)',
            transition: 'var(--transition-smooth)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center'
          }}
          onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}
          onMouseEnter={(e) => {
            e.currentTarget.style.transform = 'scale(1.1)';
            e.currentTarget.style.boxShadow = '0 12px 32px rgba(102, 126, 234, 0.6)';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.transform = 'scale(1)';
            e.currentTarget.style.boxShadow = '0 8px 24px rgba(102, 126, 234, 0.4)';
          }}
        >
          ↑
        </button>
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
