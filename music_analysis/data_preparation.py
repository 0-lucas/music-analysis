import numpy as np
import pandas as pd


def add_hour_column(dataframe: pd.DataFrame, date_column: str) -> pd.DataFrame:
	try:
		dataframe["hour_played"]: pd.Series[np.datetime64] = dataframe[date_column].dt.hour
		return dataframe
	
	except AttributeError:  # Column was not in datetime format.
		dataframe[date_column]: pd.Series[np.datetime64] = format_date_column(dataframe[date_column])
		return add_hour_column(dataframe, date_column)


def format_date_column(column: pd.Series) -> pd.Series:
	return pd.to_datetime(column, format="%Y-%m-%d %H:%M:%S")


def _process_dataframe(dataframe: pd.DataFrame) -> pd.DataFrame:
	dataframe = add_hour_column(dataframe, "date_played")
	
	return dataframe


def read_dataframe_from_csv(path: str) -> pd.DataFrame:
	data: pd.DataFrame = pd.read_csv(path)
	
	return _process_dataframe(data)


def _get_music_time_series(data: pd.DataFrame, frequency: str) -> pd.Series:
	data = data.set_index("date_played").groupby(
		pd.Grouper(freq=frequency)).agg({"artist": "nunique", "album": "nunique", "track": "count"})
	
	return data


def process_data_to_polar_plot(data: pd.DataFrame) -> pd.DataFrame:
	if "hour_played" not in data.columns:
		data = add_hour_column(data, "date_played")
	
	data = data.groupby("hour_played").count()
	data = data["track"].reset_index()
	data["r"] = (data["hour_played"] / 24) * 360
	data["am_pm"] = data["hour_played"].apply(lambda x: "AM" if x < 12 else "PM")
	
	return data
