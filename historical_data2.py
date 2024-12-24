import streamlit as st
from nselib import capital_market
from io import BytesIO
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed

st.title("NSE Historical Data")

# Initialize session state for persistence
if "processed_chunks" not in st.session_state:
    st.session_state.processed_chunks = []
if "failed_tickers" not in st.session_state:
    st.session_state.failed_tickers = []
if "uploaded_file" not in st.session_state:
    st.session_state.uploaded_file = None

def reset_session_state():
    """Resets session state variables."""
    st.session_state.processed_chunks = []
    st.session_state.failed_tickers = []
    st.session_state.uploaded_file = None

def split_dataframe(dfs, chunk_size):
    return [dfs[i:i + chunk_size] for i in range(0, len(dfs), chunk_size)]

# Sidebar inputs
uploaded_file = st.sidebar.file_uploader("Upload Excel", type=['xlsx', 'xls'])

if st.sidebar.button("Reset"):
    reset_session_state()
    st.experimental_rerun()

if uploaded_file:
    if uploaded_file != st.session_state.uploaded_file:
        # New file uploaded; reset state
        reset_session_state()
        st.session_state.uploaded_file = uploaded_file

    data = pd.read_excel(uploaded_file)

    if not data.empty:
        ticker_column = st.sidebar.selectbox("Select Column with Symbols", options=data.columns.tolist())
        period_ = st.sidebar.selectbox("Period", options=("1M", "1W", "1Y"))
        chunksize = st.sidebar.selectbox("Chunk Size", options=(100, 50))
        display_data = st.sidebar.checkbox("Display Processed Data", value=False)
    else:
        st.warning("Uploaded file is empty. Please upload a valid Excel file.")

    chunks = split_dataframe(data, chunksize)

    if st.sidebar.button("Proceed"):
        st.session_state.processed_chunks = []  # Reset for new processing
        st.session_state.failed_tickers = []

        for idx, df_chunk in enumerate(chunks):
            st.write(f"Processing chunk {idx + 1}/{len(chunks)}")

            tickers = df_chunk[ticker_column].dropna().unique().tolist()
            chunk_results = pd.DataFrame()
            failed_tickers = []

            # Progress bar for the chunk
            progress = st.progress(0)

            def fetch_ticker_data(ticker):
                """Fetch data for a single ticker."""
                try:
                    data = capital_market.price_volume_data(ticker, period=period_)
                    data=data[data['Series']=='EQ']
                    return data[["Date", "ClosePrice"]].rename(columns={"ClosePrice": f"{ticker}"})
                except Exception as e:
                    return pd.DataFrame({"Error": [f"Error for {ticker}: {e}"]})

            # Concurrent fetching
            with ThreadPoolExecutor() as executor:
                future_to_ticker = {executor.submit(fetch_ticker_data, ticker): ticker for ticker in tickers}
                for i, future in enumerate(as_completed(future_to_ticker)):
                    ticker = future_to_ticker[future]
                    try:
                        data = future.result()
                        if "Error" in data.columns:
                            failed_tickers.append(ticker)
                        else:
                            if chunk_results.empty:
                                chunk_results = data
                            else:
                                chunk_results = chunk_results.merge(data, on="Date", how="left")
                    except Exception as e:
                        failed_tickers.append(ticker)
                        st.error(f"Error processing {ticker}: {e}")
                    finally:
                        progress.progress((i + 1) / len(tickers))

            # Save chunk results and errors in session state
            st.session_state.processed_chunks.append((idx + 1, chunk_results))
            st.session_state.failed_tickers.extend(failed_tickers)

# Display processed results
if st.session_state.processed_chunks:
    for idx, (chunk_id, chunk_results) in enumerate(st.session_state.processed_chunks):
        st.write(f"Processed Data for Chunk {chunk_id}:")
        if display_data:
            st.dataframe(chunk_results)

        # Convert to Excel for download
        excel_file = BytesIO()
        with pd.ExcelWriter(excel_file, engine='xlsxwriter') as writer:
            chunk_results.to_excel(writer, index=False, sheet_name="Sheet1")
        excel_file.seek(0)

        # Download button for this chunk
        st.sidebar.download_button(
            label=f"Download Chunk {chunk_id}",
            data=excel_file,
            file_name=f"processed_chunk_{chunk_id}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

# Display failed tickers
if st.session_state.failed_tickers:
    st.warning(f"Failed to fetch data for: {', '.join(st.session_state.failed_tickers)}")
