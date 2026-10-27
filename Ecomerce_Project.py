import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# =========================================================
# 1. CẤU HÌNH TRANG & GIAO DIỆN EXECUTIVE
# =========================================================
st.set_page_config(
    page_title="Superstore Strategic Scenario & Variable Dashboard",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

PALETTE = ["#2563eb", "#16a34a", "#dc2626", "#f59e0b", "#9467bd", "#0891b2"]
px.defaults.color_discrete_sequence = PALETTE
CHART_CONFIG = {"displayModeBar": False, "responsive": True}

# CSS Tùy chỉnh
st.markdown(
    """
    <style>
    .stApp {
        background: #f8fafc;
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
    .scenario-card {
        background: #ffffff;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
        margin-bottom: 15px;
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
# 2. ĐỌC DỮ LIỆU THỰC TẾ (ĐỒNG NHẤT 100% VỚI BẢN GỐC)
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


# Xác định đường dẫn chứa tệp CSV thực tế
possible_paths = ["output", "./output", "data/processed", "."]
DATA_DIR = "."
for path in possible_paths:
    if os.path.exists(os.path.join(path, "category_profitability.csv")):
        DATA_DIR = path
        break


@st.cache_data(ttl=3600)
def load_real_data(folder):
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
    if not df_disc.empty:
        if "Discount" in df_disc.columns and "Discount_Pct" not in df_disc.columns:
            df_disc["Discount_Pct"] = df_disc["Discount"] * 100
        if "Avg_Profit" not in df_disc.columns and "Order_Count" in df_disc.columns:
            df_disc["Avg_Profit"] = df_disc["Total_Profit"] / df_disc["Order_Count"].replace(0, 1)

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
    ) = load_real_data(DATA_DIR)
except Exception as e:
    st.error(f"⚠️ Lỗi đọc tệp dữ liệu gốc: {e}")
    st.stop()


# =========================================================
# 3. SIDEBAR: ĐIỀU CHỈNH BIẾN SỐ KINH DOANH (MUTABLE VARIABLES)
# =========================================================
st.sidebar.title("🎛️ Biến Số Điều Hành")
st.sidebar.caption("Tùy chỉnh các tham số thực tế để mô phỏng tác động tài chính")

st.sidebar.subheader("1. Trần Chiết Khấu (Discount Cap)")
var_discount_cap = (
    st.sidebar.slider(
        "Đặt Trần Chiết Khấu Tối Đa (%):",
        min_value=0,
        max_value=40,
        value=15,
        step=5,
        help="Giới hạn mức chiết khấu cao nhất áp dụng trên hệ thống",
    )
    / 100.0
)

st.sidebar.subheader("2. Chiến Lược Bundle / Cross-Selling")
var_cross_sell_boost = (
    st.sidebar.slider(
        "Tăng Trưởng Doanh Số Mua Kèm (%):",
        min_value=0,
        max_value=30,
        value=10,
        step=5,
        help="% Doanh số tăng thêm nhờ ghép gói sản phẩm mua kèm",
    )
    / 100.0
)

st.sidebar.subheader("3. Giữ Chân Khách Hàng VIP (RFM)")
var_vip_recovery_rate = (
    st.sidebar.slider(
        "Tỷ Lệ Giữ Chân Khách At-Risk (%):",
        min_value=0,
        max_value=50,
        value=20,
        step=5,
        help="% Khách hàng có nguy cơ rời bỏ (>180 ngày) được kích hoạt lại",
    )
    / 100.0
)


# =========================================================
# 4. TÍNH TOÁN CÁC KỊCH BẢN DỰA TRÊN DỮ LIỆU THỰC TẾ
# =========================================================

# --- 4.1. KỊCH BẢN 1: CƠ SỞ (BASE CASE) ---
base_sales = df_cat["Total_Sales"].sum() if not df_cat.empty else 0
base_profit = df_cat["Total_Profit"].sum() if not df_cat.empty else 0
base_margin = (base_profit / base_sales * 100) if base_sales > 0 else 0

# --- 4.2. KỊCH BẢN 2: THẬN TRỌNG (CONSERVATIVE - THU HỒI LỖ CHIẾT KHẤU) ---
recoverable_loss = 0
if not df_disc.empty:
    # Lấy chính xác các đơn hàng bị thâm hụt do chiết khấu vượt quá trần đang chọn
    loss_orders = df_disc[(df_disc["Discount"] > var_discount_cap) & (df_disc["Total_Profit"] < 0)]
    recoverable_loss = loss_orders["Total_Profit"].abs().sum()

scen2_sales = base_sales
scen2_profit = base_profit + recoverable_loss
scen2_margin = (scen2_profit / scen2_sales * 100) if scen2_sales > 0 else 0

# --- 4.3. KỊCH BẢN 3: TỐI ƯU HÓA TOÀN DIỆN (AGGRESSIVE) ---
# a) Doanh số mới từ Cross-selling
scen3_sales = base_sales * (1 + var_cross_sell_boost)
additional_sales = scen3_sales - base_sales
# Giả định lợi nhuận từ doanh số bán kèm bằng biên lợi nhuận cơ sở thực tế (base_margin)
profit_from_cross_sell = additional_sales * (base_margin / 100)

# b) Thu hồi giá trị từ nhóm khách hàng At-Risk/Lost trong df_rfm thực tế
profit_from_vip = 0
if not df_rfm.empty and "Recency" in df_rfm.columns and "Monetary" in df_rfm.columns:
    at_risk_customers = df_rfm[df_rfm["Recency"] > 180]
    total_at_risk_monetary = at_risk_customers["Monetary"].sum()
    # Thu hồi lợi nhuận dựa trên tỷ lệ giữ chân khách hàng được điều chỉnh trên slider
    profit_from_vip = total_at_risk_monetary * var_vip_recovery_rate * (base_margin / 100)

scen3_profit = scen2_profit + profit_from_cross_sell + profit_from_vip
scen3_margin = (scen3_profit / scen3_sales * 100) if scen3_sales > 0 else 0


# =========================================================
# 5. GIAO DIỆN HIỂN THỊ ĐIỀU HÀNH
# =========================================================
st.title("🎯 Superstore Strategic Scenario Dashboard")
st.caption("Báo cáo Quản trị: Mô phỏng Kịch bản Kinh doanh dựa trên Dữ liệu Thực tế")

# 3 Thẻ Kịch bản Điều hành
col_kpi1, col_kpi2, col_kpi3 = st.columns(3)

with col_kpi1:
    st.markdown(
        f"""
    <div class="scenario-card" style="border-left: 6px solid #64748b;">
        <h4 style="margin:0; color:#475569;">1. Kịch Bản Cơ Sở (Base)</h4>
        <p style="color: #64748b; font-size: 0.85em; margin-bottom: 8px;">Giữ nguyên hiện trạng kinh doanh</p>
        <h2 style="color: #0f172a; margin: 0;">{format_compact_number(base_profit)}</h2>
        <p style="font-size: 0.9em; color: #475569; margin-top:5px;">Doanh thu: <b>{format_compact_number(base_sales)}</b> | Margin: <b>{base_margin:.1f}%</b></p>
    </div>
    """,
        unsafe_allow_html=True,
    )

with col_kpi2:
    st.markdown(
        f"""
    <div class="scenario-card" style="border-left: 6px solid #f59e0b;">
        <h4 style="margin:0; color:#d97706;">2. Kịch Bản Thận Trọng</h4>
        <p style="color: #64748b; font-size: 0.85em; margin-bottom: 8px;">Khóa trần chiết khấu {int(var_discount_cap*100)}%</p>
        <h2 style="color: #d97706; margin: 0;">{format_compact_number(scen2_profit)}</h2>
        <p style="font-size: 0.9em; color: #16a34a; margin-top:5px;">Thu hồi lỗ: <b>+{format_compact_number(recoverable_loss)}</b> | Margin mới: <b>{scen2_margin:.1f}%</b></p>
    </div>
    """,
        unsafe_allow_html=True,
    )

with col_kpi3:
    st.markdown(
        f"""
    <div class="scenario-card" style="border-left: 6px solid #16a34a;">
        <h4 style="margin:0; color:#16a34a;">3. Kịch Bản Tối Ưu Hóa</h4>
        <p style="color: #64748b; font-size: 0.85em; margin-bottom: 8px;">Trần {int(var_discount_cap*100)}% + Bundle + VIP</p>
        <h2 style="color: #16a34a; margin: 0;">{format_compact_number(scen3_profit)}</h2>
        <p style="font-size: 0.9em; color: #16a34a; margin-top:5px;">Doanh thu mới: <b>{format_compact_number(scen3_sales)}</b> | Margin: <b>{scen3_margin:.1f}%</b></p>
    </div>
    """,
        unsafe_allow_html=True,
    )

st.markdown("---")

# =========================================================
# 6. CHI TIẾT CÁC TAB TRỰC QUAN HÓA
# =========================================================
tab1, tab2, tab3 = st.tabs(
    [
        "📊 1. So Sánh Mô Phỏng Kịch Bản",
        "💰 2. Phân Tích Điểm Hòa Vốn Chiết Khấu",
        "👥 3. Tác Động Khách Hàng VIP (RFM)",
    ]
)

# ---------------------------------------------------------
# TAB 1: SO SÁNH 3 KỊCH BẢN
# ---------------------------------------------------------
with tab1:
    st.subheader("📊 So Sánh Tăng Trưởng Doanh Thu & Lợi Nhuận Theo Kịch Bản")

    df_scen_summary = pd.DataFrame(
        {
            "Kịch Bản": [
                "1. Base (Cơ sở)",
                "2. Conservative (Thận trọng)",
                "3. Aggressive (Tối ưu)",
            ],
            "Doanh Thu ($)": [base_sales, scen2_sales, scen3_sales],
            "Lợi Nhuận ($)": [base_profit, scen2_profit, scen3_profit],
            "Biên Lợi Nhuận (%)": [base_margin, scen2_margin, scen3_margin],
        }
    )

    c_left, c_right = st.columns(2)

    with c_left:
        fig_profit_bar = px.bar(
            df_scen_summary,
            x="Kịch Bản",
            y="Lợi Nhuận ($)",
            color="Kịch Bản",
            text="Lợi Nhuận ($)",
            title="<b>So Sánh Lợi Nhuận Ròng Dự Báo ($)</b>",
            color_discrete_sequence=["#64748b", "#f59e0b", "#16a34a"],
        )
        fig_profit_bar.update_traces(
            texttemplate="%{text:.3s}", textposition="outside"
        )
        fig_profit_bar.update_layout(showlegend=False, height=420)
        st.plotly_chart(fig_profit_bar, use_container_width=True, config=CHART_CONFIG)

    with c_right:
        fig_margin_line = px.line(
            df_scen_summary,
            x="Kịch Bản",
            y="Biên Lợi Nhuận (%)",
            markers=True,
            title="<b>Tương Quan Tăng Trưởng Biên Lợi Nhuận Ròng (%)</b>",
        )
        fig_margin_line.update_traces(
            line_color="#2563eb", line_width=4, marker_size=10
        )
        fig_margin_line.update_layout(height=420)
        st.plotly_chart(fig_margin_line, use_container_width=True, config=CHART_CONFIG)

# ---------------------------------------------------------
# TAB 2: ĐIỂM HÒA VỐN CHIẾT KHẤU THỰC TẾ
# ---------------------------------------------------------
with tab2:
    st.subheader("💰 Tác Động Thực Tế Của Chiết Khấu Đến Lợi Nhuận")

    if not df_disc.empty:
        c1, c2 = st.columns([2, 1])
        with c1:
            fig_disc_real = px.bar(
                df_disc,
                x="Discount_Pct",
                y="Total_Profit",
                color="Total_Profit",
                color_continuous_scale="RdYlGn",
                title="<b>Tổng Lợi Nhuận Theo Mức Chiết Khấu Trong Dữ Liệu Thực</b>",
                labels={
                    "Discount_Pct": "Mức Chiết Khấu (%)",
                    "Total_Profit": "Tổng Lợi Nhuận ($)",
                },
            )
            # Vạch đỏ biểu diễn trần chiết khấu đang chọn ở sidebar
            fig_disc_real.add_vline(
                x=var_discount_cap * 100,
                line_dash="dash",
                line_color="red",
                annotation_text=f"Trần đang chọn ({int(var_discount_cap*100)}%)",
            )
            st.plotly_chart(fig_disc_real, use_container_width=True, config=CHART_CONFIG)

        with c2:
            st.markdown("#### 📌 Phân Tích Lỗ Hổng Chiết Khấu")
            st.write(
                f"- **Tổng thâm hụt tài chính (Lỗ):** `{format_compact_number(recoverable_loss)}`"
            )
            st.write(
                f"- **Mức trần hiện tại:** `{int(var_discount_cap*100)}%`"
            )
            st.warning(
                "Các đơn hàng có mức chiết khấu vượt quá trần này đang làm suy giảm trực tiếp biên lợi nhuận toàn hệ thống. Áp dụng trần chiết khấu sẽ chuyển các đơn hàng này về mức hòa vốn/lãi nhẹ."
            )

# ---------------------------------------------------------
# TAB 3: KHÁCH HÀNG VIP & RFM THỰC TẾ
# ---------------------------------------------------------
with tab3:
    st.subheader("👥 Phân Tích Giá Trị Thu Hồi Từ Khách Hàng At-Risk / Lost")

    if not df_rfm.empty and "Recency" in df_rfm.columns:
        at_risk_df = df_rfm[df_rfm["Recency"] > 180]
        total_at_risk_count = len(at_risk_df)
        total_at_risk_monetary = at_risk_df["Monetary"].sum() if "Monetary" in at_risk_df.columns else 0

        c_rfm1, c_rfm2 = st.columns(2)
        with c_rfm1:
            st.metric(
                "🚨 Số Khách Hàng Nguy Cơ Rời Bỏ (>180 ngày)",
                f"{total_at_risk_count:,} Khách hàng",
            )
            st.metric(
                "💰 Tổng Giá Trị Doanh Số Nhóm At-Risk",
                format_compact_number(total_at_risk_monetary),
            )
        with c_rfm2:
            st.metric(
                "🚀 Lợi Nhuận Thu Hồi Dự Kiến (Kịch Bản 3)",
                format_compact_number(profit_from_vip),
                f"Tỷ lệ kích hoạt lại: {int(var_vip_recovery_rate*100)}%",
            )
            st.success(
                f"Bằng cách triển khai chương trình Email Re-engagement, việc cứu vãn {int(var_vip_recovery_rate*100)}% nhóm khách hàng này đóng góp trực tiếp vào mục tiêu của Kịch bản Tối ưu."
            )
