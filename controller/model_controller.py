from dotenv import load_dotenv
import os
import numpy as np
import joblib # Hoặc dùng pickle, joblib thường tốt hơn cho scikit-learn objects
import streamlit as st

load_dotenv()  # Load từ file .env
# Chỉ dùng XGB
XGB_PATH = os.getenv('XGB_PATH')

def kiem_tra_du_lieu(df_company):
    if df_company.empty:
        st.error(f"Lỗi: Không tìm thấy dữ liệu cho công ty {st.session_state.Ma_Cty} vào năm {st.session_state.Nam_hien_tai} để dự báo năm {st.session_state.Nam_hien_tai + 1}.")
        return

    try:
        features = df_company.columns.difference(['Ma_Cty', 'Nam', 'Nhan', 'target'], sort=False).tolist()
        if not features:
            raise ValueError("Không xác định được cột feature nào là số.")
        return features
    except Exception as e:
        st.error(f"Lỗi: Không xác định được các cột features. Chi tiết: {e}")

def chon_mo_hinh(df_company, features):
    try:
        if len(df_company) < 1:
            st.error(f"Lỗi: Không có dữ liệu cho công ty {st.session_state.Ma_Cty}.")
            return None, None

        X_latest = df_company[features].values

        if np.isnan(X_latest).any():
            st.error(f"Lỗi: Dữ liệu năm cuối của {st.session_state.Ma_Cty} chứa giá trị NaN.")
            return None, None

        return XGB_PATH, X_latest
    except Exception as e:
        st.error(f"Lỗi trong quá trình xử lý dữ liệu đầu vào: {e}")
        return None, None

def du_doan(model_path, model_input):
    try:
        model = joblib.load(model_path)
        prediction = model.predict(model_input)
        return int(prediction[0])
    except FileNotFoundError:
        st.error(f"Lỗi: Không tìm thấy file model {model_path}.")
    except Exception as e:
        st.error(f"Lỗi khi dự đoán: {e}")

def du_doan_ket_qua(df_company):
    features = kiem_tra_du_lieu(df_company)
    if not features:
        return None

    model_path, model_input = chon_mo_hinh(df_company, features)
    if model_path is None or model_input is None:
        return None

    return du_doan(model_path, model_input)


# from dotenv import load_dotenv
# import os
# import numpy as np
# import joblib # Hoặc dùng pickle, joblib thường tốt hơn cho scikit-learn objects
# import streamlit as st

# load_dotenv()  # Load từ file .env

# # --- Định nghĩa các hằng số từ .env ---
# MODEL_PATHS = {
#     'LSTM': os.getenv('LSTM_PATH'),
#     'MLP': os.getenv('MLP_PATH'),
#     'RF': os.getenv('RF_PATH'),
#     'XGB': os.getenv('XGB_PATH')
# }

# # SCALER_TABULAR_PATH = os.getenv('SCALER_TABULAR_PATH')
# SCALER_SEQUENCE_PATH = os.getenv('SCALER_SEQUENCE_PATH')
# SEQUENCE_LENGTH = int(os.getenv('SEQUENCE_LENGTH', 3))  # fallback mặc định là 3 nếu chưa có

# def kiem_tra_du_lieu(df_company):
#     if df_company.empty:
#         st.error(f"Lỗi: Không tìm thấy dữ liệu cho công ty {st.session_state.Ma_Cty} vào năm {st.session_state.Nam_hien_tai} để dự báo năm {st.session_state.Nam_hien_tai + 1}.")
#         return

#     # Xác định các cột features (giả sử là từ cột thứ 4 trở đi)
#     # Lấy danh sách features từ lần chạy trước hoặc định nghĩa cố định
#     # *** QUAN TRỌNG: Danh sách này PHẢI khớp với lúc huấn luyện ***
#     try:
#         # Lấy tất cả cột trừ các cột định danh/target đã biết
#         features = df_company.columns.difference(['Ma_Cty', 'Nam', 'Nhan', 'target'], sort=False).tolist()
        
#         if not features:
#             raise ValueError("Không xác định được cột feature nào là số.")
        
#         # print(f"Sử dụng {len(features)} features: {features[:5]}...{features[-5:]}") # In ra vài feature đầu cuối
#         return features
    
#     except Exception as e:
#         st.error(f"Lỗi: Không xác định được các cột features. Chi tiết: {e}")
        
# # 2. Chuẩn bị dữ liệu đầu vào dựa trên loại mô hình
# def chon_mo_hinh(df_company, features):
#     try:
#         if st.session_state.model_type == 'LSTM':
#             model_path = MODEL_PATHS[st.session_state.model_type]
#             scaler_path = SCALER_SEQUENCE_PATH # Scaler dành cho LSTM
#             if len(df_company) < SEQUENCE_LENGTH:
#                 st.error(f"Lỗi: Công ty {st.session_state.Ma_Cty} không có đủ dữ liệu ({len(df_company)} năm) cho chuỗi LSTM dài {SEQUENCE_LENGTH} năm.")

#             X_latest = df_company[features].values

#             # Kiểm tra NaN trước khi scale
#             if np.isnan(X_latest).any():
#                  st.error(f"Lỗi: Dữ liệu năm cuối của {st.session_state.Ma_Cty} chứa giá trị NaN.")

