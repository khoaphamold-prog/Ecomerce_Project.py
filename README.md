#  Superstore Executive Dashboard

Bảng điều hành quản trị phân tích dữ liệu bán hàng thương mại điện tử (E-Commerce) quy mô **1M+ dòng dữ liệu**, được tối ưu hóa hiệu năng xử lý cao và triển khai trực tiếp trên **Streamlit Cloud**.

---

##  Tính Năng Nổi Bật

Dashboard được xây dựng với kiến trúc **7 Tabs tương tác trực quan** bằng thư viện **Plotly** và tích hợp **Gemini AI**:

1. ** Báo Cáo Điều Hành & Insights (Executive Briefing):** Tự động phân tích ma trận rủi ro & cơ hội, phát hiện ngay các khu vực và sản phẩm thâm hụt lợi nhuận.
2. ** Tài Chính & Mô Phỏng (Finance & Simulation):** Phân tích doanh thu/lợi nhuận theo ngành hàng và công cụ mô phỏng trần chiết khấu (Discount Cap).
3. ** Chiết Khấu & Gánh Lỗ (Discount & Loss):** Tương quan giữa mức chiết khấu (%) và lợi nhuận, xác định ranh giới hòa vốn và sản phẩm gánh lỗ.
4. ** Khách Hàng RFM (RFM & Pareto):** Phân tích quy tắc Pareto 80/20 và công cụ tra cứu phân khúc khách hàng theo chỉ số RFM (Recency, Frequency, Monetary).
5. ** Vận Hành & Xu Hướng (Operations & Trend):** Phân tích thời gian giao hàng (Lead Time) theo phương thức vận chuyển và xu hướng doanh số theo tháng/năm.
6. ** Bán Chéo (Cross-Selling):** Gợi ý các cặp sản phẩm thường được mua cùng nhau (Co-occurrence) dựa trên thuật toán khai phá giỏ hàng (Market Basket Analysis).
7. ** Trợ Lý AI Chatbot (AI Assistant):** Tích hợp Google Gemini AI hỗ trợ hỏi đáp dữ liệu bán hàng real-time có duy trì ngữ cảnh hội thoại.

---

##  Cấu Trúc Thư Mục Repository

Để ứng dụng đạt hiệu năng tối ưu và vận hành mượt mà trên Streamlit Cloud, dữ liệu thô đã được tiền xử lý thành 9 tệp CSV phân tích nhỏ gọn:

```text
.
├── Ecomerce_Project.py       # Mã nguồn chính ứng dụng Streamlit Dashboard
├── requirements.txt          # Danh sách phụ thuộc (streamlit, pandas, plotly, google-generativeai)
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

