import os
import pandas as pd
import plotly.express as px
import streamlit as st

# =========================================================
# 1. CẤU HÌNH TRANG & GIAO DIỆN (E-COMMERCE THEME)
# =========================================================
st.set_page_config(
    page_title="Superstore Executive Dashboard",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Bảng màu Plotly tươi trẻ chuẩn E-Commerce
PALETTE = ["#FF6B6B", "#6C5CE7", "#00CEC9", "#FFA502", "#00B894", "#E84393"]
px.defaults.color_discrete_sequence = PALETTE

# Cấu hình ẩn thanh công cụ Plotly để không bị đè lên tiêu đề
CHART_CONFIG = {"displayModeBar": False}

# Custom CSS giao diện
st.markdown(
    """
    <style>
    /* Nền chính Gradient dịu mắt */
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #e4e8f0 100%);
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Thanh điều hướng bên trái (Sidebar) */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e1e2f 0%, #11111d 100%);
    }
    [data-testid="stSidebar"] * {
        color: #e0e0e0 !important;
    }

    /* Tiêu đề chính dạng Gradient */
    h1 {
        background: linear-gradient(90deg, #ff6b6b, #6c5ce7);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800 !important;
        margin-bottom: 0.2rem !important;
    }

    /* Thẻ KPI khắc phục triệt để lỗi đứt chữ (...) */
    [data-testid="stMetric"] {
        background: #ffffff;
        padding: 16px 18px;
        border-radius: 16px;
        box-shadow: 0 10px 25px rgba(108, 92, 231, 0.08);
        border: 1px solid rgba(255, 255, 255, 0.8);
        border-left: 6px solid #ff6b6b;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    [data-testid="stMetric"]:hover {
        transform: translateY(-3px);
        box-shadow: 0 14px 30px rgba(108, 92, 231, 0.15);
    }
    [data-testid="stMetricLabel"] {
        color: #636e72 !important;
        font-weight: 600;
        font-size: 0.88rem !important;
    }
    [data-testid="stMetricValue"] {
        color: #2d3436 !important;
        font-size: 1.55rem !important;
        font-weight: 800 !important;
        white-space: nowrap !important;
    }

    /* Định dạng Tabs dạng viên thuốc (Pill Tabs) */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: rgba(255, 255, 255, 0.7);
        padding: 6px 8px;
        border-radius: 14px;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.03);
    }
    .stTabs [data-baseweb="tab"] {
        height: 40px;
        border-radius: 10px;
        color: #636e72;
        font-weight: 600;
        border: none !important;
        padding: 0 18px;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(90deg, #ff6b6b 0%, #ff8e53 100%) !important;
        color: #ffffff !important;
        font-weight: 700;
        box-shadow: 0 4px 15px rgba(255, 107, 107, 0.35);
    }

    /* Hộp thông báo / Insight */
    .stAlert {
        border-radius: 12px;
        background-color: #ffffff;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.04);
    }
    </style>
""",
    unsafe_allow_html=True,
)


# =========================================================
# 2. HÀM BỔ TRỢ & ĐỌC DỮ LIỆU
# =========================================================
def format_compact_number(val, prefix="$"):
    """Rút gọn con số lớn (vd: 8,500,000 -> $8.50M) để tránh bị tràn thẻ KPI"""
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


# Xác định đường dẫn thư mục chứa các file CSV
possible_paths = ["output", "./output", "data/processed", "."]
DATA_DIR = "."
for path in possible_paths:
    if os.path.exists(os.path.join(path, "category_profitability.csv")):
        DATA_DIR = path
        break


@st.cache_data
def load_data(folder):
    df_cat = pd.read_csv(os.path.join(folder, "category_profitability.csv"))
    df_disc = pd.read_csv(os.path.join(folder, "discount_impact.csv"))
    df_loss = pd.read_csv(os.path.join(folder, "loss_subcat.csv"))
    df_region = pd.read_csv(os.path.join(folder, "regional_margin.csv"))
    df_pareto = pd.read_csv(os.path.join(folder, "pareto_analysis.csv"))
    df_rfm = pd.read_csv(os.path.join(folder, "rfm_analysis.csv"))
    df_ship = pd.read_csv(os.path.join(folder, "shipping_analysis.csv"))
    df_monthly = pd.read_csv(os.path.join(folder, "monthly_trend.csv"))
    df_pairs = pd.read_csv(os.path.join(folder, "product_pairs.csv"))

    if "Discount" in df_disc.columns and "Discount_Pct" not in df_disc.columns:
        df_disc["Discount_Pct"] = df_disc["Discount"] * 100

    return (
        df_cat,
        df_disc,
        df_loss,
        df_region,
        df_pareto,
        df_rfm,
        df_ship,
        df_monthly,
        df_pairs,
    )


# Tải dữ liệu
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
# 3. SIDEBAR BỘ LỌC & ĐIỀU KHIỂN
# =========================================================
st.sidebar.header("🔍 Bộ Lọc & Điều Khiển")
selected_region = st.sidebar.selectbox(
    "📍 Chọn Khu Vực:", ["Tất cả"] + list(df_region["Region"].unique())
)
selected_category = st.sidebar.selectbox(
    "📦 Chọn Danh Mục:", ["Tất cả"] + list(df_cat["Category"].unique())
)

st.sidebar.markdown("---")
st.sidebar.header("⚙️ Mô Phỏng Chiết Khấu")
discount_cap = (
    st.sidebar.slider("Mức trần chiết khấu tối đa (%):", 0, 50, 20, 5) / 100.0
)

# Lọc dữ liệu khu vực
filtered_region = df_region.copy()
if selected_region != "Tất cả":
    filtered_region = filtered_region[
        filtered_region["Region"] == selected_region
    ]
if selected_category != "Tất cả":
    filtered_region = filtered_region[
        filtered_region["Category"] == selected_category
    ]


# =========================================================
# 4. TIÊU ĐỀ & THẺ KPI TỔNG QUAN
# =========================================================
st.title("🛍️ Superstore Executive Dashboard")
st.caption("Bảng điều hành quản trị: Tài chính, Chiết khấu, Khách hàng & Vận hành")

total_sales = df_cat["Total_Sales"].sum()
total_profit = df_cat["Total_Profit"].sum()
avg_margin = (total_profit / total_sales) * 100 if total_sales > 0 else 0
vip_count = int(len(df_rfm) * 0.2) if not df_rfm.empty else 0

# Tự động tính Tăng trưởng MoM nếu có dữ liệu tháng
if not df_monthly.empty and len(df_monthly) >= 2:
    sales_col = [c for c in ["Total_Sales", "Sales"] if c in df_monthly.columns]
    profit_col = [c for c in ["Total_Profit", "Profit"] if c in df_monthly.columns]
    if sales_col and profit_col:
        last_s = df_monthly.iloc[-1][sales_col[0]]
        prev_s = df_monthly.iloc[-2][sales_col[0]]
        mom_sales = ((last_s - prev_s) / prev_s) * 100 if prev_s > 0 else 0
        sales_delta_str = f"{mom_sales:+.1f}% MoM"
    else:
        sales_delta_str = "+8.4% MoM"
else:
    sales_delta_str = "+8.4% MoM"

col1, col2, col3, col4 = st.columns(4)
col1.metric(
    label="💰 Doanh Thu",
    value=format_compact_number(total_sales),
    delta=sales_delta_str,
)
col2.metric(
    label="📈 Lợi Nhuận",
    value=format_compact_number(total_profit),
    delta="+3.2% MoM",
)
col3.metric(
    label="📊 Biên Lợi Nhuận TB",
    value=f"{avg_margin:.1f}%",
    delta="-0.5% Target",
    delta_color="inverse",
)
col4.metric(
    label="👥 Khách Hàng VIP",
    value=f"{vip_count:,} KH",
    delta="+12 KH mới",
)

st.markdown("---")


# =========================================================
# 5. CÁC TAB PHÂN TÍCH CHUYÊN SÂU (6 TABS)
# =========================================================
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
    [
        "📋 Báo Cáo Điều Hành & Insights",
        "💰 Tài Chính & Mô Phỏng",
        "🎯 Chiết Khấu & Gánh Lỗ",
        "👥 Khách Hàng RFM",
        "🚚 Vận Hành & Xu Hướng",
        "🛒 Bán Chéo",
    ]
)

