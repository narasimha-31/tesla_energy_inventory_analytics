-- 1. Quarterly shipment performance vs targets
SELECT 
    qt.quarter_label,
    qt.total_gwh AS target_gwh,
    ROUND(SUM(f.units_shipped * p.capacity_kwh) / 1000000, 2) AS actual_gwh,
    ROUND((SUM(f.units_shipped * p.capacity_kwh) / 1000000) / qt.total_gwh * 100, 1) AS pct_achieved
FROM fact_daily_inventory f
JOIN dim_product p ON f.product_id = p.product_id
JOIN dim_quarterly_targets qt ON f.quarter_label = qt.quarter_label
GROUP BY qt.quarter_label, qt.total_gwh
ORDER BY qt.quarter_label;

-- 2. Monthly shipment trend by warehouse
SELECT 
    d.year,
    d.month,
    d.month_name,
    w.warehouse_name,
    SUM(f.units_shipped) AS total_shipped,
    ROUND(AVG(f.units_shipped), 1) AS avg_daily_shipped
FROM fact_daily_inventory f
JOIN dim_date d ON f.date_key = d.date_key
JOIN dim_warehouse w ON f.warehouse_id = w.warehouse_id
GROUP BY d.year, d.month, d.month_name, w.warehouse_name
ORDER BY d.year, d.month, w.warehouse_name;

-- 3. Warehouse capacity utilization summary
SELECT 
    w.warehouse_name,
    f.quarter_label,
    ROUND(AVG(f.capacity_utilization_pct), 2) AS avg_utilization,
    ROUND(MAX(f.capacity_utilization_pct), 2) AS peak_utilization,
    ROUND(MIN(f.capacity_utilization_pct), 2) AS min_utilization
FROM fact_daily_inventory f
JOIN dim_warehouse w ON f.warehouse_id = w.warehouse_id
GROUP BY w.warehouse_name, f.quarter_label
ORDER BY w.warehouse_name, f.quarter_label;

-- 4. Reorder flag frequency by warehouse and quarter
SELECT 
    w.warehouse_name,
    f.quarter_label,
    COUNT(*) AS total_days,
    SUM(CASE WHEN f.reorder_flag = true THEN 1 ELSE 0 END) AS reorder_days,
    ROUND(SUM(CASE WHEN f.reorder_flag = true THEN 1 ELSE 0 END)::NUMERIC / COUNT(*) * 100, 1) AS reorder_pct
FROM fact_daily_inventory f
JOIN dim_warehouse w ON f.warehouse_id = w.warehouse_id
GROUP BY w.warehouse_name, f.quarter_label
ORDER BY w.warehouse_name, f.quarter_label;

-- 5. Production vs shipment gap analysis
SELECT 
    w.warehouse_name,
    f.quarter_label,
    SUM(f.units_produced) AS total_produced,
    SUM(f.units_shipped) AS total_shipped,
    SUM(f.units_produced) - SUM(f.units_shipped) AS surplus,
    ROUND((SUM(f.units_produced)::NUMERIC / NULLIF(SUM(f.units_shipped), 0) - 1) * 100, 1) AS surplus_pct
FROM fact_daily_inventory f
JOIN dim_warehouse w ON f.warehouse_id = w.warehouse_id
GROUP BY w.warehouse_name, f.quarter_label
ORDER BY w.warehouse_name, f.quarter_label;

-- 6. Weekday vs weekend shipping patterns
SELECT 
    w.warehouse_name,
    CASE WHEN d.is_weekend THEN 'Weekend' ELSE 'Weekday' END AS day_type,
    ROUND(AVG(f.units_shipped), 1) AS avg_shipped,
    ROUND(AVG(f.units_produced), 1) AS avg_produced
FROM fact_daily_inventory f
JOIN dim_date d ON f.date_key = d.date_key
JOIN dim_warehouse w ON f.warehouse_id = w.warehouse_id
WHERE f.units_shipped > 0
GROUP BY w.warehouse_name, d.is_weekend
ORDER BY w.warehouse_name, day_type;

-- 7. Top 10 highest shipment days
SELECT 
    f.date_key,
    w.warehouse_name,
    p.product_name,
    f.units_shipped,
    f.closing_stock,
    f.capacity_utilization_pct
FROM fact_daily_inventory f
JOIN dim_warehouse w ON f.warehouse_id = w.warehouse_id
JOIN dim_product p ON f.product_id = p.product_id
WHERE f.units_shipped > 0
ORDER BY f.units_shipped DESC
LIMIT 10;

-- 8. Quarter-over-quarter growth by product
SELECT 
    curr.quarter_label AS current_quarter,
    p.product_name,
    curr.total_shipped AS current_shipped,
    prev.total_shipped AS prev_shipped,
    ROUND((curr.total_shipped::NUMERIC / NULLIF(prev.total_shipped, 0) - 1) * 100, 1) AS qoq_growth_pct
FROM (
    SELECT quarter_label, product_id, SUM(units_shipped) AS total_shipped
    FROM fact_daily_inventory
    GROUP BY quarter_label, product_id
) curr
JOIN (
    SELECT quarter_label, product_id, SUM(units_shipped) AS total_shipped
    FROM fact_daily_inventory
    GROUP BY quarter_label, product_id
) prev ON curr.product_id = prev.product_id
JOIN dim_product p ON curr.product_id = p.product_id
JOIN dim_quarterly_targets qt_c ON curr.quarter_label = qt_c.quarter_label
JOIN dim_quarterly_targets qt_p ON prev.quarter_label = qt_p.quarter_label
WHERE (qt_c.year * 10 + CAST(SUBSTRING(qt_c.quarter FROM 2) AS INTEGER)) = 
      (qt_p.year * 10 + CAST(SUBSTRING(qt_p.quarter FROM 2) AS INTEGER)) + 1
   OR (qt_c.quarter = 'Q1' AND qt_p.quarter = 'Q4' AND qt_c.year = qt_p.year + 1)
ORDER BY curr.quarter_label, p.product_name;

-- 9. Inventory health scorecard (latest quarter)
SELECT 
    w.warehouse_name,
    p.product_name,
    ROUND(AVG(f.closing_stock), 0) AS avg_stock,
    ROUND(AVG(f.capacity_utilization_pct), 1) AS avg_util_pct,
    SUM(CASE WHEN f.reorder_flag THEN 1 ELSE 0 END) AS days_below_safety,
    ROUND(AVG(f.units_shipped), 1) AS avg_daily_shipments
FROM fact_daily_inventory f
JOIN dim_warehouse w ON f.warehouse_id = w.warehouse_id
JOIN dim_product p ON f.product_id = p.product_id
WHERE f.quarter_label = 'Q1 2026'
GROUP BY w.warehouse_name, p.product_name
ORDER BY w.warehouse_name;