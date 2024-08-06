import streamlit as st
import pandas as pd
import numpy as np

from music_analysis.last_fm_connection import LastFmConnection
from music_analysis.streamlit_helper.pagination import *

if "page" not in st.session_state:
	st.session_state.page = 0

if "lastfm" not in st.session_state:
	st.session_state["lastfm"] = LastFmConnection()

placeholder = st.empty()

if is_input_page():
	with placeholder.container():
		# Replace the placeholder with some text:
		st.title("Last.fm Analysis")
		
		username: str = st.text_input(
			"Enter your last.fm username here.",
			placeholder="e.g. saintcecilla",
			key="username-input"
		)
		
		if username:
			user_exists: bool = st.session_state["lastfm"].check_if_user_exists(username)
			if not user_exists:  # User was not found
				st.text("Username not found. Please try again!")
			
			if user_exists:
				save_user(username)
				go_to_next_page()
				st.rerun()  # Needed for checking st.session_state.page

else:
	with placeholder.container():
		if st.session_state.username:
			data: pd.DataFrame = st.session_state["lastfm"].get_user_tracks(st.session_state.username)
			
			st.dataframe(data)
			