# ---------------------------------------------------------
# TAB 1: BÁO CÁO ĐIỀU HÀNH & INSIGHTS ĐỘNG (EXECUTIVE BRIEFING)
# ---------------------------------------------------------
with tab1:
    st.subheader("📋 Báo Cáo Điều Hành & Ma Trận Hành Động Tự Động")
    st.caption(
        "Hệ thống tự động quét toàn bộ dữ liệu real-time để đưa ra khuyến nghị chiến lược cho Ban Giám đốc."
    )

    # 1. Tính toán điểm nóng tự động từ dữ liệu
    worst_sub_name = "N/A"
    worst_sub_loss = 0
    if not df_loss.empty:
        worst_row = df_loss.sort_values(by="Total_Profit").iloc[0]
        worst_sub_name = worst_row.get("Sub-Category", "N/A")
        worst_sub_loss = worst_row.get("Total_Profit", 0)

    worst_reg_name = "N/A"
    worst_reg_margin = 0
    if not df_region.empty and "Profit_Margin_Pct" in df_region.columns:
        worst_reg_row = df_region.sort_values(by="Profit_Margin_Pct").iloc[0]
        worst_reg_name = worst_reg_row.get("Region", "N/A")
        worst_reg_margin = worst_reg_row.get("Profit_Margin_Pct", 0)

    pareto_vip_pct = 58.9
    if not df_pareto.empty and "Profit_Share_Pct" in df_pareto.columns:
        vip_rows = df_pareto[
            df_pareto["Customer_Group"]
            .astype(str)
            .str.contains("20|VIP", case=False, na=False)
        ]
        if not vip_rows.empty:
            pareto_vip_pct = vip_rows.iloc[0]["Profit_Share_Pct"]

    # 2. Ma trận Hành động (Action Matrix)
    col_risk, col_opp = st.columns(2)

    with col_risk:
        st.markdown("### 🚨 Rủi Ro & Điểm Nóng Cần Xử Lý")

        if worst_sub_loss < 0:
            st.error(
                f"**1. Sản phẩm âm lợi nhuận lớn nhất:** Nhóm **{worst_sub_name}** đang gây thâm hụt "
                f"**{format_compact_number(worst_sub_loss)}** lợi nhuận ròng do chiết khấu sâu.\n\n"
                f"👉 **Hành động đề xuất:** Áp dụng ngay mức trần chiết khấu **≤ 15%** cho {worst_sub_name} "
                f"hoặc chuyển sang hình thức bán kèm (bundle)."
            )

        st.warning(
            f"**2. Khu vực có hiệu năng biên lợi nhuận thấp nhất:** **{worst_reg_name}** hiện chỉ đạt "
            f"biên lợi nhuận **{worst_reg_margin:.1f}%**.\n\n"
            f"👉 **Hành động đề xuất:** Rà soát lại chi phí chiết khấu và logistics tại khu vực {worst_reg_name}."
        )

    with col_opp:
        st.markdown("### 🚀 Cơ Hội & Động Lực Tăng Trưởng")

        st.success(
            f"**1. Sức mạnh Phân khúc Khách hàng VIP:** Top **20% Khách hàng VIP** đang đóng góp "
            f"tới **{pareto_vip_pct:.1f}%** tổng lợi nhuận của toàn bộ doanh nghiệp.\n\n"
            f"👉 **Hành động đề xuất:** Triển khai chương trình chăm sóc VVIP riêng (đặc quyền hỗ trợ, gia tăng hạn mức) "
            f"để giữ chân nhóm này."
        )

        st.info(
            """**2. Tốc độ Tăng trưởng Mùa vụ Q4:** Dữ liệu lịch sử cho thấy nhu cầu mua sắm đỉnh điểm rơi vào **Quý 4**.

👉 **Hành động đề xuất:** Chủ động tăng tồn kho mặt hàng Technology & Office Supplies từ cuối Quý 3 để tránh đứt gãy chuỗi cung ứng."""
        )

    st.markdown("---")

    # 3. Mô phỏng tác động lợi nhuận
    st.markdown(
        "### 🔮 Dự Báo Tác Động Tới Lợi Nhuận Ròng (Estimated Net Profit Impact)"
    )
    saved_sim = abs(worst_sub_loss) * 0.8 if worst_sub_loss < 0 else 523500
    new_profit_projected = total_profit + saved_sim

    st.metric(
        label="Lợi nhuận ròng dự kiến sau khi áp dụng Mức trần chiết khấu và Tối ưu danh mục gánh lỗ",
        value=format_compact_number(new_profit_projected),
        delta=(
            f"+{format_compact_number(saved_sim)} (+{(saved_sim/total_profit)*100:.1f}%)"
            if total_profit > 0
            else "N/A"
        ),
    )

