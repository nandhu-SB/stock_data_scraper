import streamlit as st
from nselib import capital_market
from io import BytesIO
import pandas as pd

st.title("Historical Data Viewer - Multiple Tickers")

# Function to download data
def download_data(data, file_name="Merged_Data.xlsx"):
    """Prepare and download merged data as an Excel file."""
    excel_file = BytesIO()
    with pd.ExcelWriter(excel_file, engine="xlsxwriter") as writer:
        data.to_excel(writer, index=False, sheet_name="Sheet1")
    excel_file.seek(0)
    st.sidebar.download_button(
        label="Download Merged Data",
        data=excel_file,
        file_name=file_name,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

# Cache function to fetch data
@st.cache_data
def fetch_ticker_period_data(data_info, ticker, period):
    """Fetch data based on ticker and period."""
    try:
        return getattr(capital_market, data_info)(ticker, period=period)
    except Exception as e:
        return pd.DataFrame()

# Sidebar inputs
uploaded_file = st.sidebar.file_uploader("Upload Excel", type=['xlsx', 'xls'])
if uploaded_file:
    df = pd.read_excel(uploaded_file)
    if not df.empty:
        ticker_column = st.sidebar.selectbox("Select Column with Symbols", options=df.columns.tolist())
        tickers = df[ticker_column].dropna().unique().tolist()  # Extract unique tickers
        period_ = st.sidebar.selectbox("Period", options=("1M", "1W", "1Y"))
    else:
        st.warning("Uploaded file is empty. Please upload a valid Excel file.")
else:
    tickers, period_ = None, None

batch_size = 50  # Define batch size for processing
if st.sidebar.button("Proceed") and tickers and period_:
    merged_data = pd.DataFrame()

    # Process tickers in batches
    for i in range(0, len(tickers), batch_size):
        batch = tickers[i:i + batch_size]
        st.sidebar.info(f"Processing batch {i // batch_size + 1} of {len(tickers) // batch_size + 1}")

        for ticker in batch:
            data = fetch_ticker_period_data("price_volume_and_deliverable_position_data", ticker, period_)
            if not data.empty:
                data = data[["Date", "ClosePrice"]].rename(columns={"ClosePrice": f"{ticker}_ClosePrice"})
                if merged_data.empty:
                    merged_data = data
                else:
                    merged_data = pd.merge(merged_data, data, on="Date", how="outer")

    # Display merged data
    if not merged_data.empty:
        merged_data.sort_values("Date", inplace=True)
        st.dataframe(merged_data)
        download_data(merged_data)
    else:
        st.warning("No data available for the selected tickers and period.")
else:
    st.info("Please upload a file, select a column, and click Proceed.")
