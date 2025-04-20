import pandas as pd
import streamlit as st
from unidecode import unidecode
import re

def xu_ly_file_upload(uploaded_file, loai_bao_cao):
    """
    Xử lý file upload, bỏ qua các dòng đầu không liên quan và tìm dòng có cột từ thứ 2 trở đi là dạng năm.
    Args:
        uploaded_file: File được upload từ Streamlit.
        loai_bao_cao: Loại báo cáo (CDKT, KQKD, LCTT).
    Returns:
        DataFrame chứa dữ liệu từ file upload hoặc None nếu không xử lý được.
    """
    if uploaded_file is None:
        return None
    
    try:
        # Kiểm tra loại file để đọc dữ liệu
        file_extension = uploaded_file.name.split('.')[-1].lower()
        if file_extension in ['xlsx', 'xls']:
            df = pd.read_excel(uploaded_file, header=None)
        elif file_extension == 'csv':
            df = pd.read_csv(uploaded_file, header=None, encoding='utf-8')
        else:
            st.warning(f"Định dạng file {loai_bao_cao} không được hỗ trợ. Vui lòng sử dụng file Excel hoặc CSV.")
            return None
        
        # Tìm dòng có tất cả các cột từ thứ 2 trở đi là dạng năm (số nguyên từ 2000 đến năm hiện tại)
        start_row = None
        for i in range(len(df)):
            row = df.iloc[i]
            all_columns_are_years = True
            
            # Kiểm tra tất cả các cột từ thứ 2 trở đi
            for j in range(1, len(row)):
                try:
                    # Bỏ qua các cột trống
                    if pd.isna(row[j]) or row[j] == '':
                        continue
                        
                    val = float(row[j])
                    if not (val.is_integer() and 2000 <= int(val) <= pd.Timestamp.now().year):
                        all_columns_are_years = False
                        break
                except (ValueError, TypeError):
                    all_columns_are_years = False
                    break
            
            # Chỉ lấy dòng làm header khi tất cả các cột từ thứ 2 trở đi đều là năm
            if all_columns_are_years and len(row) > 1:  # Đảm bảo có ít nhất một cột năm
                start_row = i
                break
        
        if start_row is None:
            st.warning(f"Không tìm thấy dòng chứa năm trong file {loai_bao_cao}. Vui lòng kiểm tra định dạng file.")
            return None
        
        # Đọc lại file với dòng tiêu đề là dòng tìm được
        if file_extension in ['xlsx', 'xls']:
            df = pd.read_excel(uploaded_file, header=start_row)
        elif file_extension == 'csv':
            df = pd.read_csv(uploaded_file, header=start_row, encoding='utf-8')
            
        df.columns = df.columns.astype(str).str.strip()
        df.fillna(0, inplace=True)
        
        return df
    
    except Exception as e:
        st.error(f"Lỗi khi xử lý file {loai_bao_cao}: {str(e)}")
        return None
    
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

def normalize_text(text):
    # Kiểm tra nếu text là kiểu chuỗi
    if isinstance(text, str):
        # Chuyển thành chữ thường và loại bỏ dấu tiếng Việt
        text = text.lower()
        text = unidecode(text)
        # Loại bỏ các ký tự không mong muốn (ngoài a-z, 0-9 và khoảng trắng)
        text = re.sub(r'[^a-z0-9\s]', '', text)
    # Nếu là kiểu số thì không làm gì, giữ nguyên
    return text
    
