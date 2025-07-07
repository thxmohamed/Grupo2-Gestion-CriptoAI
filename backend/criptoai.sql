-- Script SQL para crear la base de datos CriptoAI
-- Base de datos PostgreSQL para el sistema de análisis de criptomonedas

-- Crear la base de datos (ejecutar como superusuario)
CREATE DATABASE criptoai;
\c criptoai;

-- Tabla de criptomonedas
CREATE TABLE IF NOT EXISTS cryptocurrencies (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL UNIQUE,
    name_ VARCHAR(100) NOT NULL,
    current_price DECIMAL(20,8) NOT NULL,
    market_cap DECIMAL(20,2),
    volume_24h DECIMAL(20,2),
    price_change_24h DECIMAL(20,8),
    price_change_percentage_24h DECIMAL(10,4),
    circulating_supply DECIMAL(20,2),
    total_supply DECIMAL(20,2),
    ath DECIMAL(20,8),  -- All time high
    ath_change_percentage DECIMAL(10,4),
    atl DECIMAL(20,8),  -- All time low
    atl_change_percentage DECIMAL(10,4),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Índices para cryptocurrencies
CREATE INDEX IF NOT EXISTS idx_crypto_symbol ON cryptocurrencies(symbol);
CREATE INDEX IF NOT EXISTS idx_crypto_id ON cryptocurrencies(id);

-- Tabla de métricas de criptomonedas
CREATE TABLE IF NOT EXISTS crypto_metrics (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    current_price DECIMAL(20,10),
    market_cap BIGINT,
    price_change_24h DECIMAL(10,3),
    price_change_7d DECIMAL(10,3),
    price_change_30d DECIMAL(10,3),
    volume_24h BIGINT, -- Cambiado de volume_trend a volume_24h
    expected_return DECIMAL(10,3),
    volatility DECIMAL(10,2),
    rsi DECIMAL(10,2),
    ma_7 DECIMAL(20,8),
    ma_30 DECIMAL(20,8),
    investment_score DECIMAL(10,2),
    risk_score DECIMAL(10,2),
    risk_level VARCHAR(50), -- Ajustada longitud
    liquidity_ratio DECIMAL(10,4), -- Agregado
    market_sentiment VARCHAR(50), -- Ajustada longitud
    stability_score DECIMAL(10,2),
    growth_potential DECIMAL(10,2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE, -- La actualización automática se manejará en el ORM o con un trigger
    
    -- Restricción única para asegurar que no haya duplicados de métricas para el mismo símbolo y fuente
    CONSTRAINT unique_symbol UNIQUE (symbol)
);

-- Índices para crypto_metrics
CREATE INDEX IF NOT EXISTS idx_metrics_crypto_id ON crypto_metrics(id);
CREATE INDEX IF NOT EXISTS idx_metrics_symbol ON crypto_metrics(symbol);

-- Tabla de perfiles de usuario
CREATE TABLE IF NOT EXISTS user_profiles (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(100) UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    apellido VARCHAR(100) NOT NULL,
    telefono VARCHAR(20),
    risk_tolerance VARCHAR(20) NOT NULL DEFAULT 'moderate',
    investment_amount DECIMAL(15,2) NOT NULL DEFAULT 1000.0,
    investment_horizon VARCHAR(20) NOT NULL DEFAULT 'medium',
    preferred_sectors TEXT,  -- JSON string
    is_subscribed BOOLEAN DEFAULT FALSE,
    wallet_balance DECIMAL(15,2) DEFAULT 0.0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Índices para user_profiles
CREATE INDEX IF NOT EXISTS idx_user_profiles_user_id ON user_profiles(user_id);
CREATE INDEX IF NOT EXISTS idx_user_profiles_email ON user_profiles(email);

-- Tabla de recomendaciones de portafolio
CREATE TABLE IF NOT EXISTS portfolio_recommendations (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(100) NOT NULL,
    recommended_coins TEXT,  -- JSON string with top 5 coins
    allocation_percentages TEXT,  -- JSON string with allocation %
    expected_return DECIMAL(10,4),
    risk_score DECIMAL(5,2),
    confidence_level DECIMAL(5,2),
    reasoning TEXT,  -- Explicación de la recomendación
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Índices para portfolio_recommendations
CREATE INDEX IF NOT EXISTS idx_portfolio_user_id ON portfolio_recommendations(user_id);

-- Tabla de suscripciones
CREATE TABLE IF NOT EXISTS subscriptions (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(100) NOT NULL,
    email VARCHAR(255),
    phone VARCHAR(20),
    chat_id VARCHAR(50),
    notification_type VARCHAR(20),  -- email, sms, both
    frequency VARCHAR(20),  -- daily, weekly, monthly
    is_active BOOLEAN DEFAULT TRUE,
    telegram_pending BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Índices para subscriptions
CREATE INDEX IF NOT EXISTS idx_subscriptions_user_id ON subscriptions(user_id);

-- Tabla de precios históricos
CREATE TABLE IF NOT EXISTS historical_prices (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    source VARCHAR(20) NOT NULL,  -- 'binance', 'coingecko'
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    open DECIMAL(20,8),   -- Solo Binance
    high DECIMAL(20,8),   -- Solo Binance
    low DECIMAL(20,8),    -- Solo Binance
    close DECIMAL(20,8) NOT NULL, -- Binance (close) o CoinGecko (price)
    volume DECIMAL(20,2), -- Solo Binance
    market_cap DECIMAL(20,2), -- Solo CoinGecko
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Índices para historical_prices
CREATE INDEX IF NOT EXISTS idx_historical_symbol ON historical_prices(symbol);
CREATE INDEX IF NOT EXISTS idx_historical_timestamp ON historical_prices(timestamp);


CREATE OR REPLACE FUNCTION update_cryptocurrency_from_historical_prices()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO cryptocurrencies (
        symbol, 
        name_, 
        current_price, 
        market_cap, 
        volume_24h, 
        price_change_24h, 
        price_change_percentage_24h, 
        circulating_supply, 
        total_supply, 
        ath, 
        ath_change_percentage, 
        atl, 
        atl_change_percentage, 
        created_at, 
        updated_at
    )
    VALUES (
        NEW.symbol,
        NEW.symbol, -- O buscar el nombre real si existe en otra tabla
        NEW.close,
        NULL, -- No disponible directamente desde historical_prices
        (SELECT volume FROM historical_prices WHERE symbol = NEW.symbol AND source = 'binance' AND timestamp >= (NOW() - INTERVAL '24 hours') ORDER BY timestamp DESC LIMIT 1),
        -- Calcula price_change_24h y price_change_percentage_24h de forma similar a la función
        NULL, NULL, NULL, NULL,
        (SELECT MAX(close) FROM historical_prices WHERE symbol = NEW.symbol),
        NULL,
        (SELECT MIN(close) FROM historical_prices WHERE symbol = NEW.symbol),
        NULL,
        (SELECT MIN(created_at) FROM historical_prices WHERE symbol = NEW.symbol),
        NOW()
    )
    ON CONFLICT (symbol) DO UPDATE SET
        current_price = NEW.close,
        volume_24h = (SELECT volume FROM historical_prices WHERE symbol = NEW.symbol AND source = 'binance' AND timestamp >= (NOW() - INTERVAL '24 hours') ORDER BY timestamp DESC LIMIT 1),
        -- Actualiza price_change_24h, price_change_percentage_24h, ath, atl, etc.
        ath = GREATEST(cryptocurrencies.ath, NEW.close), -- Actualiza ATH si el nuevo precio es mayor
        atl = LEAST(cryptocurrencies.atl, NEW.close),   -- Actualiza ATL si el nuevo precio es menor
        updated_at = NOW();

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_update_cryptocurrency_prices
AFTER INSERT OR UPDATE ON historical_prices
FOR EACH ROW
EXECUTE FUNCTION update_cryptocurrency_from_historical_prices();

CREATE OR REPLACE FUNCTION get_unified_historical_crypto_data(symbol_e VARCHAR(10))
RETURNS TABLE (
    timestamp_ TIMESTAMP WITH TIME ZONE,
    coingecko_close DECIMAL(20,8),
    binance_close DECIMAL(20,8),
    binance_volume DECIMAL(20,2),
    coingecko_market_cap DECIMAL(20,2)
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    WITH coingecko_data AS (
        SELECT
            hp.symbol,
            hp.timestamp,
            hp.close AS cg_close,
            hp.market_cap -- Market_cap se guarda en historical_prices para CoinGecko
        FROM
            historical_prices hp
        WHERE
            hp.source = 'coingecko'
    ),
    binance_data AS (
        SELECT
            hp.symbol,
            hp.timestamp,
            hp.close AS bn_close,
            hp.volume AS bn_volume
        FROM
            historical_prices hp
        WHERE
            hp.source = 'binance'
    )
    SELECT
        cg.timestamp,
        cg.cg_close,
        bn.bn_close,
        bn.bn_volume,
        cg.market_cap
    FROM
        coingecko_data AS cg
    JOIN
        binance_data AS bn
        ON cg.timestamp = bn.timestamp AND cg.symbol = bn.symbol
    WHERE 
        cg.symbol = symbol_e
    ORDER BY
        cg.symbol, cg.timestamp;
END;
$$;
\q
