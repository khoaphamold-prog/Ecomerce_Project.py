import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# =========================================================
# 1. CẤU HÌNH TRANG & GIAO DIỆN EXECUTIVE
# =========================================================
st.set_page_config(
    page_title="Superstore Executive Strategic Dashboard",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

PALETTE = ["#1f77b4", "#2ca02c", "#d62728", "#9467bd", "#ff7f0e", "#17becf"]
px.defaults.color_discrete_sequence = PALETTE
CHART_CONFIG = {"displayModeBar": False, "responsive": True}

# CSS Tùy chỉnh Cao cấp
st.markdown(
    """
    <style>
    .stApp {
        background: #f4f6f9;
        font-family: 'Inter', system-ui, -apple-system, sans-serif;
    }
    [data-testid="stSidebar"] {
        background-color: #0f172a !important;
    }
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3, [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] .stMarkdown {
        color: #f8fafc !important;
    }
    [data-testid="stSidebar"] div[data-baseweb="select"] * {
        color: #0f172a !important;
        font-weight: 500 !important;
    }
    [data-testid="stSidebar"] div[data-baseweb="select"] > div {
        background-color: #ffffff !important;
        border-radius: 8px !important;
    }
    .scenario-box {
        background: #ffffff;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #cbd5e1;
        box-shadow: 0 2px 4px rgba(0,0,0,0.03);
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
# 2. XỬ LÝ DỮ LIỆU & CACHE (100% DỮ LIỆU THỰC TẾ)
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
    if not df_disc.empty and "Discount" in df_disc.columns and "Discount_Pct" not in df_disc.columns:
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
# 3. SIDEBAR: BỘ LỌC, ĐIỀU CHỈNH BIẾN SỐ & MÔ PHỎNG KỊCH BẢN
# =========================================================
st.sidebar.title("🎛️ Bộ Lọc & Kịch Bản Quản Trị")

# --- 3.1. Bộ lọc cơ bản ---
regions = ["Tất cả"] + list(df_region["Region"].unique()) if not df_region.empty else ["Tất cả"]
categories = ["Tất cả"] + list(df_cat["Category"].unique()) if not df_cat.empty else ["Tất cả"]

selected_region = st.sidebar.selectbox("📍 Vùng địa lý:", regions)
selected_category = st.sidebar.selectbox("📦 Ngành hàng:", categories)

st.sidebar.markdown("---")

# --- 3.2. Chế độ Kịch bản Kinh doanh ---
st.sidebar.subheader("🚀 Chọn Kịch Bản Vận Hành")

scenario_mode = st.sidebar.radio(
    "Kịch bản quản trị áp dụng:",
    [
        "1. Base (Cơ sở - Hiện trạng)",
        "2. Conservative (Thận trọng - Khóa trần chiết khấu)",
        "3. Aggressive (Tối ưu toàn diện - Trần + Combo + VIP)",
    ],
    index=1,
    help="Thay đổi kịch bản để tự động điều chỉnh các biến số điều hành bên dưới",
)

st.sidebar.markdown("---")
st.sidebar.subheader("⚙️ Biến Số Ảnh Hưởng (Variables)")

# Biến số 1: Trần chiết khấu (Discount Cap)
discount_cap = (
    st.sidebar.slider(
        "1. Khóa Trần Chiết Khấu Tối Đa (%):",
        min_value=0,
        max_value=50,
        value=15 if "2." in scenario_mode or "3." in scenario_mode else 50,
        step=5,
        help="Giới hạn mức chiết khấu cao nhất cho phép trên hệ thống để chặn lỗ",
    )
    / 100.0
)

# Biến số 2: Tỷ lệ bán kèm Combo
var_cross_sell_boost = 0.0
if "3." in scenario_mode:
    var_cross_sell_boost = (
        st.sidebar.slider(
            "2. % Tăng doanh số từ Combo Bundle:",
            min_value=0,
            max_value=30,
            value=10,
            step=5,
            help="Tỷ lệ doanh số tăng thêm nhờ ghép gói bán kèm sản phẩm",
        )
        / 100.0
    )

# Biến số 3: Tỷ lệ giữ chân VIP At-Risk
var_vip_recovery = 0.0
if "3." in scenario_mode:
    var_vip_recovery = (
        st.sidebar.slider(
            "3. % Giữ chân Khách VIP (>180 ngày):",
            min_value=0,
            max_value=50,
            value=20,
            step=5,
            help="Tỷ lệ kích hoạt lại thành công nhóm khách hàng VIP có nguy cơ rời bỏ",
        )
        / 100.0
    )

# Lọc dữ liệu theo khu vực & ngành hàng chọn ở sidebar
filtered_region = df_region.copy() if not df_region.empty else pd.DataFrame()
if not filtered_region.empty:
    if selected_region != "Tất cả":
        filtered_region = filtered_region[filtered_region["Region"] == selected_region]
    if selected_category != "Tất cả":
        filtered_region = filtered_region[filtered_region["Category"] == selected_category]


# =========================================================
# 4. TÍNH TOÁN ĐỘNG THEO BIẾN SỐ VÀ KỊCH BẢN
# =========================================================
# 4.1. Chỉ số Cơ sở (Base Case)
total_sales_base = df_cat["Total_Sales"].sum() if not df_cat.empty else 0
total_profit_base = df_cat["Total_Profit"].sum() if not df_cat.empty else 0
net_margin_base = (total_profit_base / total_sales_base * 100) if total_sales_base > 0 else 0

# 4.2. Số tiền lỗ thu hồi được khi chặn các đơn chiết khấu > discount_cap
recoverable_loss = 0
if not df_disc.empty:
    loss_orders = df_disc[(df_disc["Discount"] > discount_cap) & (df_disc["Total_Profit"] < 0)]
    recoverable_loss = loss_orders["Total_Profit"].abs().sum()

# 4.3. Giá trị dự báo theo Kịch bản & Biến số
if "1." in scenario_mode:
    simulated_sales = total_sales_base
    simulated_profit = total_profit_base
elif "2." in scenario_mode:
    simulated_sales = total_sales_base
    simulated_profit = total_profit_base + recoverable_loss
else:
    cross_sell_sales = total_sales_base * var_cross_sell_boost
    cross_sell_profit = cross_sell_sales * (net_margin_base / 100)

    vip_profit = 0
    if not df_rfm.empty and "Recency" in df_rfm.columns and "Monetary" in df_rfm.columns:
        at_risk_monetary = df_rfm[df_rfm["Recency"] > 180]["Monetary"].sum()
        vip_profit = at_risk_monetary * var_vip_recovery * (net_margin_base / 100)

    simulated_sales = total_sales_base + cross_sell_sales
    simulated_profit = total_profit_base + recoverable_loss + cross_sell_profit + vip_profit

simulated_margin = (simulated_profit / simulated_sales * 100) if simulated_sales > 0 else 0


# =========================================================
# 5. EXECUTIVE DASHBOARD HEADER & SMART KPIS
# =========================================================
st.title("🎯 Superstore Executive Strategic Dashboard")
st.caption(f"Báo cáo Điều hành Kinh doanh | Đang áp dụng: **{scenario_mode}**")

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("💰 Doanh Thu Dự Báo", format_compact_number(simulated_sales), f"Hiện tại: {format_compact_number(total_sales_base)}")
with col2:
    st.metric("📈 Lợi Nhuận Gốc (Base)", format_compact_number(total_profit_base), f"Margin gốc: {net_margin_base:.1f}%")
with col3:
    st.metric(
        "🛡️ Thâm Hụt Thu Hồi Được",
        format_compact_number(recoverable_loss),
        f"Chặn đơn > {int(discount_cap*100)}%",
        delta_color="normal",
    )
with col4:
    st.metric(
        "🚀 Lợi Nhuận Kịch Bản Mới",
        format_compact_number(simulated_profit),
        f"Margin mới: {simulated_margin:.1f}% (+{simulated_margin - net_margin_base:.1f}%)",
    )

st.markdown("---")


# =========================================================
# 6. PHÂN HỆ BÁO CÁO CHI TIẾT (TABS)
# =========================================================
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
    [
        "📊 1. Executive Summary & Action Matrix",
        "🔀 2. Ma Trận Tác Động Của Biến Số",
        "💰 3. Phân Tích Lợi Nhuận & Chiết Khấu",
        "👥 4. Phân Khúc Khách Hàng (RFM & Pareto)",
        "🚚 5. Chuỗi Cung Ứng & Vận Hành",
        "🛒 6. Bán Chéo & Chiến Lược Bundle",
    ]
)

# ---------------------------------------------------------
# TAB 1: EXECUTIVE SUMMARY & INSIGHT MATRIX (ĐÃ SỬA CÂU TỪ RÕ RÀNG)
# ---------------------------------------------------------
with tab1:
    st.subheader("📌 Tóm Tắt Điều Hành & Ma Trận Khuyến Nghị Chiến Lược")

    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown(
            """
        <div class="insight-box-danger">
            <h4>🚨 Top 3 Rủi Ro Cần Can Thiệp Ngay</h4>
            <ol>
                <li><b>Rủi ro lạm dụng chiết khấu:</b> Chiết khấu vượt quá <b>20%</b> làm biên lợi nhuận đảo chiều từ <b>+15% sang âm (-25%)</b>.</li>
                <li><b>Danh mục thâm hụt nghiêm trọng:</b> Nhóm <b>Tables</b> và <b>Bookcases</b> gánh lỗ lớn nhất do giảm giá kéo dài.</li>
                <li><b>Rủi ro Churn nhóm VIP:</b> Hơn 15% khách hàng mang lại lợi nhuận cao không mua hàng trong 180 ngày qua.</li>
            </ol>
        </div>
        """,
            unsafe_allow_html=True,
        )

    with col_right:
        # CÂU TỪ ĐÃ ĐƯỢC CHỈNH SỬA RÕ RÀNG ĐỂ TRÁNH HIỂU NHẦM TRẦN CHIẾT KHẤU
        st.markdown(
            f"""
        <div class="insight-box-success">
            <h4>💡 3 Khuyến Nghị Tăng Trưởng Lợi Nhuận</h4>
            <ol>
                <li><b>Chặn thất thoát từ chiết khấu:</b> Giới hạn trần chiết khấu ở mức <b>{int(discount_cap*100)}%</b> giúp ngăn ngừa thâm hụt và thu hồi ngay <b>{format_compact_number(recoverable_loss)}</b> lợi nhuận bị lãng phí.</li>
                <li><b>Khai thác nhóm VIP (Pareto 80/20):</b> Top 20% khách hàng mang lại 60% lợi nhuận. Cần ưu tiên ngân sách Loyalty cho nhóm này.</li>
                <li><b>Chiến lược Bundle (Bán kèm):</b> Ghép cặp bán kèm sản phẩm biên lợi nhuận cao (Tech) với vật tư tiêu hao (Office Supplies).</li>
            </ol>
        </div>
        """,
            unsafe_allow_html=True,
        )

    st.markdown("### 📈 Biểu Đồ Tổng Quan Xu Hướng Doanh Thu & Lợi Nhuận")
    if not df_monthly.empty:
        df_month_clean = df_monthly.copy()
        df_month_clean["Period"] = df_month_clean["Year"].astype(str) + "-" + df_month_clean["Month"].astype(int).astype(str).str.zfill(2)

        fig_trend = px.line(
            df_month_clean.sort_values("Period"),
            x="Period",
            y=["Total_Sales", "Total_Profit"],
            markers=True,
            title="<b>Xu Hướng Doanh Thu và Lợi Nhuận Theo Tháng</b>",
            color_discrete_sequence=["#2563eb", "#16a34a"],
            labels={"value": "Giá trị ($)", "Period": "Thời gian"},
        )
        fig_trend.update_layout(hovermode="x unified", height=380)
        st.plotly_chart(fig_trend, use_container_width=True, config=CHART_CONFIG)

# ---------------------------------------------------------
# TAB 2: MA TRẬN TÁC ĐỘNG CỦA CÁC BIẾN SỐ (BỔ SUNG BẢNG BIẾN SỐ)
# ---------------------------------------------------------
with tab2:
    st.subheader("🔀 Phân Tích Mức Độ Ảnh Hưởng Của Các Biến Số Kinh Doanh")

    # Bảng tổng hợp các Biến số (Dynamic Variables Summary Table)
    st.markdown("#### 📋 Bảng Tổng Hợp Tham Số & Biến Số Đang Áp Dụng:")
    var_summary_df = pd.DataFrame(
        [
            {
                "Biến số Quản trị": "1. Trần Chiết khấu Tối đa (Discount Cap)",
                "Giá trị cài đặt": f"{int(discount_cap*100)}%",
                "Tác động tài chính trực tiếp": f"Chặn lỗ & Thu hồi {format_compact_number(recoverable_loss)}",
                "Mức độ ưu tiên": "🔴 Rất Cao (Cần khóa trên hệ thống)",
            },
            {
                "Biến số Quản trị": "2. Tăng trưởng Bán kèm (Cross-sell Boost)",
                "Giá trị cài đặt": f"+{int(var_cross_sell_boost*100)}% Doanh số",
                "Tác động tài chính trực tiếp": f"Tăng doanh thu trung bình / đơn hàng (AOV)",
                "Mức độ ưu tiên": "🟡 Trung bình (Áp dụng Combo Bundle)",
            },
            {
                "Biến số Quản trị": "3. Tỷ lệ Giữ chân VIP (RFM Recovery)",
                "Giá trị cài đặt": f"{int(var_vip_recovery*100)}% Khách At-Risk",
                "Tác động tài chính trực tiếp": f"Bảo vệ 60% tổng lợi nhuận từ nhóm 20% VVIP",
                "Mức độ ưu tiên": "🟢 Cao (Chương trình Loyalty)",
            },
        ]
    )
    st.dataframe(var_summary_df, use_container_width=True, hide_index=True)

    st.markdown("---")
    st.markdown("#### 📊 So Sánh Kết Quả Dự Báo Giữa 3 Kịch Bản:")

    s1_p = total_profit_base
    s2_p = total_profit_base + recoverable_loss
    s3_p = s2_p + (total_sales_base * 0.10 * (net_margin_base / 100))

    df_scen_comp = pd.DataFrame(
        {
            "Kịch bản": ["1. Base (Hiện trạng)", "2. Conservative (Thận trọng)", "3. Aggressive (Tối ưu)"],
            "Lợi Nhuận Dự Báo ($)": [s1_p, s2_p, s3_p],
            "Biên Lợi Nhuận (%)": [net_margin_base, (s2_p / total_sales_base * 100), (s3_p / (total_sales_base * 1.1) * 100)],
        }
    )

    c_scen1, c_scen2 = st.columns(2)
    with c_scen1:
        fig_scen_bar = px.bar(
            df_scen_comp,
            x="Kịch bản",
            y="Lợi Nhuận Dự Báo ($)",
            color="Kịch bản",
            text_auto=".3s",
            title="<b>Lợi Nhuận Ròng Dự Báo ($)</b>",
            color_discrete_sequence=["#64748b", "#f59e0b", "#16a34a"],
        )
        fig_scen_bar.update_layout(showlegend=False, height=380)
        st.plotly_chart(fig_scen_bar, use_container_width=True, config=CHART_CONFIG)

    with c_scen2:
        fig_scen_line = px.line(
            df_scen_comp,
            x="Kịch bản",
            y="Biên Lợi Nhuận (%)",
            markers=True,
            title="<b>Biên Lợi Nhuận Ròng Mới (%)</b>",
        )
        fig_scen_line.update_traces(line_color="#2563eb", line_width=4, marker_size=10)
        fig_scen_line.update_layout(height=380)
        st.plotly_chart(fig_scen_line, use_container_width=True, config=CHART_CONFIG)

# ---------------------------------------------------------
# TAB 3: FINANCIAL ANALYTICS & SIMULATION
# ---------------------------------------------------------
with tab3:
    st.subheader("💰 Phân Tích Lợi Nhuận & Mô Phỏng Trần Chiết Khấu")

    c1, c2 = st.columns(2)
    with c1:
        if not df_disc.empty:
            df_disc_plot = df_disc.copy()
            if "Avg_Profit" not in df_disc_plot.columns:
                df_disc_plot["Avg_Profit"] = df_disc_plot["Total_Profit"] / df_disc_plot["Order_Count"].replace(0, 1)

            fig_disc = px.line(
                df_disc_plot,
                x="Discount_Pct",
                y="Avg_Profit",
                markers=True,
                title="<b>Lợi Nhuận Trung Bình / Đơn Theo Mức Chiết Khấu</b>",
                labels={"Discount_Pct": "Mức Chiết Khấu (%)", "Avg_Profit": "Lợi Nhuận TB ($)"},
            )
            fig_disc.update_traces(line_color="#dc2626", line_width=3, marker_size=8)
            fig_disc.add_hline(y=0, line_dash="dash", line_color="gray", annotation_text="Điểm Hòa Vốn ($0)")
            fig_disc.add_vline(x=discount_cap * 100, line_dash="dot", line_color="blue", annotation_text=f"Trần chọn ({int(discount_cap*100)}%)")
            st.plotly_chart(fig_disc, use_container_width=True, config=CHART_CONFIG)

    with c2:
        if not df_loss.empty:
            fig_loss = px.bar(
                df_loss.sort_values("Total_Profit", ascending=True),
                x="Total_Profit",
                y="Sub-Category",
                orientation="h",
                color="Total_Profit",
                title="<b>Top Danh Mục Phụ Bị Âm Lợi Nhuận Nặng Nhất</b>",
                color_continuous_scale="Reds_r",
            )
            fig_loss.update_layout(coloraxis_showscale=False)
            st.plotly_chart(fig_loss, use_container_width=True, config=CHART_CONFIG)

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
        )
        st.plotly_chart(fig_reg, use_container_width=True, config=CHART_CONFIG)

# ---------------------------------------------------------
# TAB 4: CUSTOMER SEGMENTATION (RFM & PARETO)
# ---------------------------------------------------------
with tab4:
    st.subheader("👥 Phân Tích Khách Hàng (Pareto 80/20 & RFM)")

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
            st.plotly_chart(fig_pareto, use_container_width=True, config=CHART_CONFIG)

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
                    return "Potential / New (Mới / Tiềm năng)"

            df_rfm_clean["RFM_Segment"] = df_rfm_clean.apply(rfm_label, axis=1)

            segment_summary = df_rfm_clean["RFM_Segment"].value_counts().reset_index(name="Count")

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
            st.plotly_chart(fig_rfm, use_container_width=True, config=CHART_CONFIG)

# ---------------------------------------------------------
# TAB 5: SUPPLY CHAIN & LOGISTICS
# ---------------------------------------------------------
with tab5:
    st.subheader("🚚 Phân Tích Vận Hành & Chuỗi Cung Ứng")

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
            st.plotly_chart(fig_ship_lead, use_container_width=True, config=CHART_CONFIG)

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
            st.plotly_chart(fig_ship_margin, use_container_width=True, config=CHART_CONFIG)

# ---------------------------------------------------------
# TAB 6: BASKET ANALYSIS & CROSS-SELLING (HIỂN THỊ RÕ RÀNG BUNDLE)
# ---------------------------------------------------------
with tab6:
    st.subheader("🛒 Phân Tích Giỏ Hàng & Gợi Ý Combo Bundle")

    if df_pairs.empty:
        st.warning("⚠️ Không tìm thấy dữ liệu mua kèm (`product_pairs.csv`).")
    else:
        col_p1 = "Product_A" if "Product_A" in df_pairs.columns else df_pairs.columns[0]
        col_p2 = "Product_B" if "Product_B" in df_pairs.columns else df_pairs.columns[1]
        col_count = "Times_Bought_Together" if "Times_Bought_Together" in df_pairs.columns else df_pairs.columns[2]

        prods_a = df_pairs[col_p1].dropna().astype(str).unique().tolist()
        prods_b = df_pairs[col_p2].dropna().astype(str).unique().tolist()
        all_prods = sorted(list(set(prods_a + prods_b)))

        # 1. Heatmap
        st.markdown("#### 📊 Ma Trận Tần Suất Mua Kèm (Co-occurrence Heatmap)")
        matrix_df = pd.DataFrame(0, index=all_prods, columns=all_prods, dtype=int)
        for _, row in df_pairs.iterrows():
            p1, p2, count = str(row[col_p1]), str(row[col_p2]), row[col_count]
            if p1 in matrix_df.index and p2 in matrix_df.columns:
                matrix_df.loc[p1, p2] = count
                matrix_df.loc[p2, p1] = count

        fig_heatmap = px.imshow(
            matrix_df,
            x=all_prods,
            y=all_prods,
            color_continuous_scale="YlGnBu",
            title="<b>Ma Trận Tần Suất Các Cặp Sản Phẩm Được Mua Cùng Nhau</b>",
        )
        fig_heatmap.update_layout(height=450)
        st.plotly_chart(fig_heatmap, use_container_width=True, config=CHART_CONFIG)

        st.markdown("---")

        # 2. KHU VỰC GỢI Ý COMBO BUNDLE
        st.markdown("### 🎯 Gợi Ý Combo Bundle Tối Ưu Lợi Nhuận")
        st.caption("Chọn sản phẩm gốc để hệ thống gợi ý các sản phẩm phù hợp nhất để đóng gói Bundle bán kèm.")

        c_select, c_info = st.columns([1, 2])

        with c_select:
            selected_prod = st.selectbox(
                "📌 Chọn sản phẩm / ngành hàng chính:",
                options=all_prods,
                index=0,
                key="combo_select_box_main",
            )

        recommendations = df_pairs[
            (df_pairs[col_p1].astype(str) == selected_prod) | (df_pairs[col_p2].astype(str) == selected_prod)
        ].copy()

        recommendations["Sản phẩm gợi ý bán kèm"] = recommendations.apply(
            lambda r: str(r[col_p2]) if str(r[col_p1]) == selected_prod else str(r[col_p1]), axis=1
        )
        recommendations = recommendations.sort_values(by=col_count, ascending=False)

        with c_info:
            top_bundle = recommendations.iloc[0] if not recommendations.empty else None
            if top_bundle is not None:
                st.success(
                    f"💡 **Combo Khuyến Nghị Số 1:** Ghép gói **[{selected_prod}]** đi kèm với **[{top_bundle['Sản phẩm gợi ý bán kèm']}]** "
                    f"(Đã có **{top_bundle[col_count]}** đơn hàng thực tế mua cùng nhau)."
                )
            else:
                st.info("Chưa có cặp sản phẩm mua kèm phù hợp.")

        st.markdown("##### 📋 Danh Sách Sản Phẩm Được Mua Kèm Nhiều Nhất:")
        display_df = recommendations[["Sản phẩm gợi ý bán kèm", col_count]].rename(
            columns={col_count: "Số Lần Đã Mua Cùng Nhau"}
        )
        st.dataframe(display_df, use_container_width=True, hide_index=True)
        ====
        # add chatbot 
import google.generativeai as genai
import streamlit as st

# Khai báo Tab 7 trong danh sách Tabs
# tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([...])

with tab7:
    st.subheader("💬 Trợ Lý AI Phân Tích Bán Hàng")
    st.caption(
        "Đặt câu hỏi trực tiếp cho AI về dữ liệu doanh thu, lợi nhuận và khách hàng."
    )

    # 1. Cấu hình API Key (Lấy từ Secrets của Streamlit Cloud hoặc ô Nhập)
    api_key = st.sidebar.text_input(
        "🔑 Nhập Gemini API Key:", type="password"
    )

    if api_key:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")

        # 2. Tạo ngữ cảnh dữ liệu (System Context) từ các file CSV để AI đọc hiểu
        context_data = f"""
        Bạn là Trợ lý AI Phân tích Dữ liệu Bán hàng cho dự án Superstore E-Commerce.
        Dưới đây là tóm tắt dữ liệu hiện tại của hệ thống:
        - Tổng Doanh Thu: ${total_sales:,.0f}
        - Tổng Lợi Nhuận: ${total_profit:,.0f}
        - Biên Lợi Nhuận TB: {avg_margin:.1f}%
        - Top 20% Khách hàng VIP đóng góp gần 60% tổng lợi nhuận.
        - Nhóm sản phẩm gây lỗ lớn nhất: {worst_sub_name} (Thâm hụt {worst_sub_loss:,.0f}$).
        - Mức chiết khấu an toàn tối đa: <= 20%. Chiết khấu > 30% gây âm lợi nhuận sâu.
        Hãy trả lời ngắn gọn, chuyên nghiệp, hỗ trợ ra quyết định kinh doanh cho Ban Giám đốc.
        """

        # 3. Quản lý lịch sử trò chuyện
        if "messages" not in st.session_state:
            st.session_state.messages = [
                {
                    "role": "assistant",
                    "content": "Xin chào! Tôi là Trợ lý AI của Superstore. Bạn cần hỗ trợ phân tích dữ liệu gì hôm nay?",
                }
            ]

        # Hiển thị lịch sử chat
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])

        # 4. Xử lý khi người dùng gửi câu hỏi
        if user_query := st.chat_input("Hỏi AI về báo cáo bán hàng..."):
            st.session_state.messages.append(
                {"role": "user", "content": user_query}
            )
            with st.chat_message("user"):
                st.write(user_query)

            # Gọi Gemini API
            with st.chat_message("assistant"):
                with st.spinner("AI đang suy nghĩ và phân tích dữ liệu..."):
                    prompt = f"{context_data}\n\nCâu hỏi của người dùng: {user_query}"
                    response = model.generate_content(prompt)
                    bot_reply = response.text
                    st.write(bot_reply)

            st.session_state.messages.append(
                {"role": "assistant", "content": bot_reply}
            )
    else:
        st.warning(
            "⚠️ Vui lòng nhập Gemini API Key ở thanh Sidebar bên trái để bật tính năng Chatbot AI."
        )

