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
        st.error(f"Error fetching data for {ticker}: {e}")
        return pd.DataFrame()

# Sidebar inputs
# tickers = st.sidebar.text_area("Tickers (comma-separated)", "TECHM, INFY, TCS").split(",")
# tickers=st.sidebar.input("Upload Excel")
# tickers = [ticker.strip() for ticker in tickers if ticker.strip()]  # Clean up whitespace
uploaded_file = st.sidebar.file_uploader("Upload Excel", type=['xlsx', 'xls'])
if uploaded_file:
    df=pd.read_excel(uploaded_file)
    period_ = st.sidebar.selectbox("Period", options=("1M", "1W", "1Y"))
    if not df.empty:
        tickers=st.sidebar.selectbox("Select Column with Symbols",options=(df.columns.tolist()))


if st.sidebar.button("Proceed"):
    # Initialize an empty DataFrame
    merged_data = pd.DataFrame()

    # Fetch and merge data for each ticker
    if tickers and period_:
        for ticker in df[tickers]:
            data = fetch_ticker_period_data("price_volume_and_deliverable_position_data", ticker, period_)
            if not data.empty:
                data = data[["Date", "ClosePrice"]].rename(columns={"ClosePrice": f"{ticker}_ClosePrice"})
                if merged_data.empty:
                    merged_data = data
                else:
                    merged_data = pd.merge(merged_data, data, on="Date", how="outer")
            else:
                st.warning(f"No data available for ticker: {ticker}")

        # Display merged data
        if not merged_data.empty:
            # merged_data.sort_values("Date", inplace=True)  # Ensure the data is sorted by date
            st.dataframe(merged_data)

            # Allow downloading of merged data
            download_data(merged_data)
        else:
            st.warning("No data available for the selected tickers and period.")
    else:
        st.info("Please enter at least one ticker and select a period.")