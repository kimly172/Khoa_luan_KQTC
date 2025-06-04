import pandas as pd
import streamlit as st
from unidecode import unidecode
import re
    
def xu_ly_file_upload(uploaded_file, loai_bao_cao):
    import pandas as pd

    if uploaded_file is None:
        return None
    file_extension = uploaded_file.name.split('.')[-1].lower()
    # Đọc file không có header để dò dòng tiêu đề
    if file_extension in ['xlsx', 'xls']:
        df = pd.read_excel(uploaded_file, header=None)
    elif file_extension == 'csv':
        df = pd.read_csv(uploaded_file, header=None, encoding='utf-8', on_bad_lines='skip')
    else:
        print(f"Định dạng file {loai_bao_cao} không được hỗ trợ. Vui lòng sử dụng file Excel hoặc CSV.")
        return None

    current_year = pd.Timestamp.now().year
    start_row = None

    for i in range(len(df)):
        row = df.iloc[i]
        year_count = 0

        # Bỏ qua dòng nếu cột đầu tiên là năm
        try:
            first_val = float(row[0])
            if first_val.is_integer() and 2000 <= int(first_val) <= current_year:
                continue  # Không hợp lệ nếu cột đầu là năm
        except:
            pass  # OK nếu không phải năm

        # Đếm số cột là năm (từ cột thứ 2 trở đi)
        for j in range(1, len(row)):
            try:
                val = float(row[j])
                if val.is_integer() and 2000 <= int(val) <= current_year:
                    year_count += 1
            except:
                continue

        # Chấp nhận nếu có ít nhất 3 cột là năm
        if year_count >= 3:
            start_row = i
            break

    if start_row is None:
        print(f'Không tìm thấy dòng chứa năm trong file {loai_bao_cao}. Vui lòng kiểm tra định dạng file')
        return None

    # Reset file pointer để đọc lại
    uploaded_file.seek(0)

    # Đọc lại file với header đúng
    if file_extension in ['xlsx', 'xls']:
        df = pd.read_excel(uploaded_file, header=start_row)
    elif file_extension == 'csv':
        df = pd.read_csv(uploaded_file, header=start_row, encoding='utf-8', on_bad_lines='skip')

    df.columns = df.columns.astype(str).str.strip()
    df.fillna(0, inplace=True)

    return df
    
# search_terms_LCTT = {
#     # LCTT (Báo cáo Lưu chuyển Tiền tệ)
#     "DTRTHDKD": "Lưu chuyển tiền thuần từ hoạt động kinh doanh",
#     "DTRTHDDT": "Lưu chuyển tiền thuần từ hoạt động đầu tư",
#     "DTRTHDTC": "Lưu chuyển tiền thuần từ hoạt động tài chính",
#     "KH": "Khấu hao TSCĐ và BĐSĐT",
# }

# search_terms_CDKT = {
#     # CDKT (Bảng Cân đối Kế toán)
#     "TTS": "TỔNG CỘNG TÀI SẢN",
#     "TSNH": "TÀI SẢN NGẮN HẠN",
#     "TVCKTDT": "Tiền và các khoản tương đương tiền",
#     "HTK": "Hàng tồn kho",
#     "TSCDHH": "Tài sản cố định hữu hình",
#     "TSCD": "Tài sản cố định",
#     "CKPTNH": "Các khoản phải thu ngắn hạn",
#     "VCSH": "VỐN CHỦ SỞ HỮU",
#     "NPT": "NỢ PHẢI TRẢ",
#     "NNH": "Nợ ngắn hạn",
#     "NDH": "Nợ dài hạn",
#     "PTNBNH": "Phải trả người bán ngắn hạn",
# }

# search_terms_KQKD = {
#     # KQHDKD (Báo cáo Kết quả Hoạt động Kinh doanh)
#     "DTT": "Doanh thu thuần về bán hàng và cung cấp dịch vụ",
#     "LNT": "Lợi nhuận thuần từ hoạt động kinh doanh",
#     "LNR": "Lợi nhuận sau thuế thu nhập doanh nghiệp",
#     "LNG": "Lợi nhuận gộp về bán hàng và cung cấp dịch vụ",
#     "GVHB": "Giá vốn hàng bán",
#     "LCBTCP": "Lãi cơ bản trên cổ phiếu",
#     "CPLV": "Chi phí lãi vay",
# }    

