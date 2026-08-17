import pandas as pd
import numpy as np

path  = "1m_ohlcv_5y_adjusted.csv"
df    = pd.read_csv(path)

df["Date-Time"] = pd.to_datetime(df["Date-Time"], errors="coerce")

finding = []

############ Missing data #####################
missing_dates = df["Date-Time"].isna()
missing_open  = df["Open"].isna()
missing_high  = df["High"].isna()
missing_low   = df["Low"].isna()
missing_last  = df["Last"].isna()

missing_open_ad  = df["adj_open"].isna()
missing_high_ad  = df["adj_high"].isna()
missing_low_ad   = df["adj_low"].isna()
missing_last_ad  = df["adj_last"].isna()

missing_volume  = df["Volume"].isna()
missing_volume_ad = df["adj_volume"].isna()

print(len(missing_dates))
print(len(missing_open))
print(len(missing_high))
print(len(missing_low))
print(len(missing_last))
print(len(missing_open_ad))
print(len(missing_high_ad))
print(len(missing_low_ad))
print(len(missing_last_ad))
print(len(missing_volume))
print(len(missing_volume_ad))