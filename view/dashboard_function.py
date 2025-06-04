import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st
import numpy as np # Thêm import numpy nếu cần cho fillna

# --- Bảng màu cho các chỉ số ---
# Sử dụng bảng màu Plotly và mở rộng nếu cần
_COLOR_SEQUENCE = ['#277DA1', '#F9C74F', '#90BE6D', '#F9844A', '#577590', '#F8961E', '#4D908E', '#F3722C', '#43AA8B', '#F94144']

# Ánh xạ tên chỉ số (hoặc key chuẩn hóa) sang màu cố định
# Lưu ý: Key nên được chuẩn hóa (viết thường, bỏ dấu '%', '()', thay khoảng trắng bằng '_')
INDICATOR_COLORS = {
    # Tăng trưởng & Biên LN
    'dtt': _COLOR_SEQUENCE[0], # Doanh thu thuần
    'tang_truong_doanh_thu': _COLOR_SEQUENCE[1],
    'lnr': _COLOR_SEQUENCE[2], # Lợi nhuận ròng
    'tang_truong_loi_nhuan': _COLOR_SEQUENCE[3],
    
    # THÔNG SỐ KHẢ NĂNG SINH LỜI VÀ THỊ TRƯỜNG
    'bien_loi_nhuan_gop': _COLOR_SEQUENCE[0],
    'ebitda': _COLOR_SEQUENCE[1],
    'ebit': _COLOR_SEQUENCE[2],
    'bien_loi_nhuan_rong': _COLOR_SEQUENCE[3], # Dùng chung màu với ROA/ROE Dupont
    'roa': _COLOR_SEQUENCE[4], # Dùng chung màu với ROA Dupont
    'roe': _COLOR_SEQUENCE[5], # Dùng chung màu với ROE Dupont
    'vong_quay_tai_san': _COLOR_SEQUENCE[6], # Dùng chung màu với Dupont, Vòng quay TS
    'don_bay_tai_chinh': _COLOR_SEQUENCE[7], # Dùng chung màu với ROE Dupont
    'lcbtcp': _COLOR_SEQUENCE[8], # Màu khác
    
    # PHÂN TÍCH CƠ CẤU TÀI SẢN VÀ NGUỒN VỐN
    'tsnh': _COLOR_SEQUENCE[0],
    'tsdh': _COLOR_SEQUENCE[1],
    'tvcktdt': _COLOR_SEQUENCE[2],
    'ckptnh': _COLOR_SEQUENCE[3],
    'htk': _COLOR_SEQUENCE[4], # Dùng chung màu với Vòng quay HTK
    'tscdhh': _COLOR_SEQUENCE[5],
    'tscd': _COLOR_SEQUENCE[6], # Dùng chung màu với Vòng quay TSCD
    
    'npt': _COLOR_SEQUENCE[0],
    'vcsh': _COLOR_SEQUENCE[1], # Dùng chung màu với Nợ/VCSH, NDH/VCSH
    'nnh': _COLOR_SEQUENCE[2],
    'ndh': _COLOR_SEQUENCE[3], # Dùng chung màu với Thông số nợ dài hạn
    
    # PHÂN TÍCH THÔNG SỐ HOẠT ĐỘNG
    'vong_quay_tscd': _COLOR_SEQUENCE[0], # Dùng chung màu với TSCD
    'ky_thu_tien_bq': _COLOR_SEQUENCE[1], # Màu khác
    'vong_quay_khoan_phai_thu': _COLOR_SEQUENCE[2], # Màu khác
    'chu_ky_chuyen_hoa_htk': _COLOR_SEQUENCE[3], # Màu khác
    'vong_quay_htk': _COLOR_SEQUENCE[4], # Dùng chung màu với HTK
    
    # THÔNG SỐ KHẢ NĂNG THANH TOÁN
    'kha_nang_thanh_toan_hien_thoi': _COLOR_SEQUENCE[0], # Màu khác
    'kha_nang_thanh_toan_nhanh': _COLOR_SEQUENCE[1], # Màu khác
    'kha_nang_chi_tra_bang_tien': _COLOR_SEQUENCE[2], # Màu khác
    'ky_thanh_toan_binh_quan': _COLOR_SEQUENCE[3], # Màu khác
    'vong_quay_phai_tra_nguoi_ban': _COLOR_SEQUENCE[4], # Màu khác
    'chu_ky_chuyen_hoa_thanh_tien': _COLOR_SEQUENCE[5], # Màu khác
    
    # THÔNG SỐ NỢ
    'thong_so_no_tren_tai_san': _COLOR_SEQUENCE[0], # Màu khác (Nợ/TTS)
    'thong_so_no_tren_von_chu_so_huu': _COLOR_SEQUENCE[1], # Dùng chung màu với VCSH (Nợ/VCSH)
    'thong_so_no_dai_han': _COLOR_SEQUENCE[2], # Dùng chung màu với NDH
    'no_dai_han_tren_von_chu_so_huu': _COLOR_SEQUENCE[3], # Dùng chung màu với VCSH
    'so_lan_dam_bao_lai_vay': _COLOR_SEQUENCE[4], # Màu khác
    
    # PHÂN TÍCH LƯU CHUYỂN TIỀN TỆ
    'dtrthdkd': _COLOR_SEQUENCE[0], # Màu khác
    'dtrthddt': _COLOR_SEQUENCE[1], # Màu khác
    'dtrthdtc': _COLOR_SEQUENCE[2], # Màu khác

    # Default color
    'default': _COLOR_SEQUENCE[9] # Màu xám cho các chỉ số không xác định
}

