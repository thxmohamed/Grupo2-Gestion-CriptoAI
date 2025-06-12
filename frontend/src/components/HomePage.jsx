import React from "react";
import { Link } from "react-router-dom";
import { Card, CardContent } from "@/components/ui/card";
import { LayoutDashboard, TrendingUp, BarChart2 } from "lucide-react";
import { Button } from "@/components/ui/button";

export function HomePage() {
  return (
    <div className="min-h-screen bg-white p-6 text-center">
      <h1 className="text-4xl font-bold mb-4">Tu asesor cripto con IA</h1>
      <p className="text-gray-600 max-w-xl mx-auto mb-8">
        CryptoAdvisor analiza el mercado por ti, optimiza tu portafolio y te envía recomendaciones personalizadas por WhatsApp. Todo con inteligencia artificial, 24/7.
      </p>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-10">
        <Card className="shadow-lg">
          <CardContent className="p-6 flex flex-col items-center">
            <LayoutDashboard className="w-8 h-8 text-indigo-600 mb-2" />
            <h3 className="font-semibold text-lg">Análisis Automático</h3>
            <p className="text-sm text-gray-500">Recolectamos y procesamos datos del mercado en tiempo real.</p>
          </CardContent>
        </Card>

        <Card className="shadow-lg">
          <CardContent className="p-6 flex flex-col items-center">
            <TrendingUp className="w-8 h-8 text-indigo-600 mb-2" />
            <h3 className="font-semibold text-lg">Recomendaciones Personalizadas</h3>
            <p className="text-sm text-gray-500">Adaptadas a tu perfil de riesgo y objetivos financieros.</p>
          </CardContent>
        </Card>

        <Card className="shadow-lg">
          <CardContent className="p-6 flex flex-col items-center">
            <BarChart2 className="w-8 h-8 text-indigo-600 mb-2" />
            <h3 className="font-semibold text-lg">IA 24/7</h3>
            <p className="text-sm text-gray-500">Siempre activa para detectar oportunidades y alertarte.</p>
          </CardContent>
        </Card>
      </div>

      <div className="flex justify-center gap-4 mb-12">
        <Link to="/dashboard">
          <Button className="bg-indigo-600 text-white hover:bg-indigo-700">Ir al Dashboard</Button>
        </Link>
        <Link to="/historial">
          <Button variant="outline">Ver Historial</Button>
        </Link>
      </div>

      <div className="w-full max-w-2xl h-64 border-2 border-dashed border-gray-300 rounded-xl flex items-center justify-center text-gray-400">
        <span>Gráfica de rendimiento / Demo próximamente</span>
      </div>
    </div>
  );
}