def merge_du_lieu_upload(df_total, uploaded_cdkt, uploaded_kqkd, uploaded_lctt):
    """
    Merge dữ liệu từ file upload với dữ liệu tổng hợp, chuẩn hóa đơn vị dựa trên tỷ lệ so sánh.
    Args:
        df_total: DataFrame chứa dữ liệu tổng hợp từ database hoặc web.
        uploaded_cdkt, uploaded_kqkd, uploaded_lctt: Các file upload tương ứng.
    Returns:
        DataFrame chứa dữ liệu đã được merge.
    """
    # Xử lý từng file upload
    df_cdkt = xu_ly_file_upload(uploaded_cdkt, "CDKT")
    df_kqkd = xu_ly_file_upload(uploaded_kqkd, "KQKD")
    df_lctt = xu_ly_file_upload(uploaded_lctt, "LCTT")
    
    # Nếu thiếu bất kỳ file upload nào, thông báo lỗi và trả về None
    if df_cdkt is None or df_kqkd is None or df_lctt is None:
        st.error("Thiếu file báo cáo tài chính. Vui lòng upload đầy đủ các file CDKT, KQKD và LCTT để tiếp tục.")
        return None
    
    # Nếu không có dữ liệu trong database, tạo DataFrame mới từ dữ liệu upload
    if df_total.empty:
        df_total = pd.DataFrame(columns=['Id', 'Ma_Cty', 'Nam'] + list(search_terms_CDKT.keys()) + list(search_terms_KQKD.keys()) + list(search_terms_LCTT.keys()))
    
    # Tính tỷ lệ chuẩn hóa nếu có dữ liệu trong database
    ty_le_chuan_hoa = 1.0
    if not df_total.empty:
        # Danh sách các tỷ lệ chuẩn hóa hợp lệ (các bội số của 1000)
        valid_ratios = [1000**i for i in range(-3, 4)]  # [0.000001, 0.001, 1, 1000, 1000000, 1000000000, 1000000000000]
        found_ratio = False
        
        # Kiểm tra nhiều search term khác nhau để tìm tỷ lệ chuẩn hóa
        search_terms_to_check = [
            ('CDKT', search_terms_CDKT['TTS'], df_cdkt, 'TTS'),
            ('CDKT', search_terms_CDKT['VCSH'], df_cdkt, 'VCSH'),
            ('KQKD', search_terms_KQKD['DTT'], df_kqkd, 'DTT'),
            ('KQKD', search_terms_KQKD['LNR'], df_kqkd, 'LNR'),
        ]
        
        for term_type, term, df_source, column in search_terms_to_check:
            for year in df_source.columns[1:]:
                if year in df_total['Nam'].values:
                    upload_val_series = df_source.loc[df_source.iloc[:, 0].str.contains(normalize_text(term), na=False), year]
                    if not upload_val_series.empty:
                        upload_val = float(upload_val_series.values[0])
                        db_val_series = df_total.loc[df_total['Nam'] == int(year), column]
                        if not db_val_series.empty:
                            db_val = float(db_val_series.values[0])
                            if upload_val != 0 and db_val != 0:
                                ratio = db_val / upload_val
                                # Kiểm tra nếu tỷ lệ gần với một trong các giá trị hợp lệ
                                for valid_ratio in valid_ratios:
                                    if abs(ratio - valid_ratio) / valid_ratio < 0.1:  # Sai số 10%
                                        ty_le_chuan_hoa = valid_ratio
                                        st.info(f"Đã tính tỷ lệ chuẩn hóa dữ liệu upload: {ty_le_chuan_hoa:.2f} dựa trên giá trị {term_type} năm {year}.")
                                        found_ratio = True
                                        break
                            if found_ratio:
                                break
                if found_ratio:
                    break
            if found_ratio:
                break
                
        if ty_le_chuan_hoa == 1.0 and not found_ratio:
            st.warning("Không tìm thấy giá trị phù hợp để tính tỷ lệ chuẩn hóa. Dữ liệu upload sẽ được giữ nguyên.")
    
    # Merge dữ liệu upload vào df_total
    dong_hien_tai = len(df_total)
    if df_cdkt is not None:
        for year in df_cdkt.columns[1:]:
            if year not in df_total['Nam'].values:
                df_total.at[dong_hien_tai, 'Id'] = int(dong_hien_tai + 1)
                df_total.at[dong_hien_tai, 'Ma_Cty'] = st.session_state.Ma_Cty
                df_total.at[dong_hien_tai, 'Nam'] = int(year)
                for key, term in search_terms_CDKT.items():
                    matched_rows = df_cdkt.loc[df_cdkt.iloc[:, 0].str.contains(normalize_text(term), na=False), year]
                    value = matched_rows.values
                    if value.size == 1:
                        # Điều chỉnh đơn vị dữ liệu theo tỷ lệ chuẩn hóa
                        df_total.at[dong_hien_tai, key] = float(value[0]) * ty_le_chuan_hoa
                dong_hien_tai += 1
    
    if df_kqkd is not None:
        for year in df_kqkd.columns[1:]:
            if year not in df_total['Nam'].values:
                df_total.at[dong_hien_tai, 'Id'] = int(dong_hien_tai + 1)
                df_total.at[dong_hien_tai, 'Ma_Cty'] = st.session_state.Ma_Cty
                df_total.at[dong_hien_tai, 'Nam'] = int(year)
                for key, term in search_terms_KQKD.items():
                    matched_rows = df_kqkd.loc[df_kqkd.iloc[:, 0].str.contains(normalize_text(term), na=False), year]
                    value = matched_rows.values
                    if value.size == 1:
                        # Điều chỉnh đơn vị dữ liệu theo tỷ lệ chuẩn hóa
                        df_total.at[dong_hien_tai, key] = float(value[0]) * ty_le_chuan_hoa
                dong_hien_tai += 1
    
    if df_lctt is not None:
        for year in df_lctt.columns[1:]:
            if year not in df_total['Nam'].values:
                df_total.at[dong_hien_tai, 'Id'] = int(dong_hien_tai + 1)
                df_total.at[dong_hien_tai, 'Ma_Cty'] = st.session_state.Ma_Cty
                df_total.at[dong_hien_tai, 'Nam'] = int(year)
                for key, term in search_terms_LCTT.items():
                    matched_rows = df_lctt.loc[df_lctt.iloc[:, 0].str.contains(normalize_text(term), na=False), year]
                    value = matched_rows.values
                    if value.size == 1:
                        # Điều chỉnh đơn vị dữ liệu theo tỷ lệ chuẩn hóa
                        df_total.at[dong_hien_tai, key] = float(value[0]) * ty_le_chuan_hoa
                dong_hien_tai += 1
    
    # Xóa các dòng có NaN trong 'Nam'
    na_indexes = df_total[df_total['Nam'].isna()].index
    df_total = df_total.drop(index=na_indexes).reset_index(drop=True)
    
    return df_total
