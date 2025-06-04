import streamlit as st
import pandas as pd

from view.dashboard import setup_dashboard
from view.model import setup_model

from controller.data_controller import get_thong_tin_cong_ty, get_tong_hop_du_lieu
from controller.scrape_controller import gop_file
from controller.upload_controller import xu_ly_file_upload
# --- Giao diện Streamlit ---
def setup_page():
    # Cấu hình trang
    st.set_page_config(
        page_title="Dự báo Kiệt quệ Tài chính",  # Tiêu đề hiển thị trên tab trình duyệt
        page_icon="https://res.cloudinary.com/day4wv1aw/image/upload/c_fill,h_30,w_30,q_auto,f_auto/v1744197683/flic_chatbot/logo_truong_oxnwak.png", # Icon trên tab
        layout="wide", # Giao diện rộng
        initial_sidebar_state="auto" # ("auto", "expanded", or "collapsed")
    )

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
            <img src="https://res.cloudinary.com/day4wv1aw/image/upload/c_fill,h_300,w_300,q_auto,f_auto/v1744197683/flic_chatbot/logo_truong_oxnwak.png" 
            width="150">
        </div>
        """, 
        unsafe_allow_html=True
    )
    
    # --- THÊM PHẦN NÀY ĐỂ CHỌN TRANG ---
    page_options = ["Trang chính", "Giải thích Chỉ số Tài chính"]
    if 'selected_page' not in st.session_state:
        st.session_state.selected_page = page_options[0]  # Mặc định là Trang chính
    
    # Lựa chọn trang bằng radio button
    st.session_state.selected_page = st.sidebar.radio(
        "Điều hướng ứng dụng:", 
        page_options, 
        index=page_options.index(st.session_state.selected_page) # Giữ lựa chọn hiện tại
    )
    # --- KẾT THÚC PHẦN THÊM ---

    # Thông tin và hướng dẫn sử dụng chỉ hiển thị ở trang chính
    if st.session_state.selected_page == "Trang chính":
        st.sidebar.markdown("""
            Chào mừng bạn đến với công cụ **Dự báo Kiệt quệ Tài chính**.
            Dự án này sử dụng các mô hình học máy để phân tích dữ liệu tài chính và đưa ra dự báo về khả năng Kiệt quệ Tài chính của các công ty.

            **Cách sử dụng:**
            1.  Chọn công ty cần phân tích để hệ thống tự động lấy dữ liệu từ nguồn có sẵn.
            2.  Bạn có thể tải lên báo cáo tài chính (CDKT, KQKD, LCTT) để bổ sung.
            3.  Hệ thống sẽ phân tích các chỉ số tài chính tổng quan và đưa ra dự báo về nguy cơ kiệt quệ Tài chính.
        """)
            
def chon_cong_ty():
    # Khởi tạo biến session nếu chưa có
    if 'Ma_Cty' not in st.session_state:
        st.session_state.Ma_Cty = ''
        
    df_thong_tin_cong_ty = get_thong_tin_cong_ty()
    
    # Tạo cột hiển thị
    df_thong_tin_cong_ty = df_thong_tin_cong_ty[df_thong_tin_cong_ty['co_san_Cty'] == True]
    
    # Tạo khóa duy nhất cho selectbox để tránh trùng lặp
    Ma_Cty_display = st.selectbox(
        "Vui lòng nhập tên công ty:",
        options=[""] + df_thong_tin_cong_ty['Ma_Cty'].tolist(),
        index=0,
        help="Chọn một công ty từ danh sách để xem thông tin chi tiết.",
        key="ma_cty_selectbox"
    )
    
    # Chỉ xử lý khi có công ty được chọn
    if Ma_Cty_display:
        ma_cty_moi = Ma_Cty_display
                
        # Cập nhật thông tin công ty
        if ma_cty_moi and (ma_cty_moi != st.session_state.get('Ma_Cty', '')):
            st.session_state.Ma_Cty = ma_cty_moi
            
            st.session_state.df_dashboard = pd.DataFrame([])
            st.session_state.df_model = pd.DataFrame([])
            
            st.session_state.co_san_du_lieu_du_doan = False

            st.rerun()
                    
def chon_nam():
    if st.session_state.get('Ma_Cty', ''):
        st.session_state.df_cong_ty = get_tong_hop_du_lieu()
        list_cong_ty_theo_nam = st.session_state.df_cong_ty['Nam'].tolist()

        danh_sach_nam = list(range(2013, 2025))
        model_type = st.session_state.get('model_type', 'XGB')
        nam_hien_thi = []
        for nam in danh_sach_nam:
            if model_type == 'LSTM':
                # LSTM cần 4 năm dữ liệu để tính chỉ số
                nam_can_kiem_tra = list(range(nam - 3, nam + 1))
            else:
                # Các mô hình khác cần 2 năm dữ liệu để tính chỉ số
                nam_can_kiem_tra = list(range(nam - 1, nam + 1))
            
            nam_thieu = [n for n in nam_can_kiem_tra if n not in list_cong_ty_theo_nam]
            if not nam_thieu:
                nam_hien_thi.append(f"{nam + 1}")
            else:
                nam_hien_thi.append(f"{nam + 1} - Không đủ dữ liệu")

        # Phần chọn năm trên trang chính
        Nam_can_du_doan = st.selectbox(
            "Vui lòng nhập năm cần dự báo:",
            options=[""] + nam_hien_thi, # Thêm lựa chọn rỗng ban đầu
            index=0, # Mặc định không chọn năm nào
            help="Chọn một năm từ danh sách để dự báo."
        )
        

        if Nam_can_du_doan:
            parts = Nam_can_du_doan.split(" - ")
            nam_du_bao = int(parts[0]) - 1
            st.session_state.Nam_hien_tai = nam_du_bao
            
            st.session_state.co_san_du_lieu_du_doan = True 
            
            st.session_state.df_dashboard = st.session_state.df_cong_ty
            st.session_state.df_model = st.session_state.df_cong_ty
            
        else:
            st.session_state.Nam_hien_tai = ''
            st.session_state.co_san_du_lieu_du_doan = False
            st.session_state.df_model = pd.DataFrame([])
            
    else:
        # Phần chọn năm trên trang chính
        Nam_can_du_doan = st.selectbox(
            "Vui lòng nhập năm cần dự báo:",
            options=[""], # Thêm lựa chọn rỗng ban đầu
            index=0, # Mặc định không chọn năm nào
            help="Chọn một năm từ danh sách để dự báo.",
            disabled=True
        )
        
def chon_nam_upload(df_upload):
    list_cong_ty_theo_nam = df_upload['Nam'].tolist()

    danh_sach_nam = list(range(2013, 2025))
    model_type = st.session_state.get('model_type', 'XGB')
    nam_hien_thi = []
    for nam in danh_sach_nam:
        if model_type == 'LSTM':
            # LSTM cần 4 năm dữ liệu để tính chỉ số
            nam_can_kiem_tra = list(range(nam - 3, nam + 1))
        else:
            # Các mô hình khác cần 2 năm dữ liệu để tính chỉ số
            nam_can_kiem_tra = list(range(nam - 1, nam + 1))
        
        nam_thieu = [n for n in nam_can_kiem_tra if n not in list_cong_ty_theo_nam]
        if not nam_thieu:
            nam_hien_thi.append(f"{nam + 1}")
        else:
            nam_hien_thi.append(f"{nam + 1} - Không đủ dữ liệu")

    # Phần chọn năm trên trang chính
    Nam_can_du_doan = st.selectbox(
        "Vui lòng nhập năm cần dự báo:",
        options=[""] + nam_hien_thi, # Thêm lựa chọn rỗng ban đầu
        index=0, # Mặc định không chọn năm nào
        help="Chọn một năm từ danh sách để dự báo."
    )
    
    if Nam_can_du_doan:
        parts = Nam_can_du_doan.split(" - ")
        nam_du_bao = int(parts[0]) - 1
        st.session_state.Nam_hien_tai = nam_du_bao
        
        st.session_state.co_san_du_lieu_du_doan = True 
        
        st.session_state.df_dashboard = df_upload
        st.session_state.df_model = df_upload
        
    else:
        st.session_state.Nam_hien_tai = ''
        st.session_state.co_san_du_lieu_du_doan = False
        st.session_state.df_model = pd.DataFrame([])

def upload_bao_cao():
    # st.markdown("Bạn phải upload đầy đủ các file báo cáo tài chính (CDKT, KQKD, LCTT) để hệ thống có thể xử lý dữ liệu.")
    
    gap1, col, gap2 = st.columns([1, 1.3, 1])
    with col:   
        # Tạo key động dựa trên Ma_Cty để làm mới widget khi thay đổi công ty
        cdkt_key = f"upload_cdkt_{st.session_state.get('Ma_Cty', 'default')}"
        kqkd_key = f"upload_kqkd_{st.session_state.get('Ma_Cty', 'default')}"
        lctt_key = f"upload_lctt_{st.session_state.get('Ma_Cty', 'default')}"
        
        # Ô upload cho CDKT
        uploaded_cdkt = st.file_uploader("Upload Bảng Cân Đối Kế Toán (CDKT)", type=["xlsx", "xls", "csv"], key=cdkt_key)
        if uploaded_cdkt is not None:
            st.session_state.uploaded_cdkt = uploaded_cdkt
        else:
            st.session_state.uploaded_cdkt = None
        
        # Ô upload cho KQKD
        uploaded_kqkd = st.file_uploader("Upload Báo Cáo Kết Quả Hoạt Động Kinh Doanh (KQKD)", type=["xlsx", "xls", "csv"], key=kqkd_key)
        if uploaded_kqkd is not None:
            st.session_state.uploaded_kqkd = uploaded_kqkd
        else:
            st.session_state.uploaded_kqkd = None
        
        # Ô upload cho LCTT
        uploaded_lctt = st.file_uploader("Upload Báo Cáo Lưu Chuyển Tiền Tệ (LCTT)", type=["xlsx", "xls", "csv"], key=lctt_key)
        if uploaded_lctt is not None:
            st.session_state.uploaded_lctt = uploaded_lctt
        else:
            st.session_state.uploaded_lctt = None
    
    # st.markdown("**Lưu ý:** Hệ thống yêu cầu upload đầy đủ cả 3 file báo cáo tài chính để tiếp tục xử lý.")
    
    # Nếu thiếu bất kỳ file upload nào, thông báo lỗi và trả về None
    if (st.session_state.uploaded_cdkt is not None 
        and st.session_state.uploaded_kqkd is not None 
        and st.session_state.uploaded_lctt is not None):
        
        # Xử lý từng file upload
        df_cdkt = xu_ly_file_upload(st.session_state.uploaded_cdkt, "CDKT")
        st.session_state.df_cdkt = df_cdkt
        
        df_kqkd = xu_ly_file_upload(st.session_state.uploaded_kqkd, "KQKD")
        st.session_state.df_kqkd = df_kqkd
        
        df_lctt = xu_ly_file_upload(st.session_state.uploaded_lctt, "LCTT")
        st.session_state.df_lctt = df_lctt

        df_upload = gop_file(df_cdkt, df_kqkd, df_lctt)
        
        if not df_upload.empty:
            st.success("Dữ liệu đã được upload và cập nhật thành công! Vui lòng chọn năm cần dự báo từ danh sách để tiếp tục phân tích.")
            chon_nam_upload(df_upload)

def Du_lieu_co_san():
    gap1, col, gap2 = st.columns([1, 1.5, 1])
    with col:   
        col1, col2 = st.columns([1, 1])
        with col1:    
            chon_cong_ty()
        with col2:
            chon_nam()
         
def setup_interface():
    if 'model_type' not in st.session_state:
        st.session_state.model_type = 'XGB'

    if 'Ma_Cty' not in st.session_state:
        st.session_state.Ma_Cty = ''
    
    # Tạo tiêu đề
    st.header("DỰ BÁO KIỆT QUỆ TÀI CHÍNH")
    
    gap1, col, gap2 = st.columns([1, 1.5, 1])
    
    with col:   
        col1, col2 = st.columns([1, 1])
        
        with col1:    
            if st.button(label='Dữ liệu có sẵn'):
                # Xóa toàn bộ session_state
                st.session_state.clear()                
                
                st.session_state.nguon_du_lieu = 'Dữ liệu có sẵn'

                # st.session_state.df_dashboard = pd.DataFrame([])
                # st.session_state.df_model = pd.DataFrame([])
                # st.session_state.co_san_du_lieu_du_doan = False
                
                # # # Xóa các file upload 
                # st.session_state.uploaded_cdkt = None
                # st.session_state.uploaded_kqkd = None
                # st.session_state.uploaded_lctt = None

                st.rerun()
                
        with col2:
            if st.button(label='Upload báo cáo'):
                # Xóa toàn bộ session_state
                st.session_state.clear()                
                
                st.session_state.nguon_du_lieu = 'Upload báo cáo'

                # st.session_state.df_dashboard = pd.DataFrame([])
                # st.session_state.df_model = pd.DataFrame([])
                # st.session_state.co_san_du_lieu_du_doan = False
                
                # # # Xóa các file upload 
                # st.session_state.uploaded_cdkt = None
                # st.session_state.uploaded_kqkd = None
                # st.session_state.uploaded_lctt = None
                
                st.rerun()
    
    if st.session_state.get('nguon_du_lieu', '') == 'Dữ liệu có sẵn':
        Du_lieu_co_san()
        
    elif st.session_state.get('nguon_du_lieu', '') == 'Upload báo cáo':
        upload_bao_cao()   

    if st.session_state.get('co_san_du_lieu_du_doan', False):
        list_cong_ty_theo_nam = st.session_state.df_model['Nam'].tolist()
        nam_du_bao = int(st.session_state.Nam_hien_tai) 
        model_type = st.session_state.get('model_type', 'XGB')
    
        if model_type == 'LSTM':
            nam_can_kiem_tra = list(range(nam_du_bao - 3, nam_du_bao + 1))
            
        else:
            nam_can_kiem_tra = list(range(nam_du_bao - 1, nam_du_bao + 1))
            
        nam_thieu = [n for n in nam_can_kiem_tra if n not in list_cong_ty_theo_nam]
        if nam_thieu:
            st.warning(f"Không đủ dữ liệu để dự báo cho năm {nam_du_bao + 1}. Thiếu dữ liệu cho năm: {', '.join(map(str, nam_thieu))}.") 
    
    if not st.session_state.get('df_model', pd.DataFrame([])).empty:    
        setup_model()
        
    if not st.session_state.get('df_dashboard', pd.DataFrame([])).empty:        
        setup_dashboard()




