import pandas as pd
import numpy as np

input = "1m_ohlc_5y_adjusted_afte_complet_trading_hour.csv"
missing_data_filled = "data_filter2.csv"

df = pd.read_csv(input)
price_cols = ["Open", "High", "Low", "Last", "Volume", "cum_factor", "adj_open", "adj_high", "adj_low", "adj_last", "adj_volume"]

for col in price_cols:
    df[col] = pd.to_numeric(df[col], errors="coerce")

###############  filled open/last/high/low  value total
missing_mask = df["Open"].isna()

###################### Linear interpolation across time ################
df[price_cols] = df[price_cols].interpolate(method="linear", limit_direction="both")

###################### market consistency #######################
df["High"] = np.maximum.reduce([
    df["High"],
    df["Open"],
    df["Low"],
    df["Last"]
])

df["Low"] = np.minimum.reduce([
    df["Low"],
    df["Open"],
    df["High"],
    df["Last"]
])

df.to_csv(missing_data_filled, index=False)

print("Filled Open values:", missing_mask.sum())
print("Remaining missing Open:", df["Open"].isna().sum())
print("Saved:", missing_data_filled)