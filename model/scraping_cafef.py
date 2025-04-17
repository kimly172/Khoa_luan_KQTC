import pandas as pd
import datetime
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
        self.company_name = company_name  # Lưu tên công ty
        self.report_type_mapping = {
            'LCTT': 'cashflow',
            'KQKD': 'incsta',
            'CDKT': 'bsheet',
        }

    # Hàm lấy danh mục các chỉ tiêu tài chính (tên các dòng trong bảng)
    def get_category(self, report_type, nam_hien_tai):
        ten_bao_cao_theo_url = self.report_type_mapping.get(report_type, 'Không xác định')
        
        # Tạo URL đến trang chứa báo cáo năm 2024 (chỉ để lấy danh mục)
        url = (f'https://s.cafef.vn/bao-cao-tai-chinh/'
               f'{self.company_name}/{ten_bao_cao_theo_url}/'
               f'{nam_hien_tai}/0/0/0/0/luu-chuyen-tien-te-gian-tiep-.chn')
        
        try:
            # Đọc tất cả các bảng trên trang bằng pandas
            df = pd.read_html(url)
            # Lấy bảng thứ 5 (vị trí thứ 4) thường chứa dữ liệu báo cáo
            df_temp = df[4]
            # Cột đầu tiên là danh mục (tên các dòng)
            df_category = df_temp.iloc[:, 0]
            return df_category
        except Exception as e:
            st.error(f"Lỗi khi lấy báo cáo {report_type} cho công ty {self.company_name.upper()}, năm {nam_hien_tai}: {e}")
            # Trả về Series rỗng nếu không lấy được category
    
    # Hàm lấy dữ liệu báo cáo theo từng năm
    def get_stat(self, report_type, nam_hien_tai, model_type):
        ten_bao_cao_theo_url = self.report_type_mapping.get(report_type, 'Không xác định')
        
        if model_type == 'LSTM':
            # Tạo danh sách các năm cần lấy dữ liệu
            # Năm hiện tại = 2023 thì range từ 2020 -> 2024 
            # => 4 năm vì k có 2024
            # 4 năm để tính bình quân của năm trước nữa
            year_list = range(nam_hien_tai - 3, nam_hien_tai + 1) 
            # Tạo dataframe rỗng với các cột là các năm
            result = pd.DataFrame(columns = year_list)
        
        else:
            # 2 năm
            year_list = range(nam_hien_tai - 1, nam_hien_tai + 1) 
            # Tạo dataframe rỗng với các cột là các năm
            result = pd.DataFrame(columns = year_list)
            
        for year in year_list:
            # Tạo URL theo từng năm
            
            url = (f'https://s.cafef.vn/bao-cao-tai-chinh/'
                   f'{self.company_name}/{ten_bao_cao_theo_url}/'
                   f'{year}/0/0/0/0/luu-chuyen-tien-te-gian-tiep-.chn')
            
            try:
                # Đọc dữ liệu trên web
                web_data = pd.read_html(url)
                # Cột thứ 5 (index 4) chứa số liệu, cột cuối cùng của bảng
                result[year] = web_data[4].iloc[:, 4]

                # # Nếu tất cả các dòng đều NaN => không có dữ liệu => loại bỏ năm đó
                # if result[year].isna().sum() == len(result):
                #     result.drop(columns=year, inplace=True)
            
            except Exception as e:
                st.error(f"Lỗi khi lấy báo cáo {report_type} cho công ty {self.company_name.upper()}, năm {year}: {e}")
                # Trả về Series rỗng nếu không lấy được category
                return 
            
        return result

    # Hàm kết hợp danh mục và dữ liệu thành bảng đầy đủ
    def get_findata(self, report_type, nam_hien_tai, model_type):
        """
        Tham số:
            report_type: ['LCTT', 'CDKT', 'KQKD'] - tên tiếng Anh của loại báo cáo
        """
        
        # Ghép danh mục (tên dòng) và số liệu thành một bảng
        result = pd.concat([self.get_category(report_type, nam_hien_tai),
                            self.get_stat(report_type, nam_hien_tai, model_type)],
                           axis='columns')
        # # Đặt cột đầu tiên làm chỉ mục (tên dòng)
        # result.set_index(0, inplace=True)

        print(f'Đã lưu báo cáo: {report_type} của công ty: {self.company_name.upper()}')
        return result
    
