import pandas as pd

INPUT_FILE = "1m_ohlcv_5y_adjusted.csv"
OUTPUT_FILE = "1m_ohlc_5y_adjusted_afte_complet_trading_hour.csv"

df              = pd.read_csv(INPUT_FILE)
df["Date-Time"] = pd.to_datetime(df["Date-Time"], utc=True)
df              = df.sort_values("Date-Time")
trading_days    = sorted(df["Date-Time"].dt.date.unique())
expected = []

for day in trading_days:
    start = pd.Timestamp(f"{day} 07:00:00", tz="UTC")
    end   = pd.Timestamp(f"{day} 12:30:00", tz="UTC")

    expected.extend(pd.date_range(start=start, end=end, freq="1min"))

expected = pd.DatetimeIndex(expected)

df = (
    df.set_index("Date-Time")
      .reindex(expected)
      .rename_axis("Date-Time")
      .reset_index()
)

df.to_csv(OUTPUT_FILE, index=False)

print("Rows after inserting missing timestamps:", len(df))
print("Missing rows inserted:", df["#RIC"].isna().sum())



