import pandas as pd
from datetime import datetime
import streamlit as st

# Định nghĩa lớp FinanceStat để thu thập dữ liệu báo cáo tài chính từ website cafef.vn
class FinanceStat:
    """
    Lớp này cào dữ liệu từ cafef.vn để lấy 3 loại báo cáo tài chính của một công ty.
    Tham số:
        company_name: tên công ty trên sàn chứng khoán (ví dụ: 'fpt')
    
    Các phương thức chính:
        self.get_findata(report_type):
            Lấy dữ liệu tài chính theo loại báo cáo
        self.export_findata(form='csv'):
            Xuất dữ liệu ra định dạng csv hoặc xlsx
    """
    
    # Phương thức khởi tạo (constructor)
    def __init__(self, company_name):
        self.company_name = company_name.lower()  # Lưu tên công ty
        self.report_type_mapping = {
            'LCTT': 'cashflow',
            'KQKD': 'incsta',
            'CDKT': 'bsheet',
        }
        
        self.report_type_mapping_for_display = {
            'LCTT': 'Lưu chuyển Tiền tệ',
            'KQKD': 'Kết quả Hoạt động Kinh doanh',
            'CDKT': 'Cân đối Kế toán',
        }
        
        self.report_type_list = ['LCTT', 'KQKD', 'CDKT']
    
    # def get_bao_cao_1_hoac_3_nam(self):
    #     dict_result = {}
    #     for report_type in self.report_type_list:
    #         ten_bao_cao_theo_url = self.report_type_mapping.get(report_type, 'Không xác định')
    #         ten_bao_cao_hien_thi = self.report_type_mapping_for_display.get(report_type, 'Không xác định')
            
    #         nam_can_thu_thap = 4 if st.session_state.model_type == 'LSTM' else 2

    #         url = (
    #             f'https://s.cafef.vn/bao-cao-tai-chinh/'
    #             f'{self.company_name}/{ten_bao_cao_theo_url}/'
    #             f'{st.session_state.Nam_hien_tai}/0/0/0/0/luu-chuyen-tien-te-gian-tiep-.chn'
    #         )

    #         result = {} 

    #         try:
    #             web_data = pd.read_html(url)
    #             table = web_data[4]
                
    #             # Lấy dữ liệu cho các năm nam_hien_tai, nam_hien_tai - 1, ...
    #             for i in range(nam_can_thu_thap):
    #                 col_year = st.session_state.Nam_hien_tai - i
    #                 col_data = table.iloc[:, 4 - i]

    #                 if col_data.isna().all():
    #                     return None
    #                 else:
    #                     result[col_year] = col_data
    #             result['Chỉ số'] = table.iloc[:, 0]
    #         except Exception as e:
    #             # st.error(f"Lỗi khi lấy báo cáo {ten_bao_cao_hien_thi} cho công ty {self.company_name.upper()}, năm {st.session_state.Nam_hien_tai}: {e}")
    #             return None

    #         # Tạo DataFrame và sắp xếp cột
    #         df_result = pd.DataFrame(result)
    #         sorted_cols = ['Chỉ số'] + sorted([col for col in df_result.columns if col != 'Chỉ số'])
    #         df_result = df_result[sorted_cols]

    #         dict_result[report_type] = df_result

    #     return dict_result

    
    # Hàm lấy dữ liệu báo cáo theo từng năm
    def get_bao_cao_tat_ca_nam(self):
        dict_result = {}
        for report_type in self.report_type_list:
            ten_bao_cao_theo_url = self.report_type_mapping.get(report_type, 'Không xác định')
            ten_bao_cao_hien_thi = self.report_type_mapping_for_display.get(report_type, 'Không xác định')
            
            year_list = list(range(datetime.now().year, 2020, -4))
            result = {} 

            for year in year_list:
                
                # Tạo URL theo từng năm
                url = (f'https://s.cafef.vn/bao-cao-tai-chinh/'
                    f'{self.company_name}/{ten_bao_cao_theo_url}/'
                    f'{year}/0/0/0/0/luu-chuyen-tien-te-gian-tiep-.chn')
                try:
                    # Đọc dữ liệu trên web
                    web_data = pd.read_html(url)
                    table = web_data[4]
                    
                    for i in range(4):
                        col_data = table.iloc[:, 4 - i]

                        if not col_data.isna().all() :
                            # Cột thứ 5 (index 4) chứa số liệu
                            result[year - i] = col_data

                    result['Chỉ số'] = table.iloc[:, 0]

                except Exception as e:
                    import traceback
                    import streamlit as st
                    st.error(f"Lỗi khi lấy báo cáo {ten_bao_cao_hien_thi} cho công ty {self.company_name.upper()}, năm {year}:\n{traceback.format_exc()}")
                    continue  # Tiếp tục với năm tiếp theo thay vì return
            
            # Sau khi lấy xong, tạo DataFrame và sắp xếp cột
            df_result = pd.DataFrame(result)

            if len(df_result.columns) < 2:
                return None

            # Đảm bảo 'Chỉ số' luôn là cột đầu tiên
            sorted_cols = ['Chỉ số'] + sorted([col for col in df_result.columns if col != 'Chỉ số'])
            df_result = df_result[sorted_cols]

            dict_result[report_type] = df_result
                
        return dict_result

    
