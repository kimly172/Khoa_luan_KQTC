# view/css.py
import streamlit as st  # Dùng để chèn CSS vào giao diện

# Điều chỉnh lại các css cho đẹp
def load_custom_css():
    st.markdown(
        """
        <style>

        
            /* Sidebar */
            [data-testid="stSidebarHeader"] {
                padding: 0px;
                height: 30px;
            }
            [data-testid="stSidebar"] {
                background-color: white;
                color: #333333; /* Màu nâu đậm */
                border-radius: 12px;
            }
            [data-testid="stSidebarUserContent"] {
                padding: 16px;
            }

            /* Main Layout */
            [data-testid="stHeader"] {
                background-color: transparent !important;
            }
            [data-testid="stApp"] {
                background: linear-gradient(to bottom left, #8DD0EB, #B1E0E7, #E3F2E6, #FBFDE3);
            }
            [data-testid="stMainBlockContainer"] {
                padding: 16px;
            }
            
            /* Biểu đồ */
            /* Chung */
            [data-testid="stVerticalBlock"] >
            [data-testid="stVerticalBlockBorderWrapper"] > div {
                margin: 12px;
            }

            /* 2 biểu đồ đứng chung */
            [data-testid="stMainBlockContainer"] > div > div > div > 
            [data-testid="stHorizontalBlock"]:nth-child(n+11) > div {
                background-color: rgba(255, 255, 255, 1); 
                border-radius: 20px;
                box-shadow: 0px 0px 5px rgba(0, 0, 0, 0.1);
            }
            
            [data-testid="stMainBlockContainer"] > div > div > div >    
            [data-testid="stHorizontalBlock"]:nth-child(n+11) > div * {
                background-color: transparent !important;
            }
            
            /* 1 biểu đồ đứng riêng */
            [data-testid="stMainBlockContainer"] > div > div > div > 
            [data-testid="stVerticalBlockBorderWrapper"] {
                background-color: rgba(255, 255, 255, 1); 
                border-radius: 20px;
                box-shadow: 0px 0px 5px rgba(0, 0, 0, 0.1);
            }
            [data-testid="stMainBlockContainer"] > div > div > div >    
            [data-testid="stVerticalBlockBorderWrapper"] * {
                background-color: transparent !important;
            }
            
            /* Selectbox */
            [data-testid="stSelectbox"] {
                max-width: 500px;
                min-width: 200px;
            }
            
            
            /* Heading */
            [data-testid="stElementContainer"] {
                display: flex;
                justify-content: center;
            }
            [data-testid="stHeading"] {
                text-align: center;
                justify-content: center;
            }
            h1, h2, h3, h4, h5, h6 {
                text-align: center;
            }
        

            /* DataFrame */
            .stDataFrameGlideDataEditor,
            [data-testid="stDataFrameResizable"] {
                border-radius: 20px !important;
            }
            
            /* Text Input / Select Input */
            [data-baseweb="select"],
            [data-baseweb="select"] > div {
                background-color: white; /* Màu nền */
                border-radius: 50px;
                color: #333; /* Màu chữ xám đậm */
            }
            [data-baseweb="select"] > div > div {
                padding: 8px 12px;
            }
            [data-baseweb="select"]:focus-within {
                border-color: #999999 !important;
                background-color: white;
                color: #333;
            }
            
            /* Điều chỉnh spinner */
            [data-testid="stSpinner"] i {
                width: 30px;
                height: 30px;
                border-radius: 50% !important;
                display: inline-block;
                border-top: 2px solid #007bff; /* Màu xanh dương */
                border-right: 2px solid transparent;
                border-left: none;       
                border-bottom: none;
                box-sizing: border-box;
                animation: rotation 1s linear infinite; /* Nhanh hơn và có hiệu ứng ease-in-out */
            }  
            /* Hiệu ứng xoay không ổn định */
            @keyframes rotation {
                0% { transform: rotate(0deg); }  
                25% { transform: rotate(60deg); } /* Quay chậm từ 300° đến 60° */
                75% { transform: rotate(300deg); } /* Bắt đầu chậm lại */
                100% { transform: rotate(360deg); } /* Quay chậm từ 300° đến 60° */
            }
            
            /* Button */
            
            [data-testid="stButton"] {
                display: flex;
                justify-content: center;
            }
        </style>    
        """,
        unsafe_allow_html=True,
    )
    