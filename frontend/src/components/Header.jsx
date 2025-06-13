import React from "react";
import { Link, useLocation } from "react-router-dom";
import { Home, LayoutDashboard, History } from "lucide-react";

export function Header() {
  const location = useLocation();

  const isActive = (path) => location.pathname === path;

  const linkBaseStyle = {
    display: "flex",
    alignItems: "center",
    gap: "6px",
    padding: "8px 16px",
    borderRadius: "6px",
    fontSize: "14px",
    fontWeight: 500,
    textDecoration: "none",
    transition: "background-color 0.2s ease, color 0.2s ease",
  };

  const activeStyle = {
    backgroundColor: "#4f46e5", // Indigo 600
    color: "white",
  };

  const inactiveStyle = {
    color: "#4b5563", // Gray 600
  };

  const hoverStyle = {
    backgroundColor: "#f3f4f6", // Gray 100
  };

  const mergeStyle = (path) => ({
    ...linkBaseStyle,
    ...(isActive(path) ? activeStyle : inactiveStyle),
    ...(isActive(path) ? {} : hoverStyle),
  });

  return (
    <header style={{
      width: "100%",
      backgroundColor: "#ffffff",
      boxShadow: "0 1px 4px rgba(0,0,0,0.05)",
      marginBottom: "24px",
    }}>
      <div style={{
        maxWidth: "1200px",
        margin: "0 auto",
        padding: "12px 16px",
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
      }}>
        <h1 style={{ fontSize: "20px", fontWeight: "bold", color: "#4338ca" }}>CryptoAdvisor</h1>
        <nav style={{ display: "flex", gap: "12px" }}>
          <Link to="/" style={mergeStyle("/")}>
            <Home size={16} /> Inicio
          </Link>
          <Link to="/dashboard" style={mergeStyle("/dashboard")}>
            <LayoutDashboard size={16} /> Top 20
          </Link>
        </nav>
      </div>
    </header>
  );
}

export default Header;