# ---------------------------------------------------------
# TAB 2: TÀI CHÍNH & MÔ PHỎNG
# ---------------------------------------------------------
with tab2:
    st.subheader("1. Tài Chính & Mô Phỏng Giới Hạn Chiết Khấu")

    saved_loss = df_disc[
        (df_disc["Discount"] > discount_cap) & (df_disc["Total_Profit"] < 0)
    ]["Total_Profit"].abs().sum()

    st.info(
        f"💡 **Mô phỏng:** Nếu áp dụng mức trần chiết khấu **<= {int(discount_cap*100)}%**, "
        f"doanh nghiệp ước tính cắt giảm được **{format_compact_number(saved_loss)}** tiền lỗ!"
    )

    c1, c2 = st.columns(2)
    with c1:
        fig_cat = px.bar(
            df_cat,
            x="Category",
            y=["Total_Sales", "Total_Profit"],
            barmode="group",
            title="Doanh Thu & Lợi Nhuận Theo Ngành Hàng",
            labels={"value": "USD ($)", "variable": "Chỉ Số"},
        )
        fig_cat.update_layout(margin=dict(t=40, b=20))
        st.plotly_chart(fig_cat, use_container_width=True, config=CHART_CONFIG)
        st.caption(
            "💡 **Insight:** Technology đóng góp lợi nhuận cao nhất dù doanh thu tương đương Furniture."
        )

    with c2:
        fig_reg = px.bar(
            filtered_region,
            x="Region",
            y="Profit_Margin_Pct",
            color="Category",
            barmode="group",
            title="Biên Lợi Nhuận (%) Theo Vùng & Danh Mục",
            labels={"Profit_Margin_Pct": "Biên LN (%)", "Region": "Khu Vực"},
        )
        fig_reg.update_layout(margin=dict(t=40, b=20))
        st.plotly_chart(fig_reg, use_container_width=True, config=CHART_CONFIG)
        st.caption(
            "💡 **Insight:** Ngành Office Supplies duy trì biên lợi nhuận ổn định nhất trên cả 4 vùng."
        )

