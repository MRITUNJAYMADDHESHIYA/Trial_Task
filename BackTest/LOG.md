1.Strategy:------->
Buy when the trailing 20-session return is below -10%. Enter at the next session's open. Exit at the open 5 sessions after entry. One position at a time.

#################### Data ########################
I check many thing in this data, but I am unable to find anything wrong in this
daily_ohlc_adjusted.csv file is really good data right now




######################### strategy Math ##################
20-session return = adj_close[t] / adj_close[t-20] - 1
signal generated when:--- 20-session return < -10%

entry price at entry_idx (t+1): ----    entry_idx = signal_idx + 1
exit rule on five trading sessions:---  exit_idx  = entry_idx + 5

only one position can be open at a time:- if position is open: ignore signal




##################### Dividend(cash dividens) #########################
cum_factor only changes on corporate-action ex-dates, and only two changes occur in the whole 5-year history:-

Ex-Date	   Pre-Factor	New Factor	Dividend
2022-06-09	0.970289	0.987745	SAR 0.60
2026-06-10	0.987745	1.000000	SAR 0.35      

dividend = previous_close * (1-old_factor / new_factor)

A trade receives the dividend if its ex-date satisfies:
entry_idx < ex_idx <= exit_idx

This means the position must have been entered before the ex-date and must still be held through the ex-date.

The dividend is added to the trade's gross P&L:--
gross_return =(exit_price - entry_price + dividend_credit) / entry_price




########################### Metrics ##########################
1.strategy_trades.csv ---->entry_date| exit_date| entry_price| exit_price| dividend_credit| gross_return| net_return
2.control_draws.csv ------>control_total_return | control_mean_trade_return
3.backtest_summary.csv ----> outputs form both(Main and Control strategy)



########################### Control: 1000 random-date draws #######################
Random entry dates
-->Each of the 1,000 draws: 44 entry dates sampled uniformly at random (without replacement, no overlap constraint) from all dates where a full 5-session hold is possible, run through the identical fill / dividend / cost as the strategy.

why not buy-hold:---
a comparable result can easily happen by picking dates that have nothing to do with the signal. Buy-and-hold isn't the right here, since it doesn't hold you to the same number of trades or the same 5-session exposure window, so a difference against it could just reflect being in the market less, not the signal doing anything.

