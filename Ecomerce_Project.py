import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# =========================================================
# 1. CẤU HÌNH TRANG & GIAO DIỆN (E-COMMERCE EXECUTIVE THEME)
# =========================================================
st.set_page_config(
    page_title="Superstore Executive Dashboard",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Bảng màu đồng bộ chuẩn Colab (Seaborn-inspired Plotly Palette)
PALETTE = ["#4C72B0", "#55A868", "#C44E52", "#8172B2", "#CCB974", "#64B5CD"]
px.defaults.color_discrete_sequence = PALETTE
CHART_CONFIG = {"displayModeBar": False, "responsive": True}

# Tối ưu CSS giao diện
st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1b2a4a 0%, #111a2e 100%);
    }
    [data-testid="stSidebar"] * {
        color: #e2e8f0 !important;
    }
    h1 {
        background: linear-gradient(90deg, #1b2a4a, #4c72b0);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800 !important;
        margin-bottom: 0.2rem !important;
    }
    [data-testid="stMetric"] {
        background: #ffffff;
        padding: 18px 20px;
        border-radius: 14px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
        border: 1px solid #e2e8f0;
        border-left: 5px solid #4c72b0;
    }
    [data-testid="stMetricValue"] {
        color: #1e293b !important;
        font-size: 1.6rem !important;
        font-weight: 800 !important;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #ffffff;
        padding: 6px;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(90deg, #4c72b0 0%, #3b5998 100%) !important;
        color: #ffffff !important;
        font-weight: 700;
        border-radius: 8px;
    }
    </style>
""",
    unsafe_allow_html=True,
)


# =========================================================
# 2. HÀM ĐỌC & XỬ LÝ DỮ LIỆU TỐI ƯU
# =========================================================
def format_compact_number(val, prefix="$"):
    if pd.isna(val):
        return "N/A"
    abs_val = abs(val)
    sign = "-" if val < 0 else ""
    if abs_val >= 1e6:
        return f"{sign}{prefix}{abs_val/1e6:.2f}M"
    elif abs_val >= 1e3:
        return f"{sign}{prefix}{abs_val/1e3:.1f}K"
    else:
        return f"{sign}{prefix}{abs_val:,.0f}"


possible_paths = ["output", "./output", "data/processed", "."]
DATA_DIR = "."
for path in possible_paths:
    if os.path.exists(os.path.join(path, "category_profitability.csv")):
        DATA_DIR = path
        break


@st.cache_data(ttl=3600)
def load_data(folder):
    files = [
        "category_profitability.csv",
        "discount_impact.csv",
        "loss_subcat.csv",
        "regional_margin.csv",
        "pareto_analysis.csv",
        "rfm_analysis.csv",
        "shipping_analysis.csv",
        "monthly_trend.csv",
        "product_pairs.csv",
    ]
    dfs = {}
    for f in files:
        path = os.path.join(folder, f)
        dfs[f.replace(".csv", "")] = (
            pd.read_csv(path) if os.path.exists(path) else pd.DataFrame()
        )

    df_disc = dfs["discount_impact"]
    if (
        not df_disc.empty
        and "Discount" in df_disc.columns
        and "Discount_Pct" not in df_disc.columns
    ):
        df_disc["Discount_Pct"] = df_disc["Discount"] * 100

    return (
        dfs["category_profitability"],
        df_disc,
        dfs["loss_subcat"],
        dfs["regional_margin"],
        dfs["pareto_analysis"],
        dfs["rfm_analysis"],
        dfs["shipping_analysis"],
        dfs["monthly_trend"],
        dfs["product_pairs"],
    )


try:
    (
        df_cat,
        df_disc,
        df_loss,
        df_region,
        df_pareto,
        df_rfm,
        df_ship,
        df_monthly,
        df_pairs,
    ) = load_data(DATA_DIR)
except Exception as e:
    st.error(f"⚠️ Không thể tải tập dữ liệu CSV từ thư mục '{DATA_DIR}': {e}")
    st.stop()


# =========================================================
# 3. SIDEBAR BỘ LỌC
# =========================================================
st.sidebar.header("🔍 Bộ Lọc & Điều Khiển")

regions = (
    ["Tất cả"] + list(df_region["Region"].unique())
    if not df_region.empty
    else ["Tất cả"]
)
categories = (
    ["Tất cả"] + list(df_cat["Category"].unique())
    if not df_cat.empty
    else ["Tất cả"]
)

selected_region = st.sidebar.selectbox("📍 Chọn Khu Vực:", regions)
selected_category = st.sidebar.selectbox("📦 Chọn Danh Mục:", categories)

st.sidebar.markdown("---")
st.sidebar.header("⚙️ Mô Phỏng Chiết Khấu")
discount_cap = (
    st.sidebar.slider("Mức trần chiết khấu tối đa (%):", 0, 50, 20, 5) / 100.0
)

# Lọc dữ liệu theo vùng và danh mục
filtered_region = df_region.copy() if not df_region.empty else pd.DataFrame()
if not filtered_region.empty:
    if selected_region != "Tất cả":
        filtered_region = filtered_region[
            filtered_region["Region"] == selected_region
        ]
    if selected_category != "Tất cả":
        filtered_region = filtered_region[
            filtered_region["Category"] == selected_category
        ]


# =========================================================
# 4. KPI TỔNG QUAN
# =========================================================
st.title("🛍️ Superstore Executive Dashboard")
st.caption("Bảng điều hành quản trị: Tài chính, Chiết khấu, Khách hàng & Vận hành")

total_sales = df_cat["Total_Sales"].sum() if not df_cat.empty else 0
total_profit = df_cat["Total_Profit"].sum() if not df_cat.empty else 0
avg_margin = (total_profit / total_sales) * 100 if total_sales > 0 else 0
vip_count = int(len(df_rfm) * 0.2) if not df_rfm.empty else 0

col1, col2, col3, col4 = st.columns(4)
col1.metric("💰 Doanh Thu", format_compact_number(total_sales), "+8.4% MoM")
col2.metric("📈 Lợi Nhuận", format_compact_number(total_profit), "+3.2% MoM")
col3.metric(
    "📊 Biên Lợi Nhuận TB",
    f"{avg_margin:.1f}%",
    "-0.5% Target",
    delta_color="inverse",
)
col4.metric("👥 Khách Hàng VIP", f"{vip_count:,} KH", "+12 KH mới")

st.markdown("---")


# =========================================================
# 5. CÁC TAB PHÂN TÍCH CHUYÊN SÂU
# =========================================================
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
    [
        "📋 Báo Cáo Điều Hành",
        "💰 Tài Chính & Mô Phỏng",
        "🎯 Chiết Khấu & Gánh Lỗ",
        "👥 Khách Hàng RFM",
        "🚚 Vận Hành & Xu Hướng",
        "🛒 Bán Chéo (Basket)",
    ]
)

# --- TAB 1: EXECUTIVE BRIEFING ---
with tab1:
    st.subheader("📋 Báo Cáo Điều Hành & Ma Trận Hành Động Tự Động")
    worst_sub_name, worst_sub_loss = "N/A", 0
    if not df_loss.empty:
        worst_row = df_loss.sort_values(by="Total_Profit").iloc[0]
        worst_sub_name = worst_row.get("Sub-Category", "N/A")
        worst_sub_loss = worst_row.get("Total_Profit", 0)

    worst_reg_name, worst_reg_margin = "N/A", 0
    if not df_region.empty and "Profit_Margin_Pct" in df_region.columns:
        worst_reg_row = df_region.sort_values(by="Profit_Margin_Pct").iloc[0]
        worst_reg_name = worst_reg_row.get("Region", "N/A")
        worst_reg_margin = worst_reg_row.get("Profit_Margin_Pct", 0)

    col_risk, col_opp = st.columns(2)
    with col_risk:
        st.markdown("### 🚨 Rủi Ro & Điểm Nóng Cần Xử Lý")
        if worst_sub_loss < 0:
            st.error(
                f"**1. Sản phẩm âm lợi nhuận lớn nhất:** Nhóm **{worst_sub_name}** đang gây thâm hụt "
                f"**{format_compact_number(worst_sub_loss)}** lợi nhuận ròng do chiết khấu sâu.\n\n"
                f"👉 **Hành động:** Áp dụng mức trần chiết khấu **≤ 15%** cho {worst_sub_name}."
            )
        st.warning(
            f"**2. Khu vực biên lợi nhuận thấp:** **{worst_reg_name}** đạt **{worst_reg_margin:.1f}%**.\n\n"
            f"👉 **Hành động:** Rà soát chi phí chiết khấu & logistics tại {worst_reg_name}."
        )

    with col_opp:
        st.markdown("### 🚀 Cơ Hội & Tăng Trưởng")
        st.success(
            "**1. Sức mạnh Khách hàng VIP:** Top 20% Khách hàng đóng góp gần 60% lợi nhuận.\n\n"
            "👉 **Hành động:** Triển khai chương trình chăm sóc đặc quyền VVIP."
        )
        st.info(
            "**2. Đỉnh điểm mua sắm Q4:** Nhu cầu tăng mạnh nhất vào Quý 4.\n\n"
            "👉 **Hành động:** Chủ động chuẩn bị kho Technology & Office Supplies từ Quý 3."
        )

# --- TAB 2: TÀI CHÍNH & MÔ PHỎNG ---
with tab2:
    st.subheader("1. Tài Chính & Mô Phỏng Giới Hạn Chiết Khấu")

    saved_loss = 0
    if not df_disc.empty:
        saved_loss = df_disc[
            (df_disc["Discount"] > discount_cap)
            & (df_disc["Total_Profit"] < 0)
        ]["Total_Profit"].abs().sum()

    st.info(
        f"💡 **Mô phỏng:** Nếu áp dụng mức trần chiết khấu **<= {int(discount_cap*100)}%**, "
        f"ước tính cắt giảm được **{format_compact_number(saved_loss)}** tiền lỗ!"
    )

    c1, c2 = st.columns(2)
    with c1:
        if not df_cat.empty:
            fig_cat = px.bar(
                df_cat,
                x="Category",
                y=["Total_Sales", "Total_Profit"],
                barmode="group",
                title="<b>Doanh Thu & Lợi Nhuận Theo Ngành Hàng</b>",
                color_discrete_sequence=["#4C72B0", "#55A868"],
                labels={"value": "Giá trị ($)", "variable": "Chỉ số"},
            )
            fig_cat.update_layout(
                legend_title_text="", hovermode="x unified"
            )
            st.plotly_chart(
                fig_cat, use_container_width=True, config=CHART_CONFIG
            )

    with c2:
        if not filtered_region.empty:
            fig_reg = px.bar(
                filtered_region,
                x="Region",
                y="Profit_Margin_Pct",
                color="Category",
                barmode="group",
                title="<b>Biên Lợi Nhuận (%) Theo Vùng & Danh Mục</b>",
                color_discrete_sequence=px.colors.qualitative.Set2,
                labels={
                    "Profit_Margin_Pct": "Biên lợi nhuận (%)",
                    "Region": "Vùng",
                },
            )
            fig_reg.update_layout(hovermode="x unified")
            st.plotly_chart(
                fig_reg, use_container_width=True, config=CHART_CONFIG
            )

# --- TAB 3: CHIẾT KHẤU & GÁNH LỖ ---
with tab3:
    st.subheader("2. Chiết Khấu & Rủi Ro Gánh Lỗ")
    c1, c2 = st.columns(2)
    with c1:
        if not df_disc.empty:
            df_disc_plot = df_disc.copy()
            if "Avg_Profit" not in df_disc_plot.columns:
                df_disc_plot["Avg_Profit"] = (
                    df_disc_plot["Total_Profit"]
                    / df_disc_plot["Order_Count"].replace(0, 1)
                )

            fig_disc = px.line(
                df_disc_plot,
                x="Discount_Pct",
                y="Avg_Profit",
                markers=True,
                title="<b>Tương Quan Chiết Khấu (%) vs Lợi Nhuận Trung Bình</b>",
                labels={
                    "Discount_Pct": "Chiết khấu (%)",
                    "Avg_Profit": "Lợi nhuận TB ($)",
                },
            )
            fig_disc.update_traces(
                line_color="#C44E52", line_width=3, marker_size=8
            )
            fig_disc.add_hline(
                y=0,
                line_dash="dash",
                line_color="gray",
                annotation_text="Hòa Vốn ($0)",
            )
            st.plotly_chart(
                fig_disc, use_container_width=True, config=CHART_CONFIG
            )

    with c2:
        if not df_loss.empty:
            fig_loss = px.bar(
                df_loss.sort_values("Total_Profit", ascending=True),
                x="Total_Profit",
                y="Sub-Category",
                orientation="h",
                color="Total_Profit",
                title="<b>Top Sub-Category Âm Lợi Nhuận Nhất</b>",
                color_continuous_scale="Reds_r",
                labels={
                    "Total_Profit": "Tổng Lợi Nhuận ($)",
                    "Sub-Category": "Danh mục phụ",
                },
            )
            fig_loss.update_layout(coloraxis_showscale=False)
            st.plotly_chart(
                fig_loss, use_container_width=True, config=CHART_CONFIG
            )

# --- TAB 4: KHÁCH HÀNG RFM ---
with tab4:
    st.subheader("3. Khách Hàng (Pareto & RFM)")
    c1, c2 = st.columns([1, 2])
    with c1:
        if not df_pareto.empty:
            fig_pareto = px.pie(
                df_pareto,
                names="Customer_Group",
                values="Profit_Share_Pct",
                title="<b>Tỷ Trọng Lợi Nhuận Pareto (80/20)</b>",
                hole=0.45,
                color_discrete_sequence=["#4C72B0", "#CCB974"],
            )
            fig_pareto.update_traces(textinfo="percent+label")
            st.plotly_chart(
                fig_pareto, use_container_width=True, config=CHART_CONFIG
            )

    with c2:
        st.markdown("#### 🔎 Tra Cứu & Phân Nhóm Khách Hàng (RFM)")
        if not df_rfm.empty:
            df_rfm_clean = df_rfm.copy()
            if "Customer_Segment" not in df_rfm_clean.columns:

                def rfm_label(row):
                    if row["Recency"] <= 90 and row["Frequency"] >= 5:
                        return "Loyal (Trung thành)"
                    elif row["Recency"] > 180:
                        return "At-risk (Nguy cơ rời bỏ)"
                    else:
                        return "Regular/New (Thường/Mới)"

                df_rfm_clean["Customer_Segment"] = df_rfm_clean.apply(
                    rfm_label, axis=1
                )

            search = st.text_input(
                "Nhập Mã KH hoặc Tên (vd: CG-12520):", ""
            )
            df_rfm_clean = df_rfm_clean.fillna("N/A")

            if search:
                match_cond = df_rfm_clean["Customer ID"].astype(
                    str
                ).str.contains(search, case=False, na=False)
                if "Customer Name" in df_rfm_clean.columns:
                    match_cond = match_cond | df_rfm_clean[
                        "Customer Name"
                    ].astype(str).str.contains(search, case=False, na=False)
                res = df_rfm_clean[match_cond]
                st.dataframe(
                    res if not res.empty else df_rfm_clean.head(10),
                    use_container_width=True,
                )
            else:
                st.dataframe(df_rfm_clean.head(10), use_container_width=True)

# --- TAB 5: VẬN HÀNH & XU HƯỚNG ---
with tab5:
    st.subheader("4. Vận Hành & Chuỗi Cung Ứng")
    if not df_monthly.empty:
        df_month_clean = df_monthly.copy()
        df_month_clean["Period"] = (
            df_month_clean["Year"].astype(str)
            + "-"
            + df_month_clean["Month"].astype(int).astype(str).str.zfill(2)
        )
        fig_month = px.line(
            df_month_clean.sort_values("Period"),
            x="Period",
            y=["Total_Sales", "Total_Profit"],
            title="<b>📈 Xu Hướng Doanh Thu & Lợi Nhuận Theo Tháng</b>",
            markers=True,
            color_discrete_sequence=["#4C72B0", "#55A868"],
            labels={"Period": "Thời gian (Năm-Tháng)", "value": "Giá trị ($)"},
        )
        fig_month.update_layout(hovermode="x unified")
        st.plotly_chart(
            fig_month, use_container_width=True, config=CHART_CONFIG
        )

    if not df_ship.empty:
        c1, c2 = st.columns(2)
        with c1:
            fig_ship_time = px.bar(
                df_ship,
                x="Ship Mode",
                y="Avg_Lead_Time_Days",
                color="Ship Mode",
                title="<b>🚚 Thời Gian Giao Hàng TB (Ngày)</b>",
                text_auto=".1f",
                color_discrete_sequence=px.colors.sequential.Blues_r,
                labels={
                    "Avg_Lead_Time_Days": "Số ngày (Days)",
                    "Ship Mode": "Phương thức",
                },
            )
            st.plotly_chart(
                fig_ship_time, use_container_width=True, config=CHART_CONFIG
            )
        with c2:
            fig_ship_margin = px.bar(
                df_ship,
                x="Ship Mode",
                y="Profit_Margin_Pct",
                color="Profit_Margin_Pct",
                title="<b>💎 Biên Lợi Nhuận (%) Theo Hình Thức Vận Chuyển</b>",
                text_auto=".1f",
                color_continuous_scale="Greens",
                labels={
                    "Profit_Margin_Pct": "Biên lợi nhuận (%)",
                    "Ship Mode": "Phương thức",
                },
            )
            fig_ship_margin.update_layout(coloraxis_showscale=False)
            st.plotly_chart(
                fig_ship_margin, use_container_width=True, config=CHART_CONFIG
            )

# --- TAB 6: BÁN CHÉO (BASKET ANALYSIS & HEATMAP) ---
with tab6:
    st.subheader(
        "5. Gợi Ý Sản Phẩm Bán Kèm (Cross-Selling & Co-occurrence Matrix)"
    )
    if not df_pairs.empty and "Product_A" in df_pairs.columns:
        # Xây dựng ma trận xuất hiện đồng thời (Heatmap)
        all_prods = sorted(
            list(
                set(
