import React, { useEffect, useState } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";

export default function AdminUserDashboard() {
  const [users, setUsers] = useState([]);
  const navigate = useNavigate();

  useEffect(() => {
    axios.get("http://localhost:8000/api/user-profiles/")
      .then(response => setUsers(response.data))
      .catch(error => console.error("Error al obtener usuarios:", error));
  }, []);

  const handleUserClick = (userId) => {
    navigate(`/admin/user/${userId}`);
  };

  return (
    <div style={{ padding: "24px", fontFamily: "Arial, sans-serif" }}>
      <h1 style={{ fontSize: "24px", fontWeight: "bold", marginBottom: "24px" }}>
        Vista Administrador - Usuarios
      </h1>

      <div style={{ display: "flex", flexWrap: "wrap", gap: "16px" }}>
        {users.map(user => (
          <div
            key={user.id}
            onClick={() => handleUserClick(user.user_id)}
            style={{
              border: "1px solid #ccc",
              borderRadius: "8px",
              padding: "16px",
              width: "250px",
              cursor: "pointer",
              boxShadow: "0 2px 4px rgba(0,0,0,0.1)"
            }}
          >
            <h2 style={{ fontSize: "18px", fontWeight: "600" }}>
              {user.nombre} {user.apellido}
            </h2>
            <p style={{ fontSize: "14px", margin: "8px 0" }}>
              💰 Inversión: ${user.investment_amount}
            </p>
            <p style={{ fontSize: "14px" }}>
              {user.is_subscribed ? "✅ Suscrito" : "❌ No suscrito"}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}
