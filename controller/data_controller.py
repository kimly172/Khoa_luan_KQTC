from model.database import get_list_dict_info, get_df_info

def get_thong_tin_cong_ty():
    df_thong_tin_cong_ty = get_df_info("SELECT * FROM thong_tin_cong_ty")
    
    return df_thong_tin_cong_ty
    
def get_tong_hop_du_lieu(Ma_Cty):
    df_chi_so_cong_ty = get_df_info(f"SELECT * FROM tong_hop_du_lieu WHERE Ma_Cty = '{Ma_Cty}'")
    
    return df_chi_so_cong_ty

def get_chi_so_cong_ty(Ma_Cty):
    df_chi_so_cong_ty = get_df_info(f"SELECT * FROM tinh_chi_so WHERE Ma_Cty = '{Ma_Cty}' ORDER BY Nam ASC")
    
    return df_chi_so_cong_ty

def get_chi_so_cong_ty_1_nam(Ma_Cty, Nam_hien_tai):
    df_chi_so_cong_ty = get_df_info(f"SELECT * FROM tinh_chi_so WHERE Ma_Cty = '{Ma_Cty}' AND Nam = {int(Nam_hien_tai)}")
    
    return df_chi_so_cong_ty

def get_chi_so_cong_ty_3_nam(Ma_Cty, Nam_hien_tai):
    df_chi_so_cong_ty = get_df_info(f"""
        SELECT * FROM tinh_chi_so 
        WHERE Ma_Cty = '{Ma_Cty}' 
        AND Nam BETWEEN {int(Nam_hien_tai) - 2} AND {int(Nam_hien_tai)}
    """)
    
    return df_chi_so_cong_ty