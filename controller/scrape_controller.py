import pandas as pd
import streamlit as st
import pandas as pd
from unidecode import unidecode
import re
import numpy as np

from model.scraping_cafef import FinanceStat

def normalize_text(text):
    # # Kiểm tra nếu text là kiểu chuỗi
    # if isinstance(text, str):
    #     # Chuyển thành chữ thường và loại bỏ dấu tiếng Việt
    #     #text = text.lower()
    #     #text = unidecode(text)
    #     text = text.strip()
    #     # Loại bỏ các ký tự không mong muốn (ngoài a-z, 0-9 và khoảng trắng)
    #     text = re.sub(r'[^a-z0-9\s]', '', text)
    # # Nếu là kiểu số thì không làm gì, giữ nguyên
    # return text
    if isinstance(text, str):
        text = text.strip()
        # Giữ lại ký tự chữ cái tiếng Việt, số và khoảng trắng
        text = re.sub(r'[^\w\s]', '', text, flags=re.UNICODE)
        # \w trong Unicode sẽ bao gồm các ký tự chữ cái có dấu
        # Hoặc cụ thể hơn:
        # text = re.sub(r'[^a-zA-Z0-9ÀÁÂÃÈÉÊÌÍÒÓÔÕÙÚĂĐĨŨƠàáâãèéêìíòóôõùúăđĩũơƯĂẠẢẤẦẨẪẬẮẰẲẴẶẸẺẼỀỀỂưăạảấầẩẫậắằẳẵặẹẻẽềềểỄỆỈỊỌỎỐỒỔỖỘỚỜỞỠỢỤỦỨỪễệỉịọỏốồổỗộớờởỡợụủứừ\s]', '', text)
    return text
def clean_column_name(col):
    try:
        num = float(col)
        if num.is_integer():
            return str(int(num))  # Bỏ '.0'
        else:
            return str(num)
    except:
        return col  # Nếu không chuyển được thì giữ nguyên
    
search_terms_LCTT = {
    # LCTT (Báo cáo Lưu chuyển Tiền tệ)
    "DTRTHDKD": "Lưu chuyển tiền thuần từ hoạt động kinh doanh",
    "DTRTHDDT": "Lưu chuyển tiền thuần từ hoạt động đầu tư",
    "DTRTHDTC": "Lưu chuyển tiền thuần từ hoạt động tài chính",
    "KH": "Khấu hao TSCĐ và BĐSĐT",
}

search_terms_CDKT = {
    # CDKT (Bảng Cân đối Kế toán)
    "TTS": "TỔNG CỘNG TÀI SẢN",
    "TSNH": "TÀI SẢN NGẮN HẠN",
    "TVCKTDT": "Tiền và các khoản tương đương tiền",
    "HTK": "Hàng tồn kho",
    "TSCDHH": "Tài sản cố định hữu hình",
    "TSCD": "Tài sản cố định",
    "CKPTNH": "Các khoản phải thu ngắn hạn",
    "VCSH": "VỐN CHỦ SỞ HỮU",
    "NPT": "NỢ PHẢI TRẢ",
    "NNH": "Nợ ngắn hạn",
    "NDH": "Nợ dài hạn",
    "PTNBNH": "Phải trả người bán ngắn hạn",
}

search_terms_KQKD = {
    # KQHDKD (Báo cáo Kết quả Hoạt động Kinh doanh)
    "DTT": "Doanh thu thuần về bán hàng và cung cấp dịch vụ",
    "LNT": "Lợi nhuận thuần từ hoạt động kinh doanh",
    "LNR": "Lợi nhuận sau thuế thu nhập doanh nghiệp",
    "LNG": "Lợi nhuận gộp về bán hàng và cung cấp dịch vụ",
    "GVHB": "Giá vốn hàng bán",
    "LCBTCP": "Lãi cơ bản trên cổ phiếu",
    "CPLV": "Chi phí lãi vay",
}

