# Ecomerce_Project.py
⚡ Superstore Analytics Dashboard (Optimized for 1M+ Rows)

Một ứng dụng Dashboard tương tác được xây dựng bằng Streamlit, Pandas, Matplotlib và Seaborn nhằm phân tích toàn diện hiệu quả kinh doanh, phân khúc khách hàng và chuỗi cung ứng từ bộ dữ liệu bán hàng Superstore quy mô lớn (hơn 1 triệu dòng).

🚀 Đặc điểm & Tối ưu hóa hiệu năng

Đối với bộ dữ liệu lớn (> 1.000.000 dòng), việc nạp trực tiếp file CSV vào Streamlit dễ gây tràn bộ nhớ (Out of Memory) hoặc giật lag giao diện. Dự án này áp dụng phương pháp Pre-aggregation (Tiền xử lý & Gom nhóm dữ liệu):

Chạy script prepare_data.py để trích xuất và gom nhóm file 1M+ dòng thành 5 tệp CSV nhỏ gọn trong thư mục processed_data/.

Ứng dụng app.py chỉ nạp các file CSV nhỏ đã xử lý kết hợp với @st.cache_data, giúp ứng dụng khởi chạy và xử lý bộ lọc tức thì (dưới 1 giây).

📁 Cấu trúc Dự án

.
├── prepare_data.py       # Script Python tiền xử lý bộ dữ liệu gốc 1M dòng
├── app.py                # Mã nguồn giao diện Streamlit Dashboard
├── requirements.txt      # Các thư viện Python cần thiết
├── .gitignore            # Bỏ qua tệp dữ liệu gốc nặng và thư mục tạm
├── README.md             # Tài liệu hướng dẫn dự án
└── processed_data/       # Thư mục chứa dữ liệu đã được gom nhóm (được đẩy lên GitHub)
    ├── kpi_monthly_summary.csv
    ├── discount_summary.csv
    ├── customer_rfm.csv
    ├── shipping_geo_summary.csv
    └── co_occurrence_matrix.csv


🛠️ Hướng dẫn Cài đặt & Chạy cục bộ (Local)

Bước 1: Trích xuất & Chuẩn bị Dữ liệu

Tải bộ dữ liệu gốc Superstore_1M.csv và đặt vào thư mục gốc của dự án.

Chạy kịch bản tiền xử lý dữ liệu:

python prepare_data.py


Kịch bản sẽ tự động khởi tạo thư mục processed_data/ chứa các tệp CSV tổng hợp.

Bước 2: Khởi chạy Streamlit Dashboard

Chạy lệnh sau để khởi động giao diện Dashboard trên trình duyệt:

streamlit run app.py


📤 Đưa dự án lên GitHub & Streamlit Cloud

Đảm bảo file .gitignore đã chặn file Superstore_1M.csv để không đẩy file gốc nặng vượt quá giới hạn 100MB của GitHub.

Đẩy các tệp tin cùng thư mục processed_data/ lên GitHub:

git add processed_data/ app.py prepare_data.py requirements.txt README.md .gitignore
git commit -m "Initial commit with pre-processed data"
git push origin main


Truy cập Streamlit Community Cloud và kết nối với kho lưu trữ GitHub để xuất bản ứng dụng miễn phí.

📊 Các tính năng Phân tích chính trên Dashboard

📈 Tài chính & Xu hướng: Phân tích doanh thu/lợi nhuận theo tháng, tác động của mức chiết khấu (Discount) tới lợi nhuận và biên lợi nhuận theo danh mục.

👥 Khách hàng & Phân khúc: Phân tích quy tắc Pareto 80/20 và phân loại khách hàng theo mô hình RFM (Recency, Frequency, Monetary).

🚚 Vận chuyển & Địa lý: Đo lường thời gian xử lý đơn hàng (Lead time) theo phương thức vận chuyển và Top 10 bang có doanh số lớn nhất.

🛒 Khai thác Bán chéo: Biểu diễn ma trận xuất hiện đồng thời (Co-occurrence Matrix) của các sản phẩm mua cùng nhau trong giỏ hàng.