# def normalize_text(text):
#     # Kiểm tra nếu text là kiểu chuỗi
#     if isinstance(text, str):
#         # Chuyển thành chữ thường và loại bỏ dấu tiếng Việt
#         text = text.lower()
#         text = unidecode(text)
#         # Loại bỏ các ký tự không mong muốn (ngoài a-z, 0-9 và khoảng trắng)
#         text = re.sub(r'[^a-z0-9\s]', '', text)
#     # Nếu là kiểu số thì không làm gì, giữ nguyên
#     return text
    
# def merge_du_lieu_upload(uploaded_cdkt, uploaded_kqkd, uploaded_lctt):
#     """
#     Merge dữ liệu từ file upload với dữ liệu tổng hợp, chuẩn hóa đơn vị dựa trên tỷ lệ so sánh.
#     Args:
#         df_total: DataFrame chứa dữ liệu tổng hợp từ database hoặc web.
#         uploaded_cdkt, uploaded_kqkd, uploaded_lctt: Các file upload tương ứng.
#     Returns:
#         DataFrame chứa dữ liệu đã được merge.
#     """
#     # Xử lý từng file upload
#     df_cdkt = xu_ly_file_upload(uploaded_cdkt, "CDKT")
#     st.session_state.df_cdkt = df_cdkt
    
#     df_kqkd = xu_ly_file_upload(uploaded_kqkd, "KQKD")
#     st.session_state.df_kqkd = df_kqkd
    
#     df_lctt = xu_ly_file_upload(uploaded_lctt, "LCTT")
#     st.session_state.df_lctt = df_lctt
    
#     # Nếu thiếu bất kỳ file upload nào, thông báo lỗi và trả về None
#     if df_cdkt is None or df_kqkd is None or df_lctt is None:
#         st.error("Thiếu file báo cáo tài chính. Vui lòng upload đầy đủ các file CDKT, KQKD và LCTT để tiếp tục.")
#         return None
    
#     df_total = pd.DataFrame([])
#     # Merge dữ liệu upload vào df_total
#     dong_hien_tai = len(df_total)
#     if df_cdkt is not None:
#         for year in df_cdkt.columns[1:]:
#                 df_total.at[dong_hien_tai, 'Id'] = int(dong_hien_tai + 1)
#                 df_total.at[dong_hien_tai, 'Ma_Cty'] = st.session_state.Ma_Cty
#                 df_total.at[dong_hien_tai, 'Nam'] = int(year)
#                 for key, term in search_terms_CDKT.items():
#                     matched_rows = df_cdkt.loc[df_cdkt.iloc[:, 0].str.contains(normalize_text(term), na=False), year]
#                     value = matched_rows.values
#                     if value.size == 1:
#                         # Điều chỉnh đơn vị dữ liệu theo tỷ lệ chuẩn hóa
#                         df_total.at[dong_hien_tai, key] = float(value[0])
#                 dong_hien_tai += 1
    
#     if df_kqkd is not None:
#         for year in df_kqkd.columns[1:]:
#                 df_total.at[dong_hien_tai, 'Id'] = int(dong_hien_tai + 1)
#                 df_total.at[dong_hien_tai, 'Ma_Cty'] = st.session_state.Ma_Cty
#                 df_total.at[dong_hien_tai, 'Nam'] = int(year)
#                 for key, term in search_terms_KQKD.items():
#                     matched_rows = df_kqkd.loc[df_kqkd.iloc[:, 0].str.contains(normalize_text(term), na=False), year]
#                     value = matched_rows.values
#                     if value.size == 1:
#                         # Điều chỉnh đơn vị dữ liệu theo tỷ lệ chuẩn hóa
#                         df_total.at[dong_hien_tai, key] = float(value[0])
#                 dong_hien_tai += 1
    
#     if df_lctt is not None:
#         for year in df_lctt.columns[1:]:
#                 df_total.at[dong_hien_tai, 'Id'] = int(dong_hien_tai + 1)
#                 df_total.at[dong_hien_tai, 'Ma_Cty'] = st.session_state.Ma_Cty
#                 df_total.at[dong_hien_tai, 'Nam'] = int(year)
#                 for key, term in search_terms_LCTT.items():
#                     matched_rows = df_lctt.loc[df_lctt.iloc[:, 0].str.contains(normalize_text(term), na=False), year]
#                     value = matched_rows.values
#                     if value.size == 1:
#                         # Điều chỉnh đơn vị dữ liệu theo tỷ lệ chuẩn hóa
#                         df_total.at[dong_hien_tai, key] = float(value[0])
#                 dong_hien_tai += 1
    
#     # Xóa các dòng có NaN trong 'Nam'
#     na_indexes = df_total[df_total['Nam'].isna()].index
#     df_total = df_total.drop(index=na_indexes).reset_index(drop=True)
    
#     return df_total
