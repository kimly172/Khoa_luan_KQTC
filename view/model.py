import streamlit as st
import pandas as pd

from controller.data_controller import get_chi_so_cong_ty_1_nam, get_chi_so_cong_ty_3_nam
from controller.model_controller import du_doan_ket_qua
from controller.scrape_controller import scrape_cafeF, gop_file, tinh_chi_so

# --- Hàm dự đoán chính ---
def setup_model(Ma_Cty, model_type, Nam_hien_tai):
    """
    Dự đoán tình trạng công ty (Bị/Không bị) sử dụng mô hình đã chọn.

    Args:
        Ma_Cty (str): Mã công ty cần dự đoán.
        model_type (str): Loại mô hình ('LSTM', 'MLP', 'RF', 'XGB').

    Returns:
        str: Kết quả dự đoán ("Bị", "Không bị", hoặc thông báo lỗi).
    """
    # print(f"Bắt đầu dự đoán cho {Ma_Cty} sử dụng mô hình {model_type}")
    if st.session_state.get('co_san', False):
        if model_type == 'LSTM':
            # 1. Lấy dữ liệu công ty
            df_company = get_chi_so_cong_ty_3_nam(Ma_Cty, Nam_hien_tai)
        
        else:
            df_company = get_chi_so_cong_ty_1_nam(Ma_Cty, Nam_hien_tai)
            
    else:
        all_reports_result = scrape_cafeF(Ma_Cty, Nam_hien_tai, model_type)
        if all_reports_result:
            df_total = gop_file(all_reports_result)
            df_company = tinh_chi_so(df_total)
        else: 
            df_company = pd.DataFrame([])
            
    if not df_company.empty:
        ket_qua = du_doan_ket_qua(model_type, df_company, Ma_Cty, Nam_hien_tai)
        if ket_qua == 1:
            st.success(f'Kết quả: Công ty {Ma_Cty} sẽ Kiệt quệ Tài chính vào {Nam_hien_tai + 1}')
        else:
            st.info(f'Kết quả: Công ty {Ma_Cty} sẽ không Kiệt quệ Tài chính vào {Nam_hien_tai + 1}')
    else:
        st.warning(f"Thông báo: Không có dữ liệu của báo cáo trên CafeF.")