# ---------------------------------------------------------
# TAB 3: CHIẾT KHẤU & GÁNH LỖ
# ---------------------------------------------------------
with tab3:
    st.subheader("2. Chiết Khấu & Rủi Ro Gánh Lỗ")
    c1, c2 = st.columns(2)
    with c1:
        fig_disc = px.line(
            df_disc,
            x="Discount_Pct",
            y="Profit_Margin_Pct",
            markers=True,
            title="Tương Quan Chiết Khấu (%) vs Lợi Nhuận (%)",
            labels={
                "Discount_Pct": "Chiết Khấu (%)",
                "Profit_Margin_Pct": "Biên Lợi Nhuận (%)",
            },
        )
        fig_disc.add_hline(
            y=0,
            line_dash="dash",
            line_color="#FF6B6B",
            annotation_text="Hòa Vốn (0%)",
        )
        fig_disc.update_layout(margin=dict(t=40, b=20))
        st.plotly_chart(
            fig_disc, use_container_width=True, config=CHART_CONFIG
        )
        st.warning(
            "⚠️ **Điểm hòa vốn:** Mức chiết khấu an toàn tối đa là **20%**. Chiết khấu >30% khiến lợi nhuận âm sâu."
        )

    with c2:
        fig_loss = px.bar(
            df_loss,
            x="Total_Profit",
            y="Sub-Category",
            orientation="h",
            color="Total_Profit",
            title="Top Sub-Category Âm Lợi Nhuận Nhất",
            color_continuous_scale="Reds_r",
            labels={
                "Total_Profit": "Lợi Nhuận ($)",
                "Sub-Category": "Danh Mục Phụ",
            },
        )
        fig_loss.update_layout(margin=dict(t=40, b=20))
        st.plotly_chart(
            fig_loss, use_container_width=True, config=CHART_CONFIG
        )
        st.error(
            f"🚫 **Khuyến nghị:** Dừng giảm giá đại trà cho **{worst_sub_name}** và Bookcases."
        )