# Hàm chuẩn hóa tên chỉ số để làm key tra cứu màu
def _normalize_indicator_name(name):
    """Chuẩn hóa tên chỉ số để tra cứu màu."""
    if not isinstance(name, str):
        return 'default'
    # Chuẩn hóa cơ bản: viết thường, bỏ ký tự đặc biệt, thay khoảng trắng/dấu gạch bằng gạch dưới
    norm = name.lower().replace('(%)', '').replace('.', '').replace('&', '').strip()
    norm = norm.replace(' ', '_').replace('/', '_').replace('-', '_')
    # Loại bỏ các hậu tố phổ biến không ảnh hưởng đến ý nghĩa chính
    norm = norm.replace('_bq', '').replace('_binh_quan', '')

    # Xử lý các trường hợp đặc biệt đã biết (ánh xạ các biến thể về một key chuẩn)
    mapping = {
        'doanh_thu_thuần': 'dtt', 'dtt': 'dtt',
        'tăng_trưởng_doanh_thu': 'tang_truong_doanh_thu',
        'lợi_nhuận_sau_thuế': 'lnr', 'lợi_nhuận_ròng': 'lnr', 'lnr': 'lnr',
        'tăng_trưởng_lợi_nhuận': 'tang_truong_loi_nhuan',
        'biên_lợi_nhuận_gộp': 'bien_loi_nhuan_gop',
        'ebitda': 'ebitda',
        'ebit': 'ebit',
        'biên_ln_ròng': 'bien_loi_nhuan_rong', 'biên_lợi_nhuận_ròng': 'bien_loi_nhuan_rong',
        'roa': 'roa',
        'roe': 'roe',
        'vòng_quay_tổng_tài_sản': 'vong_quay_tai_san', 'vong_quay_tai_san': 'vong_quay_tai_san',
        'đòn_bẩy_tài_chính': 'don_bay_tai_chinh',
        'tài_sản_ngắn_hạn': 'tsnh', 'tsnh': 'tsnh',
        'tài_sản_dài_hạn': 'tsdh', 'tsdh': 'tsdh',
        'tiền_và_ck_tương_đương_tiền': 'tvcktdt', 'tvcktdt': 'tvcktdt',
        'các_khoản_phải_thu_ngắn_hạn': 'ckptnh', 'ckptnh': 'ckptnh',
        'hàng_tồn_kho': 'htk', 'htk': 'htk',
        'tài_sản_cố_định_hữu_hình': 'tscdhh', 'tscdhh': 'tscdhh',
        'tài_sản_cố_định': 'tscd', 'tscd': 'tscd',
        'nợ_phải_trả': 'npt', 'npt': 'npt',
        'vốn_chủ_sở_hữu': 'vcsh', 'vcsh': 'vcsh',
        'nợ_ngắn_hạn': 'nnh', 'nnh': 'nnh',
        'nợ_dài_hạn': 'ndh', 'ndh': 'ndh',
        'vòng_quay_tscđ': 'vong_quay_tscd', 'vong_quay_tscd': 'vong_quay_tscd',
        'kỳ_thu_tiền': 'ky_thu_tien_bq', 'ky_thu_tien_bq': 'ky_thu_tien_bq',
        'vòng_quay_kpt': 'vong_quay_khoan_phai_thu', 'vong_quay_khoan_phai_thu': 'vong_quay_khoan_phai_thu',
        'chu_kỳ_htk': 'chu_ky_chuyen_hoa_htk', 'chu_ky_chuyen_hoa_htk': 'chu_ky_chuyen_hoa_htk',
        'vòng_quay_htk': 'vong_quay_htk',
        'khả_năng_thanh_toán_hiện_thời': 'kha_nang_thanh_toan_hien_thoi',
        'khả_năng_thanh_toán_nhanh': 'kha_nang_thanh_toan_nhanh',
        'khả_năng_chi_trả_bằng_tiền': 'kha_nang_chi_tra_bang_tien',
        'kỳ_thanh_toán': 'ky_thanh_toan_binh_quan', 'kỳ_thanh_toán_bình_quân': 'ky_thanh_toan_binh_quan',
        'vòng_quay_phải_trả_người_bán': 'vong_quay_phai_tra_nguoi_ban',
        'chu_kỳ_chuyển_hóa_thành_tiền': 'chu_ky_chuyen_hoa_thanh_tien', 'chu_kỳ_tiền_mặt': 'chu_ky_chuyen_hoa_thanh_tien',
        'nợ_tts': 'thong_so_no_tren_tai_san', 'thông_số_nợ_trên_tài_sản': 'thong_so_no_tren_tai_san',
        'nợ_vcsh': 'thong_so_no_tren_von_chu_so_huu', 'thông_số_nợ_trên_vốn_chủ_sở_hữu': 'thong_so_no_tren_von_chu_so_huu',
        'ndh_(ndh+vcsh)': 'thong_so_no_dai_han', 'thông_số_nợ_dài_hạn': 'thong_so_no_dai_han',
        'ndh_vcsh': 'no_dai_han_tren_von_chu_so_huu', 'nợ_dài_hạn_trên_vốn_chủ_sở_hữu': 'no_dai_han_tren_von_chu_so_huu',
        'số_lần_đảm_bảo_lãi_vay': 'so_lan_dam_bao_lai_vay',
        'dòng_tiền_từ_hđ_kinh_doanh': 'dtrthdkd', 'dtrthdkd': 'dtrthdkd',
        'dòng_tiền_từ_hđ_đầu_tư': 'dtrthddt', 'dtrthddt': 'dtrthddt',
        'dòng_tiền_từ_hđ_tài_chính': 'dtrthdtc', 'dtrthdtc': 'dtrthdtc',
        'lãi_cơ_bản_trên_1_cổ_phiếu': 'lcbtcp', 'lcbtcp': 'lcbtcp', 'eps': 'lcbtcp'
    }

    # Trả về key chuẩn nếu tìm thấy trong mapping
    if norm in mapping:
        return mapping[norm]

    # Nếu không khớp chính xác, thử tìm key chuẩn trong INDICATOR_COLORS chứa norm
    # Ví dụ: 'tsnh' sẽ khớp với 'tsnh'
    for key in INDICATOR_COLORS:
        if key == norm:
             return key

    # Fallback cuối cùng
    # print(f"Warning: Could not normalize indicator name '{name}', using default color.") # Bỏ comment nếu muốn debug
    return 'default'

