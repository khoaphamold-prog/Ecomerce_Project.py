import os
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import streamlit as st

# 1. Cấu hình trang Streamlit
st.set_page_config(
    page_title="Superstore Lightweight Dashboard",
    page_icon="⚡",
    layout="wide",
)
sns.set_theme(style="whitegrid")

# Tự động xác định thư mục chứa dữ liệu
if os.path.exists("processed_data/kpi_monthly_summary.csv"):
    DATA_DIR = "processed_data"
else:
    DATA_DIR = "."


# 2. Đọc các file CSV dữ liệu nhỏ
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
        df_ship = pd.DataFrame()

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

# 5. Khởi tạo các Tabs
tab1, tab2, tab3, tab4 = st.tabs(
    [
        "📈 1. Tài chính & Xu hướng",
        "👥 2. Phân khúc Khách hàng",
        "🚚 3. Vận chuyển & Địa lý",
        "🛒 4. Bán chéo (Co-occurrence)",
    ]
)

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
        ax.plot(
            df_disc["Discount"],
            df_disc["Avg_Profit"],
            marker="o",
            color="crimson",
            linewidth=2,
        )
        ax.axhline(0, color="gray", linestyle="--")
        ax.set_xlabel("Mức Chiết khấu")
        ax.set_ylabel("Lợi nhuận Trung bình ($)")  # Lệnh chuẩn xác ở đây
        st.pyplot(fig)
# --- TAB 2: KHÁCH HÀNG ---
with tab2:
    st.subheader("Phân tích Phân khúc Khách hàng (RFM)")


    def classify_rfm(row):
        if row["Recency"] <= 90 and row["Frequency"] >= 5:
            return "Loyal (Trung thành)"
        elif row["Recency"] > 180:
            return "At-risk (Nguy cơ rời bỏ)"
        else:
            return "Regular/New (Thường/Mới)"


    df_rfm["RFM_Segment"] = df_rfm.apply(classify_rfm, axis=1)
    rfm_counts = df_rfm["RFM_Segment"].value_counts()

    col_rfm1, col_rfm2 = st.columns(2)
    with col_rfm1:
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.pie(
            rfm_counts,
            labels=rfm_counts.index,
            autopct="%1.1f%%",
            colors=["#66b3ff", "#ff9999", "#99ff99"],
        )
        st.pyplot(fig)

    with col_rfm2:
        st.write("**Top 10 Khách hàng có Doanh thu lớn nhất:**")
        df_top_cust = (
            df_rfm.sort_values(by="Monetary", ascending=False)
            .head(10)[["Customer ID", "Segment", "Monetary", "Total_Profit"]]
            .copy()
        )
        df_top_cust["Monetary"] = df_top_cust["Monetary"].map("${:,.2f}".format)
        df_top_cust["Total_Profit"] = df_top_cust["Total_Profit"].map(
            "${:,.2f}".format
        )
        st.dataframe(df_top_cust)
    # --- TAB 3: VẬN CHUYỂN & ĐỊA LÝ ---
with tab3:
    if not df_ship.empty:
        col_s1, col_s2 = st.columns(2)

        with col_s1:
            st.subheader("Thời gian giao hàng trung bình (Ngày)")
            ship_summary = (
                df_ship.groupby("Ship Mode")["Avg_Lead_Time"]
                .mean()
                .reset_index()
            )
            fig, ax = plt.subplots(figsize=(7, 4))
            sns.barplot(
                data=ship_summary,
                x="Ship Mode",
                y="Avg_Lead_Time",
                hue="Ship Mode",
                palette="Blues_d",
                legend=False,
                ax=ax,
            )
            st.pyplot(fig)

        with col_s2:
            st.subheader("Top 10 Bang có Doanh thu cao nhất")
            top_states = (
                df_ship.groupby("State")["Total_Sales"]
                .sum()
                .nlargest(10)
                .reset_index()
            )
            fig, ax = plt.subplots(figsize=(7, 4))
            sns.barplot(
                data=top_states,
                x="Total_Sales",
                y="State",
                hue="State",
                palette="Viridis",
                legend=False,
                ax=ax,
            )
            st.pyplot(fig)
    else:
        st.warning(
            "⚠️ Chưa tìm thấy file `shipping_geo_summary.csv` trên GitHub. Vui lòng upload thêm file này."
        )
    # --- TAB 4: MUA CÙNG NHAU ---
with tab4:
    st.subheader("Ma Trận Mua Cùng Nhau (Co-occurrence)")
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.heatmap(df_co, cmap="YlGnBu", linewidths=0.3, ax=ax)
    st.pyplot(fig)

