Problems with data:-
Two main problem with this data Missing data and Gaps in time

1.Missing data:-
1-minute timestamp exists as a row in the source file, but Open/High/Low/Last (and the adj_* equivalents) are blank. Volume is present and non-zero on every one of these rows, so a minute was recorded but no clean trade price came through it.

solution:- 1.linear-interplation across time (I preferd this right now)
           2.ML models(Decision Trees, Random Forests, and XGBoost)


2.Gaps in Date-Time:-
1-minute timestamp inside the trading session has no row at all in the source file (as opposed to Problem 1, where the row exists but is empty).

solution:- 1.Fill the gaps except holidays, market close
---->total missing_bars  === 132,467 in (7:00 to  12:30 trading hour) it's not included market close
----> then I am using previous model for the missing data



3.high>= open, close, low and low <= open, close, high
sloution:- if this case happend, then fixed with the model



##############################################################