# Hàm lấy màu, có fallback về màu default
def get_indicator_color(indicator_name):
    """Lấy màu cho chỉ số dựa trên tên đã chuẩn hóa."""
    normalized_name = _normalize_indicator_name(indicator_name)
    return INDICATOR_COLORS.get(normalized_name, INDICATOR_COLORS['default'])


# --- Hàm vẽ biểu đồ gốc (Cột chồng - Cơ cấu) ---
def ve_bieu_do(df, title, chi_tieu_con):
    """Vẽ biểu đồ cột chồng thể hiện cơ cấu."""
    df = df.copy()
    if not pd.api.types.is_string_dtype(df.index.dtype):
         df["Nam"] = df.index.astype(str)
    else:
         df["Nam"] = df.index

    valid_cols = []
    for col in chi_tieu_con:
        if col in df.columns and pd.api.types.is_numeric_dtype(df[col]):
            valid_cols.append(col)
        # else: # Bỏ cảnh báo nếu không cần thiết
        #     print(f"Cảnh báo: Cột '{col}' không hợp lệ cho biểu đồ '{title}'.")

    if not valid_cols:
        st.info(f"Không có dữ liệu hợp lệ để vẽ biểu đồ: {title}")
        return

    # Kiểm tra nếu tất cả giá trị đều là 0 (hoặc NaN)
    if df[valid_cols].isnull().all().all() or (df[valid_cols].fillna(0).abs().sum().sum() == 0):
         st.info(f"Dữ liệu bằng 0 hoặc không có, không thể vẽ biểu đồ: {title}")
         return

    df["Tổng"] = df[valid_cols].sum(axis=1)

    fig = go.Figure()

    for col in valid_cols:
        label = col # Giữ nguyên tên gốc cho label nếu không có yêu cầu khác
        color = get_indicator_color(col) # Lấy màu nhất quán
        percent = pd.Series(index=df.index, dtype=float)
        mask = df["Tổng"] != 0
        if mask.any():
            # Tính phần trăm, xử lý chia cho 0
            percent[mask] = (df.loc[mask, col].fillna(0) / df.loc[mask, "Tổng"] * 100)
        percent.fillna(0, inplace=True) # Điền 0 cho các trường hợp NaN hoặc Tổng=0

        fig.add_trace(go.Bar(
            x=df["Nam"],
            y=df[col],
            name=label,
            marker_color=color, # Sử dụng màu đã lấy
            text=percent.round(1).astype(str) + '%',
            # Chuẩn hóa hovertemplate, hiển thị giá trị ngay cả khi là NaN/0
            hovertemplate=(
                f"<b>{label}</b><br>"
                f"Năm: %{{x}}<br>"
                f"Giá trị: %{{y:,.0f}}<br>"
                f"Cơ cấu: %{{text}}"
                f"<extra></extra>"
            )
        ))

    fig.update_layout(
        title=dict(text=title, x=0.5, xanchor='center', font=dict(size=20)), # Chuẩn hóa layout
        barmode='stack',
        xaxis=dict(type='category', showgrid=False, zeroline=False, showline=True, linecolor='black'),
        yaxis=dict(tickformat=',.0f', showgrid=False, zeroline=False, showline=True, linecolor='black'),
        plot_bgcolor='white',
        legend=dict(title="", x=0.5, y=1.25, orientation='h', xanchor='center', font=dict(size=10)), # Chuẩn hóa vị trí legend
        margin=dict(l=50, r=50, t=100, b=40), # Chuẩn hóa margin
        height=300 # Chuẩn hóa height
    )
    st.plotly_chart(fig, use_container_width=True)

