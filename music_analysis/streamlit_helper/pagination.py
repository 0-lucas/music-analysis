import streamlit as st


def save_user(username: str) -> None:
	if "username" not in st.session_state:
		st.session_state["username"] = username


def is_input_page() -> bool:
	""" Returns True if active page is 'username input page' """
	return True if st.session_state.page == 0 else False


def is_dashboard_page() -> bool:
	""" Returns True if active page is data visualization page/ dashboard """
	return True if st.session_state.page > 0 else False


def go_to_next_page(): st.session_state.page += 1


def restart_page(): st.session_state.page = 0