def gop_file(df_CDKT, df_KQKD, df_LCTT):
    # Chuẩn hóa tên cột
    for df in [df_CDKT, df_KQKD, df_LCTT]:
        df.columns = df.columns.astype(str).str.strip()
         
    df_CDKT.fillna(0, inplace=True)
    df_KQKD.fillna(0, inplace=True)
    df_LCTT.fillna(0, inplace=True) 
    
    # Dictionary chứa dữ liệu cho từng công ty
    df_total = pd.DataFrame([])
    dong_hien_tai = 0
    
    #Lấy năm của công ty
    Nam_CDKT = df_CDKT.columns.tolist()
    Nam_KQKD = df_KQKD.columns.tolist()
    Nam_LCTT = df_LCTT.columns.tolist()

    # Chuyển các danh sách thành tập hợp (set) và lấy giao (intersection)
    Nam_trung = set(Nam_CDKT) & set(Nam_KQKD) & set(Nam_LCTT)

    # Xóa số 0, sắp xếp tăng dần
    Nam_trung = sorted(n for n in Nam_trung if n != '0' and n != 'Chỉ số')
    # Dictionary chứa dữ liệu cho từng công ty

    for year in Nam_trung:  # Lặp qua từng năm trùng
        df_total.at[dong_hien_tai, 'Id'] = int(dong_hien_tai + 1)
        df_total.at[dong_hien_tai, 'Ma_Cty'] = st.session_state.Ma_Cty
        df_total.at[dong_hien_tai, 'Nam'] = year

        # Áp dụng normalize_text vào cột đầu tiên của DataFrame
        df_CDKT.iloc[:, 0] = df_CDKT.iloc[:, 0].apply(normalize_text)
        df_KQKD.iloc[:, 0] = df_KQKD.iloc[:, 0].apply(normalize_text)
        df_LCTT.iloc[:, 0] = df_LCTT.iloc[:, 0].apply(normalize_text)

        # Duyệt qua các từ khóa tìm kiếm
        for key, term in search_terms_CDKT.items():  
            df_processing = df_CDKT              
            # Tìm trong các file, sử dụng normalize_text cho cột đầu tiên\
            matched_rows = df_processing.loc[df_processing.iloc[:, 0].str.contains(normalize_text(term), na=False), year]
            value = matched_rows.values

            if value.size >= 1:
                df_total.at[dong_hien_tai, key] = float(value[0])

        # Duyệt qua các từ khóa tìm kiếm
        for key, term in search_terms_KQKD.items():  
            df_processing = df_KQKD              
            # Tìm trong các file, sử dụng normalize_text cho cột đầu tiên\
            matched_rows = df_processing.loc[df_processing.iloc[:, 0].str.contains(normalize_text(term), na=False), year]
            value = matched_rows.values
            
            if value.size >= 1:
                df_total.at[dong_hien_tai, key] = float(value[0])      
                
        for key, term in search_terms_LCTT.items():  
            df_processing = df_LCTT              
            # Tìm trong các file, sử dụng normalize_text cho cột đầu tiên\
            matched_rows = df_processing.loc[df_processing.iloc[:, 0].str.contains(normalize_text(term), na=False), year]
            value = matched_rows.values
            
            if value.size >= 1:
                df_total.at[dong_hien_tai, key] = float(value[0])
        
        dong_hien_tai += 1  # Tiến sang dòng tiếp theo
        

    print(f"Đã xử lý xong công ty {st.session_state.Ma_Cty}")
    
    # Lấy index của các dòng có NaN trong 'Nam'
    na_indexes = df_total[df_total['Nam'].isna()].index
    print("Chỉ số các dòng có NaN trong cột 'Nam':", list(na_indexes))

    # Xoá các dòng có NaN trong 'Nam'
    df_total = df_total.drop(index=na_indexes).reset_index(drop=True)
    
    # Đổi kiểu dữ liệu
    for column in df_total.columns[3:]:
        df_total[column] = pd.to_numeric(df_total[column], errors='coerce').astype('float64')
        
    df_total['Nam'] = pd.to_numeric(df_total['Nam'], errors='coerce').astype('Int64')

    # Gộp tất cả các từ khóa lại với hậu tố tương ứng
    all_keys = (
        [key for key in search_terms_LCTT.keys()] +
        [key for key in search_terms_CDKT.keys()] +
        [key for key in search_terms_KQKD.keys()]
    )

    # Lấy danh sách các cột trong dataframe
    df_columns = df_total.columns.tolist()

    # Tìm các key bị thiếu
    missing_keys = [key for key in all_keys if key not in df_columns]

    # In ra kết quả
    if not missing_keys:
        print("✅ Tất cả các key đều có mặt trong df.columns")
    else:
        print("❌ Thiếu các key sau trong df.columns:")
        print(missing_keys)
    st.session_state.df_total = df_total
    return df_total