# --- Hàm vẽ biểu đồ đường (Có thể vẽ nhiều đường) ---
# Thay thế cho hàm vong_quay_tai_san cũ
def ve_bieu_do_duong(df, title, chi_tieu_con, hover_labels=None, y_format='.2f', y_suffix='%'):
    """
    Vẽ biểu đồ đường cho một hoặc nhiều chỉ tiêu.
    Sử dụng màu sắc nhất quán từ INDICATOR_COLORS.
    Đã gộp chức năng của vong_quay_tai_san.
    """
    df = df.copy()
    if not pd.api.types.is_string_dtype(df.index.dtype):
        df["Nam"] = df.index.astype(str)
    else:
        df["Nam"] = df.index

    fig = go.Figure()

    if hover_labels is None:
        hover_labels = chi_tieu_con # Nếu không cung cấp hover_labels, dùng tên cột

    valid_trace_added = False
    for i, col in enumerate(chi_tieu_con):
         if col in df.columns and pd.api.types.is_numeric_dtype(df[col]):
             # Bỏ qua nếu cột toàn NaN
             if df[col].isnull().all():
                 # print(f"Cảnh báo: Cột '{col}' toàn giá trị NaN cho biểu đồ đường '{title}'.")
                 continue

             # Lấy tên hiển thị và màu sắc
             display_name = hover_labels[i] if hover_labels and i < len(hover_labels) else col # Ưu tiên hover_labels nếu có
             color = get_indicator_color(col) # Lấy màu từ bảng màu chung

             fig.add_trace(go.Scatter(
                 x=df["Nam"],
                 y=df[col],
                 name=display_name, # Tên hiển thị trong legend
                 mode='lines+markers',
                 marker=dict(color=color), # Sử dụng màu đã lấy
                 line=dict(color=color), # Đảm bảo màu đường giống màu marker
                 hovertemplate=( # Chuẩn hóa hovertemplate
                     f'<b>{display_name}</b><br>'
                     f'Năm: %{{x}}<br>'
                     f'Giá trị: %{{y:{y_format}}}{y_suffix}'
                     f'<extra></extra>'
                 )
             ))
             valid_trace_added = True
         # else: # Bỏ qua cảnh báo nếu muốn
         #     print(f"Cảnh báo: Cột '{col}' không tồn tại hoặc không phải dạng số cho biểu đồ đường '{title}'.")

    if not valid_trace_added:
        st.info(f"Không có dữ liệu hợp lệ để vẽ biểu đồ: {title}")
        return

    fig.update_layout(
        title=dict(text=title, x=0.5, xanchor='center', font=dict(size=20)), # Chuẩn hóa layout
        xaxis=dict(type='category', showgrid=False, zeroline=False, showline=True, linecolor='black'),
        yaxis=dict(tickformat=y_format, ticksuffix=y_suffix, showgrid=False, zeroline=False, showline=True, linecolor='black'), # Sử dụng y_format và y_suffix
        plot_bgcolor='white',
        legend=dict(x=0.5, y=1.25, orientation='h', xanchor='center', font=dict(size=10)), # Chuẩn hóa layout
        margin=dict(l=50, r=50, t=100, b=40), # Chuẩn hóa layout
        height=300 # Chuẩn hóa layout
    )
    st.plotly_chart(fig, use_container_width=True)

# --- Hàm vẽ biểu đồ cột và đường (2 trục Y) ---
def ve_bieu_do_bar_line(df, title, bar_col, line_col, bar_name, line_name, bar_hover, line_hover, y1_format=',.0f', y2_format='.2f', y1_suffix='', y2_suffix='%'):
    """Vẽ biểu đồ kết hợp cột và đường với 2 trục Y."""
    df = df.copy()
    if not pd.api.types.is_string_dtype(df.index.dtype):
         df["Nam"] = df.index.astype(str)
    else:
         df["Nam"] = df.index

    fig = go.Figure()

    # Lấy màu sắc nhất quán
    bar_color = get_indicator_color(bar_col)
    line_color = get_indicator_color(line_col)

    # Kiểm tra cột tồn tại, là số và không toàn NaN
    bar_valid = bar_col in df.columns and pd.api.types.is_numeric_dtype(df[bar_col]) and not df[bar_col].isnull().all()
    line_valid = line_col in df.columns and pd.api.types.is_numeric_dtype(df[line_col]) and not df[line_col].isnull().all()

    if not bar_valid and not line_valid:
        st.info(f"Không có dữ liệu hợp lệ để vẽ biểu đồ: {title}")
        return

    # Thêm trace cho cột nếu hợp lệ
    if bar_valid:
        fig.add_trace(go.Bar(
            x=df["Nam"],
            y=df[bar_col],
            name=bar_name,
            marker_color=bar_color, # Sử dụng màu đã lấy
            hovertemplate=( # Chuẩn hóa hover
                f'<b>{bar_hover}</b><br>'
                f'Năm: %{{x}}<br>'
                f'Giá trị: %{{y:{y1_format}}}{y1_suffix}'
                f'<extra></extra>'
            ),
            yaxis='y1' # Gán trục y1
        ))

    # Thêm trace cho đường nếu hợp lệ
    if line_valid:
        fig.add_trace(go.Scatter(
            x=df["Nam"],
            y=df[line_col],
            name=line_name,
            mode='lines+markers',
            marker=dict(color=line_color), # Sử dụng màu đã lấy
            line=dict(color=line_color), # Đảm bảo màu đường giống màu marker
            hovertemplate=( # Chuẩn hóa hover
                f'<b>{line_hover}</b><br>'
                f'Năm: %{{x}}<br>'
                f'Giá trị: %{{y:{y2_format}}}{y2_suffix}'
                f'<extra></extra>'
            ),
            yaxis='y2' if bar_valid else 'y1' # Gán trục y2 nếu có cột, ngược lại dùng y1
        ))

    # Cấu hình layout động dựa trên dữ liệu có sẵn
    layout_yaxis = {}
    layout_yaxis2 = {}

    if bar_valid:
        layout_yaxis = dict(
            title=dict(text=bar_name, font=dict(color=bar_color)), # Sử dụng màu động
            tickformat=y1_format, ticksuffix=y1_suffix, # Thêm suffix
            showgrid=False, zeroline=False, showline=True, linecolor='black', # Giữ màu trục đen
            tickfont=dict(color=bar_color) # Màu tick theo màu chỉ số
        )

    if line_valid:
        # Nếu có cả cột và đường, cấu hình trục y2 cho đường
        if bar_valid:
            layout_yaxis2 = dict(
                title=dict(text=line_name, font=dict(color=line_color)), # Sử dụng màu động
                overlaying='y', side='right',
                tickformat=y2_format, ticksuffix=y2_suffix, # Thêm suffix
                showgrid=False, zeroline=False, showline=True, linecolor=line_color, # Màu trục theo màu chỉ số
                tickfont=dict(color=line_color) # Màu tick theo màu chỉ số
            )
        # Nếu chỉ có đường (không có cột), cấu hình trục y1 cho đường
        else:
            layout_yaxis = dict(
                title=dict(text=line_name, font=dict(color=line_color)),
                tickformat=y2_format, ticksuffix=y2_suffix,
                showgrid=False, zeroline=False, showline=True, linecolor='black',
                tickfont=dict(color=line_color)
            )

    fig.update_layout(
        title=dict(text=title, x=0.5, xanchor='center', font=dict(size=20)), # Chuẩn hóa layout
        xaxis=dict(type='category', showgrid=False, zeroline=False, showline=True, linecolor='black'),
        yaxis=layout_yaxis,
        yaxis2=layout_yaxis2 if bar_valid and line_valid else None, # Chỉ thêm yaxis2 nếu cả hai đều hợp lệ
        plot_bgcolor='white',
        legend=dict(x=0.5, y=1.25, orientation='h', xanchor='center', font=dict(size=10)), # Chuẩn hóa layout
        margin=dict(l=50, r=50, t=100, b=40), # Chuẩn hóa layout
        height=300 # Chuẩn hóa layout
    )
    st.plotly_chart(fig, use_container_width=True)

