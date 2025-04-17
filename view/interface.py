import streamlit as st
import pandas as pd

from view.dashboard import setup_dashboard
from view.model import setup_model

from controller.data_controller import get_thong_tin_cong_ty, get_chi_so_cong_ty

# --- Giao diện Streamlit ---
def setup_page():
    # Cấu hình trang
    st.set_page_config(
        page_title="Dự đoán Rủi ro Kiệt quệ kinh tế",   # Tiêu đề hiển thị trên tab trình duyệt
        page_icon="https://res.cloudinary.com/day4wv1aw/image/upload/v1744197683/logo_truong_oxnwak.png", # Icon trên tab
        layout="wide", # Giao diện rộng
        initial_sidebar_state="auto" # ("auto", "expanded", or "collapsed")
    )

# --- Sidebar ---
def setup_sidebar():
    # Thêm CSS tùy chỉnh để căn giữa tiêu đề trong sidebar
    st.markdown(
        """
        <style>
            /* Căn giữa tiêu đề trong sidebar */
            [data-testid="stHeading"] {
                text-align: center;
            }
            
            /* Xóa khoảng trống trên cùng cho sidebar */
            [data-testid="stSidebarHeader"] {
                height: 50px;  /* Giảm chiều cao */
                padding: 20px;  /* Xóa padding để thu gọn hơn */
            }
        </style>
        """,
        unsafe_allow_html=True
    )
    st.sidebar.subheader('DỰ BÁO KIỆT QUỆ TÀI CHÍNH VÀ PHÂN TÍCH BÁO CÁO TÀI CHÍNH')
    
    st.sidebar.markdown(
        """
        <div style="display: flex; justify-content: center;">
            <img src="https://res.cloudinary.com/day4wv1aw/image/upload/v1744197683/logo_truong_oxnwak.png" 
            width="150">
        </div>
        """, 
        unsafe_allow_html=True
    )
    
    st.sidebar.markdown("""
        Chào mừng bạn đến với công cụ **Dự báo Kiệt quệ Tài chính**.
        Dự án này sử dụng các mô hình học máy để phân tích dữ liệu tài chính và đưa ra dự báo về khả năng phá sản của các công ty.

        **Cách sử dụng:**
        1.  Chọn tên công ty bạn muốn phân tích từ ô chọn bên dưới.
        2.  Xem các chỉ số tài chính và biểu đồ trực quan hóa.
        3.  (Tính năng tương lai) Nhận dự đoán về rủi ro phá sản.
    """)
    
def chon_cong_ty():
    df_thong_tin_cong_ty = get_thong_tin_cong_ty()
    # Phần chọn công ty trên trang chính
    
    # Tạo cột hiển thị: thêm trạng thái " - Có sẵn" hoặc " - Cần thu thập"
    df_thong_tin_cong_ty['Ma_Cty_display'] = df_thong_tin_cong_ty['Ma_Cty'] + df_thong_tin_cong_ty['co_san'].map(
        lambda x: ' - Có sẵn' if x else ' - Cần thu thập'
    )
    
    Ma_Cty_display = st.selectbox(
        "Vui lòng nhập tên công ty:",
        options=[""] + df_thong_tin_cong_ty['Ma_Cty_display'].tolist(), # Thêm lựa chọn rỗng ban đầu
        index=0, # Mặc định không chọn công ty nào
        help="Chọn một công ty từ danh sách để xem thông tin chi tiết."
    )
    
    parts = Ma_Cty_display.split(" - ")
    
    if len(parts) == 2 and parts[1] == 'Có sẵn':
        st.session_state.co_san = True
    else:
        st.session_state.co_san = False  
    
    if len(parts) == 2 and parts[0] != '':
        st.session_state.Ma_Cty = parts[0]
    
    else: 
        st.session_state.Ma_Cty = ''
        
def chon_nam():
    if st.session_state.get('co_san', False):
        df_cong_ty_theo_nam = get_chi_so_cong_ty(st.session_state.Ma_Cty)
        df_cong_ty_theo_nam['Nam'] = df_cong_ty_theo_nam['Nam'] + 1
    else:    
        df_cong_ty_theo_nam = pd.DataFrame([])
        df_cong_ty_theo_nam['Nam']  = list(range(2014, 2025)) # 2025 không bao gồm
    
    # Phần chọn công ty trên trang chính
    Nam_can_du_doan = st.selectbox(
        "Vui lòng nhập năm cần dự báo:",
        options=[""] + df_cong_ty_theo_nam['Nam'].tolist(), # Thêm lựa chọn rỗng ban đầu
        index=0, # Mặc định không chọn công ty nào
        help="Chọn một năm từ danh sách để dự báo."
    )
    if Nam_can_du_doan != '':
        st.session_state.Nam_hien_tai = Nam_can_du_doan - 1
        st.session_state.Nam_filter = df_cong_ty_theo_nam['Nam'].tolist()
    else: 
        st.session_state.Nam_hien_tai = ''
        st.session_state.Nam_filter = df_cong_ty_theo_nam['Nam'].tolist()

def setup_introduce():
    # Tạo tiêu đề trong sidebar
    st.header("DỰ BÁO KIỆT QUỆ TÀI CHÍNH")

    gap1, col, gap2 = st.columns([1, 1.5, 1])
    with col:   
        col1, col2 = st.columns([1, 1])
        with col1:    
            chon_cong_ty()
        with col2:
            chon_nam()


def setup_interface():
    
    setup_introduce()

    if st.session_state.get('Ma_Cty', '') != '' and st.session_state.get('Nam_hien_tai', '') != '':
        setup_model(st.session_state.Ma_Cty, 'XGB', st.session_state.Nam_hien_tai)
        
    if st.session_state.get('Ma_Cty', '') != '' and st.session_state.get('Nam_hien_tai', '') != '':
        setup_dashboard(st.session_state.Ma_Cty)
    
    