import pandas as pd
import numpy as np

df_warehouses = pd.read_csv("../data/raw/warehouses.csv")
df_products = pd.read_csv("../data/raw/products.csv")
df_deployments = pd.read_csv("../data/raw/quarterly_deployments.csv")


MEGAPACK_SHARE = 0.90
POWERWALL_SHARE=0.10

df_deployments["megapack_gwh"]=(df_deployments["GWh"]*0.90)
df_deployments["powerwall_gwh"]=(df_deployments["GWh"]*0.10)

df_deployments["megapack_units"]=(df_deployments["megapack_gwh"]/0.0039).astype(int)
df_deployments["powerwall_units"]=(df_deployments["powerwall_gwh"]/0.0000135).astype(int)

