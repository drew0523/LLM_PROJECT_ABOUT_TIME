from config import *
import streamlit as st
import time
from page import *

def main():

    st.set_page_config(page_title="About Time", page_icon=":hourglass:", layout="wide")

    if "page" not in st.session_state:
        st.session_state.page = "input"

    if st.session_state.page == "input":
        input_page()
    else:
        chatbot_page()

if __name__ == "__main__":
    main()