#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from agents.portfolio_optimizer import PortfolioOptimizationAgent

def test_usdc_vs_usdt_scoring():
    """Test para comparar scores entre USDC y USDT"""
    
    optimizer = PortfolioOptimizationAgent()
    
    # Datos de ejemplo basados en tu resultado
    usdt_data = {
        "symbol": "USDT",
        "name": "Tether",
        "current_price": 1.001,
        "market_cap": 155294255396,
        "investment_score": 57.35,
        "risk_score": 0.01,
        "expected_return": 0.057,
        "volatility": 0.01,
        "stability_score": 99.98,
        "liquidity_ratio": 32.8174,
        "market_sentiment": "neutral",
        "risk_level": "low",
        "price_change_24h": 0.05147,
        "volume_24h": 50963582360
    }
    
    usdc_data = {
        "symbol": "USDC", 
        "name": "USDC",
        "current_price": 0.999745,
        "market_cap": 61075816989,
        "investment_score": 35.97,
        "risk_score": 0.0,
        "expected_return": -0.002,
        "volatility": 0.0,
        "stability_score": 100.0,
        "liquidity_ratio": 16.9647,
        "market_sentiment": "neutral",
        "risk_level": "low",
        "price_change_24h": -0.00177,
        "volume_24h": 10361334266
    }
    
    user_profile = {
        "risk_tolerance": "moderate",
        "investment_horizon": "long"
    }
    
    # Calcular scores
    usdt_score = optimizer._calculate_coin_score(
        usdt_data, 
        user_profile["risk_tolerance"], 
        user_profile["investment_horizon"]
    )
    
    usdc_score = optimizer._calculate_coin_score(
        usdc_data, 
        user_profile["risk_tolerance"], 
        user_profile["investment_horizon"]
    )
    
    print("=== COMPARACIÓN USDT vs USDC ===")
    print(f"\nUSDT:")
    print(f"  - Risk Score: {usdt_data['risk_score']}")
    print(f"  - Stability Score: {usdt_data['stability_score']}")
    print(f"  - Investment Score: {usdt_data['investment_score']}")
    print(f"  - Score Calculado: {usdt_score:.2f}")
    
    print(f"\nUSDC:")
    print(f"  - Risk Score: {usdc_data['risk_score']}")
    print(f"  - Stability Score: {usdc_data['stability_score']}")
    print(f"  - Investment Score: {usdc_data['investment_score']}")
    print(f"  - Score Calculado: {usdc_score:.2f}")
    
    print(f"\n=== RESULTADO ===")
    if usdc_score > usdt_score:
        print(f"✅ USDC tiene mayor score (+{usdc_score - usdt_score:.2f})")
    elif usdt_score > usdc_score:
        print(f"❌ USDT tiene mayor score (+{usdt_score - usdc_score:.2f})")
    else:
        print("🤝 Empate")
    
    # Calcular pesos
    coins = [usdt_data, usdc_data]
    weights = optimizer.calculate_portfolio_weights(coins, user_profile)
    
    print(f"\n=== PESOS CALCULADOS ===")
    print(f"USDT: {weights['USDT']*100:.2f}%")
    print(f"USDC: {weights['USDC']*100:.2f}%")

if __name__ == "__main__":
    test_usdc_vs_usdt_scoring()
