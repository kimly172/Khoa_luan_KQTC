import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st

# --- Hàm vẽ biểu đồ gốc (Cột chồng - Cơ cấu) ---
def ve_bieu_do(df, title, chi_tieu_con):
    df = df.copy()
    if not pd.api.types.is_string_dtype(df.index.dtype):
         df["Nam"] = df.index.astype(str)
    else:
         df["Nam"] = df.index

    valid_cols = []
    for col in chi_tieu_con:
        if col in df.columns and pd.api.types.is_numeric_dtype(df[col]):
            valid_cols.append(col)

    if not valid_cols:
        st.info(f"Không có dữ liệu hợp lệ để vẽ biểu đồ: {title}")
        return

    if not df[valid_cols].empty and (df[valid_cols].abs().sum().sum() == 0): # Kiểm tra tổng tuyệt đối
         st.info(f"Dữ liệu bằng 0, không thể vẽ biểu đồ: {title}")
         return

    df["Tổng"] = df[valid_cols].sum(axis=1)

    fig = go.Figure()

    for col in valid_cols:
        label = col
        percent = pd.Series(index=df.index, dtype=float)
        mask = df["Tổng"] != 0
        if mask.any():
            percent[mask] = (df.loc[mask, col] / df.loc[mask, "Tổng"] * 100)
        percent.fillna(0, inplace=True)

        fig.add_trace(go.Bar(
            x=df["Nam"],
            y=df[col],
            name=label,
            text=percent.round(1).astype(str) + '%',
            hovertemplate=f"{label}<br>Năm: %{{x}}<br>Giá trị: %{{y:,.0f}}<br>Cơ cấu: %{{text}}<extra></extra>",
        ))

    fig.update_layout(
        title=dict(text=title, x=0.5, xanchor='center', font=dict(size=20)), # Giảm size title
        barmode='stack',
        xaxis=dict(type='category', showgrid=False, zeroline=False, showline=True, linecolor='black'),
        yaxis=dict(tickformat=',.0f', showgrid=False, zeroline=False, showline=True, linecolor='black'),
        plot_bgcolor='white',
        legend=dict(title="", x=0.5, y=1.12, orientation='h', xanchor='center', font=dict(size=10)), # Tăng y, giảm size legend
        margin=dict(l=50, r=50, t=100, b=40), # Tăng t margin
        height=300 # Giảm height
    )
    st.plotly_chart(fig, use_container_width=True)

# --- Hàm vẽ biểu đồ đường ---
def ve_bieu_do_duong(df, title, chi_tieu_con, hover_labels=None, y_label='%'):
    df = df.copy()
    if not pd.api.types.is_string_dtype(df.index.dtype):
        df["Nam"] = df.index.astype(str)
    else:
        df["Nam"] = df.index

    fig = go.Figure()
    colors = px.colors.qualitative.Plotly # Bảng màu

    if hover_labels is None:
        hover_labels = chi_tieu_con

    for i, col in enumerate(chi_tieu_con):
         if col in df.columns and pd.api.types.is_numeric_dtype(df[col]):
             hover_name = hover_labels[i] if i < len(hover_labels) else col
             fig.add_trace(go.Scatter(
                 x=df["Nam"],
                 y=df[col],
                 name=col, # Tên hiển thị trong legend
                 mode='lines+markers',
                 marker=dict(color=colors[i % len(colors)]),
                 hovertemplate=f'Năm: %{{x}}<br>{hover_name}: %{{y:.2f}}{y_label}<extra></extra>'
             ))
         # else: # Bỏ qua cảnh báo
         #     print(f"Cảnh báo: Cột '{col}' không tồn tại hoặc không phải dạng số cho biểu đồ đường '{title}'.")

    if not fig.data:
        st.info(f"Không có dữ liệu hợp lệ để vẽ biểu đồ: {title}")
        return

    fig.update_layout(
        title=dict(text=title, x=0.5, xanchor='center', font=dict(size=20)),
        xaxis=dict(type='category', showgrid=False, zeroline=False, showline=True, linecolor='black'),
        yaxis=dict(tickformat=f',.2f{y_label}', showgrid=False, zeroline=False, showline=True, linecolor='black'),
        plot_bgcolor='white',
        legend=dict(x=0.5, y=1.15, orientation='h', xanchor='center', font=dict(size=10)),
        margin=dict(l=50, r=50, t=100, b=40),
        height=300
    )
    st.plotly_chart(fig, use_container_width=True)

