import pandas as pd
import statsmodels.api as sm
from statsmodels.tsa.arima.model import ARIMA


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