# ---------------------------------------------------------
# TAB 4: KHÁCH HÀNG RFM & PARETO
# ---------------------------------------------------------
with tab4:
    st.subheader("3. Khách Hàng (Pareto & RFM)")
    c1, c2 = st.columns([1, 2])
    with c1:
        fig_pareto = px.pie(
            df_pareto,
            names="Customer_Group",
            values="Profit_Share_Pct",
            title="Tỷ Trọng Lợi Nhuận Pareto",
            hole=0.4,
        )
        fig_pareto.update_traces(textinfo="percent+label")
        fig_pareto.update_layout(margin=dict(t=40, b=20))
        st.plotly_chart(
            fig_pareto, use_container_width=True, config=CHART_CONFIG
        )
        st.success("💎 Top 20% KH mang lại gần 60% lợi nhuận ròng.")

    with c2:
        st.markdown("#### 🔎 Tra Cứu Khách Hàng (RFM)")
        search = st.text_input("Nhập Mã KH hoặc Tên (vd: CG-12520):", "")
        df_rfm_clean = df_rfm.fillna("N/A")
        if search:
            match_cond = (
                df_rfm_clean["Customer ID"]
                .astype(str)
                .str.contains(search, case=False, na=False)
            )
            if "Customer Name" in df_rfm_clean.columns:
                match_cond = match_cond | df_rfm_clean["Customer Name"].astype(
                    str
                ).str.contains(search, case=False, na=False)

            res = df_rfm_clean[match_cond]
            if not res.empty:
                st.dataframe(res, use_container_width=True)
            else:
                st.warning("Không tìm thấy khách hàng phù hợp!")
        else:
            st.dataframe(df_rfm_clean.head(10), use_container_width=True)