# --- Hàm vẽ biểu đồ cột và đường (2 trục Y) ---
def ve_bieu_do_bar_line(df, title, bar_col, line_col, bar_name, line_name, bar_hover, line_hover, y1_format=',.0f', y2_format='.2f', y1_suffix='', y2_suffix='%'):
    df = df.copy()
    if not pd.api.types.is_string_dtype(df.index.dtype):
         df["Nam"] = df.index.astype(str)
    else:
         df["Nam"] = df.index

    fig = go.Figure()

    # Kiểm tra cột tồn tại và là số
    bar_valid = bar_col in df.columns and pd.api.types.is_numeric_dtype(df[bar_col])
    line_valid = line_col in df.columns and pd.api.types.is_numeric_dtype(df[line_col])

    if not bar_valid and not line_valid:
        st.info(f"Không có dữ liệu hợp lệ để vẽ biểu đồ: {title}")
        return

    if bar_valid:
        fig.add_trace(go.Bar(
            x=df["Nam"],
            y=df[bar_col],
            name=bar_name,
            marker_color='skyblue',
            hovertemplate=f'Năm: %{{x}}<br>{bar_hover}: %{{y:{y1_format}}}{y1_suffix}<extra></extra>',
            yaxis='y1'
        ))

    if line_valid:
        fig.add_trace(go.Scatter(
            x=df["Nam"],
            y=df[line_col],
            name=line_name,
            mode='lines+markers',
            marker=dict(color='crimson'),
            hovertemplate=f'Năm: %{{x}}<br>{line_hover}: %{{y:{y2_format}}}{y2_suffix}<extra></extra>',
            yaxis='y2'
        ))

    fig.update_layout(
        title=dict(text=title, x=0.5, xanchor='center', font=dict(size=20)),
        xaxis=dict(type='category', showgrid=False, zeroline=False, showline=True, linecolor='black'),
        yaxis=dict(
            title=dict(text=bar_name, font=dict(color='skyblue')), # Sửa lỗi: Đặt font trong title
            tickformat=y1_format,
            showgrid=False, zeroline=False, showline=True, linecolor='black',
            tickfont=dict(color='skyblue')
        ),
        yaxis2=dict(
            title=dict(text=line_name, font=dict(color='crimson')), # Sửa lỗi: Đặt font trong title
            overlaying='y', side='right',
            tickformat=y2_format,
            showgrid=False, zeroline=False, showline=True, linecolor='crimson',
            tickfont=dict(color='crimson')
        ),
        plot_bgcolor='white',
        legend=dict(x=0.5, y=1.15, orientation='h', xanchor='center', font=dict(size=10)),
        margin=dict(l=50, r=50, t=100, b=40),
        height=300
    )
    st.plotly_chart(fig, use_container_width=True)

# --- Hàm vẽ biểu đồ cột nhóm ---
def ve_bieu_do_bar_group(df, title, cols, names=None, hovers=None, y_format=',.2f', y_suffix=''):
    df = df.copy()
    if not pd.api.types.is_string_dtype(df.index.dtype):
        df["Nam"] = df.index.astype(str)
    else:
        df["Nam"] = df.index

    fig = go.Figure()
    colors = px.colors.qualitative.Plotly

    if names is None: names = cols
    if hovers is None: hovers = names

    valid_cols_data = []
    for i, col in enumerate(cols):
        if col in df.columns and pd.api.types.is_numeric_dtype(df[col]):
            valid_cols_data.append({
                "col": col,
                "name": names[i] if i < len(names) else col,
                "hover": hovers[i] if i < len(hovers) else names[i] if i < len(names) else col,
                "color": colors[i % len(colors)]
            })

    if not valid_cols_data:
        st.info(f"Không có dữ liệu hợp lệ để vẽ biểu đồ: {title}")
        return

    for data in valid_cols_data:
        fig.add_trace(go.Bar(
            x=df["Nam"],
            y=df[data["col"]],
            name=data["name"],
            marker_color=data["color"],
            hovertemplate=f'Năm: %{{x}}<br>{data["hover"]}: %{{y:{y_format}}}{y_suffix}<extra></extra>'
        ))

    fig.update_layout(
        barmode='group',
        title=dict(text=title, x=0.5, xanchor='center', font=dict(size=20)),
        xaxis=dict(type='category', showgrid=False, zeroline=False, showline=True, linecolor='black'),
        yaxis=dict(tickformat=y_format, showgrid=False, zeroline=False, showline=True, linecolor='black'),
        plot_bgcolor='white',
        legend=dict(x=0.5, y=1.15, orientation='h', xanchor='center', font=dict(size=10)),
        margin=dict(l=50, r=50, t=100, b=40),
        height=300
    )
    st.plotly_chart(fig, use_container_width=True)

