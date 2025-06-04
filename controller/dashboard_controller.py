import streamlit as st
import numpy as np
import pandas as pd
from unidecode import unidecode
import re

def normalize_text(text):
    # Kiểm tra nếu text là kiểu chuỗi
    if isinstance(text, str):
        text = text.strip()
        # Giữ lại ký tự chữ cái tiếng Việt, số và khoảng trắng
        text = re.sub(r'[^\w\s]', '', text, flags=re.UNICODE)
        # \w trong Unicode sẽ bao gồm các ký tự chữ cái có dấu
        # Hoặc cụ thể hơn:
        # text = re.sub(r'[^a-zA-Z0-9ÀÁÂÃÈÉÊÌÍÒÓÔÕÙÚĂĐĨŨƠàáâãèéêìíòóôõùúăđĩũơƯĂẠẢẤẦẨẪẬẮẰẲẴẶẸẺẼỀỀỂưăạảấầẩẫậắằẳẵặẹẻẽềềểỄỆỈỊỌỎỐỒỔỖỘỚỜỞỠỢỤỦỨỪễệỉịọỏốồổỗộớờởỡợụủứừ\s]', '', text)
    return text

def loc_theo_nam(df_total):
    # Lấy danh sách năm duy nhất từ df_total và sắp xếp
    years = sorted(df_total['Nam'].unique())

    gap1, col, gap2 = st.columns([1, 1.5, 1])
    with col:  
        col1, col2 = st.columns(2)
        with col1:
            start_year = st.selectbox("Từ năm:", options=years, index=0)
        with col2:
            end_year = st.selectbox("Đến năm:", options=years, index=len(years) - 1)

    # Kiểm tra điều kiện để lọc
    if start_year > end_year:
        st.warning("Năm bắt đầu phải nhỏ hơn hoặc bằng năm kết thúc.")
        return df_total.iloc[0:0]  # Trả về DataFrame rỗng
    else:
        return df_total[(df_total['Nam'] >= start_year) & (df_total['Nam'] <= end_year)]
        
