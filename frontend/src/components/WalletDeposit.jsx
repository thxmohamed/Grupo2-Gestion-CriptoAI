import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import apiClient from '../http-common';

export default function WalletDeposit({ user, onBalanceUpdate, onClose }) {
  const navigate = useNavigate();
  const [amount, setAmount] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const MAX_DEPOSIT = 10000;
  const currentBalance = user?.wallet_balance || 0;

  const validateAmount = (value) => {
    const numValue = parseFloat(value);
    
    if (isNaN(numValue) || numValue <= 0) {
      return 'El monto debe ser mayor a $0';
    }
    
    if (numValue > MAX_DEPOSIT) {
      return `El monto máximo permitido es $${MAX_DEPOSIT.toLocaleString()}`;
    }
    
    if (currentBalance + numValue > MAX_DEPOSIT) {
      const maxAllowed = MAX_DEPOSIT - currentBalance;
      return `Solo puedes depositar $${maxAllowed.toLocaleString()} más (límite de $${MAX_DEPOSIT.toLocaleString()})`;
    }
    
    return null;
  };

  const handleAmountChange = (e) => {
    const value = e.target.value;
    setAmount(value);
    setError('');
    setSuccess('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!user) {
      navigate('/login');
      return;
    }

    const validationError = validateAmount(amount);
    if (validationError) {
      setError(validationError);
      return;
    }

    setLoading(true);
    setError('');
    setSuccess('');

    try {
      const depositAmount = parseFloat(amount);
      const response = await apiClient.post(`/api/wallet/deposit/${user.user_id}`, {
        amount: depositAmount
      });

      setSuccess(`¡Depósito exitoso! Se han agregado $${depositAmount.toLocaleString()} a tu wallet.`);
      
      // Actualizar el balance del usuario
      const newBalance = currentBalance + depositAmount;
      const updatedUser = {
        ...user,
        wallet_balance: newBalance
      };
      
      // Actualizar localStorage
      localStorage.setItem('userData', JSON.stringify(updatedUser));
      
      // Notificar al componente padre
      if (onBalanceUpdate) {
        onBalanceUpdate(updatedUser);
      }
      
      setAmount('');
      
      // Cerrar el modal después de 2 segundos
      setTimeout(() => {
        if (onClose) {
          onClose();
        }
      }, 2000);
      
    } catch (error) {
      console.error('Error en depósito:', error);
      if (error.response?.data?.detail) {
        setError(error.response.data.detail);
      } else {
        setError('Error al procesar el depósito. Intenta nuevamente.');
      }
    } finally {
      setLoading(false);
    }
  };

  const quickAmounts = [100, 500, 1000, 2500, 5000];
  const remainingLimit = MAX_DEPOSIT - currentBalance;

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2
    }).format(value);
  };

  return (
    <div style={{
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
      padding: '20px'
    }}>
      <div className="card" style={{
        width: '100%',
        maxWidth: '500px',
        padding: '40px',
        position: 'relative',
        background: 'var(--bg-card)',
        border: '1px solid var(--border-primary)',
        borderRadius: 'var(--radius-lg)',
        backdropFilter: 'blur(20px)',
        boxShadow: 'var(--shadow-xl)'
      }}>
        {/* Close Button */}
        <button
          onClick={onClose}
          style={{
            position: 'absolute',
            top: '16px',
            right: '16px',
            background: 'rgba(239, 68, 68, 0.1)',
            border: '1px solid rgba(239, 68, 68, 0.3)',
            borderRadius: '50%',
            width: '40px',
            height: '40px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            cursor: 'pointer',
            color: '#ef4444',
            fontSize: '18px',
            transition: 'var(--transition-smooth)'
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.background = 'rgba(239, 68, 68, 0.2)';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.background = 'rgba(239, 68, 68, 0.1)';
          }}
        >
          ×
        </button>

        {/* Header */}
        <div style={{ textAlign: 'center', marginBottom: '32px' }}>
          <div style={{ fontSize: '4rem', marginBottom: '16px' }}>💰</div>
          <h2 style={{
            fontSize: '2rem',
            fontWeight: '700',
            color: 'var(--text-primary)',
            marginBottom: '8px'
          }}>
            Cargar Wallet
          </h2>
          <p style={{
            color: 'var(--text-secondary)',
            fontSize: '16px'
          }}>
            Agrega fondos a tu wallet de CriptoAI
          </p>
        </div>

        {/* Current Balance */}
        <div style={{
          padding: '20px',
          background: 'linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(139, 92, 246, 0.1) 100%)',
          border: '1px solid rgba(102, 126, 234, 0.2)',
          borderRadius: 'var(--radius-md)',
          marginBottom: '24px',
          textAlign: 'center'
        }}>
          <p style={{
            fontSize: '14px',
            color: 'var(--text-tertiary)',
            margin: '0 0 8px 0',
            textTransform: 'uppercase',
            letterSpacing: '0.5px'
          }}>
            Balance Actual
          </p>
          <p style={{
            fontSize: '28px',
            fontWeight: '900',
            color: 'var(--text-accent)',
            margin: 0
          }}>
            {formatCurrency(currentBalance)}
          </p>
          <p style={{
            fontSize: '12px',
            color: 'var(--text-secondary)',
            margin: '8px 0 0 0'
          }}>
            Límite disponible: {formatCurrency(remainingLimit)}
          </p>
        </div>

        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
          {/* Amount Input */}
          <div>
            <label style={{
              display: 'block',
              marginBottom: '8px',
              color: 'var(--text-primary)',
              fontSize: '14px',
              fontWeight: '600'
            }}>
              Monto a depositar
            </label>
            <div style={{ position: 'relative' }}>
              <span style={{
                position: 'absolute',
                left: '16px',
                top: '50%',
                transform: 'translateY(-50%)',
                color: 'var(--text-secondary)',
                fontSize: '18px',
                fontWeight: '600'
              }}>
                $
              </span>
              <input
                type="number"
                value={amount}
                onChange={handleAmountChange}
                placeholder="0.00"
                min="0.01"
                max={remainingLimit}
                step="0.01"
                style={{
                  width: '100%',
                  padding: '16px 16px 16px 40px',
                  background: 'var(--bg-card)',
                  border: error ? '2px solid #ef4444' : '1px solid var(--border-primary)',
                  borderRadius: 'var(--radius-md)',
                  color: 'var(--text-primary)',
                  fontSize: '18px',
                  fontWeight: '600',
                  transition: 'var(--transition-smooth)',
                  backdropFilter: 'blur(10px)'
                }}
                onFocus={(e) => e.target.style.borderColor = '#667eea'}
                onBlur={(e) => e.target.style.borderColor = error ? '#ef4444' : 'var(--border-primary)'}
              />
            </div>
          </div>

          {/* Quick Amount Buttons */}
          <div>
            <p style={{
              fontSize: '14px',
              color: 'var(--text-tertiary)',
              marginBottom: '12px',
              fontWeight: '600'
            }}>
              Montos rápidos:
            </p>
            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(80px, 1fr))',
              gap: '8px'
            }}>
              {quickAmounts
                .filter(quickAmount => quickAmount <= remainingLimit)
                .map((quickAmount) => (
                <button
                  key={quickAmount}
                  type="button"
                  onClick={() => setAmount(quickAmount.toString())}
                  style={{
                    padding: '12px 8px',
                    background: amount === quickAmount.toString() 
                      ? 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' 
                      : 'var(--bg-card)',
                    border: amount === quickAmount.toString() 
                      ? 'none' 
                      : '1px solid var(--border-primary)',
                    borderRadius: 'var(--radius-sm)',
                    color: amount === quickAmount.toString() 
                      ? 'white' 
                      : 'var(--text-secondary)',
                    fontSize: '14px',
                    fontWeight: '600',
                    cursor: 'pointer',
                    transition: 'var(--transition-smooth)'
                  }}
                  onMouseEnter={(e) => {
                    if (amount !== quickAmount.toString()) {
                      e.currentTarget.style.background = 'var(--bg-card-hover)';
                      e.currentTarget.style.color = 'var(--text-primary)';
                    }
                  }}
                  onMouseLeave={(e) => {
                    if (amount !== quickAmount.toString()) {
                      e.currentTarget.style.background = 'var(--bg-card)';
                      e.currentTarget.style.color = 'var(--text-secondary)';
                    }
                  }}
                >
                  ${quickAmount.toLocaleString()}
                </button>
              ))}
            </div>
          </div>

          {/* Error Message */}
          {error && (
            <div style={{
              padding: '16px',
              background: 'rgba(239, 68, 68, 0.1)',
              border: '1px solid #ef4444',
              borderRadius: 'var(--radius-md)',
              color: '#ef4444',
              fontSize: '14px',
              display: 'flex',
              alignItems: 'center',
              gap: '8px'
            }}>
              <span>⚠️</span>
              {error}
            </div>
          )}

          {/* Success Message */}
          {success && (
            <div style={{
              padding: '16px',
              background: 'rgba(16, 185, 129, 0.1)',
              border: '1px solid #10b981',
              borderRadius: 'var(--radius-md)',
              color: '#10b981',
              fontSize: '14px',
              display: 'flex',
              alignItems: 'center',
              gap: '8px'
            }}>
              <span>✅</span>
              {success}
            </div>
          )}

          {/* Submit Button */}
          <button
            type="submit"
            disabled={loading || !amount || parseFloat(amount) <= 0}
            className="btn btn-primary"
            style={{
              width: '100%',
              padding: '16px',
              fontSize: '16px',
              fontWeight: '700',
              opacity: (loading || !amount || parseFloat(amount) <= 0) ? 0.7 : 1,
              cursor: (loading || !amount || parseFloat(amount) <= 0) ? 'not-allowed' : 'pointer'
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
                Procesando...
              </span>
            ) : (
              '💰 Depositar Fondos'
            )}
          </button>

          {/* Info */}
          <div style={{
            padding: '16px',
            background: 'rgba(59, 130, 246, 0.1)',
            border: '1px solid rgba(59, 130, 246, 0.2)',
            borderRadius: 'var(--radius-md)',
            fontSize: '12px',
            color: 'var(--text-secondary)',
            textAlign: 'center'
          }}>
            <p style={{ margin: 0 }}>
              💡 <strong>Información:</strong> El depósito se procesará instantáneamente. 
              Límite máximo de wallet: {formatCurrency(MAX_DEPOSIT)}
            </p>
          </div>
        </form>
      </div>

      {/* Animation styles */}
      <style jsx>{`
        @keyframes spin {
          0% {
            transform: rotate(0deg);
          }
          100% {
            transform: rotate(360deg);
          }
        }
      `}</style>
    </div>
  );
}
