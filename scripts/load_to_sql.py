import pandas as pd
import psycopg2
from dotenv import load_dotenv
import os

load_dotenv(dotenv_path="../.env")

conn = psycopg2.connect(
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT"),
    database=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD")
)
conn.autocommit = False
cursor = conn.cursor()

with open("../sql/create_schema.sql", "r") as f:
    cursor.execute(f.read())
conn.commit()

RAW = "../data/raw"

df_warehouses = pd.read_csv(f"{RAW}/warehouses.csv")
for _, r in df_warehouses.iterrows():
    cursor.execute(
        "INSERT INTO dim_warehouse VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
        (r["id"], r["name"], r["state"], r["country"],
         r["Product"], float(r["capacity_gwh"]), r["status"], int(r["opened_year"]))
    )

df_products = pd.read_csv(f"{RAW}/products.csv")
for _, r in df_products.iterrows():
    cursor.execute(
        "INSERT INTO dim_product VALUES (%s,%s,%s,%s,%s)",
        (r["id"], r["name"], r["type"], float(r["capacity_kWh"]), float(r["unit_weight_tons"]))
    )

df_dep = pd.read_csv(f"{RAW}/quarterly_deployments.csv")
for _, r in df_dep.iterrows():
    q, y, gwh = r["quarter"], int(r["year"]), float(r["GWh"])
    mp_gwh = gwh * 0.90
    pw_gwh = gwh * 0.10
    mp_units = int(mp_gwh / 0.0039)
    pw_units = int(pw_gwh / 0.0000135)
    cursor.execute(
        "INSERT INTO dim_quarterly_targets VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
        (f"{q} {y}", q, y, gwh, mp_gwh, pw_gwh, mp_units, pw_units)
    )

df_inv = pd.read_csv(f"{RAW}/daily_inventory.csv")
dates = pd.to_datetime(df_inv["date"].unique())
for d in dates:
    dk = d.strftime("%Y-%m-%d")
    qn = (d.month - 1) // 3 + 1
    cursor.execute(
        "INSERT INTO dim_date VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) ON CONFLICT DO NOTHING",
        (dk, dk, d.year, f"Q{qn}", f"Q{qn} {d.year}",
         d.month, d.strftime("%B"), d.isocalendar()[1],
         d.dayofweek, d.strftime("%A"),
         d.dayofweek >= 5, d.is_month_end)
    )

for _, r in df_inv.iterrows():
    cursor.execute(
        "INSERT INTO fact_daily_inventory (date_key,quarter_label,warehouse_id,product_id,"
        "units_received,units_produced,units_shipped,closing_stock,reorder_flag,capacity_utilization_pct) "
        "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
        (r["date"], r["quarter"], r["warehouse_id"], r["product_id"],
         int(r["units_received"]), int(r["units_produced"]), int(r["units_shipped"]),
         int(r["closing_stock"]), bool(r["reorder_flag"]), float(r["capacity_utilization_pct"]))
    )

conn.commit()

print("Database loaded successfully\n")
for t in ["dim_warehouse","dim_product","dim_date","dim_quarterly_targets","fact_daily_inventory"]:
    cursor.execute(f"SELECT COUNT(*) FROM {t}")
    print(f"  {t}: {cursor.fetchone()[0]}")

cursor.execute("""
    SELECT f.quarter_label, w.warehouse_name, SUM(f.units_shipped)
    FROM fact_daily_inventory f
    JOIN dim_warehouse w ON f.warehouse_id = w.warehouse_id
    GROUP BY f.quarter_label, w.warehouse_name
    ORDER BY f.quarter_label, w.warehouse_name
    LIMIT 10
""")
print("\nVerification:")
for row in cursor.fetchall():
    print(f"  {row[0]} | {row[1]} | {row[2]:,} units")

conn.close()