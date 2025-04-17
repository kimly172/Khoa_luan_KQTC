import streamlit as st
import pandas as pd
import plotly.express as px

from view.css import load_custom_css  # Tải CSS
from view.interface import setup_page, setup_sidebar, setup_interface # Thiết lập giao diện

def main():
    setup_page()
    setup_sidebar()

    setup_interface()
    load_custom_css()

if __name__ == "__main__":
    main()  # Chạy ứng dụng