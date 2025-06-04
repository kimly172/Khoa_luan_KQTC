import streamlit as st
import pandas as pd

def display_financial_metrics():
    st.header("GIẢI THÍCH CÁC THÔNG SỐ TÀI CHÍNH📊")
    st.markdown("""
    Trang này cung cấp giải thích chi tiết về các thông số tài chính được sử dụng trong phân tích và dự báo.
    Việc hiểu rõ ý nghĩa của từng chỉ số sẽ giúp bạn đánh giá tình hình tài chính của doanh nghiệp một cách toàn diện hơn.
    """)

    # Dữ liệu mô tả các chỉ số tài chính
    data = {
        "Nhóm thông số": [
            "THÔNG SỐ KHẢ NĂNG SINH LỜI", "THÔNG SỐ KHẢ NĂNG SINH LỜI", "THÔNG SỐ KHẢ NĂNG SINH LỜI", "THÔNG SỐ KHẢ NĂNG SINH LỜI", "THÔNG SỐ KHẢ NĂNG SINH LỜI",
            "THÔNG SỐ THỊ TRƯỜNG",
            "THÔNG SỐ HOẠT ĐỘNG", "THÔNG SỐ HOẠT ĐỘNG", "THÔNG SỐ HOẠT ĐỘNG", "THÔNG SỐ HOẠT ĐỘNG", "THÔNG SỐ HOẠT ĐỘNG", "THÔNG SỐ HOẠT ĐỘNG", "THÔNG SỐ HOẠT ĐỘNG", "THÔNG SỐ HOẠT ĐỘNG",
            "THÔNG SỐ KHẢ NĂNG THANH TOÁN", "THÔNG SỐ KHẢ NĂNG THANH TOÁN",
            "THÔNG SỐ NỢ", "THÔNG SỐ NỢ", "THÔNG SỐ NỢ", "THÔNG SỐ NỢ"
        ],
        "Tên thông số": [
            "Lợi nhuận gộp biên",
            "Lợi nhuận hoạt động biên",
            "Lợi nhuận ròng biên",
            "Thu nhập trên tổng tài sản (ROA)",
            "Thu nhập trên vốn chủ (ROE)",
            "Lãi cơ bản trên cổ phiếu lưu hành (EPS)",
            "Vòng quay khoản phải thu",
            "Kỳ thu tiền bình quân",
            "Vòng quay hàng tồn kho",
            "Chu kỳ chuyển hóa tiền mặt của tồn kho",
            "Vòng quay phải trả người bán",
            "Kỳ thanh toán bình quân",
            "Vòng quay TSCĐ",
            "Vòng quay tổng tài sản",
            "Khả năng thanh toán hiện thời",
            "Khả năng thanh toán nhanh",
            "Thông số nợ trên VCSH",
            "Thông số nợ trên tài sản",
            "Thông số nợ dài hạn trên vốn dài hạn",
            "Số lần đảm bảo lãi vay"
        ],
        "Công thức và ý nghĩa": [
            "Lợi nhuận gộp biên là một chỉ số tài chính quan trọng, dùng để đo lường khả năng sinh lời từ hoạt động kinh doanh chính của doanh nghiệp. Đây là thước đo cho thấy mỗi đồng doanh thu tạo ra bao nhiêu lợi nhuận trước khi tính đến các chi phí khác như chi phí bán hàng, quản lý, lãi vay và thuế.<br><b>Công thức:</b> <i>Lợi nhuận gộp biên = Lợi nhuận gộp / Doanh thu</i>",
            "Lợi nhuận hoạt động biên là chỉ số tài chính quan trọng, dùng để đo lường khả năng sinh lời của một công ty từ hoạt động kinh doanh chính, trước khi tính đến các chi phí tài chính (như lãi vay) và thuế. Chỉ số này cho biết mỗi đồng doanh thu mà công ty kiếm được có bao nhiêu đồng là lợi nhuận từ hoạt động kinh doanh chính.<br><b>Công thức:</b> <i>Lợi nhuận hoạt động biên = Lợi nhuận thuần từ hoạt động kinh doanh / Doanh thu</i>",
            "Lợi nhuận ròng biên là một chỉ số tài chính quan trọng đo lường khả năng sinh lời cuối cùng của một doanh nghiệp sau khi đã trừ tất cả các chi phí, bao gồm chi phí hoạt động, chi phí tài chính, thuế và các chi phí khác. Chỉ số này cho biết mỗi đồng doanh thu mang lại bao nhiêu đồng lợi nhuận ròng thực tế cho công ty.<br><b>Công thức:</b> <i>Lợi nhuận ròng biên = Lợi nhuận sau thuế / Doanh thu</i>",
            "ROA đo lường khả năng tạo ra lợi nhuận từ mỗi đồng tài sản mà công ty sở hữu.<br><b>Công thức:</b> <i>ROA = Lợi nhuận sau thuế / Tổng tài sản bình quân</i>",
            "ROE đo lường khả năng sinh lợi của vốn chủ, cứ 1 đồng vốn chủ sở hữu thì tạo ra được bao nhiêu lợi nhuận.<br><b>Công thức:</b> <i>ROE = Lợi nhuận sau thuế / Vốn chủ sở hữu bình quân</i>",
            "Mô tả mức lợi nhuận sau thuế TNDN mà công ty đạt được trên mỗi cổ phiếu được phát hành và lưu hành.<br><b>Công thức:</b> <i>EPS = (Lợi nhuận sau thuế - Cổ tức cổ phiếu ưu đãi) / Số trung bình cổ phiếu lưu hành trong kỳ</i>",
            "Thông số vòng quay phải thu khách hàng cung cấp nguồn thông tin nội bộ về chất lượng phải thu khách hàng và mức độ hiệu quả của công ty trong hoạt động thu nợ. Nó cho biết số lần phải thu khách hàng được chuyển hóa thành tiền trong năm.<br><b>Công thức:</b> <i>Vòng quay khoản phải thu = Doanh thu / Khoản phải thu bình quân</i>",
            "Kỳ thu tiền bình quân là khoảng thời gian bình quân mà phải thu khách hàng của công ty có thể chuyển thành tiền, cho biết số ngày bình quân doanh số duy trì dưới hình thức phải thu khách hàng cho đến khi được thu hồi và chuyển thành tiền.<br><b>Công thức:</b> <i>Kỳ thu tiền bình quân = Số ngày trong năm / Vòng quay khoản phải thu</i>",
            "Hàng tồn kho là một bộ phận tài sản dự trữ với mục đích đảm bảo cho quá trình sản xuất kinh doanh diễn ra bình thường liên tục. Số vòng quay hàng tồn kho thể hiện số lần mà hàng tồn kho bình quân được bán trong kỳ.<br><b>Công thức:</b> <i>Vòng quay hàng tồn kho = Giá vốn hàng bán / Tồn kho bình quân</i>",
            "Chu kỳ chuyển hóa tiền mặt của tồn kho đo lường số ngày hàng nằm trong kho trước khi được bán ra thị trường.<br><b>Công thức:</b> <i>Chu kỳ chuyển hóa tiền mặt của tồn kho = Số ngày trong năm / Vòng quay hàng tồn kho</i>",
            "Vòng quay phải trả người bán là một chỉ số tài chính dùng để đo lường mức độ hiệu quả của doanh nghiệp trong việc thanh toán các khoản nợ đối với nhà cung cấp. Nó cho biết số lần mà doanh nghiệp thanh toán hết các khoản phải trả cho nhà cung cấp trong một kỳ kế toán (thường là một năm).<br><b>Công thức 1:</b> <i>Vòng quay phải trả người bán = Trị giá hàng mua tín dụng / Khoản phải trả bình quân</i><br><b>Công thức 2:</b> <i>Vòng quay phải trả người bán = (HTK cuối kỳ + GVHB - HTK đầu kỳ) / Khoản phải trả bình quân</i>",
            "Kỳ thanh toán bình quân là thời gian trung bình mà doanh nghiệp mất để thanh toán các khoản nợ phải trả cho nhà cung cấp.<br><b>Công thức:</b> <i>Kỳ thanh toán bình quân = Số ngày trong năm / Vòng quay phải trả người bán</i>",
            "Thông số vòng quay TSCĐ đo lường tốc độ chuyển hóa của TSCĐ để tạo ra doanh thu. Tăng vòng quay tài sản cố định thể hiện việc tăng hiệu quả sử dụng của TSCĐ.<br><b>Công thức:</b> <i>Vòng quay TSCĐ = Doanh thu / TSCĐ bình quân</i>",
            "Thông số vòng quay tổng tài sản đo lường tốc độ chuyển hóa của tổng tài sản để tạo ra doanh thu. Nó cho biết hiệu quả tương đối của công ty trong việc sử dụng tổng tài sản để tạo ra doanh thu.<br><b>Công thức:</b> <i>Vòng quay tổng tài sản = Doanh thu thuần về BH và CCDV / Tổng tài sản bình quân</i>",
            "Chỉ số này cho biết khả năng của một công ty trong việc dùng các tài sản lưu động như tiền mặt, hàng tồn kho hay các khoản phải thu để chi trả cho các khoản nợ ngắn hạn của mình. Chỉ số này càng cao chứng tỏ công ty càng có nhiều khả năng sẽ hoàn trả được hết khoản nợ.<br><b>Công thức:</b> <i>Khả năng thanh toán hiện thời = Tài sản ngắn hạn / Nợ ngắn hạn</i>",
            "Chỉ số thanh toán nhanh là một tỷ số tài chính dùng nhằm đo khả năng huy động tài sản lưu động của một công ty để thanh toán ngay các khoản nợ ngắn hạn của công ty.<br><b>Công thức:</b> <i>Khả năng thanh toán nhanh = (Tài sản ngắn hạn - Hàng tồn kho) / Nợ ngắn hạn</i>",
            "Thông số nợ trên VCSH dùng để đánh giá mức độ sử dụng vốn vay của công ty. Có nhiều thông số nợ khác nhau, trong đó, tỷ lệ nợ trên vốn chủ sở hữu được tính đơn giản bằng cách chia tổng nợ (bao gồm cả nợ ngắn hạn).<br><b>Công thức:</b> <i>Thông số nợ trên VCSH = (Tổng nợ / VCSH) * 100%</i>",
            "Thông số này được sử dụng với cùng mục đích thông số nợ trên vốn chủ. Thông số nợ (D/A) cho biết tổng tài sản đã được tài trợ bằng vốn vay như thế nào và được tính bằng cách lấy tổng nợ chia cho tổng tài sản.<br><b>Công thức:</b> <i>Thông số nợ trên tài sản = (Tổng nợ / Tổng tài sản) * 100%</i>",
            "Tỷ lệ này cho biết tỷ lệ nợ dài hạn chiếm bao nhiêu trong tổng cơ cấu vốn dài hạn của công ty. Cơ cấu vốn dài hạn cộng với vốn cổ phần.<br><b>Công thức:</b> <i>Thông số nợ dài hạn trên vốn dài hạn = (Tổng nợ dài hạn / (Tổng nợ dài hạn + Vốn chủ sở hữu)) * 100%</i>",
            "Là tỷ lệ tổng lợi nhuận kế toán trước thuế và lãi trong kỳ báo cáo trên tổng chi phí tài chính trong kỳ.<br><b>Công thức:</b> <i>Số lần đảm bảo lãi vay = Lợi nhuận thuần từ hoạt động kinh doanh / Chi phí tài chính</i>"
        ]
    }
    df_metrics = pd.DataFrame(data)

    # Hiển thị DataFrame dưới dạng bảng với HTML để render xuống dòng và định dạng
    # st.dataframe(df_metrics, hide_index=True, use_container_width=True)

    # Hoặc hiển thị từng nhóm một để dễ đọc hơn
    for group in df_metrics["Nhóm thông số"].unique():
        st.subheader(group)
        group_df = df_metrics[df_metrics["Nhóm thông số"] == group][["Tên thông số", "Công thức và ý nghĩa"]]
        
        for _, row in group_df.iterrows():
            with st.expander(f"**{row['Tên thông số']}**"):
                st.markdown(row["Công thức và ý nghĩa"], unsafe_allow_html=True)
        st.markdown("---")


if __name__ == '__main__':
    display_financial_metrics()