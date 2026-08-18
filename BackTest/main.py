import numpy as np
import pandas as pd
np.random.seed(42)

DAILY_FILE       = "daily_ohlcv_adjusted.csv"
ROUND_TRIP_COST  = 0.00168  #### 16.8 bp
HOLDING_SESSIONS = 5
LOOKBACK         = 20
SIGNAL_THRESHOLD = -0.10    ####-10%
N_CONTROL_DRAWS  = 1000

##################### ex_date_index_in_daily: dividend_per_share
DIVIDENDS = {
    "2022-06-09": 0.60,
    "2026-06-10": 0.35,
}

######################## Data ###########################
def load_daily():
    daily          = pd.read_csv(DAILY_FILE)
    daily["date"]  = pd.to_datetime(daily["date"], format="%d-%m-%Y")
    daily          = daily.sort_values("date").reset_index(drop=True)
    daily["ret20"] = daily["adj_close"] / daily["adj_close"].shift(LOOKBACK) - 1
    return daily

############### Map ex-dividend calendar dates to their integer position in daily
def dividend_index_map(daily):
    idx_map = {}
    for date_str, amt in DIVIDENDS.items():
        d       = pd.Timestamp(date_str)
        matches = daily.index[daily["date"] == d]
        if len(matches):
            idx_map[matches[0]] = amt
    return idx_map

############### Dividend Credit ###################################
def apply_dividend_credit(entry_idx, exit_idx, div_map):
    credit = 0.0
    for ex_idx, amt in div_map.items():
        if entry_idx < ex_idx <= exit_idx:
            credit += amt
    return credit


def run_trades(entry_indices, daily, div_map):
    n    = len(daily)
    rows = []
    for entry_idx in entry_indices:
        exit_idx = entry_idx + HOLDING_SESSIONS

        if exit_idx >= n:
            continue
        entry_price = daily.loc[entry_idx, "open"]
        exit_price  = daily.loc[exit_idx, "open"]
        div_credit  = apply_dividend_credit(entry_idx, exit_idx, div_map)

        gross_return = (exit_price - entry_price + div_credit) / entry_price
        net_return   = gross_return - ROUND_TRIP_COST

        rows.append({
            "entry_date":      daily.loc[entry_idx, "date"],
            "exit_date":       daily.loc[exit_idx, "date"],
            "entry_price":     entry_price,
            "exit_price":      exit_price,
            "dividend_credit": div_credit,
            "gross_return":    gross_return,
            "net_return":      net_return,
        })
    return pd.DataFrame(rows)


#################### One-position-at-a-time + list of entry index ####################
def generate_strategy_entries(daily):
    n                = len(daily)
    entries          = []
    in_position      = False
    exit_idx_current = -1

    for t in range(LOOKBACK, n - 1):  ############## need t+1 to exist for entry
        if in_position and t <= exit_idx_current:
            continue
        in_position = False

        if daily.loc[t, "ret20"] < SIGNAL_THRESHOLD:
            entry_idx = t + 1
            exit_idx  = entry_idx + HOLDING_SESSIONS
            if exit_idx >= n:
                break
            entries.append(entry_idx)
            in_position = True
            exit_idx_current = exit_idx
    return entries


def main():
    daily   = load_daily()
    div_map = dividend_index_map(daily)
    n       = len(daily)

    ################ Strategy runing ##################
    strat_entries = generate_strategy_entries(daily)
    strat_trades  = run_trades(strat_entries, daily, div_map)
    strat_trades.to_csv("strategy_trades.csv", index=False)

    n_trades           = len(strat_trades)
    strat_equity       = (1 + strat_trades["net_return"]).cumprod()
    strat_total_return = strat_equity.iloc[-1] - 1
    strat_mean_trade   = strat_trades["net_return"].mean()
    strat_win_rate     = (strat_trades["net_return"] > 0).mean()

    ############################ Control: random entry dates, matched N trades, matched holding length
    valid_entry_pool   = np.arange(LOOKBACK, n - HOLDING_SESSIONS - 1)

    control_total_returns = []
    control_mean_returns  = []
    for _ in range(N_CONTROL_DRAWS):
        rand_entries = np.random.choice(valid_entry_pool, size=n_trades, replace=False)
        rand_entries = np.sort(rand_entries)
        trades       = run_trades(rand_entries, daily, div_map)
        eq           = (1 + trades["net_return"]).cumprod()
        control_total_returns.append(eq.iloc[-1] - 1)
        control_mean_returns.append(trades["net_return"].mean())

    control_total_returns = np.array(control_total_returns)
    control_mean_returns  = np.array(control_mean_returns)

    p_total = (control_total_returns >= strat_total_return).mean()
    p_mean  = (control_mean_returns >= strat_mean_trade).mean()

    ###################### Results on Main and Control strategy ####################
    print("STRATEGY RESULTS")
    print(f"Number of trades              : {n_trades}")
    print(f"Mean net return per trade     : {strat_mean_trade:.4%}")
    print(f"Win rate                      : {strat_win_rate:.2%}")
    print(f"Total compounded net return   : {strat_total_return:.4%}")
    print(f"Final equity (from 1.0)       : {strat_equity.iloc[-1]:.4f}")
    print()
    print(f"CONTROL DISTRIBUTION ({N_CONTROL_DRAWS} random-date draws, "f"{n_trades} trades each, 5-session hold)")
    print(f"Control total return   mean={control_total_returns.mean():.4%}  "
          f"std={control_total_returns.std():.4%}  "
          f"5th pct={np.percentile(control_total_returns,5):.4%}  "
          f"95th pct={np.percentile(control_total_returns,95):.4%}")
    print(f"Control mean-trade ret mean={control_mean_returns.mean():.4%}  "
          f"std={control_mean_returns.std():.4%}  "
          f"5th pct={np.percentile(control_mean_returns,5):.4%}  "
          f"95th pct={np.percentile(control_mean_returns,95):.4%}")
    print()
    print(f"P(control total return >= strategy total return)  : {p_total:.3f}")
    print(f"P(control mean trade return >= strategy mean trade): {p_mean:.3f}")

    ########################## Save control distribution + summary for the report
    pd.DataFrame({
        "control_total_return": control_total_returns,
        "control_mean_trade_return": control_mean_returns,
    }).to_csv("control_draws.csv", index=False)

    summary = {
        "n_trades":                       n_trades,
        "strat_mean_trade_return":        strat_mean_trade,
        "strat_win_rate":                 strat_win_rate,
        "strat_total_return":             strat_total_return,
        "strat_final_equity":             strat_equity.iloc[-1],
        "control_total_return_mean":      control_total_returns.mean(),
        "control_total_return_std":       control_total_returns.std(),
        "control_mean_trade_return_mean": control_mean_returns.mean(),
        "control_mean_trade_return_std":  control_mean_returns.std(),
        "p_value_total_return":           p_total,
        "p_value_mean_trade_return":      p_mean,
    }
    pd.Series(summary).to_csv("backtest_summary.csv")


if __name__ == "__main__":
    main()

