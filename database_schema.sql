-- Own1Shop Database Schema für Supabase
-- Diese SQL-Befehle in Supabase SQL Editor ausführen

-- ========================================
-- PROFILES TABELLE (Shop-Betreiber & Kunden)
-- ========================================
CREATE TABLE IF NOT EXISTS profiles (
    id BIGINT PRIMARY KEY,  -- Telegram User ID
    username TEXT,
    is_pro BOOLEAN DEFAULT FALSE,
    shop_id TEXT UNIQUE,
    
    -- Zahlungsmethoden
    wallet_btc TEXT,
    wallet_ltc TEXT,
    wallet_eth TEXT,  -- Nur PRO
    wallet_sol TEXT,  -- Nur PRO
    paypal_email TEXT,  -- Nur PRO
    
    -- PRO Features
    custom_bot_token TEXT UNIQUE,
    expiry_date TIMESTAMPTZ,
    
    -- Migration
    migration_completed BOOLEAN DEFAULT FALSE,
    migration_date TIMESTAMPTZ,
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ========================================
-- PRODUCTS TABELLE
-- ========================================
CREATE TABLE IF NOT EXISTS products (
    id BIGSERIAL PRIMARY KEY,
    owner_id BIGINT NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    description TEXT,
    price DECIMAL(10, 2) NOT NULL,
    content TEXT,  -- Lagerbestand (eine Zeile pro Item)
    
    -- PRO Features
    category TEXT,  -- Nur PRO: Kategorie-Name
    image_url TEXT,  -- Nur PRO: Bild-URL (Telegram file_id oder externe URL)
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ========================================
-- ORDERS TABELLE
-- ========================================
CREATE TABLE IF NOT EXISTS orders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    buyer_id BIGINT NOT NULL,
    product_id BIGINT NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    seller_id BIGINT NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    status TEXT DEFAULT 'pending',  -- pending, completed, cancelled
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ========================================
-- KATEGORIEN TABELLE (Optional - für bessere Organisation)
-- ========================================
CREATE TABLE IF NOT EXISTS categories (
    id SERIAL PRIMARY KEY,
    owner_id BIGINT NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(owner_id, name)
);

-- ========================================
-- INDIZES für Performance
-- ========================================
CREATE INDEX IF NOT EXISTS idx_products_owner ON products(owner_id);
CREATE INDEX IF NOT EXISTS idx_orders_seller ON orders(seller_id);
CREATE INDEX IF NOT EXISTS idx_orders_buyer ON orders(buyer_id);
CREATE INDEX IF NOT EXISTS idx_profiles_shop_id ON profiles(shop_id);
CREATE INDEX IF NOT EXISTS idx_profiles_token ON profiles(custom_bot_token);

-- ========================================
-- RLS (Row Level Security) - Optional aber empfohlen
-- ========================================
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE products ENABLE ROW LEVEL SECURITY;
ALTER TABLE orders ENABLE ROW LEVEL SECURITY;

-- Policy: Jeder kann Profile lesen (für Shop-Ansicht)
CREATE POLICY "Profiles are viewable by everyone" ON profiles
    FOR SELECT USING (true);

-- Policy: Nur eigene Profile können aktualisiert werden
CREATE POLICY "Users can update own profile" ON profiles
    FOR UPDATE USING (auth.uid()::text = id::text);

-- Policy: Produkte sind für alle lesbar
CREATE POLICY "Products are viewable by everyone" ON products
    FOR SELECT USING (true);

-- Policy: Nur Besitzer können Produkte ändern/löschen
CREATE POLICY "Users can manage own products" ON products
    FOR ALL USING (auth.uid()::text = owner_id::text);

-- ========================================
-- TRIGGER für updated_at
-- ========================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_profiles_updated_at BEFORE UPDATE ON profiles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_products_updated_at BEFORE UPDATE ON products
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_orders_updated_at BEFORE UPDATE ON orders
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
