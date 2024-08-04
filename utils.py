import pandas as pd
from scipy.signal import periodogram
import matplotlib.pyplot as plt
import statsmodels.api as sm
from statsmodels.tsa.arima.model import ARIMA


def read_csv_properly(path: str) -> pd.DataFrame:
	data = pd.read_csv(path, usecols=["utc_time", "artist", "album", "track"]
	                   ).rename(columns={"utc_time": "date_played"})
	
	data["date_played"] = format_date_column(data["date_played"])
	
	return data


def format_date_column(column: pd.Series) -> pd.Series:
	column["date_played"] = pd.to_datetime(column["date_played"], format="%d %b %Y, %H:%M")
	return column


def get_music_time_series(data: pd.DataFrame, frequency: str) -> pd.Series:
	data = data.set_index("date_played").groupby(pd.Grouper(freq=frequency)
	                                             ).agg({"artist": "nunique", "album": "nunique", "track": "count"})
	return data


def plot_periodogram(ts: pd.Series, detrend='linear', ax=None):
	fs = pd.Timedelta("365D") / pd.Timedelta("1D")
	freqencies, spectrum = periodogram(
		ts,
		fs=fs,
		detrend=detrend,
		window="boxcar",
		scaling='spectrum',
	)
	if ax is None:
		_, ax = plt.subplots()
	ax.step(freqencies, spectrum, color="purple")
	ax.set_xscale("log")
	ax.set_xticks([1, 2, 4, 6, 12, 26, 52, 104])
	ax.set_xticklabels(
		[
			"Annual (1)",
			"Semiannual (2)",
			"Quarterly (4)",
			"Bimonthly (6)",
			"Monthly (12)",
			"Biweekly (26)",
			"Weekly (52)",
			"Semiweekly (104)",
		],
		rotation=30,
	)
	ax.ticklabel_format(axis="y", style="sci", scilimits=(0, 0))
	ax.set_ylabel("Variance")
	ax.set_title("Periodogram")
	return ax


def test_augmented_df(series: pd.Series) -> None:
	adf = sm.tsa.adfuller(series, autolag=None, maxlag=4)
	print("adf : ", adf[0])
	print("p-value : ", adf[1])


def get_optimized_arima(data: pd.Series):
	aic = 0
	persist_model = None
	
	for ar_order in range(0, 5):
		for ma_order in range(1, 6):
			for diff_order in range(0, 5):
				model = ARIMA(data, order=(ar_order, diff_order, ma_order)).fit()
				
				if model.aic < aic:
					aic = model.aic
					persist_model = model
	
	return persist_model
