import pandas as pd
import numpy as np

df = pd.read_csv("data/fashion.csv")
np.random.seed(42)
df["sold_count"] = np.random.randint(0, 1000, len(df))
df["rating"] = np.round(np.random.uniform(2.5, 5.0, len(df)), 1)
df["views"] = np.random.randint(100, 5000, len(df))
df.to_csv("fashion_sales.csv", index=False)