# --- Hàm vẽ biểu đồ cột nhóm ---
def ve_bieu_do_bar_group(df, title, cols, names=None, hovers=None, y_format=',.2f', y_suffix=''):
    """Vẽ biểu đồ cột nhóm cho nhiều chỉ tiêu."""
    df = df.copy()
    if not pd.api.types.is_string_dtype(df.index.dtype):
        df["Nam"] = df.index.astype(str)
    else:
        df["Nam"] = df.index

    fig = go.Figure()

    if names is None: names = cols
    if hovers is None: hovers = names

    valid_cols_data = []
    valid_trace_added = False
    for i, col in enumerate(cols):
        if col in df.columns and pd.api.types.is_numeric_dtype(df[col]):
            # Bỏ qua nếu cột toàn NaN
            if df[col].isnull().all():
                # print(f"Cảnh báo: Cột '{col}' toàn giá trị NaN cho biểu đồ cột nhóm '{title}'.")
                continue
            # Lấy màu từ bảng màu chung
            color = get_indicator_color(col)
            display_name = names[i] if names and i < len(names) else col
            hover_name = hovers[i] if hovers and i < len(hovers) else display_name

            valid_cols_data.append({
                "col": col,
                "name": display_name,
                "hover": hover_name,
                "color": color # Sử dụng màu đã lấy
            })
            valid_trace_added = True
        # else:
        #     print(f"Cảnh báo: Cột '{col}' không hợp lệ cho biểu đồ cột nhóm '{title}'.")


    if not valid_trace_added:
        st.info(f"Không có dữ liệu hợp lệ để vẽ biểu đồ: {title}")
        return

    for data in valid_cols_data:
        fig.add_trace(go.Bar(
            x=df["Nam"],
            y=df[data["col"]],
            name=data["name"],
            marker_color=data["color"], # Màu đã lấy từ dict
            hovertemplate=( # Chuẩn hóa hover
                f'<b>{data["hover"]}</b><br>'
                f'Năm: %{{x}}<br>'
                f'Giá trị: %{{y:{y_format}}}{y_suffix}'
                f'<extra></extra>'
            )
        ))

    fig.update_layout(
        barmode='group', # Giữ nguyên
        title=dict(text=title, x=0.5, xanchor='center', font=dict(size=20)), # Chuẩn hóa layout
        xaxis=dict(type='category', showgrid=False, zeroline=False, showline=True, linecolor='black'),
        yaxis=dict(tickformat=y_format, ticksuffix=y_suffix, showgrid=False, zeroline=False, showline=True, linecolor='black'), # Thêm suffix
        plot_bgcolor='white',
        legend=dict(x=0.5, y=1.25, orientation='h', xanchor='center', font=dict(size=10)), # Chuẩn hóa layout
        margin=dict(l=50, r=50, t=100, b=40), # Chuẩn hóa layout
        height=300 # Chuẩn hóa layout
    )
    st.plotly_chart(fig, use_container_width=True)

