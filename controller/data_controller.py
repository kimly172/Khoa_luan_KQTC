from model.database import get_list_dict_info, get_df_info
import streamlit as st

def get_thong_tin_cong_ty():
    df_thong_tin_cong_ty = get_df_info("SELECT * FROM thong_tin_cong_ty")
    
    return df_thong_tin_cong_ty

def get_tong_hop_du_lieu():
    df_chi_so_cong_ty = get_df_info(f"SELECT * FROM tong_hop_du_lieu WHERE Ma_Cty = '{st.session_state.Ma_Cty}'")
    
    return df_chi_so_cong_ty

def get_chi_so_cong_ty():
    if st.session_state.model_type == 'LSTM':
        df_chi_so_cong_ty = get_df_info(f"""
            SELECT * FROM tinh_chi_so_cho_du_doan 
            WHERE Ma_Cty = '{st.session_state.Ma_Cty}' 
            AND Nam BETWEEN {int(st.session_state.Nam_hien_tai) - 2} AND {int(st.session_state.Nam_hien_tai)}
        """)
    else:
        df_chi_so_cong_ty = get_df_info(f"""
            SELECT * FROM tinh_chi_so_cho_du_doan
            WHERE Ma_Cty = '{st.session_state.Ma_Cty}'
            AND Nam = {int(st.session_state.Nam_hien_tai)}
        """)
    return df_chi_so_cong_ty
    