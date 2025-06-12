import React from "react";
import { Link, useLocation } from "react-router-dom";
import { Home, LayoutDashboard, History } from "lucide-react";

export function Header() {
  const location = useLocation();

  const linkStyle = (path) =>
    `flex items-center gap-1 px-4 py-2 rounded-md text-sm font-medium transition ${
      location.pathname === path
        ? "bg-indigo-600 text-white"
        : "text-gray-600 hover:bg-gray-100"
    }`;

  return (
    <header className="w-full bg-white shadow-sm mb-6">
      <div className="max-w-7xl mx-auto px-4 py-3 flex justify-between items-center">
        <h1 className="text-xl font-bold text-indigo-700">CryptoAdvisor</h1>
        <nav className="flex gap-2">
          <Link to="/" className={linkStyle("/")}>
            <Home className="w-4 h-4" /> Inicio
          </Link>
          <Link to="/dashboard" className={linkStyle("/dashboard")}>
            <LayoutDashboard className="w-4 h-4" /> Dashboard
          </Link>
          <Link to="/historial" className={linkStyle("/historial")}>
            <History className="w-4 h-4" /> Historial
          </Link>
        </nav>
      </div>
    </header>
  );
}