# --- Hàm vẽ biểu đồ cột đơn giản ---
def ve_bieu_do_bar_simple(df, title, col, name=None, hover=None, y_format=',.2f', y_suffix=''):
    df = df.copy()
    if not pd.api.types.is_string_dtype(df.index.dtype):
        df["Nam"] = df.index.astype(str)
    else:
        df["Nam"] = df.index

    if name is None: name = col
    if hover is None: hover = name

    if col not in df.columns or not pd.api.types.is_numeric_dtype(df[col]):
        st.info(f"Không có dữ liệu hợp lệ ('{col}') để vẽ biểu đồ: {title}")
        return

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df["Nam"],
        y=df[col],
        name=name,
        marker_color='skyblue',
        hovertemplate=f'Năm: %{{x}}<br>{hover}: %{{y:{y_format}}}{y_suffix}<extra></extra>'
    ))

    fig.update_layout(
        title=dict(text=title, x=0.5, xanchor='center', font=dict(size=20)),
        xaxis=dict(type='category', showgrid=False, zeroline=False, showline=True, linecolor='black'),
        yaxis=dict(tickformat=y_format, showgrid=False, zeroline=False, showline=True, linecolor='black'),
        plot_bgcolor='white',
        legend=dict(x=0.5, y=1.15, orientation='h', xanchor='center', font=dict(size=10)),
        margin=dict(l=50, r=50, t=100, b=40),
        height=300
    )
    st.plotly_chart(fig, use_container_width=True)
        
def ROA_bieu_do_Dupont(df_total):
    df = df_total.copy()

    if not pd.api.types.is_string_dtype(df.index.dtype):
        df["Nam"] = df.index.astype(str)
    else:
        df["Nam"] = df.index

    bar_ROA = go.Bar(
        x=df["Nam"],
        y=df['ROA (%)'],
        name='ROA',
        hovertemplate='Năm: %{x}<br>ROA: %{y:.2f}%<extra></extra>',
        marker_color='skyblue')

    line_BLNR = go.Scatter(
        x=df["Nam"],
        y=df['Biên lợi nhuận ròng (%)'],
        name='Biên lợi nhuận ròng (%)',
        mode='lines+markers',
        hovertemplate='Năm: %{x}<br>Biên lợi nhuận ròng: %{y:.2f}%<extra></extra>',
        marker=dict(color='red'),
    )
    line_VQTTS = go.Scatter(
        x=df["Nam"],
        y=df['Vong_quay_tai_san'],
        name='Vòng quay tổng tài sản',
        mode='lines+markers',
        marker=dict(color='blue'),
        hovertemplate='Năm: %{x}<br>Vòng quay tổng tài sản: %{y:.2f}<extra></extra>',
        yaxis='y2'
    )
    # Kết hợp hai biểu đồ
    fig = go.Figure(data=[bar_ROA, line_BLNR,line_VQTTS])

    # Cấu hình layout
    fig.update_layout(
        title=dict(
            text='ROA theo mô hình Dupont ',
            x=0.5,
            xanchor='center',
            font=dict(size=22)
        ),
        xaxis=dict(
            showgrid=False,
            zeroline=False,
            showline=True,
            linecolor='black'
        ),
        yaxis=dict(

            tickformat=',.2f%',
            showgrid=False,
            zeroline=False,
            showline=True,
            linecolor='black'
        ),
        yaxis2=dict(
            overlaying='y',
            side='right',
            tickformat='.2f',
            showgrid=False,
            zeroline=False,
            tickfont=dict(color='crimson'),
            showline=True,
            linecolor='crimson'
        ),
        plot_bgcolor='white',
        legend=dict(x=0.5, y=1.1, orientation='h', xanchor='center'),
        margin=dict(l=60, r=60, t=80, b=40),
        height=300
    )

    st.plotly_chart(fig, use_container_width=True)
    