# --- Hàm vẽ biểu đồ cột đơn giản ---
# Thay thế cho kha_nang_chi_tra_bang_tien cũ
def ve_bieu_do_bar_simple(df, title, col, name=None, hover=None, y_format=',.2f', y_suffix=''):
    """
    Vẽ biểu đồ cột đơn giản cho một chỉ tiêu.
    Sử dụng màu sắc nhất quán từ INDICATOR_COLORS.
    Đã gộp chức năng của kha_nang_chi_tra_bang_tien.
    """
    df = df.copy()
    if not pd.api.types.is_string_dtype(df.index.dtype):
        df["Nam"] = df.index.astype(str)
    else:
        df["Nam"] = df.index

    # Lấy tên hiển thị và màu sắc
    display_name = name if name is not None else col
    hover_name = hover if hover is not None else display_name
    color = get_indicator_color(col) # Lấy màu từ bảng màu chung

    if col not in df.columns or not pd.api.types.is_numeric_dtype(df[col]):
        st.info(f"Không có dữ liệu hợp lệ ('{col}') để vẽ biểu đồ: {title}")
        return
    if df[col].isnull().all():
         st.info(f"Dữ liệu cho '{col}' toàn giá trị NaN, không thể vẽ biểu đồ: {title}")
         return

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df["Nam"],
        y=df[col],
        name=display_name, # Tên hiển thị trong legend
        marker_color=color, # Sử dụng màu đã lấy
        hovertemplate=( # Chuẩn hóa hover
            f'<b>{hover_name}</b><br>'
            f'Năm: %{{x}}<br>'
            f'Giá trị: %{{y:{y_format}}}{y_suffix}'
            f'<extra></extra>'
        )
    ))

    fig.update_layout(
        title=dict(text=title, x=0.5, xanchor='center', font=dict(size=20)), # Chuẩn hóa layout
        xaxis=dict(type='category', showgrid=False, zeroline=False, showline=True, linecolor='black'),
        yaxis=dict(tickformat=y_format, ticksuffix=y_suffix, showgrid=False, zeroline=False, showline=True, linecolor='black'), # Thêm suffix
        plot_bgcolor='white',
        legend=dict(x=0.5, y=1.25, orientation='h', xanchor='center', font=dict(size=10)), # Chuẩn hóa layout
        margin=dict(l=50, r=50, t=100, b=40), # Chuẩn hóa layout
        height=300 # Chuẩn hóa layout
    )
    st.plotly_chart(fig, use_container_width=True)

# --- Biểu đồ Dupont ROA ---
def ROA_bieu_do_Dupont(df_total):
    """Vẽ biểu đồ Dupont cho ROA."""
    df = df_total.copy()

    if not pd.api.types.is_string_dtype(df.index.dtype):
        df["Nam"] = df.index.astype(str)
    else:
        df["Nam"] = df.index

    # Kiểm tra dữ liệu cần thiết
    required_cols = ['ROA (%)', 'Biên lợi nhuận ròng (%)', 'Vong_quay_tai_san']
    if not all(col in df.columns and pd.api.types.is_numeric_dtype(df[col]) and not df[col].isnull().all() for col in required_cols):
        st.info("Thiếu dữ liệu hoặc dữ liệu không hợp lệ để vẽ biểu đồ Dupont ROA.")
        return

    # Lấy màu
    color_roa = get_indicator_color('ROA (%)')
    color_blnr = get_indicator_color('Biên lợi nhuận ròng (%)')
    color_vqts = get_indicator_color('Vong_quay_tai_san')

    bar_ROA = go.Bar(
        x=df["Nam"],
        y=df['ROA (%)'],
        name='ROA', # Giữ tên ngắn gọn
        hovertemplate='<b>ROA</b><br>Năm: %{x}<br>Giá trị: %{y:.2f}%<extra></extra>',
        marker_color=color_roa) # Màu nhất quán

    line_BLNR = go.Scatter(
        x=df["Nam"],
        y=df['Biên lợi nhuận ròng (%)'],
        name='Biên LN ròng (%)', # Tên ngắn gọn
        mode='lines+markers',
        hovertemplate='<b>Biên LN ròng</b><br>Năm: %{x}<br>Giá trị: %{y:.2f}%<extra></extra>',
        marker=dict(color=color_blnr), # Màu nhất quán
        line=dict(color=color_blnr)
    )
    line_VQTTS = go.Scatter(
        x=df["Nam"],
        y=df['Vong_quay_tai_san'],
        name='Vòng quay TS', # Tên ngắn gọn
        mode='lines+markers',
        marker=dict(color=color_vqts), # Màu nhất quán
        line=dict(color=color_vqts),
        hovertemplate='<b>Vòng quay TS</b><br>Năm: %{x}<br>Giá trị: %{y:.2f} lần<extra></extra>', # Thêm đơn vị "lần"
        yaxis='y2' # Trục y2
    )
    # Kết hợp hai biểu đồ
    fig = go.Figure(data=[bar_ROA, line_BLNR, line_VQTTS])

    # Cấu hình layout
    fig.update_layout(
        title=dict(
            text='Phân tích ROA (Dupont)', # Tiêu đề rõ ràng hơn
            x=0.5,
            xanchor='center',
            font=dict(size=20) # Chuẩn hóa size
        ),
        xaxis=dict(
            type='category', # Đảm bảo là category
            showgrid=False,
            zeroline=False,
            showline=True,
            linecolor='black'
        ),
        yaxis=dict(
            title=dict(text="ROA / Biên LN ròng", font=dict(color='black')), # Gộp title trục Y1
            tickformat='.2f', # Định dạng số thập phân
            ticksuffix='%', # Thêm suffix %
            showgrid=False,
            zeroline=False,
            showline=True,
            linecolor='black',
            # tickfont=dict(color='black') # Giữ màu đen cho dễ đọc
        ),
        yaxis2=dict(
            title=dict(text="Vòng quay TS (lần)", font=dict(color=color_vqts)), # Title trục Y2
            overlaying='y',
            side='right',
            tickformat='.2f', # Định dạng số thập phân
            ticksuffix=' lần', # Thêm suffix lần
            showgrid=False,
            zeroline=False,
            showline=True, # Hiển thị đường trục
            linecolor=color_vqts, # Màu trục theo màu chỉ số
            tickfont=dict(color=color_vqts) # Màu tick theo màu chỉ số
        ),
        plot_bgcolor='white',
        legend=dict(x=0.5, y=1.25, orientation='h', xanchor='center', font=dict(size=10)), # Chuẩn hóa legend
        margin=dict(l=60, r=60, t=100, b=40), # Chuẩn hóa margin
        height=300 # Chuẩn hóa height
    )

    st.plotly_chart(fig, use_container_width=True)

