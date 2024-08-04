import os
import requests
from requests import Response
import time

import pandas as pd
from dotenv import load_dotenv

from utils import format_date_column

# ATTENTION - For development purposes only
load_dotenv("secrets.env")


class LastFmConnection:
	def __init__(self):
		self.api_key: str = os.environ.get("API_KEY")
		self.endpoint: str = "https://ws.audioscrobbler.com/2.0/"
		self.headers: dict[str:str] = {"user-agent": "MusicAnalysis"}
		self.max_tracks: int = 200
	
	def _build_base_payload(self, method: str, user: str) -> dict[str:str]:
		""" Returns a base payload for HTTP request depending on the method passed """
		payload: dict[str:str] = {
			"api_key": self.api_key,
			"extended": 0,
			"method": method,
			"user": user,
			"limit": self.max_tracks,
			"format": "json"
		}
		
		return payload
	
	@staticmethod
	def _get_first_key(dictionary: dict) -> str:
		""" Returns the first key of a dictionary """
		
		for key in dictionary:
			return key
	
	@staticmethod
	def _add_pagination_to_payload(payload: dict[str: str], page: int) -> dict[str: str]:
		""" Add page parameter to payload dictionary """
		payload["page"] = page
		
		return payload
	
	def get(self, method: str, user: str, page: int = 1) -> Response:
		""" Public method for making requests to Last.fm API """
		payload: dict[str:str] = self._build_base_payload(method, user)
		payload: dict[str:str] = self._add_pagination_to_payload(payload, page)
		
		response: Response = requests.get(self.endpoint, headers=self.headers, params=payload)
		
		return response
	
	def _get_total_pages(self, method: str, user: str) -> int:
		""" Method for retrieving total pages from a single call to API """
		response_json: dict = self.get(method, user).json()
		
		# Because the first key is related to the method used, it needs to be dynamic.
		# Also, you need this first key to access the rest of the data, once it wraps around it all.
		first_key: str = self._get_first_key(response_json)
		total_pages: int = int(response_json[first_key]["@attr"]["totalPages"])
		
		return total_pages
	
	def get_paginated_responses(self, method: str, user: str, ) -> list[Response]:
		""" Paginates requests to endpoint, to get all available pages """
		total_pages: int = self._get_total_pages(method, user)
		responses: list[Response] = []
		
		for page in range(1, total_pages + 1):
			response: Response = self.get(method, user, page)
			responses.append(response)
			time.sleep(0.2)
		
		return responses
	
	@staticmethod
	def _build_dataframe(responses: list[Response]) -> pd.DataFrame:
		""" Build a base DataFrame based on a list of HTTP responses """
		dataframe: pd.DataFrame = pd.DataFrame()
		appending_rows: list[dict] = []
		
		rows: list[list[dict]] = [response.json()["recenttracks"]["track"] for response in responses]
		for sublist in rows:
			[appending_rows.append(row) for row in sublist]
		
		return pd.DataFrame(appending_rows)
	
	def _process_dataframe(self, dataframe: pd.DataFrame) -> pd.DataFrame:
		""" Removes unused columns and get real valued data inside dicts from encoded columns """
		dataframe = dataframe[["artist", "album", "name", "date"]]
		
		dataframe = dataframe.map(lambda col: col["#text"] if self._is_dict_encoded(col) else col)
		
		dataframe = format_date_column(dataframe["date"])
		
		return dataframe
	
	def get_dataframe_from_pagination(self, responses: list[Response]) -> pd.DataFrame:
		dataframe: pd.DataFrame = self._build_dataframe(responses)
		dataframe: pd.DataFrame = self._process_dataframe(dataframe)
		
		return dataframe
	
	@staticmethod
	def _is_dict_encoded(value: str | dict) -> bool:
		return True if type(value) is dict else False