#             # Load scaler đã fit cho LSTM
#             try:
#                 scaler = joblib.load(scaler_path)
#             except FileNotFoundError:
#                 st.error(f"Lỗi: Không tìm thấy file scaler {scaler_path}. Hãy chắc chắn bạn đã lưu scaler sau khi huấn luyện.")
#             except Exception as e:
#                 st.error(f"Lỗi khi tải scaler {scaler_path}: {e}")
#                 return 

#             # Chuẩn hóa dữ liệu (scaler được fit trên dữ liệu đã reshape, nên cần reshape trước khi transform)
#             n_features = X_latest.shape[1]
#             X_latest_reshaped_flat = X_latest.reshape(1, -1) # Reshape thành (1, SEQUENCE_LENGTH * n_features)
#             X_scaled_flat = scaler.transform(X_latest_reshaped_flat)

#             # Reshape lại thành (1, SEQUENCE_LENGTH, n_features) cho LSTM input
#             model_input = X_scaled_flat.reshape(1, SEQUENCE_LENGTH, n_features)
#             # print(f"Input shape cho LSTM: {model_input.shape}")
            
#             return model_path, model_input

#         elif st.session_state.model_type == 'MLP':
#             model_path = MODEL_PATHS[st.session_state.model_type]
#             scaler_path = SCALER_SEQUENCE_PATH # Scaler dành cho MLP
#             if len(df_company) < 1:
#                 st.error(f"Lỗi: Không có dữ liệu cho công ty {st.session_state.Ma_Cty}.") # Trường hợp này ít xảy ra nếu get_chi_so_cong_ty hoạt động đúng

#             # Lấy dữ liệu năm cuối cùng
#             X_latest = df_company[features].values

#             # Kiểm tra NaN trước khi scale
#             if np.isnan(X_latest).any():
#                 st.error(f"Lỗi: Dữ liệu năm cuối của {st.session_state.Ma_Cty} chứa giá trị NaN.")

#             # Load scaler đã fit cho MLP
#             try:
#                 scaler = joblib.load(scaler_path)
#             except FileNotFoundError:
#                 st.error(f"Lỗi: Không tìm thấy file scaler {scaler_path}. Hãy chắc chắn bạn đã lưu scaler sau khi huấn luyện.")
#             except Exception as e:
#                 st.error(f"Lỗi khi tải scaler {scaler_path}: {e}")

#             # Chuẩn hóa dữ liệu (dạng 2D: [n_samples, n_features])
#             model_input = scaler.transform(X_latest)
#             # print(f"Input shape cho MLP: {model_input.shape}")
            
#             return model_path, model_input

#         elif st.session_state.model_type in ['RF', 'XGB']:
#             model_path = MODEL_PATHS[st.session_state.model_type]
#             # RF và XGB thường không yêu cầu chuẩn hóa, dựa theo code gốc của bạn
#             if len(df_company) < 1:
#                 st.error(f"Lỗi: Không có dữ liệu cho công ty {st.session_state.Ma_Cty}.")

#             X_latest = df_company[features].values

#             # Kiểm tra NaN (quan trọng vì mô hình có thể không xử lý được)
#             if np.isnan(X_latest).any():
#                 st.error(f"Lỗi: Dữ liệu năm cuối của {st.session_state.Ma_Cty} chứa giá trị NaN.")

#             model_input = X_latest
#             # print(f"Input shape cho {model_type}: {model_input.shape}")
            
#             return model_path, model_input

#         else:
#             st.error(f"Lỗi: Loại mô hình '{st.session_state.model_type}' không được hỗ trợ. Chọn từ 'LSTM', 'MLP', 'RF', 'XGB'.")

#     except Exception as e:
#         return None, None
    
# # 3. Load mô hình và dự đoán
# def du_doan(model_path, model_input):
#     try:
#         # Load model
#         try:
#             model = joblib.load(model_path) # Hoặc pickle.load(open(model_path, 'rb'))
#         except FileNotFoundError:
#             st.error(f"Lỗi: Không tìm thấy file model {model_path}. Hãy chắc chắn bạn đã lưu model sau khi huấn luyện.")
#         except Exception as e:
#             st.error(f"Lỗi khi tải model {model_path}: {e}")

#         # Dự đoán
#         prediction = model.predict(model_input)
#         # print(f"Dự đoán thô từ model {model_type}: {prediction}")

#         # Lấy kết quả dự đoán đầu tiên (vì input chỉ là 1 công ty/1 sequence)
#         result = int(prediction[0])

#         # 4. Trả về kết quả dạng chuỗi
#         return result

        
#     except Exception as e:
#         # Ghi lại lỗi chi tiết có thể hữu ích khi debug
#         print(f"Lỗi trong quá trình dự đoán bằng mô hình {st.session_state.model_type}: {e}")

# def du_doan_ket_qua(df_company):
#     features = kiem_tra_du_lieu(df_company)
    
#     model_path, model_input = chon_mo_hinh(df_company, features)

#     ket_qua = du_doan(model_path, model_input)
    
#     return ket_qua