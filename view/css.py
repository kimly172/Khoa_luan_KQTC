# view/css.py
import streamlit as st  # Dùng để chèn CSS vào giao diện

# Điều chỉnh lại các css cho đẹp
def load_custom_css():
    st.markdown(
                """
        <style>
        [data-testid="stSidebarHeader"] {
            padding: 0px;
            height: 30px;
        }
        
        [data-testid="stSidebar"] {
            background-color: white ;
            color: #333333; /* Màu nâu đậm */
        }
        
        [data-testid="stHeader"] {
            background-color: transparent !important;
        }

        [data-testid="stMainBlockContainer"] {
            padding: 16px;
        }
        
        [data-testid="stApp"] {
            background: linear-gradient(to bottom left, #8DD0EB, #B1E0E7, #E3F2E6, #FBFDE3);
        }
        
        [data-testid="stSidebar"] {
            border-radius: 12px;
        }
        
        [data-testid="stSidebarUserContent"] {
            padding: 16px;
        }
        
        [data-testid="stVerticalBlock"] >
        [data-testid="stVerticalBlockBorderWrapper"] > div {
            margin:12px;
        }
        
        [data-testid="stHorizontalBlock"] > 
        [data-testid="stColumn"] > 
        [data-testid="stVerticalBlockBorderWrapper"]:first-child {
            background-color: rgba(256, 256, 256, 1);
            border-radius: 20px;
            box-shadow: 0px 0px 5px rgba(0, 0, 0, 0.1);
        }
        
        [data-testid="stHorizontalBlock"] > 
        [data-testid="stColumn"] >
        [data-testid="stVerticalBlockBorderWrapper"] * {
            background-color: transparent !important;
        }
        
        
        [data-testid="stElementContainer"] {
            display: flex ;
            justify-content: center ;
        }

        [data-testid="stSelectbox"] {
            max-width: 500px;
            min-width: 200px;
        }
        
        .stDataFrameGlideDataEditor,
        [data-testid="stDataFrameResizable"] {
            border-radius:20px !important;
        }
        
        [data-testid="stMainBlockContainer"] > div > div > div > div:nth-child(4) > div:nth-child(2) > div {
            background-color: transparent !important;
            box-shadow: none !important;
        }
        
        /* Ô nhập Text_input */
        [data-baseweb="select"],
        [data-baseweb="select"] > div
        {
            background-color: white; /* Màu nền */
            border-radius: 50px;
            color: #333; /* Màu chữ xám đậm */
        }
        /* Ô nhập Text_input */
        [data-baseweb="select"] > div > div
        {
            padding: 8px 12px;
        }
        /* Khi nhấn vào hộp nhập liệu, đổi viền ngoài thành đen */
        [data-baseweb="select"]:focus-within {
            border-color: #999999 !important;
            background-color: white; /* Màu nền */
            color: #333; /* Màu chữ xám đậm */
        } 
        
        </style>    
        """,
        unsafe_allow_html=True,
    )
    