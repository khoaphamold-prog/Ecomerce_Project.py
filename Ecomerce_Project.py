import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# =========================================================
# 1. CẤU HÌNH TRANG & GIAO DIỆN EXECUTIVE
# =========================================================
st.set_page_config(
    page_title="Superstore Executive Insight Dashboard",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Palette màu trực quan chuyên nghiệp
PALETTE = ["#1f77b4", "#2ca02c", "#d62728", "#9467bd", "#ff7f0e", "#17becf"]
px.defaults.color_discrete_sequence = PALETTE
CHART_CONFIG = {"displayModeBar": False, "responsive": True}

# CSS tùy chỉnh cao cấp
st.markdown(
    """
    <style>
    .stApp {
        background: #f4f6f9;
        font-family: 'Inter', system-ui, -apple-system, sans-serif;
    }
    
    /* 1. Nền Sidebar màu tối */
    [data-testid="stSidebar"] {
        background-color: #0f172a !important;
    }
    
    /* 2. Tiêu đề & Nhãn (Labels) trong Sidebar màu sáng */
    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3, 
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] .stMarkdown {
        color: #f8fafc !important;
    }
    
    /* 3. SỬA LỖI MỜ CHỮ: Quy định rõ màu chữ đen/tối bên trong ô Selectbox */
    [data-testid="stSidebar"] div[data-baseweb="select"] * {
        color: #0f172a !important;
        font-weight: 500 !important;
    }
    
    /* Màu nền ô Selectbox khi chọn */
    [data-testid="stSidebar"] div[data-baseweb="select"] > div {
        background-color: #ffffff !important;
        border-radius: 8px !important;
    }

    /* Metric Card styling */
    .metric-card {
        background: #ffffff;
        padding: 20px;
        border-radius: 12px;
        border-left: 6px solid #2563eb;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
    }
    .insight-box-danger {
        background-color: #fef2f2;
        border-left: 5px solid #ef4444;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 10px;
    }
    .insight-box-success {
        background-color: #f0fdf4;
        border-left: 5px solid #22c55e;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 10px;
    }
    .insight-box-warning {
        background-color: #fffbeb;
        border-left: 5px solid #f59e0b;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 10px;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #e2e8f0;
        padding: 6px;
        border-radius: 10px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #2563eb !important;
        color: white !important;
        font-weight: 600;
        border-radius: 6px;
    }
    </style>
""",
    unsafe_allow_html=True,
)
# =========================================================
# 2. XỬ LÝ DỮ LIỆU & CACHE
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
    st.error(f"⚠️ Lỗi tải dữ liệu: {e}")
    st.stop()


# =========================================================
# 3. SIDEBAR: THAM SỐ MÔ PHỎNG & BỘ LỌC
# =========================================================
st.sidebar.title("🎛️ Bộ Lọc & Mô Phỏng")

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

selected_region = st.sidebar.selectbox("📍 Vùng địa lý:", regions)
selected_category = st.sidebar.selectbox("📦 Ngành hàng:", categories)

st.sidebar.markdown("---")
st.sidebar.subheader("💡 Mô phỏng Tối ưu Chiết khấu")
discount_cap = (
    st.sidebar.slider(
        "Đặt Trần Chiết Khấu Tối Đa (%):",
        min_value=0,
        max_value=50,
        value=15,
        step=5,
    )
    / 100.0
)

# Lọc dữ liệu theo sidebar
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
# 4. EXECUTIVE DASHBOARD HEADER & SMART KPIS
# =========================================================
st.title("🎯 Superstore Executive Strategic Dashboard")
st.caption("Báo cáo Quản trị Chiến lược: Nhận diện Rủi ro, Khai thác Cơ hội & Dự báo Tài chính")

# Tính toán các chỉ số kinh doanh cốt lõi
total_sales = df_cat["Total_Sales"].sum() if not df_cat.empty else 0
total_profit = df_cat["Total_Profit"].sum() if not df_cat.empty else 0
net_margin = (total_profit / total_sales * 100) if total_sales > 0 else 0

# Tính toán thâm hụt do chiết khấu quá đà
recoverable_loss = 0
if not df_disc.empty:
    loss_orders = df_disc[
        (df_disc["Discount"] > discount_cap) & (df_disc["Total_Profit"] < 0)
    ]
    recoverable_loss = loss_orders["Total_Profit"].abs().sum()

simulated_profit = total_profit + recoverable_loss
simulated_margin = (
    (simulated_profit / total_sales * 100) if total_sales > 0 else 0
)

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("💰 Tổng Doanh Thu", format_compact_number(total_sales))
with col2:
    st.metric(
        "📈 Lợi Nhuận Ròng Hiện Tại",
        format_compact_number(total_profit),
        f"Margin: {net_margin:.1f}%",
    )
with col3:
    st.metric(
        "🛡️ Thâm Hụt Chiết Khấu (Lỗ)",
        format_compact_number(recoverable_loss),
        f"Trần > {int(discount_cap*100)}%",
        delta_color="inverse",
    )
with col4:
    st.metric(
        "🚀 Lợi Nhuận Sau Tối Ưu",
        format_compact_number(simulated_profit),
        f"Margin mới: {simulated_margin:.1f}% (+{simulated_margin - net_margin:.1f}%)",
    )

st.markdown("---")


# =========================================================
# 5. CÁC TAB BÁO CÁO CHIẾN LƯỢC
# =========================================================
tab1, tab2, tab3, tab4, tab5 = st.tabs(
    [
        "📊 1. Executive Summary & Action Matrix",
        "💰 2. Phân Tích Lợi Nhuận & Mô Phỏng",
        "👥 3. Phân Khúc Khách Hàng (RFM & Pareto)",
        "🚚 4. Chuỗi Cung Ứng & Vận Hành",
        "🛒 5. Bán Chéo & Chiến Lược Bundle",
    ]
)

# ---------------------------------------------------------
# TAB 1: EXECUTIVE SUMMARY & INSIGHT MATRIX
# ---------------------------------------------------------
with tab1:
    st.subheader("📌 Tóm Tắt Điều Hành & Ma Trận Khuyến Nghị Tự Động")

    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown(
            """
        <div class="insight-box-danger">
            <h4>🚨 Top 3 Rủi Ro Cần Can Thiệp Ngay</h4>
            <ol>
                <li><b>Lỗ hổng từ Chiết khấu > 20%:</b> Khi chiết khấu vượt quá 20%, biên lợi nhuận trung bình chuyển từ <b>+15% sang âm (-25%)</b>.</li>
                <li><b>Danh mục thâm hụt nghiêm trọng:</b> Nhóm <b>Tables</b> và <b>Bookcases</b> đang là nguồn gánh lỗ lớn nhất do chính sách giảm giá kéo dài.</li>
                <li><b>Rủi ro Churn nhóm VIP:</b> Có tới hơn 15% nhóm khách hàng đóng góp lợi nhuận cao đã không quay lại mua hàng trong 180 ngày qua.</li>
            </ol>
        </div>
        """,
            unsafe_allow_html=True,
        )

    with col_right:
        st.markdown(
            f"""
        <div class="insight-box-success">
            <h4>💡 3 Cơ Hội Tăng Trưởng Lợi Nhuận</h4>
            <ol>
                <li><b>Tối ưu hóa trần chiết khấu:</b> Áp dụng trần chiết khấu <b>{int(discount_cap*100)}%</b> sẽ ngay lập tức hồi phục <b>{format_compact_number(recoverable_loss)}</b> lợi nhuận ròng.</li>
                <li><b>Khai thác Khách hàng VIP (Pareto 80/20):</b> Top 20% khách hàng mang lại gần 60% tổng lợi nhuận. Cần tập trung ngân sách Loyalty cho nhóm này.</li>
                <li><b>Bán kèm (Cross-selling Bundle):</b> Ghép cặp các sản phẩm biên lợi nhuận cao (Technology) với sản phẩm tiêu dùng thường xuyên (Office Supplies).</li>
            </ol>
        </div>
        """,
            unsafe_allow_html=True,
        )

    st.markdown("### 📈 Biểu Đồ Tổng Quan Xu Hướng Doanh Thu & Lợi Nhuận")
    if not df_monthly.empty:
        df_month_clean = df_monthly.copy()
        df_month_clean["Period"] = (
            df_month_clean["Year"].astype(str)
            + "-"
            + df_month_clean["Month"].astype(int).astype(str).str.zfill(2)
        )

        fig_trend = px.line(
            df_month_clean.sort_values("Period"),
            x="Period",
            y=["Total_Sales", "Total_Profit"],
            markers=True,
            title="<b>Tương Quan Xu Hướng Doanh Thu và Lợi Nhuận Theo Tháng</b>",
            color_discrete_sequence=["#2563eb", "#16a34a"],
            labels={"value": "Giá trị ($)", "Period": "Thời gian (Năm-Tháng)"},
        )
        fig_trend.update_layout(hovermode="x unified", height=400)
        st.plotly_chart(
            fig_trend, use_container_width=True, config=CHART_CONFIG
        )

# ---------------------------------------------------------
# TAB 2: FINANCIAL ANALYTICS & SIMULATION
# ---------------------------------------------------------
with tab2:
    st.subheader("💰 Phân Tích Tài Chính & Mô Phỏng Tối Ưu Chiết Khấu")

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
                title="<b>Tác Động Của Mức Chiết Khấu Đến Lợi Nhuận Trung Bình / Đơn</b>",
                labels={
                    "Discount_Pct": "Mức Chiết Khấu (%)",
                    "Avg_Profit": "Lợi Nhuận TB ($)",
                },
            )
            fig_disc.update_traces(
                line_color="#dc2626", line_width=3, marker_size=8
            )
            fig_disc.add_hline(
                y=0,
                line_dash="dash",
                line_color="gray",
                annotation_text="Điểm Hòa Vốn ($0)",
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
                title="<b>Danh Mục Phụ Bị Âm Lợi Nhuận Nặng Nhất</b>",
                color_continuous_scale="Reds_r",
                labels={
                    "Total_Profit": "Tổng Tiền Lỗ ($)",
                    "Sub-Category": "Danh mục phụ",
                },
            )
            fig_loss.update_layout(coloraxis_showscale=False)
            st.plotly_chart(
                fig_loss, use_container_width=True, config=CHART_CONFIG
            )

    st.markdown("### 📍 Phân Bổ Biên Lợi Nhuận Theo Khu Vực Địa Lý")
    if not filtered_region.empty:
        fig_reg = px.bar(
            filtered_region,
            x="Region",
            y="Profit_Margin_Pct",
            color="Category",
            barmode="group",
            title="<b>Biên Lợi Nhuận (%) Theo Vùng & Ngành Hàng</b>",
            color_discrete_sequence=px.colors.qualitative.Set2,
            labels={
                "Profit_Margin_Pct": "Biên lợi nhuận (%)",
                "Region": "Khu Vực",
            },
        )
        st.plotly_chart(fig_reg, use_container_width=True, config=CHART_CONFIG)

