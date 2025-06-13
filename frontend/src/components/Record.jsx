import React from "react";

export function Record() {
  const historial = [
    { fecha: "2025-06-10", monedas: ["Bitcoin", "Solana"], riesgo: "Alto" },
    { fecha: "2025-06-09", monedas: ["Ethereum", "Cardano"], riesgo: "Moderado" },
    { fecha: "2025-06-08", monedas: ["Polkadot", "Litecoin"], riesgo: "Bajo" },
  ];

  const riesgoColor = {
    "Alto": "tag red",
    "Moderado": "tag yellow",
    "Bajo": "tag green",
  };

  return (
    <div className="record-page">
      <h1>Historial de Recomendaciones</h1>
      {historial.map((item, i) => (
        <div className="record-card" key={i}>
          <div className="record-header">
            <h3>{item.fecha}</h3>
            <span className={riesgoColor[item.riesgo]}>{item.riesgo}</span>
          </div>
          <p>Monedas recomendadas: {item.monedas.join(", ")}</p>
          <button className="view-btn">Ver detalles</button>
        </div>
      ))}
    </div>
  );
}

export default Record;