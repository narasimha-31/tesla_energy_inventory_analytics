import pandas as pd
import numpy as np

np.random.seed(42)

df_warehouses = pd.read_csv("../data/raw/warehouses.csv")
df_products = pd.read_csv("../data/raw/products.csv")
df_deployments = pd.read_csv("../data/raw/quarterly_deployments.csv")

MEGAPACK_SHARE = 0.90
POWERWALL_SHARE = 0.10

df_deployments["megapack_gwh"] = df_deployments["GWh"] * MEGAPACK_SHARE
df_deployments["powerwall_gwh"] = df_deployments["GWh"] * POWERWALL_SHARE
df_deployments["megapack_units"] = (df_deployments["megapack_gwh"] / 0.0039).astype(int)
df_deployments["powerwall_units"] = (df_deployments["powerwall_gwh"] / 0.0000135).astype(int)

quarter_dates = {
    "Q1": ("01-01", "03-31"),
    "Q2": ("04-01", "06-30"),
    "Q3": ("07-01", "09-30"),
    "Q4": ("10-01", "12-31")
}

def distribute_to_daily(target_total, num_days, variation=0.3):
    if target_total == 0:
        return np.zeros(num_days, dtype=int)
    raw = np.random.normal(loc=1, scale=variation, size=num_days)
    raw = np.maximum(raw, 0.1)
    daily_units = (raw / raw.sum()) * target_total
    daily_units = np.round(daily_units).astype(int)
    daily_units = np.maximum(daily_units, 0)
    diff = target_total - daily_units.sum()
    daily_units[0] += diff
    return daily_units

all_rows = []

for _, dep in df_deployments.iterrows():
    quarter = dep["quarter"]
    year = int(dep["year"])
    megapack_total = int(dep["megapack_units"])
    powerwall_total = int(dep["powerwall_units"])

    start_str = f"{year}-{quarter_dates[quarter][0]}"
    end_str = f"{year}-{quarter_dates[quarter][1]}"
    dates = pd.date_range(start=start_str, end=end_str)
    num_days = len(dates)

    shanghai_active = (year > 2025) or (year == 2025)

    if shanghai_active:
        lathrop_units = int(megapack_total * 0.67)
        shanghai_units = megapack_total - lathrop_units
    else:
        lathrop_units = megapack_total
        shanghai_units = 0

    warehouse_runs = [
        ("WH-01", "PRD-01", lathrop_units, 40),
        ("WH-02", "PRD-01", shanghai_units, 20),
        ("WH-03", "PRD-03", powerwall_total, 6),
    ]

    for wh_id, prod_id, q_shipped, cap_gwh in warehouse_runs:
        daily_shipped = distribute_to_daily(q_shipped, num_days)
        daily_produced = distribute_to_daily(int(q_shipped * 1.05), num_days, variation=0.25)
        daily_received = distribute_to_daily(int(q_shipped * 1.10), num_days, variation=0.2)

        if prod_id == "PRD-01":
            cap_kwh = 3900.0
        elif prod_id == "PRD-02":
            cap_kwh = 5000.0
        else:
            cap_kwh = 13.5

        max_storage = int((cap_gwh * 1_000_000 / cap_kwh) * 0.04)
        if max_storage == 0:
            max_storage = 1

        safety_stock = int(q_shipped * 0.05) if q_shipped > 0 else 0
        initial_stock = int(q_shipped * 0.12) if q_shipped > 0 else 0

        closing_stock = initial_stock

        for i, date in enumerate(dates):
            produced = int(daily_produced[i])
            shipped = int(daily_shipped[i])
            received = int(daily_received[i])

            closing_stock = closing_stock + produced - shipped
            if closing_stock < 0:
                closing_stock = 0

            cap_util = round(min((closing_stock / max_storage) * 100, 100.0), 2)
            reorder = closing_stock < safety_stock

            all_rows.append({
                "date": date.strftime("%Y-%m-%d"),
                "quarter": f"{quarter} {year}",
                "warehouse_id": wh_id,
                "product_id": prod_id,
                "units_received": received,
                "units_produced": produced,
                "units_shipped": shipped,
                "closing_stock": closing_stock,
                "reorder_flag": reorder,
                "capacity_utilization_pct": cap_util
            })

df_inventory = pd.DataFrame(all_rows)

df_inventory.to_csv("../data/raw/daily_inventory.csv", index=False)

print(f"Total rows: {len(df_inventory)}")
print(f"Date range: {df_inventory['date'].min()} to {df_inventory['date'].max()}")
print(f"Warehouses: {df_inventory['warehouse_id'].unique()}")
print(f"\nSample rows:")
print(df_inventory.head(10))
print(f"\nQuarterly shipped totals (verification):")
print(df_inventory.groupby(["quarter", "warehouse_id"])["units_shipped"].sum())