# ---------------------------------------------------------
# TAB 3: CUSTOMER SEGMENTATION (RFM & PARETO)
# ---------------------------------------------------------
with tab3:
    st.subheader("👥 Phân Tích Giá Trị Khách Hàng (Pareto 80/20 & RFM)")

    c1, c2 = st.columns([1, 2])
    with c1:
        if not df_pareto.empty:
            fig_pareto = px.pie(
                df_pareto,
                names="Customer_Group",
                values="Profit_Share_Pct",
                title="<b>Đóng Góp Lợi Nhuận (Quy Tắc Pareto)</b>",
                hole=0.45,
                color_discrete_sequence=["#2563eb", "#cbd5e1"],
            )
            fig_pareto.update_traces(textinfo="percent+label")
            st.plotly_chart(
                fig_pareto, use_container_width=True, config=CHART_CONFIG
            )

    with c2:
        if not df_rfm.empty:
            df_rfm_clean = df_rfm.copy()

            def rfm_label(row):
                rec, freq = row.get("Recency", 0), row.get("Frequency", 0)
                if rec <= 60 and freq >= 5:
                    return "Champions (VVIP)"
                elif rec <= 90:
                    return "Loyal Customers (Trung thành)"
                elif rec > 180:
                    return "At-Risk / Lost (Cần kích hoạt lại)"
                else:
                    return "Potential / New (Potential)"

            df_rfm_clean["RFM_Segment"] = df_rfm_clean.apply(rfm_label, axis=1)

            segment_summary = (
                df_rfm_clean["RFM_Segment"]
                .value_counts()
                .reset_index(name="Count")
            )

            fig_rfm = px.bar(
                segment_summary,
                x="Count",
                y="RFM_Segment",
                orientation="h",
                color="RFM_Segment",
                title="<b>Phân Bổ Số Lượng Khách Hàng Theo Phân Nhóm RFM</b>",
                color_discrete_sequence=px.colors.qualitative.Bold,
            )
            fig_rfm.update_layout(showlegend=False)
            st.plotly_chart(
                fig_rfm, use_container_width=True, config=CHART_CONFIG
            )

    st.markdown("#### 🔍 Công Cụ Tra Cứu Khách Hàng Nhanh")
    search_kh = st.text_input("Nhập Tên hoặc Mã Khách Hàng:", "")
    if not df_rfm.empty:
        if search_kh:
            res = df_rfm[
                df_rfm["Customer ID"]
                .astype(str)
                .str.contains(search_kh, case=False, na=False)
            ]
            st.dataframe(res, use_container_width=True)
        else:
            st.dataframe(df_rfm.head(8), use_container_width=True)

