import streamlit as st
import pandas as pd
from nselib import capital_market
from json.decoder import JSONDecodeError
import logging
from io import BytesIO

# Configure logging
logging.basicConfig(level=logging.ERROR)

# App title
st.title("NSE Dashboard")


# Sidebar instrument selection
instrument = st.sidebar.selectbox("Instrument Type", options=("NSE Equity Market", "NSE Derivatives Market"))

# Function to download data
def download_data(data, file_name="Data.xlsx"):
    excel_file = BytesIO()
    with pd.ExcelWriter(excel_file, engine='xlsxwriter') as writer:
        data.to_excel(writer, index=False, sheet_name="Sheet1")
    excel_file.seek(0)
    st.sidebar.download_button(
        label="Download",
        data=excel_file,
        file_name=file_name,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# Caching the API call results
@st.cache_data
def fetch_static_data(data_info):
    """Fetch static data like equity lists."""
    return getattr(capital_market, data_info)()

@st.cache_data
def fetch_date_based_data(data_info, date):
    """Fetch date-based data like bhav copy."""
    return getattr(capital_market, data_info)(date)

@st.cache_data
def fetch_period_based_data(data_info, period):
    """Fetch period-based data like bulk deals."""
    return getattr(capital_market, data_info)(period=period)

@st.cache_data
def fetch_ticker_period_data(data_info, ticker, period):
    """Fetch data based on ticker and period."""
    return getattr(capital_market, data_info)(ticker, period=period)

# Equity Market
if instrument == "NSE Equity Market":
    st.sidebar.write("Equity Market Options")
    data_info = st.sidebar.selectbox(
        "Data to Extract",
        options=(
            "bhav_copy_equities", "bhav_copy_with_delivery", "block_deals_data", "bulk_deal_data",
            "deliverable_position_data", "price_volume_and_deliverable_position_data",
            "price_volume_data", "equity_list", "fno_equity_list",
            "index_data", "market_watch_all_indices", "nifty50_equity_list", "short_selling_data"
        )
    )

    # Initialize data variable
    data = None
    st.write(data_info)

    try:
        with st.spinner("Fetching data..."):
            # Handle static data types
            if data_info in ["equity_list", "fno_equity_list", "market_watch_all_indices", "nifty50_equity_list"]:
                data = fetch_static_data(data_info)

            # Handle date-based data types
            elif data_info in ["bhav_copy_equities", "bhav_copy_with_delivery"]:
                date = st.sidebar.date_input("Date")
                if date:
                    date_str = date.strftime("%d-%m-%Y")
                    data = fetch_date_based_data(data_info, date_str)

            # Handle period-based data types
            elif data_info in ["bulk_deal_data", "block_deals_data", "short_selling_data"]:
                period_ = st.sidebar.text_input("Period", "1M")
                if period_:
                    data = fetch_period_based_data(data_info, period_)

            # Handle ticker and period-based data types
            elif data_info in ["deliverable_position_data", "price_volume_and_deliverable_position_data", "price_volume_data"]:
                ticker = st.sidebar.text_input("Ticker", "TECHM")
                period_ = st.sidebar.text_input("Period", "1M")
                if ticker and period_:
                    data = fetch_ticker_period_data(data_info, ticker, period_)

                                # Handle ticker and period-based data types
            elif data_info in ['index_data']:
                ticker = st.sidebar.text_input("Ticker", "NIFTY 50")
                period_ = st.sidebar.text_input("Period", "1M")
                if ticker and period_:
                    data = fetch_ticker_period_data(data_info, ticker, period_)

        # Display and download data
        if data is not None and not data.empty:
            st.dataframe(data)
            download_data(data)
        else:
            st.warning("No data available for the selected parameters.")

    except JSONDecodeError as e:
        logging.error(f"JSONDecodeError: {e}")
        st.error(f"Error decoding JSON: {e}")
    except Exception as e:
        logging.error(f"Error fetching data: {e}")
        st.error(f"An error occurred: {e}")

# Derivatives Market Placeholder
elif instrument == "NSE Derivatives Market":
    st.info("Derivatives Market functionality is under development.")
