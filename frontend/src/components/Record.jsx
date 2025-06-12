import React from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Eye } from "lucide-react";

export function Historial() {
  const historial = [
    { fecha: "2025-06-10", monedas: ["Bitcoin", "Solana"], riesgo: "Alto" },
    { fecha: "2025-06-09", monedas: ["Ethereum", "Cardano"], riesgo: "Moderado" },
    { fecha: "2025-06-08", monedas: ["Polkadot", "Litecoin"], riesgo: "Bajo" },
  ];

  const riesgoColor = {
    "Alto": "bg-red-100 text-red-600",
    "Moderado": "bg-yellow-100 text-yellow-600",
    "Bajo": "bg-green-100 text-green-600",
  };

  return (
    <div className="min-h-screen p-6 bg-white text-center">
      <h1 className="text-3xl font-bold mb-6">Historial de Recomendaciones</h1>

      <div className="space-y-4">
        {historial.map((item, index) => (
          <Card key={index} className="shadow-sm text-left">
            <CardContent className="p-4">
              <div className="flex justify-between items-center mb-2">
                <h3 className="text-lg font-semibold">{item.fecha}</h3>
                <span className={`text-xs px-2 py-1 rounded-full ${riesgoColor[item.riesgo]}`}>
                  {item.riesgo}
                </span>
              </div>
              <p className="text-gray-600 text-sm mb-3">
                Monedas recomendadas: {item.monedas.join(", ")}
              </p>
              <Button variant="outline" className="flex items-center gap-1">
                <Eye className="w-4 h-4" /> Ver detalles
              </Button>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}