def tinh_chi_so(df_cal):
        # Giá trị bình quân (xử lý NaN năm đầu)
    for col in ['TTS', 'VCSH', 'TSCD', 'CKPTNH', 'HTK', 'NNH', 'PTNBNH']:
        avg_col = f'{col}_binh_quan'
        df_cal[avg_col] = (df_cal[col] + df_cal[col].shift(1)) / 2
        df_cal[avg_col] = df_cal[avg_col].fillna(df_cal[col]) # Năm đầu dùng chính giá trị đó

    # TSDH
    df_cal['TSDH'] = df_cal['TTS'] - df_cal['TSNH']

    # Tăng trưởng
    df_cal['Tăng trưởng doanh thu (%)'] = df_cal['DTT'].pct_change() * 100
    df_cal['Tăng trưởng lợi nhuận (%)'] = df_cal['LNR'].pct_change() * 100

    # Biên lợi nhuận
    df_cal['Biên lợi nhuận gộp (%)'] = (df_cal['LNG'] * 100 / df_cal['DTT']).replace([np.inf, -np.inf], 0).fillna(0)
    df_cal['Biên lợi nhuận ròng (%)'] = (df_cal['LNR'] * 100 / df_cal['DTT']).replace([np.inf, -np.inf], 0).fillna(0)
    df_cal['EBIT (%)'] = (df_cal['LNT'] * 100 / df_cal['DTT']).replace([np.inf, -np.inf], 0).fillna(0)
    df_cal['EBITDA (%)'] = ((df_cal['LNT'] + df_cal['KH']) * 100 / df_cal['DTT']).replace([np.inf, -np.inf], 0).fillna(0)

    # ROA, ROE
    df_cal['ROA (%)'] = (df_cal['LNR'] * 100 / df_cal['TTS_binh_quan']).replace([np.inf, -np.inf], 0).fillna(0)
    df_cal['ROE (%)'] = (df_cal['LNR'] * 100 / df_cal['VCSH_binh_quan']).replace([np.inf, -np.inf], 0).fillna(0)

    # Dupont
    df_cal['Vong_quay_tai_san'] = (df_cal['DTT'] / df_cal['TTS_binh_quan']).replace([np.inf, -np.inf], 0).fillna(0)
    # Biên lợi nhuận ròng (%) đã tính ở trên
    df_cal["Đòn bẩy tài chính"] = (df_cal['TTS_binh_quan'] / df_cal['VCSH_binh_quan']).replace([np.inf, -np.inf], 0).fillna(0)

    # Vòng quay TSCD
    df_cal['Vong_quay_TSCD'] = (df_cal['DTT'] / df_cal['TSCD_binh_quan']).replace([np.inf, -np.inf], 0).fillna(0)

    # Vòng quay khoản phải thu
    df_cal['Vong_quay_khoan_phai_thu'] = (df_cal['DTT'] / df_cal['CKPTNH_binh_quan']).replace([np.inf, -np.inf], 0).fillna(0) # Sửa lại mẫu số
    df_cal['Ky_thu_tien_bq'] = (365 / df_cal['Vong_quay_khoan_phai_thu']).replace([np.inf, -np.inf], 0).fillna(0)

    # Vòng quay HTK
    df_cal['Vong_quay_HTK'] = (df_cal['GVHB'] / df_cal['HTK_binh_quan']).replace([np.inf, -np.inf], 0).fillna(0)
    df_cal['Chu_ky_chuyen_hoa_HTK'] = (365 / df_cal['Vong_quay_HTK']).replace([np.inf, -np.inf], 0).fillna(0)

    # Khả năng thanh toán
    df_cal["Khả năng thanh toán hiện thời"] = (df_cal['TSNH'] / df_cal['NNH']).replace([np.inf, -np.inf], 0).fillna(0)
    df_cal["Khả năng thanh toán nhanh"] = ((df_cal['TSNH'] - df_cal['HTK']) / df_cal["NNH"]).replace([np.inf, -np.inf], 0).fillna(0)
    df_cal["Khả năng chi trả bằng tiền"] = (df_cal['DTRTHDKD'] / df_cal["NNH_binh_quan"]).replace([np.inf, -np.inf], 0).fillna(0)

    # Vòng quay khoản phải trả
    htk_change = df_cal['HTK'] - df_cal['HTK'].shift(1)
    htk_change.fillna(df_cal['HTK'], inplace=True) # Năm đầu coi như tăng bằng chính nó
    df_cal["Vòng quay phải trả người bán"] = ((df_cal['GVHB'] + htk_change) / df_cal['PTNBNH_binh_quan']).replace([np.inf, -np.inf], 0).fillna(0)
    df_cal["Kỳ thanh toán bình quân"] = (365 / df_cal["Vòng quay phải trả người bán"]).replace([np.inf, -np.inf], 0).fillna(0)

    # Chu kỳ tiền mặt
    df_cal['Chu kỳ chuyển hóa thành tiền'] = df_cal['Ky_thu_tien_bq'] + df_cal['Chu_ky_chuyen_hoa_HTK'] - df_cal["Kỳ thanh toán bình quân"]

    # Thông số nợ
    df_cal['Thông số nợ trên tài sản'] = (df_cal['NPT'] / df_cal['TTS']).replace([np.inf, -np.inf], 0).fillna(0)
    df_cal['Thông số nợ trên vốn chủ sở hữu'] = (df_cal['NPT'] / df_cal['VCSH']).replace([np.inf, -np.inf], 0).fillna(0)
    nen_mau_ndh = df_cal['NDH'] + df_cal['VCSH']
    df_cal['Thông số nợ dài hạn'] = (df_cal['NDH'] / nen_mau_ndh).replace([np.inf, -np.inf], 0).fillna(0)
    df_cal['Nợ dài hạn trên vốn chủ sở hữu'] = (df_cal['NDH'] / df_cal['VCSH']).replace([np.inf, -np.inf], 0).fillna(0)
    df_cal['Số lần đảm bảo lãi vay'] = (df_cal['LNT'] / df_cal['CPLV']).replace([np.inf, -np.inf], 0).fillna(0) # Giả sử LNT là EBIT
    
    return df_cal

