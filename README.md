# Ecomerce_Project.py
# 🛍️ Superstore Executive Dashboard

Bảng điều hành quản trị phân tích dữ liệu bán hàng thương mại điện tử (E-Commerce) quy mô 1M+ dòng dữ liệu, được tối ưu hóa hiệu năng cao và triển khai trực tiếp trên **Streamlit Cloud**.

---

## 🌟 Tính Năng Nổi Bật

Dashboard được xây dựng với kiến trúc 6 Tabs tương tác trực quan bằng thư viện **Plotly**:

1. **📋 Báo Cáo Điều Hành & Insights (Executive Briefing):** Tự động phân tích ma trận rủi ro & cơ hội, dự báo tác động lợi nhuận ròng.
2. **💰 Tài Chính & Mô Phỏng (Finance & Simulation):** Phân tích doanh thu/lợi nhuận theo ngành hàng và bộ mô phỏng trần chiết khấu (Discount Cap).
3. **🎯 Chiết Khấu & Gánh Lỗ (Discount & Loss):** Xác định điểm hòa vốn chiết khấu và phát hiện các danh mục sản phẩm gây thâm hụt lợi nhuận.
4. **👥 Khách Hàng RFM (RFM & Pareto):** Phân tích quy tắc Pareto 80/20 và công cụ tra cứu chi tiết phân khúc khách hàng theo chỉ số RFM.
5. **🚚 Vận Hành & Xu Hướng (Operations & Trend):** Phân tích chuỗi cung ứng, thời gian giao hàng (Lead Time) và xu hướng bán hàng theo chuỗi thời gian liên tục.
6. **🛒 Bán Chéo (Cross-Selling):** Gợi ý các cặp sản phẩm thường được mua cùng nhau (Co-occurrence) dựa trên thuật toán Market Basket Analysis.

---

## 📁 Cấu Trúc Thư Mục Repository

Để ứng dụng đạt hiệu năng tối ưu và không bị gián đoạn bộ nhớ trên Streamlit Cloud, dữ liệu thô đã được tiền xử lý thành 9 file CSV tổng hợp nhỏ:

```text
├── Ecomerce_Project.py       # Mã nguồn chính ứng dụng Streamlit
├── requirements.txt          # Danh sách thư viện phụ thuộc (streamlit, pandas, plotly)
├── README.md                 # Tài liệu hướng dẫn dự án
├── category_profitability.csv
├── discount_impact.csv
├── loss_subcat.csv
├── monthly_trend.csv
├── pareto_analysis.csv
├── product_pairs.csv
├── regional_margin.csv
├── rfm_analysis.csv
└── shipping_analysis.csv
