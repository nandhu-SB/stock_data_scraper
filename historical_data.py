import streamlit as st
from nselib import capital_market
from io import BytesIO
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
import zipfile

st.title("Historical Data Viewer - Concurrent Batch Processing")

# Function to download a single batch of data
def save_batch_to_excel(data, batch_number):
    """Prepare batch data as an Excel file."""
    excel_file = BytesIO()
    with pd.ExcelWriter(excel_file, engine="xlsxwriter") as writer:
        data.to_excel(writer, index=False, sheet_name=f"Batch_{batch_number}")
    excel_file.seek(0)
    return excel_file

# Function to fetch data for a single ticker
@st.cache_data
def fetch_ticker_data(ticker, period):
    """Fetch data for a single ticker."""
    try:
        data = capital_market.price_volume_and_deliverable_position_data(ticker, period=period)
        return data[["Date", "ClosePrice"]].rename(columns={"ClosePrice": f"{ticker}"})
    except Exception as e:
        return pd.DataFrame({"Error": [f"Error for {ticker}: {e}"]})

# Function to process a batch of tickers
def process_batch(batch, batch_number, period):
    """Process a single batch of tickers."""
    batch_data = pd.DataFrame()
    for ticker in batch:
        data = fetch_ticker_data(ticker, period)
        if not data.empty and "Error" not in data.columns:
            if batch_data.empty:
                batch_data = data
            else:
                batch_data = pd.merge(batch_data, data, on="Date", how="outer")
    return batch_data

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
    progress_bar = st.progress(0)  # Progress bar

    # Divide tickers into batches
    batches = [tickers[i:i + batch_size] for i in range(0, len(tickers), batch_size)]
    num_batches = len(batches)

    # Dictionary to store each batch's processed data
    all_batches = {}

    # Display status dynamically
    status_placeholder = st.empty()

    with ThreadPoolExecutor() as executor:
        future_to_batch = {
            executor.submit(process_batch, batch, batch_number, period_): batch_number
            for batch_number, batch in enumerate(batches, start=1)
        }

        for future in as_completed(future_to_batch):
            batch_number = future_to_batch[future]
            try:
                batch_data = future.result()
                if not batch_data.empty:
                    # Save the processed batch in memory
                    all_batches[batch_number] = save_batch_to_excel(batch_data, batch_number)

                    # Display download button for the completed batch
                    st.sidebar.download_button(
                        label=f"Download Batch {batch_number}",
                        data=all_batches[batch_number],
                        file_name=f"Batch_{batch_number}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    )
                    st.success(f"Batch {batch_number} processed successfully!")
                else:
                    st.warning(f"Batch {batch_number} has no data.")
            except Exception as e:
                st.error(f"Error processing batch {batch_number}: {e}")

            # Update progress bar and status
            progress_bar.progress(len(all_batches) / num_batches)
            status_placeholder.text(f"Processed {len(all_batches)} of {num_batches} batches.")

    # Option to download all batches at the end
    if all_batches:
        # Create a zip file containing all batches
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as zip_file:
            for batch_number, excel_file in all_batches.items():
                zip_file.writestr(f"Batch_{batch_number}.xlsx", excel_file.getvalue())
        zip_buffer.seek(0)

        # Provide a single download button for the zip file
        st.sidebar.download_button(
            label="Download All Batches",
            data=zip_buffer,
            file_name="All_Batches.zip",
            mime="application/zip",
        )
        st.success("All batches processed and available for download!")
else:
    st.info("Please upload a file, select a column, and click Proceed.")
