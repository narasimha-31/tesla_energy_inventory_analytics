DROP TABLE IF EXISTS fact_daily_inventory;
DROP TABLE IF EXISTS dim_warehouse;
DROP TABLE IF EXISTS dim_product;
DROP TABLE IF EXISTS dim_date;
DROP TABLE IF EXISTS dim_quarterly_targets;

CREATE TABLE dim_warehouse (
    warehouse_id VARCHAR(10) PRIMARY KEY,
    warehouse_name VARCHAR(100) NOT NULL,
    state VARCHAR(50) NOT NULL,
    country VARCHAR(50) NOT NULL,
    primary_product VARCHAR(50) NOT NULL,
    capacity_gwh NUMERIC(10,2) NOT NULL,
    status VARCHAR(20) NOT NULL,
    opened_year INTEGER NOT NULL
);

CREATE TABLE dim_product (
    product_id VARCHAR(10) PRIMARY KEY,
    product_name VARCHAR(50) NOT NULL,
    product_type VARCHAR(20) NOT NULL,
    capacity_kwh NUMERIC(10,2) NOT NULL,
    unit_weight_tons NUMERIC(10,3) NOT NULL
);

CREATE TABLE dim_date (
    date_key VARCHAR(10) PRIMARY KEY,
    full_date DATE NOT NULL,
    year INTEGER NOT NULL,
    quarter VARCHAR(5) NOT NULL,
    quarter_label VARCHAR(10) NOT NULL,
    month INTEGER NOT NULL,
    month_name VARCHAR(15) NOT NULL,
    week_of_year INTEGER NOT NULL,
    day_of_week INTEGER NOT NULL,
    day_name VARCHAR(15) NOT NULL,
    is_weekend BOOLEAN NOT NULL,
    is_month_end BOOLEAN NOT NULL
);

CREATE TABLE dim_quarterly_targets (
    quarter_label VARCHAR(10) PRIMARY KEY,
    quarter VARCHAR(5) NOT NULL,
    year INTEGER NOT NULL,
    total_gwh NUMERIC(10,2) NOT NULL,
    megapack_gwh NUMERIC(10,2) NOT NULL,
    powerwall_gwh NUMERIC(10,2) NOT NULL,
    megapack_units INTEGER NOT NULL,
    powerwall_units INTEGER NOT NULL
);

CREATE TABLE fact_daily_inventory (
    id SERIAL PRIMARY KEY,
    date_key VARCHAR(10) NOT NULL REFERENCES dim_date(date_key),
    quarter_label VARCHAR(10) NOT NULL REFERENCES dim_quarterly_targets(quarter_label),
    warehouse_id VARCHAR(10) NOT NULL REFERENCES dim_warehouse(warehouse_id),
    product_id VARCHAR(10) NOT NULL REFERENCES dim_product(product_id),
    units_received INTEGER NOT NULL,
    units_produced INTEGER NOT NULL,
    units_shipped INTEGER NOT NULL,
    closing_stock INTEGER NOT NULL,
    reorder_flag BOOLEAN NOT NULL,
    capacity_utilization_pct NUMERIC(6,2) NOT NULL
);

CREATE INDEX idx_fact_date ON fact_daily_inventory(date_key);
CREATE INDEX idx_fact_warehouse ON fact_daily_inventory(warehouse_id);
CREATE INDEX idx_fact_product ON fact_daily_inventory(product_id);
CREATE INDEX idx_fact_quarter ON fact_daily_inventory(quarter_label);