def ROE_bieu_do_Dupont(df_total):  
    df = df_total.copy()

    if not pd.api.types.is_string_dtype(df.index.dtype):
        df["Nam"] = df.index.astype(str)
    else:
        df["Nam"] = df.index  
        
    bar_ROE = go.Bar(
        x=df['Nam'],
        y=df['ROE (%)'],
        name='ROE (%)',
        hovertemplate='Năm: %{x}<br>ROE: %{y:.2f}%<extra></extra>',
        marker=dict(color='green'),
        )
    line_VQTS = go.Scatter(
        x=df['Nam'],
        y=df['Vong_quay_tai_san'],
        name='Vòng quay tổng tài sản',
        mode='lines+markers',
        marker=dict(color='blue'),
        hovertemplate='Năm: %{x}<br>Vòng quay tổng tài sản: %{y:.2f}<extra></extra>',
        yaxis='y2'
    )
    line_DBTC = go.Scatter(
        x=df['Nam'],
        y=df["Đòn bẩy tài chính"],
        name='Đòn bẩy tài chính',
        mode='lines+markers',
        marker=dict(color='brown'),
        hovertemplate='Năm: %{x}<br>Đòn bẩy tài chính: %{y:.2f}<extra></extra>',
        yaxis='y2'
    )
    line_BLNR = go.Scatter(
        x=df['Nam'],
        y=df['Biên lợi nhuận ròng (%)'],
        name='Biên lợi nhuận ròng (%)',
        mode='lines+markers',
        hovertemplate='Năm: %{x}<br>Biên lợi nhuận ròng: %{y:.2f}%<extra></extra>',
        marker=dict(color='red'),
    )
    # Kết hợp hai biểu đồ
    fig = go.Figure(data=[bar_ROE, line_DBTC,line_VQTS,line_BLNR])

    # Cấu hình layout
    fig.update_layout(
        title=dict(
            text='ROA theo mô hình Dupont ',
            x=0.5,
            xanchor='center',
            font=dict(size=22)
        ),
        xaxis=dict(
            showgrid=False,
            zeroline=False,
            showline=True,
            linecolor='black'
        ),
        yaxis=dict(

            tickformat=',.2f%',
            showgrid=False,
            zeroline=False,
            showline=True,
            linecolor='black'
        ),
        yaxis2=dict(
            overlaying='y',
            side='right',
            tickformat='.2f',
            showgrid=False,
            zeroline=False,
            tickfont=dict(color='crimson'),

            showline=True,
            linecolor='crimson'
        ),
        plot_bgcolor='white',
        legend=dict(x=0.5, y=1.1, orientation='h', xanchor='center'),
        margin=dict(l=60, r=60, t=80, b=40),
        height=300
    )

    st.plotly_chart(fig, use_container_width=True)
    
def vong_quay_tai_san(df_total):
    df = df_total.copy()

    if not pd.api.types.is_string_dtype(df.index.dtype):
        df["Nam"] = df.index.astype(str)
    else:
        df["Nam"] = df.index
        
    line1 = go.Scatter(
        x=df['Nam'],
        y=df['Vong_quay_tai_san'],
        name='Vòng quay tổng tài sản',
        mode='lines+markers',
        marker=dict(color='seagreen'),
        hovertemplate='Năm: %{x}<br>Vòng quay tổng tài sản: %{y:.2f}<extra></extra>'
    )

    line2 = go.Scatter(
        x=df['Nam'],
        y=df['Vong_quay_TSCD'],
        name='Vòng quay tài sản cố định',
        marker=dict(color='skyblue'),  # hoặc '#2E8B57'
        mode='lines+markers',
        hovertemplate='Năm: %{x}<br>Vòng quay TSCĐ: %{y:.2f}<extra></extra>'
    )

    fig = go.Figure(data=[line1, line2])

    fig.update_layout(
        title=dict(
            text='Vòng quay tài sản',
            x=0.5,
            xanchor='center',
            font=dict(size=22)
        ),
        xaxis=dict(
            showgrid=False,
            zeroline=False,
            showline=True,
            linecolor='black'
        ),
        yaxis=dict(

            tickformat=',.0f',
            showgrid=False,
            zeroline=False,
            showline=True,
            linecolor='black'
        ),
        plot_bgcolor='white',
        legend=dict(x=0.5, y=1.1, orientation='h', xanchor='center'),
        margin=dict(l=60, r=60, t=80, b=40),
        height=300
    )

    st.plotly_chart(fig, use_container_width=True)

