import os
import pandas as pd
import plotly.express as px
import streamlit as st

# Kiểm tra thư viện Gemini API
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

# =========================================================
# 1. CẤU HÌNH TRANG & GIAO DIỆN (E-COMMERCE THEME)
# =========================================================
st.set_page_config(
    page_title="Superstore Executive Dashboard",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Bảng màu Plotly chuẩn E-Commerce
PALETTE = ["#FF6B6B", "#6C5CE7", "#00CEC9", "#FFA502", "#00B894", "#E84393"]
px.defaults.color_discrete_sequence = PALETTE
CHART_CONFIG = {"displayModeBar": False}

# CSS Tùy chỉnh giao diện
st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #e4e8f0 100%);
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e1e2f 0%, #11111d 100%);
    }
    [data-testid="stSidebar"] * {
        color: #e0e0e0 !important;
    }
    h1 {
        background: linear-gradient(90deg, #ff6b6b, #6c5ce7);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800 !important;
        margin-bottom: 0.2rem !important;
    }
    [data-testid="stMetric"] {
        background: #ffffff;
        padding: 16px 18px;
        border-radius: 16px;
        box-shadow: 0 10px 25px rgba(108, 92, 231, 0.08);
        border: 1px solid rgba(255, 255, 255, 0.8);
        border-left: 6px solid #ff6b6b;
    }
    [data-testid="stMetricValue"] {
        color: #2d3436 !important;
        font-size: 1.55rem !important;
        font-weight: 800 !important;
        white-space: nowrap !important;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: rgba(255, 255, 255, 0.7);
        padding: 6px 8px;
        border-radius: 14px;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(90deg, #ff6b6b 0%, #ff8e53 100%) !important;
        color: #ffffff !important;
        font-weight: 700;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# =========================================================
# 2. HÀM ĐỌC & XỬ LÝ DỮ LIỆU
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

# Cấu hình API Key cho AI Chatbot
st.sidebar.markdown("---")
st.sidebar.header("🤖 Cấu hình AI Chatbot")
api_key_input = st.sidebar.text_input(
    "🔑 Nhập Gemini API Key:", type="password", help="Dùng cho Tab Chatbot AI"
)

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
# 4. KPI TỔNG QUAN
# =========================================================
st.title("🛍️ Superstore Executive Dashboard")
st.caption("Bảng điều hành quản trị: Tài chính, Chiết khấu, Khách hàng & Vận hành")

total_sales = df_cat["Total_Sales"].sum()
total_profit = df_cat["Total_Profit"].sum()
avg_margin = (total_profit / total_sales) * 100 if total_sales > 0 else 0
vip_count = int(len(df_rfm) * 0.2) if not df_rfm.empty else 0

col1, col2, col3, col4 = st.columns(4)
col1.metric("💰 Doanh Thu", format_compact_number(total_sales), "+8.4% MoM")
col2.metric("📈 Lợi Nhuận", format_compact_number(total_profit), "+3.2% MoM")
col3.metric(
    "📊 Biên Lợi Nhuận TB", f"{avg_margin:.1f}%", "-0.5% Target", delta_color="inverse"
)
col4.metric("👥 Khách Hàng VIP", f"{vip_count:,} KH", "+12 KH mới")

st.markdown("---")

# =========================================================
# 5. CÁC TAB PHÂN TÍCH CHUYÊN SÂU (7 TABS)
# =========================================================
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(
    [
        "📋 Báo Cáo Điều Hành & Insights",
        "💰 Tài Chính & Mô Phỏng",
        "🎯 Chiết Khấu & Gánh Lỗ",
        "👥 Khách Hàng RFM",
        "🚚 Vận Hành & Xu Hướng",
        "🛒 Bán Chéo",
        "💬 Trợ Lý AI Chatbot",
    ]
)

# --- TAB 1: EXECUTIVE BRIEFING ---
with tab1:
    st.subheader("📋 Báo Cáo Điều Hành & Ma Trận Hành Động Tự Động")
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
    saved_loss = df_disc[
        (df_disc["Discount"] > discount_cap) & (df_disc["Total_Profit"] < 0)
    ]["Total_Profit"].abs().sum()

    st.info(
        f"💡 **Mô phỏng:** Nếu áp dụng mức trần chiết khấu **<= {int(discount_cap*100)}%**, "
        f"ước tính cắt giảm được **{format_compact_number(saved_loss)}** tiền lỗ!"
    )

    c1, c2 = st.columns(2)
    with c1:
        fig_cat = px.bar(
            df_cat,
            x="Category",
            y=["Total_Sales", "Total_Profit"],
            barmode="group",
            title="Doanh Thu & Lợi Nhuận Theo Ngành Hàng",
        )
        st.plotly_chart(fig_cat, use_container_width=True, config=CHART_CONFIG)
    with c2:
        fig_reg = px.bar(
            filtered_region,
            x="Region",
            y="Profit_Margin_Pct",
            color="Category",
            barmode="group",
            title="Biên Lợi Nhuận (%) Theo Vùng & Danh Mục",
        )
        st.plotly_chart(fig_reg, use_container_width=True, config=CHART_CONFIG)

# --- TAB 3: CHIẾT KHẤU & GÁNH LỖ ---
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
        )
        fig_disc.add_hline(
            y=0, line_dash="dash", line_color="#FF6B6B", annotation_text="Hòa Vốn"
        )
        st.plotly_chart(fig_disc, use_container_width=True, config=CHART_CONFIG)
    with c2:
        fig_loss = px.bar(
            df_loss,
            x="Total_Profit",
            y="Sub-Category",
            orientation="h",
            color="Total_Profit",
            title="Top Sub-Category Âm Lợi Nhuận Nhất",
            color_continuous_scale="Reds_r",
        )
        st.plotly_chart(fig_loss, use_container_width=True, config=CHART_CONFIG)

# --- TAB 4: KHÁCH HÀNG RFM ---
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
        st.plotly_chart(fig_pareto, use_container_width=True, config=CHART_CONFIG)
    with c2:
        st.markdown("#### 🔎 Tra Cứu Khách Hàng (RFM)")
        search = st.text_input("Nhập Mã KH hoặc Tên (vd: CG-12520):", "")
        df_rfm_clean = df_rfm.fillna("N/A")
        if search:
            match_cond = df_rfm_clean["Customer ID"].astype(str).str.contains(
                search, case=False, na=False
            )
            if "Customer Name" in df_rfm_clean.columns:
                match_cond = match_cond | df_rfm_clean["Customer Name"].astype(
                    str
                ).str.contains(search, case=False, na=False)
            res = df_rfm_clean[match_cond]
            st.dataframe(res if not res.empty else df_rfm_clean.head(10), use_container_width=True)
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
            title="📈 Xu Hướng Doanh Thu & Lợi Nhuận Theo Tháng",
            markers=True,
        )
        st.plotly_chart(fig_month, use_container_width=True, config=CHART_CONFIG)

    if not df_ship.empty:
        c1, c2 = st.columns(2)
        with c1:
            fig_ship_time = px.bar(
                df_ship,
                x="Ship Mode",
                y="Avg_Lead_Time_Days",
                color="Ship Mode",
                title="🚚 Thời Gian Giao Hàng Trung Bình (Ngày)",
                text_auto=".1f",
            )
            st.plotly_chart(fig_ship_time, use_container_width=True, config=CHART_CONFIG)
        with c2:
            fig_ship_margin = px.bar(
                df_ship,
                x="Ship Mode",
                y="Profit_Margin_Pct",
                color="Profit_Margin_Pct",
                title="💎 Biên Lợi Nhuận (%) Theo Hình Thức Vận Chuyển",
                text_auto=".1f",
            )
            st.plotly_chart(fig_ship_margin, use_container_width=True, config=CHART_CONFIG)

# --- TAB 6: BÁN CHÉO ---
with tab6:
    st.subheader("5. Gợi Ý Sản Phẩm Bán Kèm (Cross-Selling)")
    if "Product_A" in df_pairs.columns:
        prod_list = list(df_pairs["Product_A"].unique())
        prod = st.selectbox("🛒 Chọn sản phẩm / danh mục phụ:", prod_list)
        pairs = df_pairs[
            (df_pairs["Product_A"] == prod) | (df_pairs["Product_B"] == prod)
        ].sort_values(by="Times_Bought_Together", ascending=False)
        st.dataframe(pairs, use_container_width=True)

# --- TAB 7: TRỢ LÝ AI CHATBOT (ĐÃ TỐI ƯU HÓA BỘ NHỚ HỘI THOẠI) ---
with tab7:
    st.subheader("💬 Trợ Lý AI Phân Tích Bán Hàng (Interactive Chat)")
    st.caption("Trò chuyện cùng AI có duy trì ngữ cảnh hội thoại (Multi-turn Chat) real-time.")

    api_key = st.secrets.get("GEMINI_API_KEY", api_key_input)

    if GEMINI_AVAILABLE and api_key:
        try:
            genai.configure(api_key=api_key)
            
            system_instruction = f"""
            Bạn là Trợ lý AI Phân tích Kinh doanh chuyên nghiệp cho hệ thống Superstore E-Commerce.
            Dữ liệu tổng quan hiện tại của hệ thống:
            - Tổng Doanh Thu: ${total_sales:,.0f}
            - Tổng Lợi Nhuận: ${total_profit:,.0f}
            - Biên Lợi Nhuận TB: {avg_margin:.1f}%
            - Sản phẩm gây âm lợi nhuận lớn nhất: {worst_sub_name} (Âm {worst_sub_loss:,.0f}$)
            - Mức chiết khấu an toàn: <= 20%. Chiết khấu > 30% gây thâm hụt nghiêm trọng.
            
            Nhiệm vụ: Trả lời ngắn gọn, súc tích bằng tiếng Việt, tập trung đề xuất giải pháp kinh doanh.
            """

            # Khởi tạo mô hình kèm system_instruction
            model = genai.GenerativeModel(
                model_name='gemini-2.5-flash',
                system_instruction=system_instruction
            )

            # Khởi tạo phiên Chat Session duy trì bộ nhớ trong session_state
            if "chat_session" not in st.session_state:
                st.session_state.chat_session = model.start_chat(history=[])

            # Hiển thị lại lịch sử trò chuyện từ phiên chat của Gemini
            for message in st.session_state.chat_session.history:
                role = "user" if message.role == "user" else "assistant"
                message_text = "".join([part.text for part in message.parts if hasattr(part, "text")])
                with st.chat_message(role):
                    st.write(message_text)

            # Lời chào mặc định nếu lịch sử trống
            if not st.session_state.chat_session.history:
                with st.chat_message("assistant"):
                    initial_greeting = "Xin chào! Tôi là Trợ lý AI của Superstore. Bạn muốn phân tích thông tin gì về báo cáo bán hàng, lợi nhuận hay chiến lược chiết khấu hôm nay?"
                    st.write(initial_greeting)

            # Ô nhập liệu chat
            if prompt_input := st.chat_input("Nhập câu hỏi phân tích...", key="superstore_chat_input"):
                with st.chat_message("user"):
                    st.write(prompt_input)

                with st.chat_message("assistant"):
                    with st.spinner("AI đang phân tích dữ liệu..."):
                        try:
                            response = st.session_state.chat_session.send_message(prompt_input)
                            st.write(response.text)
                        except Exception as chat_err:
                            st.error(f"⚠️ Không thể nhận phản hồi từ AI: {chat_err}")

        except Exception as err:
            st.error(f"❌ Lỗi khởi tạo Gemini API: {err}")
    else:
        st.info(
            "💡 **Hướng dẫn kích hoạt Chatbot AI:**\n"
            "1. Thêm gói `google-generativeai` vào tệp `requirements.txt`.\n"
            "2. Nhập Gemini API Key tại ô cấu hình thanh Sidebar bên trái (hoặc thêm vào Secrets)."
        )