# --- Biểu đồ Dupont ROE ---
def ROE_bieu_do_Dupont(df_total):
    """Vẽ biểu đồ Dupont cho ROE."""
    df = df_total.copy()

    if not pd.api.types.is_string_dtype(df.index.dtype):
        df["Nam"] = df.index.astype(str)
    else:
        df["Nam"] = df.index

    # Kiểm tra dữ liệu cần thiết
    required_cols = ['ROE (%)', 'Biên lợi nhuận ròng (%)', 'Vong_quay_tai_san', 'Đòn bẩy tài chính']
    if not all(col in df.columns and pd.api.types.is_numeric_dtype(df[col]) and not df[col].isnull().all() for col in required_cols):
        st.info("Thiếu dữ liệu hoặc dữ liệu không hợp lệ để vẽ biểu đồ Dupont ROE.")
        return

    # Lấy màu
    color_roe = get_indicator_color('ROE (%)')
    color_blnr = get_indicator_color('Biên lợi nhuận ròng (%)')
    color_vqts = get_indicator_color('Vong_quay_tai_san')
    color_dbtc = get_indicator_color('Đòn bẩy tài chính')

    bar_ROE = go.Bar(
        x=df['Nam'],
        y=df['ROE (%)'],
        name='ROE', # Tên ngắn gọn
        hovertemplate='<b>ROE</b><br>Năm: %{x}<br>Giá trị: %{y:.2f}%<extra></extra>',
        marker=dict(color=color_roe), # Màu nhất quán
        yaxis='y1' # Trục y1
        )
    line_BLNR = go.Scatter(
        x=df['Nam'],
        y=df['Biên lợi nhuận ròng (%)'],
        name='Biên LN ròng (%)', # Tên ngắn gọn
        mode='lines+markers',
        hovertemplate='<b>Biên LN ròng</b><br>Năm: %{x}<br>Giá trị: %{y:.2f}%<extra></extra>',
        marker=dict(color=color_blnr), # Màu nhất quán
        line=dict(color=color_blnr),
        yaxis='y1' # Trục y1
    )
    line_VQTS = go.Scatter(
        x=df['Nam'],
        y=df['Vong_quay_tai_san'],
        name='Vòng quay TS', # Tên ngắn gọn
        mode='lines+markers',
        marker=dict(color=color_vqts), # Màu nhất quán
        line=dict(color=color_vqts),
        hovertemplate='<b>Vòng quay TS</b><br>Năm: %{x}<br>Giá trị: %{y:.2f} lần<extra></extra>', # Thêm đơn vị "lần"
        yaxis='y2' # Trục y2
    )
    line_DBTC = go.Scatter(
        x=df['Nam'],
        y=df["Đòn bẩy tài chính"],
        name='Đòn bẩy TC', # Tên ngắn gọn
        mode='lines+markers',
        marker=dict(color=color_dbtc), # Màu nhất quán
        line=dict(color=color_dbtc),
        hovertemplate='<b>Đòn bẩy TC</b><br>Năm: %{x}<br>Giá trị: %{y:.2f} lần<extra></extra>', # Thêm đơn vị "lần"
        yaxis='y2' # Trục y2
    )

    # Kết hợp các biểu đồ
    fig = go.Figure(data=[bar_ROE, line_BLNR, line_VQTS, line_DBTC])

    # Cấu hình layout
    fig.update_layout(
        title=dict(
            text='Phân tích ROE (Dupont)', # Tiêu đề rõ ràng hơn
            x=0.5,
            xanchor='center',
            font=dict(size=20) # Chuẩn hóa size
        ),
        xaxis=dict(
            type='category', # Đảm bảo là category
            showgrid=False,
            zeroline=False,
            showline=True,
            linecolor='black'
        ),
        yaxis=dict(
            title=dict(text="ROE / Biên LN ròng", font=dict(color='black')), # Gộp title trục Y1
            tickformat='.2f', # Định dạng số thập phân
            ticksuffix='%', # Thêm suffix %
            showgrid=False,
            zeroline=False,
            showline=True,
            linecolor='black',
            # tickfont=dict(color='black') # Giữ màu đen cho dễ đọc
        ),
        yaxis2=dict(
            title=dict(text="Vòng quay TS / Đòn bẩy TC (lần)", font=dict(color='black')), # Gộp title trục Y2
            overlaying='y',
            side='right',
            tickformat='.2f', # Định dạng số thập phân
            ticksuffix=' lần', # Thêm suffix lần
            showgrid=False,
            zeroline=False,
            showline=True, # Hiển thị đường trục
            linecolor='black', # Giữ màu đen cho dễ đọc
            # tickfont=dict(color='black') # Giữ màu đen cho dễ đọc
        ),
        plot_bgcolor='white',
        legend=dict(x=0.5, y=1.25, orientation='h', xanchor='center', font=dict(size=10)), # Chuẩn hóa legend
        margin=dict(l=60, r=60, t=100, b=40), # Chuẩn hóa margin
        height=300 # Chuẩn hóa height
    )

    st.plotly_chart(fig, use_container_width=True)

