import streamlit as st
import pandas as pd

from view.dashboard import setup_dashboard
from view.model import setup_model

from controller.data_controller import get_thong_tin_cong_ty, get_tong_hop_du_lieu
from controller.scrape_controller import crawl_tong_hop_du_lieu_tat_ca_cho_dashboard
# --- Giao diện Streamlit ---
def setup_page():
    # Cấu hình trang
    st.set_page_config(
        page_title="Dự báo Kiệt quệ Tài chính",   # Tiêu đề hiển thị trên tab trình duyệt
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
    # Khởi tạo biến session nếu chưa có
    if 'da_lay_du_lieu' not in st.session_state:
        st.session_state.da_lay_du_lieu = False
    if 'Ma_Cty' not in st.session_state:
        st.session_state.Ma_Cty = ''
    if 'co_san_Cty' not in st.session_state:
        st.session_state.co_san_Cty = True
        
    df_thong_tin_cong_ty = get_thong_tin_cong_ty()
    
    # Tạo cột hiển thị
    df_thong_tin_cong_ty['Ma_Cty_display'] = df_thong_tin_cong_ty['Ma_Cty'] + df_thong_tin_cong_ty['co_san_Cty'].map(
        lambda x: ' - Có sẵn' if x else ' - Cần thu thập'
    )
    
    # Tạo khóa duy nhất cho selectbox để tránh trùng lặp
    Ma_Cty_display = st.selectbox(
        "Vui lòng nhập tên công ty:",
        options=[""] + df_thong_tin_cong_ty['Ma_Cty_display'].tolist(),
        index=0,
        help="Chọn một công ty từ danh sách để xem thông tin chi tiết.",
        key="ma_cty_selectbox"
    )
    
    # Chỉ xử lý khi có công ty được chọn
    if Ma_Cty_display:
        parts = Ma_Cty_display.split(" - ")
        ma_cty_moi = ''
        co_san_cty_moi = True

        if len(parts) == 2:
            ma_cty_moi = parts[0]
            co_san_cty_moi = parts[1] == 'Có sẵn'
                
        # Cập nhật thông tin công ty
        if ma_cty_moi and (ma_cty_moi != st.session_state.get('Ma_Cty', '')):
            st.session_state.Ma_Cty = ma_cty_moi
            st.session_state.co_san_Cty = co_san_cty_moi
            st.session_state.da_lay_du_lieu = False
            
def chon_nam():
    if st.session_state.get('da_lay_du_lieu', False) and not st.session_state.get('df_tong_hop', pd.DataFrame()).empty:
        df_cong_ty = st.session_state.df_tong_hop 
        list_cong_ty_theo_nam = df_cong_ty['Nam'].tolist()
        print(list_cong_ty_theo_nam)
        danh_sach_nam = list(range(2013, 2025))
        nam_hien_thi = []
        for nam in danh_sach_nam:
            if nam in list_cong_ty_theo_nam:
                if st.session_state.da_cao_du_lieu:
                    nam_hien_thi.append(f"{nam + 1} - Đã thu thập") 
                else:    
                    nam_hien_thi.append(f"{nam + 1} - Có sẵn") 
            else:
                if st.session_state.da_cao_du_lieu:
                    nam_hien_thi.append(f"{nam + 1} - Không có") 
                else:
                    nam_hien_thi.append(f"{nam + 1} - Cần thu thập") 

        # Phần chọn công ty trên trang chính
        Nam_can_du_doan = st.selectbox(
            "Vui lòng nhập năm cần dự báo:",
            options=[""] + nam_hien_thi, # Thêm lựa chọn rỗng ban đầu
            index=0, # Mặc định không chọn công ty nào
            help="Chọn một năm từ danh sách để dự báo."
        )
        
        parts = Nam_can_du_doan.split(" - ")
        
        # Không có dữ liệu nên cần thu thập
        if len(parts) == 2 and parts[1] == 'Cần thu thập':
            st.session_state.co_san_du_lieu_du_doan = False  
            
        # Đã thu thập nhưng không có 
        elif len(parts) == 2 and parts[1] == 'Không có':
            st.session_state.co_san_du_lieu_du_doan = False 
            
        # Có sẵn dữ liệu nên không cần thu thập
        elif len(parts) == 2 and parts[1] == 'Có sẵn':
            st.session_state.co_san_du_lieu_du_doan = True  
            
        # Không có dữ liệu nên đã thu thập 
        elif len(parts) == 2 and parts[1] == 'Đã thu thập':
             st.session_state.co_san_du_lieu_du_doan = True     
            
        if len(parts) == 2 and parts[0] != '':
            st.session_state.Nam_hien_tai = int(parts[0]) - 1
        else: 
            st.session_state.Nam_hien_tai = ''
            
    else:
        # Phần chọn công ty trên trang chính
        Nam_can_du_doan = st.selectbox(
            "Vui lòng nhập năm cần dự báo:",
            options=[""], # Thêm lựa chọn rỗng ban đầu
            index=0, # Mặc định không chọn công ty nào
            help="Chọn một năm từ danh sách để dự báo.",
            disabled= True
        )

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
    
    # Kiểm tra mã công ty có tồn tại và chưa lấy dữ liệu
    if not st.session_state.get('da_lay_du_lieu', False) and st.session_state.get('Ma_Cty', ''):
        if st.session_state.get('co_san_Cty', False):
            with st.spinner(f'Đang lấy dữ liệu từ Database cho công ty {st.session_state.Ma_Cty}'):
                st.session_state.df_tong_hop = get_tong_hop_du_lieu()
                st.session_state.da_lay_du_lieu = True
                st.session_state.da_cao_du_lieu = False
                st.rerun()
        else:    
            with st.spinner(f'Đang thu thập dữ liệu từ CafeF cho công ty {st.session_state.Ma_Cty}'):
                df_tong_hop = crawl_tong_hop_du_lieu_tat_ca_cho_dashboard()
                
                if df_tong_hop is None:    
                    st.session_state.df_tong_hop = pd.DataFrame([])
                    st.warning(f'Không có dữ liệu của công ty {st.session_state.Ma_Cty} trên CafeF')
                else:
                    st.session_state.df_tong_hop = df_tong_hop
                    st.session_state.da_lay_du_lieu = True
                    st.session_state.da_cao_du_lieu = True
                    st.rerun()
                    
def setup_interface():
    
    setup_introduce()
    if 'model_type' not in st.session_state:
        st.session_state.model_type = 'XGB'

    if 'da_lay_du_lieu' not in st.session_state:
        st.session_state.da_lay_du_lieu = False
    if 'Ma_Cty' not in st.session_state:
        st.session_state.Ma_Cty = ''
    if 'co_san_Cty' not in st.session_state:
        st.session_state.co_san_Cty = True
    if 'df_tong_hop' not in st.session_state:
        st.session_state.df_tong_hop = pd.DataFrame()
    if 'da_cao_du_lieu' not in st.session_state:
        st.session_state.da_cao_du_lieu = False


    if (st.session_state.get('Ma_Cty', '') != '' 
        and st.session_state.get('Nam_hien_tai', '') != ''
        and not st.session_state.get('df_tong_hop', pd.DataFrame()).empty
    ):
        setup_model()
        
    if (st.session_state.get('Ma_Cty', '') != '' 
        and st.session_state.get('Nam_hien_tai', '') != '' 
        and not st.session_state.get('df_tong_hop', pd.DataFrame()).empty
    ):
        setup_dashboard()
    
    