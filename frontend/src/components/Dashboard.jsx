import React from "react";
import { Card, CardContent } from "@/components/ui/card";
import { BarChart2, TrendingUp, Activity, PieChart } from "lucide-react";

export function Dashboard() {
  const monedas = [
    { nombre: "Bitcoin", rentabilidad: "+8.5%", riesgo: "Moderado" },
    { nombre: "Ethereum", rentabilidad: "+6.2%", riesgo: "Alto" },
    { nombre: "Solana", rentabilidad: "+12.1%", riesgo: "Alto" },
    { nombre: "Cardano", rentabilidad: "+3.4%", riesgo: "Bajo" },
  ];

  const metricas = [
    { nombre: "Sharpe Ratio", valor: "1.87", icon: <TrendingUp className="text-green-600 w-6 h-6" /> },
    { nombre: "Rentabilidad esperada", valor: "7.4%", icon: <BarChart2 className="text-blue-600 w-6 h-6" /> },
    { nombre: "Volatilidad", valor: "2.3%", icon: <Activity className="text-yellow-600 w-6 h-6" /> },
  ];

  return (
    <div className="min-h-screen p-6 bg-gray-50 text-center">
      <h1 className="text-3xl font-bold mb-6"> Tu Panel Diario</h1>

      <Card className="mb-6 shadow-md">
        <CardContent className="p-6">
          <h2 className="text-xl font-semibold mb-2">Recomendación de Hoy</h2>
          <p className="text-gray-600">Hoy te recomendamos distribuir tu portafolio en estas 4 monedas clave según tu perfil de riesgo.</p>
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-10">
        {monedas.map((m, i) => (
          <Card key={i} className="shadow-sm">
            <CardContent className="p-4 text-left">
              <h3 className="text-lg font-bold text-indigo-700">{m.nombre}</h3>
              <p className="text-sm text-gray-500">Rentabilidad: {m.rentabilidad}</p>
              <p className="text-sm text-gray-500">Riesgo: {m.riesgo}</p>
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="w-full max-w-2xl h-64 border-2 border-dashed border-gray-300 rounded-xl flex items-center justify-center text-gray-400 mb-10">
        <PieChart className="w-6 h-6 mr-2" />
        <span>Gráfico de portafolio próximamente</span>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        {metricas.map((m, i) => (
          <Card key={i} className="shadow-sm">
            <CardContent className="p-4 flex flex-col items-center">
              {m.icon}
              <h4 className="font-semibold mt-2">{m.nombre}</h4>
              <p className="text-gray-600 text-sm">{m.valor}</p>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}