# --- Biểu đồ Vòng quay và Kỳ thanh toán bình quân ---
def vong_quay_va_ky_thanh_toan_binh_quan(df_total):
    """Vẽ biểu đồ Vòng quay phải trả và Kỳ thanh toán bình quân."""
    df = df_total.copy()

    if not pd.api.types.is_string_dtype(df.index.dtype):
        df["Nam"] = df.index.astype(str)
    else:
        df["Nam"] = df.index

    # Kiểm tra dữ liệu
    bar_col = "Kỳ thanh toán bình quân"
    line_col = "Vòng quay phải trả người bán"
    if not (bar_col in df.columns and pd.api.types.is_numeric_dtype(df[bar_col]) and not df[bar_col].isnull().all() and \
            line_col in df.columns and pd.api.types.is_numeric_dtype(df[line_col]) and not df[line_col].isnull().all()):
        st.info("Thiếu dữ liệu hoặc dữ liệu không hợp lệ để vẽ biểu đồ Vòng quay và kỳ thanh toán bình quân.")
        return

    # Lấy màu
    color_bar = get_indicator_color(bar_col)
    color_line = get_indicator_color(line_col)

    # Tạo biểu đồ cột
    bar_KTTBQ = go.Bar(
        x=df['Nam'],
        y=df[bar_col],
        name='Kỳ thanh toán BQ (ngày)', # Tên rõ ràng hơn
        marker_color=color_bar, # Màu nhất quán
        hovertemplate='<b>Kỳ thanh toán BQ</b><br>Năm: %{x}<br>Giá trị: %{y:.1f} ngày<extra></extra>', # Format .1f
        yaxis='y1'
    )

    # Tạo biểu đồ đường
    line_VQPTNB = go.Scatter(
        x=df['Nam'],
        y=df[line_col],
        name='Vòng quay PTNB (lần)', # Tên rõ ràng hơn
        mode='lines+markers',
        marker=dict(color=color_line), # Màu nhất quán
        line=dict(color=color_line),
        hovertemplate='<b>Vòng quay PTNB</b><br>Năm: %{x}<br>Giá trị: %{y:.2f} lần<extra></extra>', # Format .2f
        yaxis='y2'
    )

    # Kết hợp hai biểu đồ
    fig = go.Figure(data=[bar_KTTBQ, line_VQPTNB])

    # Cấu hình layout
    fig.update_layout(
        title=dict(
        text='Vòng quay và Kỳ thanh toán bình quân',
        x=0.5,
        xanchor='center',
        font=dict(size=20) # Chuẩn hóa size
        ),
        xaxis=dict(
            type='category', # Đảm bảo là category
            showgrid=False,
            zeroline=False,
            showline=True,
            linecolor='black'
        ),
        yaxis=dict(
            title=dict(text="Kỳ thanh toán BQ (ngày)", font=dict(color=color_bar)), # Title trục Y1
            tickformat='.1f', # Format .1f
            ticksuffix=' ngày',
            showgrid=False,
            zeroline=False,
            showline=True,
            linecolor='black', # Trục màu đen
            tickfont=dict(color=color_bar) # Tick màu theo chỉ số
        ),
        yaxis2=dict(
            title=dict(text="Vòng quay PTNB (lần)", font=dict(color=color_line)), # Title trục Y2
            overlaying='y',
            side='right',
            tickformat='.2f', # Format .2f
            ticksuffix=' lần',
            showgrid=False,
            zeroline=False,
            showline=True, # Hiển thị đường trục
            linecolor=color_line, # Màu trục theo màu chỉ số
            tickfont=dict(color=color_line) # Tick màu theo chỉ số
        ),
        plot_bgcolor='white',
        legend=dict(x=0.5, y=1.25, orientation='h', xanchor='center', font=dict(size=10)), # Chuẩn hóa legend
        margin=dict(l=60, r=60, t=100, b=40), # Chuẩn hóa margin
        height=300 # Chuẩn hóa height
    )

    st.plotly_chart(fig, use_container_width=True)

# --- Xóa các hàm không cần thiết ---
# Hàm vong_quay_tai_san đã được gộp vào ve_bieu_do_duong
# Hàm kha_nang_chi_tra_bang_tien đã được gộp vào ve_bieu_do_bar_simple
