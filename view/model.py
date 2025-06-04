import streamlit as st
import pandas as pd

from controller.model_controller import du_doan_ket_qua
from controller.scrape_controller import tinh_chi_so

# --- Hàm dự đoán chính ---
def setup_model():
    """
    Dự đoán tình trạng công ty (Bị/Không bị) sử dụng mô hình đã chọn.
    Sử dụng dữ liệu đã merge từ database, web và file upload để tính toán chỉ số.
    """

    df_total = st.session_state.df_model
    nam_ht = st.session_state.Nam_hien_tai
    
    # Lấy dữ liệu theo loại mô hình
    model_type = st.session_state.get('model_type', 'XGB')
    if model_type == 'LSTM':
        # LSTM cần dữ liệu 3 năm trước đó cộng với năm hiện tại (tổng 4 năm)
        cac_nam_can = [nam_ht - i for i in range(3)] + [nam_ht]
    else:
        # Các mô hình khác chỉ cần dữ liệu năm hiện tại
        cac_nam_can = [nam_ht]
    df_du_lieu_du_doan = tinh_chi_so(df_total[df_total['Nam'].isin(cac_nam_can)])
    if not df_du_lieu_du_doan.empty:
        ket_qua = du_doan_ket_qua(df_du_lieu_du_doan)
        if ket_qua == 1:
            st.markdown(f"""
                <div style='padding: 20px; border-radius: 10px; background-color: #ffe6e6; color: #b30000; font-weight: bold; font-size: 24px; text-align: center; text-transform: uppercase;'>
                    ⚠️ CẢNH BÁO CÔNG TY {st.session_state.Ma_Cty} SẼ KIỆT QUỆ TÀI CHÍNH VÀO NĂM {st.session_state.Nam_hien_tai + 1}
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
                <div style='padding: 20px; border-radius: 10px; background-color: #e6ffe6; color: #006600; font-weight: bold; font-size: 24px; text-align: center; text-transform: uppercase;'>
                    ✅ CÔNG TY {st.session_state.Ma_Cty} SẼ KHÔNG KIỆT QUỆ TÀI CHÍNH VÀO NĂM {st.session_state.Nam_hien_tai + 1}
                </div>
            """, unsafe_allow_html=True)