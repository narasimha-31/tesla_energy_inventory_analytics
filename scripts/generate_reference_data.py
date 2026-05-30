import pandas as pd

#warehouse reference
warehouses = [
    {"id":"WH-01","name":"Megafactory Lathrop","state":"California","country":"USA","Product":"Megapack","capacity_gwh":40,"status":"active","opened_year":2022},
    {"id":"WH-02","name":"Megafactory Shanghai","state":"Shanghai","country":"China","Product":"Megapack","capacity_gwh":20,"status":"active","opened_year":2025},
    {"id":"WH-03","name":"Gigafactory Nevada","state":"Nevada","country":"USA","Product":"Powerwall","capacity_gwh":6,"status":"active","opened_year":2019},
    {"id":"WH-04","name":"Megafactory Houston","state":"Texas","country":"USA","Product":"Megapack 3","capacity_gwh":50,"status":"construction","opened_year":2026}
]

df_warehouses = pd.DataFrame(warehouses)

#product reference
products = [
    {"id": "PRD-01", "name": "Megapack 2", "type": "utility", "capacity_kWh": 3900, "unit_weight_tons": 35},
    {"id": "PRD-02", "name": "Megapack 3", "type": "utility", "capacity_kWh": 5000, "unit_weight_tons": 39},
    {"id": "PRD-03", "name": "Powerwall 3", "type": "residential", "capacity_kWh": 13.5, "unit_weight_tons": 0.114},

]
df_products = pd.DataFrame(products)

#quarterly deployments
deployments = [
    {"quarter":"Q1","year":2024,"GWh":4.1},
    {"quarter":"Q2","year":2024,"GWh":9.4},
    {"quarter":"Q3","year":2024,"GWh":6.9},
    {"quarter":"Q4","year":2024,"GWh":11.0},
    {"quarter":"Q1","year":2025,"GWh":10.4},
    {"quarter":"Q2","year":2025,"GWh":9.6},
    {"quarter":"Q3","year":2025,"GWh":12.5},
    {"quarter":"Q4","year":2025,"GWh":14.2},
    {"quarter":"Q1","year":2026,"GWh":8.8}
]
df_deployments = pd.DataFrame(deployments)


df_warehouses.to_csv("../data/raw/warehouses.csv", index=False)
df_products.to_csv("../data/raw/products.csv", index=False)
df_deployments.to_csv("../data/raw/quarterly_deployments.csv", index=False)

print("\nFiles saved to data/raw/")