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
    if st.session_state.get('da_lay_du_lieu', False) and not st.session_state.get('df_tong_hop', pd.DataFrame()).empty:
        df_total = st.session_state.df_tong_hop
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
                st.success(f'Kết quả: Công ty {st.session_state.Ma_Cty} sẽ Kiệt quệ Tài chính vào {st.session_state.Nam_hien_tai + 1}')
            else:
                st.info(f'Kết quả: Công ty {st.session_state.Ma_Cty} sẽ không Kiệt quệ Tài chính vào {st.session_state.Nam_hien_tai + 1}')
        # else:
        #     st.warning(f"Không thể tính toán chỉ số để dự báo cho năm {nam_ht + 1}.")
    else:
        st.warning("Không có dữ liệu để dự báo. Vui lòng chọn công ty và đảm bảo dữ liệu đã được tải.")
