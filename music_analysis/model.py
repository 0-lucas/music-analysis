import pandas as pd
import numpy as np
from sklearn.base import RegressorMixin, BaseEstimator
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from statsmodels.tsa.deterministic import DeterministicProcess, CalendarFourier


class CustomMusicModel(BaseEstimator, RegressorMixin):
	def __init__(
			self,
			first_model=LinearRegression(fit_intercept=False),
			second_model=RandomForestRegressor(n_jobs=-1, criterion="absolute_error", max_depth=5, n_estimators=50)
	) -> None:
		self.trend_model: LinearRegression = first_model
		self.seasonal_model: RandomForestRegressor = second_model
		self.trend_dp: DeterministicProcess | None = None
		self.seasonal_dp: DeterministicProcess | None = None
	
	@staticmethod
	def __train_test_from_ts(time_series: pd.Series) -> (np.array, np.array):
		""" Converts time series with datetime index and real valued data to train and test arrays.
		Because the model only sees datetime features, the index of the time series itself creates all training features.
		The actual values are used as target.
		
		Returns:
			features (np.array)
			target (np.array)
		"""
		
		return time_series.index, time_series.values
	
	@staticmethod
	def build_trend_deterministic_process(data: np.array) -> DeterministicProcess:
		""" Returns a pre-built DeterministicProcess object for trend fitting """
		return DeterministicProcess(data, constant=True, drop=True, order=2)
	
	@staticmethod
	def build_seasonal_deterministic_process(data: np.array) -> DeterministicProcess:
		""" Returns a pre-built DeterministicProcess object for seasonal fitting """
		return DeterministicProcess(
			data,
			order=0,
			seasonal=True,
			drop=True,
			additional_terms=[CalendarFourier("ME", 4), CalendarFourier("YE", 4)]
		)
	
	@staticmethod
	def __fit_inner_model(dp: DeterministicProcess, target: pd.Series, model) -> None:
		""" Helper function to fit models depending on algorithm and deterministic process """
		model.fit(dp.in_sample(), target)
	
	def fit(self, time_series: pd.Series):
		train, target = self.__train_test_from_ts(time_series)
		
		self.trend_dp: DeterministicProcess = self.build_trend_deterministic_process(train)
		self.__fit_inner_model(self.trend_dp, target, self.trend_model)
		
		# Predicts trend component and passes and converts to pd.Series, maintaining index
		trend_prediction: pd.Series = pd.Series(
			self.trend_model.predict(self.trend_dp.in_sample()), index=train)
		
		# Difference time series based on modelled trend
		seasonal_target: pd.Series = target - trend_prediction
		
		self.seasonal_dp: DeterministicProcess = self.build_seasonal_deterministic_process(train)
		self.__fit_inner_model(self.seasonal_dp, seasonal_target, self.seasonal_model)
	
	def predict(self, steps: int = 4) -> np.array:
		""" Predicts data points out of sample after model has been trained.
		Args:
			steps (int): Quantity of steps to forecast, aka forecast horizon. Model calibrated to 4 steps.
		"""
		trend_forecast: np.array = self.trend_model.predict(self.trend_dp.out_of_sample(steps))
		seasonal_forecast: np.array = self.seasonal_model.predict(self.seasonal_dp.out_of_sample(steps))
		
		return trend_forecast + seasonal_forecast
