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
    st.error

