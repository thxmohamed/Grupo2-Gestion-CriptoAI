import React, { useState, useEffect } from "react";
import { Link, useLocation } from "react-router-dom";

export function Header() {
  const location = useLocation();
  const [isScrolled, setIsScrolled] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 20);
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const isActive = (path) => location.pathname === path;

  const navItems = [
    { path: "/", label: "Inicio", icon: "🏠" },
    { path: "/dashboard", label: "Dashboard", icon: "📊" },
    { path: "/admin", label: "Administración", icon: "⚙️" },
  ];

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
            {navItems.map((item) => (
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
        </div>
      </div>
    </header>
  );
}

export default Header;