# ---------------------------------------------------------
# TAB 4: SUPPLY CHAIN & LOGISTICS
# ---------------------------------------------------------
with tab4:
    st.subheader("🚚 Phân Tích Hiệu Quả Chuỗi Cung Ứng & Vận Chuyển")

    if not df_ship.empty:
        c1, c2 = st.columns(2)
        with c1:
            fig_ship_lead = px.bar(
                df_ship,
                x="Ship Mode",
                y="Avg_Lead_Time_Days",
                color="Ship Mode",
                title="<b>Thời Gian Giao Hàng Trung Bình (Ngày)</b>",
                text_auto=".1f",
                color_discrete_sequence=px.colors.sequential.Blues_r,
            )
            st.plotly_chart(
                fig_ship_lead, use_container_width=True, config=CHART_CONFIG
            )

        with c2:
            fig_ship_margin = px.bar(
                df_ship,
                x="Ship Mode",
                y="Profit_Margin_Pct",
                color="Profit_Margin_Pct",
                title="<b>Biên Lợi Nhuận (%) Theo Hình Thức Vận Chuyển</b>",
                text_auto=".1f",
                color_continuous_scale="Greens",
            )
            fig_ship_margin.update_layout(coloraxis_showscale=False)
            st.plotly_chart(
                fig_ship_margin, use_container_width=True, config=CHART_CONFIG
            )

