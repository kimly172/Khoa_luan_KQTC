import streamlit as st
import pandas as pd

from controller.data_controller import get_chi_so_cong_ty
from controller.model_controller import du_doan_ket_qua
from controller.scrape_controller import tinh_chi_so, crawl_tong_hop_du_lieu_2_hoac_4_nam_cho_dashboard

# --- Hàm dự đoán chính ---
def setup_model():
    """
    Dự đoán tình trạng công ty (Bị/Không bị) sử dụng mô hình đã chọn.

    Args:
        Ma_Cty (str): Mã công ty cần dự đoán.
        model_type (str): Loại mô hình ('LSTM', 'MLP', 'RF', 'XGB').

    Returns:
        str: Kết quả dự đoán ("Bị", "Không bị", hoặc thông báo lỗi).
    """
    st.session_state.Nam_hien_tai
    # print(f"Bắt đầu dự đoán cho {Ma_Cty} sử dụng mô hình {model_type}")
    if st.session_state.get('co_san_du_lieu_du_doan', False):
        
        # Không có sẵn dữ liệu và phải thu thập vì dữ liệu có sẵn thiếu năm
        if st.session_state.get('da_cao_du_lieu', False):
            df_total = st.session_state.df_tong_hop
            
            if st.session_state.model_type == 'LSTM':
                nam_ht = st.session_state.Nam_hien_tai
                cac_nam_can = [nam_ht - i for i in range(4)]  # [n, n-1, n-2, n-3]
                if all(nam in df_total['Nam'].tolist() for nam in cac_nam_can):
                    df_du_lieu_du_doan = tinh_chi_so(df_total[df_total['Nam'].isin(cac_nam_can)])
            else:
                nam_ht = st.session_state.Nam_hien_tai
                cac_nam_can = [nam_ht, nam_ht - 1]
                df_du_lieu_du_doan = tinh_chi_so(df_total[df_total['Nam'].isin(cac_nam_can)])
                
        # Đã có sẵn dữ liệu nên lấy trong database
        else:
            df_du_lieu_du_doan = get_chi_so_cong_ty()
            
    else:
        # Dữ liệu đã cào nhưng không có
        if st.session_state.get('da_cao_du_lieu', False):
            df_du_lieu_du_doan = pd.DataFrame([])
        
        # Dữ liệu chưa cào và chưa có dữ liệu vì dữ liệu trong database không có   
        else:
            with st.spinner(f'Đang thu thập dữ liệu từ CafeF cho công ty {st.session_state.Ma_Cty}'):
                df_total = crawl_tong_hop_du_lieu_2_hoac_4_nam_cho_dashboard()
                if df_total is None:
                    df_du_lieu_du_doan = pd.DataFrame([])
                else:   
                    df_du_lieu_du_doan = tinh_chi_so(df_total)
    
    so_nam = 4 if st.session_state.model_type == "LSTM" else 2
    danh_sach_nam = [str(n) for n in sorted([st.session_state.Nam_hien_tai - i for i in range(so_nam)])]
    
    if not df_du_lieu_du_doan.empty:
        ket_qua = du_doan_ket_qua(df_du_lieu_du_doan)
        if ket_qua == 1:
            st.success(f'Kết quả: Công ty {st.session_state.Ma_Cty} sẽ Kiệt quệ Tài chính vào {st.session_state.Nam_hien_tai + 1}')
        else:
            st.info(f'Kết quả: Công ty {st.session_state.Ma_Cty} sẽ không Kiệt quệ Tài chính vào {st.session_state.Nam_hien_tai + 1}')
    else:
        st.warning(f"Thông báo: Dữ liệu báo cáo của các năm {', '.join(danh_sach_nam)} trên CafeF.")