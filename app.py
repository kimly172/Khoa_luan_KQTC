import streamlit as st
import pandas as pd
# import plotly.express as px # Bỏ import này nếu không dùng trực tiếp trong app.py

from view.css import load_custom_css  # Tải CSS
from view.interface import setup_page, setup_sidebar, setup_interface
from view.financial_metrics_view import display_financial_metrics # Import trang mới

def main():
    setup_page()
    setup_sidebar()  # Sidebar sẽ set st.session_state.selected_page
    
    load_custom_css()
    
    # Dựa vào lựa chọn trên sidebar để hiển thị trang tương ứng
    if st.session_state.selected_page == "Trang chính":
        setup_interface() # Gọi giao diện chính
    elif st.session_state.selected_page == "Giải thích Chỉ số Tài chính":
        display_financial_metrics() # Gọi trang giải thích chỉ số
    
if __name__ == "__main__":
    main()  # Chạy ứng dụng