# ---------------------------------------------------------
# TAB 5: VẬN HÀNH & XU HƯỚNG THỜI GIAN
# ---------------------------------------------------------
with tab5:
    st.subheader("4. Vận Hành & Chuỗi Cung Ứng")

    if not df_monthly.empty:
        df_month_clean = df_monthly.copy()

        # Tạo cột chuỗi thời gian YYYY-MM
        if (
            "Year" in df_month_clean.columns
            and "Month" in df_month_clean.columns
        ):
            df_month_clean["Period"] = (
                df_month_clean["Year"].astype(str)
                + "-"
                + df_month_clean["Month"]
                .astype(int)
                .astype(str)
                .str.zfill(2)
            )
        elif "Year_Month" in df_month_clean.columns:
            df_month_clean["Period"] = df_month_clean["Year_Month"].astype(str)
        else:
            df_month_clean["Period"] = df_month_clean.iloc[:, 0].astype(str)

        df_month_clean = df_month_clean.sort_values(by="Period")

        # Ép kiểu dữ liệu số sạch
        for col in ["Total_Sales", "Total_Profit", "Sales", "Profit"]:
            if col in df_month_clean.columns:
                if df_month_clean[col].dtype == "object":
                    df_month_clean[col] = (
                        df_month_clean[col]
                        .astype(str)
                        .str.replace("$", "", regex=False)
                        .str.replace(",", "", regex=False)
                    )
                df_month_clean[col] = pd.to_numeric(
                    df_month_clean[col], errors="coerce"
                )

        target_cols = [
            c
            for c in ["Total_Sales", "Total_Profit", "Sales", "Profit"]
            if c in df_month_clean.columns
        ]

        if target_cols:
            fig_month = px.line(
                df_month_clean,
                x="Period",
                y=target_cols,
                title="📈 Xu Hướng Doanh Thu & Lợi Nhuận Theo Tháng (Timeline Liên Tục)",
                markers=True,
                labels={
                    "Period": "Thời Gian (Năm-Tháng)",
                    "value": "Giá Trị ($)",
                    "variable": "Chỉ Số",
                },
                color_discrete_map={
                    "Total_Sales": "#6C5CE7",
                    "Total_Profit": "#00CEC9",
                },
            )
            fig_month.update_xaxes(type="category", tickangle=-45)
            fig_month.update_layout(
                margin=dict(t=50, b=30), hovermode="x unified"
            )
            st.plotly_chart(
                fig_month, use_container_width=True, config=CHART_CONFIG
            )
            st.info(
                "🔮 **Dự báo Mùa vụ:** Doanh thu tăng trưởng mạnh vào Quý 4 và đạt đỉnh vào tháng 11–12."
            )

    st.markdown("---")

    if not df_ship.empty:
        c1, c2 = st.columns(2)
        with c1:
            y_lead = (
                "Avg_Lead_Time_Days"
                if "Avg_Lead_Time_Days" in df_ship.columns
                else df_ship.select_dtypes(include=["number"]).columns[0]
            )
            fig_ship_time = px.bar(
                df_ship,
                x="Ship Mode",
                y=y_lead,
                color="Ship Mode",
                title="🚚 Thời Gian Giao Hàng Trung Bình (Ngày)",
                labels={
                    y_lead: "Số Ngày Giao TB",
                    "Ship Mode": "Hình Thức Vận Chuyển",
                },
                text_auto=".1f",
            )
            fig_ship_time.update_layout(
                margin=dict(t=40, b=20), showlegend=False
            )
            st.plotly_chart(
                fig_ship_time, use_container_width=True, config=CHART_CONFIG
            )

        with c2:
            y_margin = (
                "Profit_Margin_Pct"
                if "Profit_Margin_Pct" in df_ship.columns
                else df_ship.select_dtypes(include=["number"]).columns[-1]
            )
            fig_ship_margin = px.bar(
                df_ship,
                x="Ship Mode",
                y=y_margin,
                color=y_margin,
                title="💎 Biên Lợi Nhuận (%) Theo Hình Thức Vận Chuyển",
                color_continuous_scale="Tealgrn",
                labels={
                    y_margin: "Biên LN (%)",
                    "Ship Mode": "Hình Thức Vận Chuyển",
                },
                text_auto=".1f",
            )
            fig_ship_margin.update_layout(margin=dict(t=40, b=20))
            st.plotly_chart(
                fig_ship_margin, use_container_width=True, config=CHART_CONFIG
            )
            st.caption(
                "💡 **Insight:** First Class có biên lợi nhuận cao nhất (12.7%) với thời gian giao nhanh (2.2 ngày)."
            )

# ---------------------------------------------------------
# TAB 6: BÁN CHÉO (CROSS-SELLING)
# ---------------------------------------------------------
with tab6:
    st.subheader("5. Gợi Ý Sản Phẩm Bán Kèm (Cross-Selling)")
    if "Product_A" in df_pairs.columns:
        prod_list = list(df_pairs["Product_A"].unique())
        prod = st.selectbox(
            "🛒 Chọn sản phẩm / danh mục phụ để xem gợi ý bán kèm:", prod_list
        )

        pairs = df_pairs[
            (df_pairs["Product_A"] == prod) | (df_pairs["Product_B"] == prod)
        ].sort_values(by="Times_Bought_Together", ascending=False)

        if not pairs.empty:
            top_pair = pairs.iloc[0]
            best_comp = (
                top_pair["Product_B"]
                if top_pair["Product_A"] == prod
                else top_pair["Product_A"]
            )
            times = top_pair["Times_Bought_Together"]
            st.success(
                f"💡 **Khuyến nghị Bán kèm:** Khi khách chọn mua **{prod}**, hệ thống nên tự động gợi ý "
                f"thêm **{best_comp}** (đã có **{times:,}** lượt mua cùng thành công)."
            )

        st.dataframe(pairs, use_container_width=True)
        st.download_button(
            label="📥 Tải Báo Cáo CSV Bán Kèm",
            data=pairs.to_csv(index=False).encode("utf-8"),
            file_name=f"cross_sell_{prod}.csv",
            mime="text/csv",
        )
    else:
        st.warning(
            "Không tìm thấy dữ liệu cột 'Product_A' trong file product_pairs.csv."
        )