def phan_tich_khoi(ten_bao_cao):
    if ten_bao_cao == 'CDKT':
        ten_chi_so = 'TỔNG CỘNG TÀI SẢN'
        ten_hien_thi = 'Tổng cộng Tài sản'
        if not st.session_state.get('df_cdkt', pd.DataFrame([])).empty:
            df_KQKD = st.session_state.df_cdkt
        else:
            df_KQKD = pd.read_excel(rf'data/Đúng/Tổng hợp/{st.session_state.Ma_Cty}_{ten_bao_cao}.xlsx')
        
    elif ten_bao_cao == 'KQKD':
        ten_chi_so = 'Doanh thu thuần'
        ten_hien_thi = 'Doanh thu thuần'
        if not st.session_state.get('df_kqkd', pd.DataFrame([])).empty:
            df_KQKD = st.session_state.df_kqkd
        else:
            df_KQKD = pd.read_excel(rf'data/Đúng/Tổng hợp/{st.session_state.Ma_Cty}_{ten_bao_cao}.xlsx')
        
    # Loại bỏ các dòng mà ngoài cột đầu tiên ra, tất cả các cột còn lại đều là None
    mask = df_KQKD.iloc[:, 1:].notna().any(axis=1)  # Tạo mask đánh dấu các dòng có ít nhất một giá trị không phải None từ cột thứ 2 trở đi
    df_KQKD = df_KQKD.loc[mask].reset_index(drop=True)  # Giữ lại chỉ những dòng thỏa mãn và reset index    
        
    # Tick box chọn phân tích khối
    phan_tich_khoi = st.checkbox(f"Đơn vị: % {ten_hien_thi}")

    if not phan_tich_khoi:
        df_KQKD_display = df_KQKD.astype({col: str for col in df_KQKD.select_dtypes(include='object').columns})

        # Nếu không chọn thì hiển thị bình thường
        st.dataframe(df_KQKD_display, hide_index = True)
    else:
        try:
            # Tìm chỉ số dòng của doanh thu thuần
            idx_doanh_thu = df_KQKD[df_KQKD.iloc[:, 0].astype(str).str.contains(ten_chi_so, case=False, na=False)].index[0]
            #idx_doanh_thu = df_KQKD[df_KQKD.iloc[:, 0].astype(str).str.contains(normalize_text(ten_chi_so), case=False, na=False)].index[0]
            
            # Lấy dòng doanh thu thuần
            doanh_thu_thuan = df_KQKD.iloc[idx_doanh_thu, 1:].values
                        
            # Tạo DataFrame mới để chứa kết quả phân tích khối
            df_phan_tich = df_KQKD.copy()
            
            # Tính % so với doanh thu thuần cho các dòng và thay thế giá trị
            for i in range(len(df_phan_tich)):
                for col_idx in range(1, len(df_phan_tich.columns)):
                    # Kiểm tra nếu giá trị hiện tại và doanh thu thuần đều không phải None/NaN và doanh thu thuần khác 0
                    current_value = df_KQKD.iloc[i, col_idx]
                    dt_value = doanh_thu_thuan[col_idx-1]
                    
                    if (pd.notna(current_value) and pd.notna(dt_value) and dt_value != 0):
                        # Thay thế giá trị bằng phần trăm so với doanh thu thuần
                        df_phan_tich.iloc[i, col_idx] = round(current_value / dt_value * 100, 2)
                    # Nếu không thỏa điều kiện, giữ nguyên giá trị None
            
            # Hiển thị kết quả
            df_phan_tich_display = df_phan_tich.astype({col: str for col in df_phan_tich.select_dtypes(include='object').columns})

            st.dataframe(df_phan_tich_display, hide_index = True)
            
        except IndexError:
            st.warning("Không tìm thấy chỉ tiêu 'Doanh thu thuần về bán hàng và cung cấp dịch vụ' trong file Excel.")