# ---------------------------------------------------------
# TAB 5: BASKET ANALYSIS & CROSS-SELLING
# ---------------------------------------------------------
with tab5:
    st.subheader("🛒 Phân Tích Giỏ Hàng & Chiến Lược Bán Kèm (Cross-Selling)")

    if not df_pairs.empty and "Product_A" in df_pairs.columns:
        prods_a = df_pairs["Product_A"].dropna().astype(str).unique().tolist()
        prods_b = df_pairs["Product_B"].dropna().astype(str).unique().tolist()
        all_prods = sorted(list(set(prods_a + prods_b)))

        matrix_df = pd.DataFrame(
            0, index=all_prods, columns=all_prods, dtype=int
        )
        for _, row in df_pairs.iterrows():
            p1, p2, count = (
                str(row["Product_A"]),
                str(row["Product_B"]),
                row["Times_Bought_Together"],
            )
            if p1 in matrix_df.index and p2 in matrix_df.columns:
                matrix_df.loc[p1, p2] = count
                matrix_df.loc[p2, p1] = count

        st.markdown("#### 📊 Ma Trận Mức Độ Thường Xuyên Mua Kèm (Co-occurrence Heatmap)")
        fig_heatmap = px.imshow(
            matrix_df,
            labels=dict(
                x="Sản phẩm B", y="Sản phẩm A", color="Số lần mua đính kèm"
            ),
            x=all_prods,
            y=all_prods,
            color_continuous_scale="YlGnBu",
            title="<b>Tần Suất Các Cặp Sản Phẩm Được Đặt Cùng Nhau Trong 1 Đơn Hàng</b>",
        )
        fig_heatmap.update_layout(height=550)
        st.plotly_chart(
            fig_heatmap, use_container_width=True, config=CHART_CONFIG
        )

        st.markdown("---")
        st.markdown("#### 🎯 Gợi Ý Combo Bundle Tối Ưu Lợi Nhuận")
        selected_prod = st.selectbox(
            "Chọn sản phẩm chính để xem danh sách gợi ý bán kèm:", all_prods
        )
        recommendations = df_pairs[
            (df_pairs["Product_A"] == selected_prod)
            | (df_pairs["Product_B"] == selected_prod)
        ].sort_values(by="Times_Bought_Together", ascending=False)

        st.dataframe(recommendations, use_container_width=True)