# Tính NNH bình quân (NNH năm sau + NNH năm trước) / 2
def calculate_average(group, group_name):
    """
    Tính NNH bình quân cho mỗi nhóm (Ma_Cty).

    Args:
        group (pd.DataFrame): DataFrame của một nhóm (Ma_Cty).

    Returns:
        pd.Series: Series chứa NNH bình quân.
    """
    shifted = group[group_name].shift(1)
    return (group[group_name] + shifted) / 2    
        
def tinh_chi_so(df_total):
    df_filtered = df_total
    # Chọn ra 2 cột 'Ma_Cty' (Mã Công ty) và 'Nam' (Năm) từ DataFrame df_filtered, lưu vào DataFrame mới tên là 'data'.
    data = df_filtered[['Ma_Cty', 'Nam']].copy() # Sử dụng .copy() để tránh cảnh báo SettingWithCopyWarning

    # Tính toán tỷ lệ LNT/CPLV (Lợi nhuận thuần / Chi phí lãi vay) và lưu vào mảng numpy 'ratio_conditon'.
    # Sử dụng np.where để xử lý các điều kiện một cách vector hóa (áp dụng cho toàn bộ cột).
    ratio_conditon = np.where(
        df_filtered["CPLV"].notna() & (df_filtered["CPLV"] != 0), # Điều kiện: CPLV không phải NaN và khác 0.
        df_filtered["LNT"] / df_filtered["CPLV"], # Nếu điều kiện đúng, tính LNT/CPLV.
        np.nan # Nếu điều kiện sai, gán giá trị NaN.
    )

    # Tạo cột mới 'Nhan' trong DataFrame 'data' dựa trên giá trị của 'ratio_conditon' và 'VCSH' (Vốn chủ sở hữu).
    # Sử dụng np.where để gán giá trị '1' hoặc '0' cho cột 'Nhan'.
    data["Nhan"] = np.where(
        ratio_conditon < 1, # Điều kiện 1: Tỷ lệ LNT/CPLV nhỏ hơn 1.
        "1", # Nếu điều kiện 1 đúng, gán giá trị "1".
        np.where(
            df_filtered["VCSH"] < 0, # Điều kiện 2 (nếu điều kiện 1 sai): VCSH nhỏ hơn 0.
            "1", # Nếu điều kiện 2 đúng, gán giá trị "1".
            "0" # Nếu cả hai điều kiện đều sai, gán giá trị "0".
        )
    )

    data['Nhan'].value_counts()
    
    ds_chi_so_binh_quan = ['NNH','TTS','VCSH','HTK','TSCD','CKPTNH']

    # Sắp xếp DataFrame theo Mã Công ty và Năm để đảm bảo shift hoạt động đúng
    df_filtered = df_filtered.sort_values(by=['Ma_Cty', 'Nam'])

    for chi_so_binh_quan in ds_chi_so_binh_quan:
        # Tính giá trị dịch chuyển (năm trước) trong mỗi nhóm 'Ma_Cty'
        shifted_values = df_filtered.groupby('Ma_Cty')[chi_so_binh_quan].shift(1)
        # Tính giá trị trung bình
        average_values = (df_filtered[chi_so_binh_quan] + shifted_values) / 2
        # Gán giá trị trung bình vào cột mới
        df_filtered[f'{chi_so_binh_quan}_binh_quan'] = average_values
        # Với năm đầu tiên của mỗi công ty (shifted_values sẽ là NaN), lấy giá trị gốc
        df_filtered[f'{chi_so_binh_quan}_binh_quan'] = df_filtered[f'{chi_so_binh_quan}_binh_quan'].fillna(df_filtered[chi_so_binh_quan])

    # --- Tính toán các chỉ số x ---

    data["x1"]=df_filtered['TSNH'] / df_filtered['NNH']
    data["x2"]=(df_filtered['TSNH'] - df_filtered['HTK']) / df_filtered["NNH"]
    data["x3"]=(df_filtered['TSNH'] - df_filtered['NNH']) / df_filtered["TTS"]
    data["x4"]=df_filtered['NNH'] / df_filtered['TTS']
    data["x5"]=df_filtered['TVCKTDT'] / df_filtered['TTS']
    data["x6"]=df_filtered['TVCKTDT'] / df_filtered['NNH']
    data["x7"]=df_filtered['HTK'] / df_filtered['TTS']
    data["x8"]=(df_filtered['TSNH'] - df_filtered['NNH']) / df_filtered["DTT"]
    data["x9"]=df_filtered['NNH'] / df_filtered['DTT']
    data["x10"]=df_filtered['TVCKTDT'] / df_filtered['TSNH']
    data["x11"]=df_filtered['NPT'] / df_filtered['TTS']
    data["x12"]=df_filtered['NPT'] / df_filtered['VCSH']
    data["x13"]=df_filtered['NNH'] / df_filtered['TTS']
    data["x14"] = df_filtered['DTRTHDKD'] / df_filtered['NNH_binh_quan']
    data["x15"]=df_filtered['LNR'] / df_filtered['TTS_binh_quan']
    data["x16"]=df_filtered['LNR'] / df_filtered['VCSH_binh_quan']
    data["x17"]=df_filtered['LNG'] / df_filtered['DTT']
    data["x18"]=df_filtered['LNR'] / df_filtered['DTT']
    data["x19"]=df_filtered['LNT'] / df_filtered['TTS']
    data["x20"]=df_filtered['LNR'] / df_filtered['TSCDHH']
    data["x21"]=(df_filtered['LNR'] + df_filtered['KH']) / df_filtered['TTS']
    data["x22"]=df_filtered['GVHB'] / df_filtered['HTK_binh_quan']
    data["x23"]=df_filtered['DTT'] / df_filtered['TSCD_binh_quan']
    data["x24"]=df_filtered['DTT'] / df_filtered['CKPTNH_binh_quan']
    data["x25"]=df_filtered['DTT'] / df_filtered['TTS_binh_quan']
    data["x26"]=df_filtered['DTRTHDKD'] / df_filtered['NPT']
    data["x27"]=df_filtered['DTRTHDKD'] / df_filtered['TTS']
    data["x28"]=df_filtered['DTRTHDKD'] / df_filtered['DTT']
    data["x29"]=df_filtered['TSNH'] / df_filtered['TTS']
    data["x30"]=df_filtered['TSCD'] / df_filtered['TTS']
    data["x31"]=df_filtered['VCSH'] / df_filtered['TTS']
    data["x32"]=df_filtered['NDH'] / df_filtered['VCSH']
    data["x33"]=df_filtered['LCBTCP'] 
    data["x34"]= df_filtered.groupby('Ma_Cty')['LNR'].pct_change() * 100 
    data["x35"]=df_filtered.groupby('Ma_Cty')['TTS'].pct_change() * 100 
    data["x36"]=df_filtered.groupby('Ma_Cty')['DTT'].pct_change() * 100 
    data["x37"]=df_filtered.groupby('Ma_Cty')['VCSH'].pct_change() * 100 
    data["x34"]=data["x34"].fillna(0)
    data["x35"]=data["x35"].fillna(0)
    data["x36"]=data["x36"].fillna(0)
    data["x37"]=data["x37"].fillna(0)

    companies_to_remove = data[data.isnull().any(axis=1)]['Ma_Cty'].unique()

    # Xóa tất cả các dòng có Ma_Cty trong danh sách trên
    data_cleaned = data[~data['Ma_Cty'].isin(companies_to_remove)]

    # Kiểm tra lại
    data_cleaned.isnull().sum()

    # Chỉnh lại cột Id
    data_cleaned['Id'] = range(1, len(data_cleaned) + 1)
    
    return data_cleaned

def crawl_tong_hop_du_lieu_tat_ca_cho_dashboard():
    financeStat = FinanceStat(st.session_state.Ma_Cty) 
    all_reports_result = financeStat.get_bao_cao_tat_ca_nam()
    
    if all_reports_result is None:
        return None
    else:
        df_total = gop_file(all_reports_result)
        return df_total
