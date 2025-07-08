import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import apiClient from '../http-common';

export default function Register() {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    user_id: '',
    email: '',
    password: '',
    nombre: '',
    apellido: '',
    telefono: '',
    risk_tolerance: 'moderate',
    investment_amount: 1000,
    investment_horizon: 'medium'
  });
  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

  const validateForm = () => {
    const newErrors = {};

    if (!formData.user_id.trim()) {
      newErrors.user_id = 'User ID es requerido';
    }

    if (!formData.email.trim()) {
      newErrors.email = 'Email es requerido';
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = 'Email no es válido';
    }

    if (!formData.password.trim()) {
      newErrors.password = 'Contraseña es requerida';
    } else if (formData.password.length < 6) {
      newErrors.password = 'La contraseña debe tener al menos 6 caracteres';
    }

    if (!formData.nombre.trim()) {
      newErrors.nombre = 'Nombre es requerido';
    }

    if (!formData.apellido.trim()) {
      newErrors.apellido = 'Apellido es requerido';
    }

    if (!formData.telefono.trim()) {
      newErrors.telefono = 'Teléfono es requerido';
    }

    if (formData.investment_amount < 100) {
      newErrors.investment_amount = 'El monto mínimo de inversión es $100';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: name === 'investment_amount' ? Number(value) : value
    }));

    // Clear error when user starts typing
    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: ''
      }));
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    setLoading(true);
    try {
      const response = await apiClient.post('/api/register', formData);
      console.log('Registro exitoso:', response.data);
      
      // Show success message or redirect
      alert('¡Registro exitoso! Ahora puedes iniciar sesión.');
      navigate('/login');
    } catch (error) {
      console.error('Error en registro:', error);
      if (error.response?.data?.detail) {
        setErrors({ submit: error.response.data.detail });
      } else {
        setErrors({ submit: 'Error en el registro. Intenta nuevamente.' });
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      minHeight: '100vh',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      background: 'var(--bg-primary)',
      padding: '20px'
    }}>
      {/* Background Effects */}
      <div style={{
        position: 'absolute',
        top: '10%',
        left: '15%',
        width: '300px',
        height: '300px',
        background: 'radial-gradient(circle, rgba(102, 126, 234, 0.1) 0%, transparent 70%)',
        borderRadius: '50%',
        filter: 'blur(60px)',
        animation: 'float 6s ease-in-out infinite'
      }} />
      
      <div style={{
        position: 'absolute',
        bottom: '10%',
        right: '15%',
        width: '200px',
        height: '200px',
        background: 'radial-gradient(circle, rgba(139, 92, 246, 0.1) 0%, transparent 70%)',
        borderRadius: '50%',
        filter: 'blur(40px)',
        animation: 'float 8s ease-in-out infinite reverse'
      }} />

      <div className="card" style={{
        width: '100%',
        maxWidth: '600px',
        padding: '40px',
        position: 'relative',
        zIndex: 2
      }}>
        <div style={{ textAlign: 'center', marginBottom: '32px' }}>
          <h1 style={{
            fontSize: '2.5rem',
            fontWeight: '900',
            marginBottom: '8px',
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            backgroundClip: 'text'
          }}>
            Únete a CriptoAI
          </h1>
          <p style={{
            color: 'var(--text-secondary)',
            fontSize: '1.1rem'
          }}>
            Crea tu cuenta y comienza a invertir con inteligencia artificial
          </p>
        </div>

        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          {/* User ID y Email */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
            <div>
              <label style={{
                display: 'block',
                marginBottom: '8px',
                color: 'var(--text-primary)',
                fontSize: '14px',
                fontWeight: '600'
              }}>
                User ID
              </label>
              <input
                type="text"
                name="user_id"
                value={formData.user_id}
                onChange={handleChange}
                placeholder="Ej: meow123"
                style={{
                  width: '100%',
                  padding: '12px 16px',
                  background: 'var(--bg-card)',
                  border: errors.user_id ? '2px solid #ef4444' : '1px solid var(--border-primary)',
                  borderRadius: 'var(--radius-md)',
                  color: 'var(--text-primary)',
                  fontSize: '14px',
                  transition: 'var(--transition-smooth)',
                  backdropFilter: 'blur(10px)'
                }}
                onFocus={(e) => e.target.style.borderColor = '#667eea'}
                onBlur={(e) => e.target.style.borderColor = errors.user_id ? '#ef4444' : 'var(--border-primary)'}
              />
              {errors.user_id && (
                <span style={{ color: '#ef4444', fontSize: '12px', marginTop: '4px', display: 'block' }}>
                  {errors.user_id}
                </span>
              )}
            </div>

            <div>
              <label style={{
                display: 'block',
                marginBottom: '8px',
                color: 'var(--text-primary)',
                fontSize: '14px',
                fontWeight: '600'
              }}>
                Email
              </label>
              <input
                type="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                placeholder="tu@email.com"
                style={{
                  width: '100%',
                  padding: '12px 16px',
                  background: 'var(--bg-card)',
                  border: errors.email ? '2px solid #ef4444' : '1px solid var(--border-primary)',
                  borderRadius: 'var(--radius-md)',
                  color: 'var(--text-primary)',
                  fontSize: '14px',
                  transition: 'var(--transition-smooth)',
                  backdropFilter: 'blur(10px)'
                }}
                onFocus={(e) => e.target.style.borderColor = '#667eea'}
                onBlur={(e) => e.target.style.borderColor = errors.email ? '#ef4444' : 'var(--border-primary)'}
              />
              {errors.email && (
                <span style={{ color: '#ef4444', fontSize: '12px', marginTop: '4px', display: 'block' }}>
                  {errors.email}
                </span>
              )}
            </div>
          </div>

          {/* Contraseña */}
          <div>
            <label style={{
              display: 'block',
              marginBottom: '8px',
              color: 'var(--text-primary)',
              fontSize: '14px',
              fontWeight: '600'
            }}>
              Contraseña
            </label>
            <div style={{ position: 'relative' }}>
              <input
                type={showPassword ? 'text' : 'password'}
                name="password"
                value={formData.password}
                onChange={handleChange}
                placeholder="Mínimo 6 caracteres"
                style={{
                  width: '100%',
                  padding: '12px 16px',
                  paddingRight: '50px',
                  background: 'var(--bg-card)',
                  border: errors.password ? '2px solid #ef4444' : '1px solid var(--border-primary)',
                  borderRadius: 'var(--radius-md)',
                  color: 'var(--text-primary)',
                  fontSize: '14px',
                  transition: 'var(--transition-smooth)',
                  backdropFilter: 'blur(10px)'
                }}
                onFocus={(e) => e.target.style.borderColor = '#667eea'}
                onBlur={(e) => e.target.style.borderColor = errors.password ? '#ef4444' : 'var(--border-primary)'}
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                style={{
                  position: 'absolute',
                  right: '12px',
                  top: '50%',
                  transform: 'translateY(-50%)',
                  background: 'none',
                  border: 'none',
                  color: 'var(--text-secondary)',
                  cursor: 'pointer',
                  fontSize: '16px'
                }}
              >
                {showPassword ? '👁️' : '👁️‍🗨️'}
              </button>
            </div>
            {errors.password && (
              <span style={{ color: '#ef4444', fontSize: '12px', marginTop: '4px', display: 'block' }}>
                {errors.password}
              </span>
            )}
          </div>

          {/* Nombre y Apellido */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
            <div>
              <label style={{
                display: 'block',
                marginBottom: '8px',
                color: 'var(--text-primary)',
                fontSize: '14px',
                fontWeight: '600'
              }}>
                Nombre
              </label>
              <input
                type="text"
                name="nombre"
                value={formData.nombre}
                onChange={handleChange}
                placeholder="Tu nombre"
                style={{
                  width: '100%',
                  padding: '12px 16px',
                  background: 'var(--bg-card)',
                  border: errors.nombre ? '2px solid #ef4444' : '1px solid var(--border-primary)',
                  borderRadius: 'var(--radius-md)',
                  color: 'var(--text-primary)',
                  fontSize: '14px',
                  transition: 'var(--transition-smooth)',
                  backdropFilter: 'blur(10px)'
                }}
                onFocus={(e) => e.target.style.borderColor = '#667eea'}
                onBlur={(e) => e.target.style.borderColor = errors.nombre ? '#ef4444' : 'var(--border-primary)'}
              />
              {errors.nombre && (
                <span style={{ color: '#ef4444', fontSize: '12px', marginTop: '4px', display: 'block' }}>
                  {errors.nombre}
                </span>
              )}
            </div>

            <div>
              <label style={{
                display: 'block',
                marginBottom: '8px',
                color: 'var(--text-primary)',
                fontSize: '14px',
                fontWeight: '600'
              }}>
                Apellido
              </label>
              <input
                type="text"
                name="apellido"
                value={formData.apellido}
                onChange={handleChange}
                placeholder="Tu apellido"
                style={{
                  width: '100%',
                  padding: '12px 16px',
                  background: 'var(--bg-card)',
                  border: errors.apellido ? '2px solid #ef4444' : '1px solid var(--border-primary)',
                  borderRadius: 'var(--radius-md)',
                  color: 'var(--text-primary)',
                  fontSize: '14px',
                  transition: 'var(--transition-smooth)',
                  backdropFilter: 'blur(10px)'
                }}
                onFocus={(e) => e.target.style.borderColor = '#667eea'}
                onBlur={(e) => e.target.style.borderColor = errors.apellido ? '#ef4444' : 'var(--border-primary)'}
              />
              {errors.apellido && (
                <span style={{ color: '#ef4444', fontSize: '12px', marginTop: '4px', display: 'block' }}>
                  {errors.apellido}
                </span>
              )}
            </div>
          </div>

          {/* Teléfono */}
          <div>
            <label style={{
              display: 'block',
              marginBottom: '8px',
              color: 'var(--text-primary)',
              fontSize: '14px',
              fontWeight: '600'
            }}>
              Teléfono
            </label>
            <input
              type="tel"
              name="telefono"
              value={formData.telefono}
              onChange={handleChange}
              placeholder="+1 234 567 890"
              style={{
                width: '100%',
                padding: '12px 16px',
                background: 'var(--bg-card)',
                border: errors.telefono ? '2px solid #ef4444' : '1px solid var(--border-primary)',
                borderRadius: 'var(--radius-md)',
                color: 'var(--text-primary)',
                fontSize: '14px',
                transition: 'var(--transition-smooth)',
                backdropFilter: 'blur(10px)'
              }}
              onFocus={(e) => e.target.style.borderColor = '#667eea'}
              onBlur={(e) => e.target.style.borderColor = errors.telefono ? '#ef4444' : 'var(--border-primary)'}
            />
            {errors.telefono && (
              <span style={{ color: '#ef4444', fontSize: '12px', marginTop: '4px', display: 'block' }}>
                {errors.telefono}
              </span>
            )}
          </div>

          {/* Tolerancia al Riesgo */}
          <div>
            <label style={{
              display: 'block',
              marginBottom: '8px',
              color: 'var(--text-primary)',
              fontSize: '14px',
              fontWeight: '600'
            }}>
              Tolerancia al Riesgo
            </label>
            <select
              name="risk_tolerance"
              value={formData.risk_tolerance}
              onChange={handleChange}
              style={{
                width: '100%',
                padding: '12px 16px',
                background: 'var(--bg-card)',
                border: '1px solid var(--border-primary)',
                borderRadius: 'var(--radius-md)',
                color: 'var(--text-primary)',
                fontSize: '14px',
                transition: 'var(--transition-smooth)',
                backdropFilter: 'blur(10px)',
                cursor: 'pointer'
              }}
              onFocus={(e) => e.target.style.borderColor = '#667eea'}
              onBlur={(e) => e.target.style.borderColor = 'var(--border-primary)'}
            >
              <option value="conservative">Conservador - Menor riesgo, menor retorno</option>
              <option value="moderate">Moderado - Riesgo equilibrado</option>
            </select>
          </div>

          {/* Monto de Inversión */}
          <div>
            <label style={{
              display: 'block',
              marginBottom: '8px',
              color: 'var(--text-primary)',
              fontSize: '14px',
              fontWeight: '600'
            }}>
              Horizonte de inversión (USD)
            </label>
            <input
              type="number"
              name="investment_amount"
              value={formData.investment_amount}
              onChange={handleChange}
              min="100"
              step="100"
              placeholder="1000"
              style={{
                width: '100%',
                padding: '12px 16px',
                background: 'var(--bg-card)',
                border: errors.investment_amount ? '2px solid #ef4444' : '1px solid var(--border-primary)',
                borderRadius: 'var(--radius-md)',
                color: 'var(--text-primary)',
                fontSize: '14px',
                transition: 'var(--transition-smooth)',
                backdropFilter: 'blur(10px)'
              }}
              onFocus={(e) => e.target.style.borderColor = '#667eea'}
              onBlur={(e) => e.target.style.borderColor = errors.investment_amount ? '#ef4444' : 'var(--border-primary)'}
            />
            {errors.investment_amount && (
              <span style={{ color: '#ef4444', fontSize: '12px', marginTop: '4px', display: 'block' }}>
                {errors.investment_amount}
              </span>
            )}
          </div>

          {/* Horizonte de Inversión */}
          <div>
            <label style={{
              display: 'block',
              marginBottom: '8px',
              color: 'var(--text-primary)',
              fontSize: '14px',
              fontWeight: '600'
            }}>
              Horizonte de Inversión
            </label>
            <select
              name="investment_horizon"
              value={formData.investment_horizon}
              onChange={handleChange}
              style={{
                width: '100%',
                padding: '12px 16px',
                background: 'var(--bg-card)',
                border: '1px solid var(--border-primary)',
                borderRadius: 'var(--radius-md)',
                color: 'var(--text-primary)',
                fontSize: '14px',
                transition: 'var(--transition-smooth)',
                backdropFilter: 'blur(10px)',
                cursor: 'pointer'
              }}
              onFocus={(e) => e.target.style.borderColor = '#667eea'}
              onBlur={(e) => e.target.style.borderColor = 'var(--border-primary)'}
            >
              <option value="short">Corto plazo (1-6 meses)</option>
              <option value="medium">Mediano plazo (6 meses - 2 años)</option>
              <option value="long">Largo plazo (2+ años)</option>
            </select>
          </div>

          {/* Error general */}
          {errors.submit && (
            <div style={{
              padding: '12px',
              background: 'rgba(239, 68, 68, 0.1)',
              border: '1px solid #ef4444',
              borderRadius: 'var(--radius-md)',
              color: '#ef4444',
              fontSize: '14px',
              textAlign: 'center'
            }}>
              {errors.submit}
            </div>
          )}

          {/* Botón de registro */}
          <button
            type="submit"
            disabled={loading}
            className="btn btn-primary"
            style={{
              width: '100%',
              padding: '16px',
              fontSize: '16px',
              fontWeight: '700',
              opacity: loading ? 0.7 : 1,
              cursor: loading ? 'not-allowed' : 'pointer'
            }}
          >
            {loading ? (
              <span style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px' }}>
                <div style={{
                  width: '16px',
                  height: '16px',
                  border: '2px solid transparent',
                  borderTop: '2px solid white',
                  borderRadius: '50%',
                  animation: 'spin 1s linear infinite'
                }} />
                Registrando...
              </span>
            ) : (
              '🚀 Crear Cuenta'
            )}
          </button>

          {/* Link a login */}
          <div style={{ textAlign: 'center', marginTop: '16px' }}>
            <p style={{ color: 'var(--text-secondary)', fontSize: '14px' }}>
              ¿Ya tienes cuenta?{' '}
              <Link
                to="/login"
                style={{
                  color: 'var(--text-accent)',
                  textDecoration: 'none',
                  fontWeight: '600'
                }}
                onMouseEnter={(e) => e.target.style.textDecoration = 'underline'}
                onMouseLeave={(e) => e.target.style.textDecoration = 'none'}
              >
                Iniciar Sesión
              </Link>
            </p>
          </div>
        </form>
      </div>

      {/* Animation styles */}
      <style jsx>{`
        @keyframes float {
          0%, 100% {
            transform: translateY(0px);
          }
          50% {
            transform: translateY(-20px);
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

        @media (max-width: 768px) {
          .card {
            margin: 20px;
            padding: 24px !important;
          }
          
          .grid-2 {
            grid-template-columns: 1fr !important;
          }
        }
      `}</style>
    </div>
  );
}
