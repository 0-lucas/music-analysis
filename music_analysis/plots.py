import pandas as pd
from scipy.signal import periodogram
import matplotlib.pyplot as plt
import plotly.express as px

def plot_periodogram(ts: pd.Series, detrend='linear', ax=None):
	fs = pd.Timedelta("365D") / pd.Timedelta("1D")
	frequencies, spectrum = periodogram(
		ts,
		fs=fs,
		detrend=detrend,
		window="boxcar",
		scaling='spectrum',
	)
	if ax is None:
		_, ax = plt.subplots()
	ax.step(frequencies, spectrum, color="purple")
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
