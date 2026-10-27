import os
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import streamlit as st

# 1. Cấu hình giao diện Streamlit
st.set_page_config(
    page_title="Superstore Lightweight Dashboard",
    page_icon="⚡",
    layout="wide",
)
sns.set_theme(style="whitegrid")

# Tự động xác định thư mục dữ liệu
if os.path.exists("processed_data/kpi_monthly_summary.csv"):
    DATA_DIR = "processed_data"
else:
    DATA_DIR = "."


# 2. Load các file CSV vào bộ nhớ đệm
@st.cache_data
def load_processed_data():
    df_kpi = pd.read_csv(f"{DATA_DIR}/kpi_monthly_summary.csv")
    df_disc = pd.read_csv(f"{DATA_DIR}/discount_summary.csv")
    df_rfm = pd.read_csv(f"{DATA_DIR}/customer_rfm.csv")
    df_co = pd.read_csv(f"{DATA_DIR}/co_occurrence_matrix.csv", index_col=0)

    shipping_path = f"{DATA_DIR}/shipping_geo_summary.csv"
    if os.path.exists(shipping_path):
        df_ship = pd.read_csv(shipping_path)
    else:
        df_ship = pd.DataFrame(
            columns=["State", "Ship Mode", "Avg_Lead_Time", "Total_Sales"]
        )

    return df_kpi, df_disc, df_rfm, df_ship, df_co


try:
    df_kpi, df_disc, df_rfm, df_ship, df_co = load_processed_data()
except Exception as e:
    st.error(
        f"❌ Không thể đọc file dữ liệu CSV. Vui lòng kiểm tra lại các tệp CSV trên GitHub! Lỗi: {e}"
    )
    st.stop()

# 3. Thanh bộ lọc tương tác (Sidebar)
st.sidebar.header("🔍 Bộ Lọc Dữ Liệu")

regions = ["Tất cả"] + list(df_kpi["Region"].unique())
selected_region = st.sidebar.selectbox("Chọn Vùng (Region):", regions)

segments = ["Tất cả"] + list(df_kpi["Segment"].unique())
selected_segment = st.sidebar.selectbox("Chọn Phân khúc:", segments)

# Áp dụng bộ lọc
filtered_kpi = df_kpi.copy()
if selected_region != "Tất cả":
    filtered_kpi = filtered_kpi[filtered_kpi["Region"] == selected_region]
if selected_segment != "Tất cả":
    filtered_kpi = filtered_kpi[filtered_kpi["Segment"] == selected_segment]

# 4. Hiển thị Chỉ số KPI Tổng quan
st.title("⚡ Superstore Performance Dashboard")
st.caption("Dashboard phân tích dữ liệu bán hàng tối ưu hiệu năng.")
st.markdown("---")

total_sales = filtered_kpi["Total_Sales"].sum()
total_profit = filtered_kpi["Total_Profit"].sum()
total_orders = filtered_kpi["Total_Orders"].sum()
margin = (total_profit / total_sales * 100) if total_sales > 0 else 0

col1, col2, col3, col4 = st.columns(4)
col1.metric("Tổng Doanh Thu", f"${total_sales:,.0f}")
col2.metric("Tổng Lợi Nhuận", f"${total_profit:,.0f}")
col3.metric("Biên Lợi Nhuận", f"{margin:.2f}%")
col4.metric("Ước Tính Đơn Hàng", f"{total_orders:,}")

st.markdown("---")

# 5. Phân chia các Tabs hiển thị (Viết gọn trên 1 dòng để tránh lỗi ngắt ngoặc)
tab_names = [
    "📈 1. Tài chính & Xu hướng",
    "👥 2. Phân khúc Khách hàng",
    "🚚 3. Vận chuyển & Địa lý",
    "🛒 4. Bán chéo (Co-occurrence)",
]
tab1, tab2, tab3, tab4 = st.tabs(tab_names)

# --- TAB 1: TÀI CHÍNH & XU HƯỚNG ---
with tab1:
    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader("Xu hướng Doanh thu & Lợi nhuận theo Tháng")
        monthly = (
            filtered_kpi.groupby("YearMonth")[["Total_Sales", "Total_Profit"]]
            .sum()
            .reset_index()
        )
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.plot(
            monthly["YearMonth"],
            monthly["Total_Sales"],
            label="Doanh thu",
            color="#1f77b4",
            linewidth=2,
        )
        ax.plot(
            monthly["YearMonth"],
            monthly["Total_Profit"],
            label="Lợi nhuận",
            color="#2ca02c",
            linewidth=2,
        )
        step = max(1, len(monthly) // 6)
        plt.xticks(monthly["YearMonth"][::step], rotation=45)
        ax.legend()
        st.pyplot(fig)

    with col_b:
        st.subheader("Tác động của Mức Chiết khấu (Discount)")
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.plot)
            