def kha_nang_chi_tra_bang_tien(df_total):
    df = df_total.copy()

    if not pd.api.types.is_string_dtype(df.index.dtype):
        df["Nam"] = df.index.astype(str)
    else:
        df["Nam"] = df.index
        
    bar = go.Bar(
        x=df['Nam'],
        y=df["Khả năng chi trả bằng tiền"],
        name="Khả năng chi trả bằng tiền",
        marker_color='skyblue',
        hovertemplate='Năm: %{x}<br>Khả năng chi trả bằng tiền: %{y:.2f} <extra></extra>',
        yaxis='y1'
    )
    # Tạo biểu đồ
    fig = go.Figure(data=[bar])

    # Layout đẹp hơn
    fig.update_layout(
        title=dict(
            text='Khả năng chi trả bằng tiền',
            x=0.5,
            xanchor='center',
            font=dict(size=22)
        ),
        xaxis=dict(
            showgrid=False,
            zeroline=False,
            showline=True,
            linecolor='black'
        ),
        yaxis=dict(

            tickformat=',.2f',
            showgrid=False,
            zeroline=False,
            showline=True,
            linecolor='black'
        ),
    
        plot_bgcolor='white',
        legend=dict(x=0.5, y=1.1, orientation='h', xanchor='center'),
        margin=dict(l=60, r=60, t=80, b=40),
        height=300
    )

    st.plotly_chart(fig, use_container_width=True)



def vong_quay_va_ky_thanh_toan_binh_quan(df_total):
    df = df_total.copy()

    if not pd.api.types.is_string_dtype(df.index.dtype):
        df["Nam"] = df.index.astype(str)
    else:
        df["Nam"] = df.index
    # Tạo biểu đồ cột
    bar_KTTBQ = go.Bar(
        x=df['Nam'],
        y=df["Kỳ thanh toán bình quân"],
        name='Kỳ thanh toán bình quân',
        marker_color='skyblue',
        hovertemplate='Năm: %{x}<br>Chu kỳ: %{y:.2f} ngày<extra></extra>',
        yaxis='y1'
    )

    # Tạo biểu đồ đường (tăng trưởng %)
    line_VQPTNB = go.Scatter(
        x=df['Nam'],
        y=df["Vòng quay phải trả người bán"],
        name='Vòng quay phải trả người bán',
        mode='lines+markers',
        marker=dict(color='red'),
        hovertemplate='Năm: %{x}<br>Vòng quay: %{y:.2f}<extra></extra>',
        yaxis='y2'
    )

    # Kết hợp hai biểu đồ
    fig = go.Figure(data=[bar_KTTBQ, line_VQPTNB])

    # Cấu hình layout
    fig.update_layout(
        title=dict(
        text='Vòng quay và kỳ thanh toán bình quân',
        x=0.5,
        xanchor='center',
        font=dict(size=22)
        ),
        xaxis=dict(
            showgrid=False,
            zeroline=False,
            showline=True,
            linecolor='black'
        ),
        yaxis=dict(

            tickformat=',.0f',
            showgrid=False,
            zeroline=False,
            showline=True,
            linecolor='black'
        ),
        yaxis2=dict(
            overlaying='y',
            side='right',
            tickformat='.1f',
            showgrid=False,
            zeroline=False,
            tickfont=dict(color='crimson'),

            showline=True,
            linecolor='crimson'
        ),
        plot_bgcolor='white',
        legend=dict(x=0.5, y=1.1, orientation='h', xanchor='center'),
        margin=dict(l=60, r=60, t=80, b=40),
        height=300
    )

    st.plotly_chart(fig, use_container_width=True)
