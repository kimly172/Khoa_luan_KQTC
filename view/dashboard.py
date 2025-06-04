import streamlit as st
import pandas as pd

from controller.data_controller import get_tong_hop_du_lieu
from controller.dashboard_controller import loc_theo_nam, tinh_chi_so, phan_tich_khoi

from view.dashboard_function import (
    ve_bieu_do, 
    ve_bieu_do_bar_group, 
    ve_bieu_do_bar_line, 
    ve_bieu_do_bar_simple, 
    ve_bieu_do_duong,
    ROA_bieu_do_Dupont,
    ROE_bieu_do_Dupont,
    vong_quay_va_ky_thanh_toan_binh_quan,
)

# --- Trang chính ---
def setup_dashboard():
    # Lấy dữ liệu
    if not st.session_state.get('df_dashboard', pd.DataFrame()).empty:
        df_total = st.session_state.df_dashboard

    st.header(f"PHÂN TÍCH BÁO CÁO TÀI CHÍNH")

    df_total = loc_theo_nam(df_total)

    # --- Sao chép và chuẩn bị dữ liệu ---
    df_cal = df_total.copy()
    # Đặt 'Năm' làm index nếu chưa phải
    if 'Nam' in df_cal.columns and df_cal.index.name != 'Nam':
        df_cal = df_cal.set_index('Nam')

    # Sắp xếp theo index (Năm)
    df_cal.sort_index(inplace=True)

    # # Danh sách các cột cần thiết từ dữ liệu gốc và tính toán
    # required_cols = ['TTS', 'TSNH', 'TVCKTDT', 'CKPTNH', 'HTK', 'TSCDHH', 'TSCD',
    #                  'NPT', 'NNH', 'NDH', 'VCSH', 'DTT', 'LNR', 'LNG', 'LNT',
    #                  'LCBTCP', 'DTRTHDKD', 'DTRTHDDT', 'DTRTHDTC', 'KH', 'GVHB',
    #                  'CPLV', 'PTNBNH'] # Thêm các cột cần cho tính toán

    # for col in required_cols:
    #     if col in df_cal.columns:
    #         try:
    #             # Xử lý chuỗi có dấu phẩy
    #             if isinstance(df_cal[col].iloc[0], str):
    #                  df_cal[col] = df_cal[col].str.replace(',', '', regex=False)
    #             df_cal[col] = pd.to_numeric(df_cal[col])
    #         except (ValueError, TypeError, AttributeError, IndexError):
    #             df_cal[col] = 0 # Gán 0 nếu lỗi
    #     else:
    #         df_cal[col] = 0 # Thêm cột 0 nếu thiếu

    # df_cal.fillna(0, inplace=True)

    # --- Thực hiện các tính toán từ bieudo.ipynb ---

    df_cal = tinh_chi_so(df_cal)

    # --- Vẽ biểu đồ theo bố cục ---

    # PHÂN TÍCH CƠ CẤU TÀI SẢN VÀ NGUỒN VỐN
    st.markdown("### PHÂN TÍCH KẾT QUẢ HOẠT ĐỘNG KINH DOANH")
    st.markdown("#### PHÂN TÍCH KHỐI")
    phan_tich_khoi('KQKD')
    
    st.markdown("#### THÔNG SỐ TĂNG TRƯỞNG")
    
        # CHỈ SỐ TĂNG TRƯỞNG
    #st.header("CHỈ SỐ TĂNG TRƯỞNG")
    col5, col6 = st.columns(2)
    with col5:
         ve_bieu_do_bar_line(df_cal, "Doanh thu và Tăng trưởng", 'DTT', 'Tăng trưởng doanh thu (%)',
                             'Doanh thu thuần', 'Tăng trưởng DT (%)', 'Doanh thu', 'Tăng trưởng', y1_suffix=' VNĐ')
    with col6:
         ve_bieu_do_bar_line(df_cal, "Lợi nhuận và Tăng trưởng", 'LNR', 'Tăng trưởng lợi nhuận (%)',
                             'Lợi nhuận sau thuế', 'Tăng trưởng LN (%)', 'Lợi nhuận', 'Tăng trưởng', y1_suffix=' VNĐ')
    
    st.markdown("#### THÔNG SỐ KHẢ NĂNG SINH LỜI VÀ THỊ TRƯỜNG")
    
    col1, col2 = st.columns([1,1]) # Chiếm tỷ lệ bao nhiêu
    with col1:
        ve_bieu_do_duong(
            df_cal, "Biên Lợi nhuận",
            ['Biên lợi nhuận gộp (%)', 'EBITDA (%)', 'EBIT (%)', 'Biên lợi nhuận ròng (%)'],
            hover_labels=['Biên LN gộp', 'EBITDA', 'EBIT', 'Biên LN ròng']
        )
    with col2:
        ve_bieu_do_duong(df_cal, "ROA và ROE", ['ROA (%)', 'ROE (%)'])
        
    col1, col2 = st.columns(2)
    with col1:
        ROA_bieu_do_Dupont(df_cal)
        
    with col2:
        ROE_bieu_do_Dupont(df_cal)
    with st.container():
        ve_bieu_do_bar_simple(df_cal, "Lãi cơ bản trên 1 cổ phiếu (EPS)", "LCBTCP", y_format=',.0f', y_suffix=' VNĐ')
    
    
    st.markdown("### PHÂN TÍCH BẢNG CÂN ĐỐI KẾ TOÁN")
    st.markdown("#### PHÂN TÍCH KHỐI")
    phan_tich_khoi('CDKT')
    
    st.markdown("#### PHÂN TÍCH CƠ CẤU TÀI SẢN VÀ NGUỒN VỐN")
    
    st.markdown("##### Cơ cấu Tài sản")
    
    with st.container():
        ve_bieu_do(df_cal, "Cơ cấu Tài sản", ["TSNH", "TSDH"])
    
    col1, col2 = st.columns(2)
    with col1:
        ve_bieu_do(df_cal, "Cơ cấu Tài sản ngắn hạn", ["TVCKTDT", "CKPTNH", "HTK"])
    with col2:
        ve_bieu_do(df_cal, "Cơ cấu Tài sản dài hạn", ["TSCDHH", "TSCD"])
        
        
    st.markdown("##### Cơ cấu Nguồn vốn")
    
    with st.container():
        ve_bieu_do(df_cal, "Cơ cấu Nguồn vốn", ["NPT", "VCSH"])

    col1, col2 = st.columns(2)
    with col1:
        ve_bieu_do(df_cal, "Cơ cấu Nợ phải trả", ["NNH", "NDH"])
    with col2:
        ve_bieu_do(df_cal, "Cơ cấu Vốn chủ sở hữu", ["VCSH"])

    # THÔNG SỐ KHẢ NĂNG SINH LỜI
    st.markdown("#### PHÂN TÍCH THÔNG SỐ HOẠT ĐỘNG")

    # Thay thế vong_quay_tai_san bằng ve_bieu_do_duong
    with st.container():
        ve_bieu_do_duong(
            df_cal, "Vòng quay tài sản",
            ['Vong_quay_tai_san', 'Vong_quay_TSCD'],
            hover_labels=['Vòng quay tổng tài sản', 'Vòng quay tài sản cố định'],
            y_format='.2f', y_suffix=' lần'
        ) # Sử dụng format và suffix mới

    col1, col2 = st.columns(2)
    with col1:
        ve_bieu_do_bar_line(
            df_cal, "Vòng quay và Kỳ thu tiền BQ", 'Ky_thu_tien_bq', 'Vong_quay_khoan_phai_thu',
            'Kỳ thu tiền BQ (ngày)', 'Vòng quay KPT (lần)', 'Kỳ thu tiền', 'Vòng quay KPT', 
            y1_format='.1f', y1_suffix=' ngày', y2_format='.2f', y2_suffix=' lần'
        )
    with col2:
        ve_bieu_do_bar_line(
            df_cal, "Vòng quay và Chu kỳ HTK", 'Chu_ky_chuyen_hoa_HTK', 'Vong_quay_HTK',
            'Chu kỳ HTK (ngày)', 'Vòng quay HTK (lần)', 'Chu kỳ HTK', 'Vòng quay HTK', 
            y1_format='.1f', y1_suffix=' ngày', y2_format='.2f', y2_suffix=' lần'
        )

    # THÔNG SỐ KHẢ NĂNG THANH TOÁN
    st.markdown("#### THÔNG SỐ KHẢ NĂNG THANH TOÁN")
    
    col1, col2 = st.columns(2)
    with col1:    
        ve_bieu_do_duong(
            df_cal, "Khả năng thanh toán hiện thời & nhanh",
            ["Khả năng thanh toán hiện thời", "Khả năng thanh toán nhanh"],
            hover_labels=["Khả năng thanh toán hiện thời", "Khả năng thanh toán nhanh"], # Thêm hover_labels cho rõ ràng
            y_format='.2f', y_suffix=' lần'
        ) # Sử dụng format và suffix mới
    with col2:
        # Thay thế kha_nang_chi_tra_bang_tien bằng ve_bieu_do_bar_simple
        ve_bieu_do_bar_simple(
            df_cal, "Khả năng chi trả bằng tiền",
            'Khả năng chi trả bằng tiền',
            name="Khả năng chi trả bằng tiền", # Giữ name cũ nếu muốn
            hover="Khả năng chi trả bằng tiền", # Giữ hover cũ nếu muốn
            y_format='.2f', y_suffix=' lần'
        ) # Sử dụng format và suffix mới, đơn vị là "lần"

    col1, col2 = st.columns(2)
    with col1:   
        vong_quay_va_ky_thanh_toan_binh_quan(df_cal)
    with col2:          
        ve_bieu_do_bar_simple(df_cal, "Chu kỳ chuyển hóa thành tiền", 'Chu kỳ chuyển hóa thành tiền', y_format='.1f', y_suffix=' ngày')


    # THÔNG SỐ NỢ
    st.markdown("#### THÔNG SỐ NỢ")
    
    with st.container():
        ve_bieu_do_bar_group(
            df_cal, "Tỷ lệ Nợ/TTS và Nợ/VCSH",
            ['Thông số nợ trên tài sản', 'Thông số nợ trên vốn chủ sở hữu'],
            names=['Nợ/TTS', 'Nợ/VCSH'], y_format='.2f', y_suffix=' lần'
        )

    col1, col2 = st.columns(2)
    with col1:
        ve_bieu_do_bar_group(df_cal, "Tỷ lệ Nợ dài hạn",
                             ['Thông số nợ dài hạn', 'Nợ dài hạn trên vốn chủ sở hữu'],
                             names=['NDH/(NDH+VCSH)', 'NDH/VCSH'], y_format='.2f', y_suffix=' lần')
    with col2:
        ve_bieu_do_bar_simple(df_cal, "Số lần đảm bảo lãi vay (LNT/CPLV)", 'Số lần đảm bảo lãi vay', y_format='.2f', y_suffix=' lần')

    # PHÂN TÍCH DÒNG TIỀN
    st.markdown("### PHÂN TÍCH LƯU CHUYỂN TIỀN TỆ")
    
    # ve_bieu_do(df_cal, "Phân tích Dòng tiền", ["DTRTHDKD", "DTRTHDDT", "DTRTHDTC"]) # Dùng biểu đồ cơ cấu gốc
    
    col1, col2 = st.columns(2)
    with col1:
        ve_bieu_do_bar_simple(df_cal, "Dòng tiền từ HĐ Tài chính", "DTRTHDTC", y_format=',.0f', y_suffix=' VNĐ')

    with col2:         
        ve_bieu_do_bar_simple(df_cal, "Dòng tiền từ HĐ Đầu tư", "DTRTHDDT", y_format=',.0f', y_suffix=' VNĐ')
    
    with st.container():
        ve_bieu_do_bar_simple(df_cal, "Dòng tiền từ HĐ Kinh doanh", "DTRTHDKD", y_format=',.0f', y_suffix=' VNĐ')
