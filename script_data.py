import pandas as pd
import streamlit as st
from io import BytesIO
import time
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor

st.title("MOAT SCRAPPER")
# st.divider()

# File uploader
home,data,logs=st.tabs(['Home','Processed Data','Logs'])
uploaded_file = st.sidebar.file_uploader("Upload Excel", type=['xlsx', 'xls'])
if uploaded_file:
    # st.divider()
    with home:
        st.caption("Loaded Data")
        df = pd.read_excel(uploaded_file)
        st.dataframe(df.head())

    # Dropdown to select the column containing company identifiers
    column_options = list(df.columns)
    selected_column = st.sidebar.selectbox("Select the column with Ticker Values", column_options)

    # Function to fetch all ratios with exponential backoff
    def fetch_all_ratios(url, retries=5):
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        backoff_time = 5  # Initial backoff time in seconds
        for attempt in range(retries):
            try:
                response = requests.get(url, headers=headers)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, "html.parser")
                    ratios_div = soup.find("div", class_="company-ratios")
                    if ratios_div:
                        ratios = {}
                        for item in ratios_div.find_all("li"):
                            ratio_name = item.find("span", class_="name").get_text(strip=True)
                            ratio_value = item.find("span", class_="value").get_text(strip=True)
                            ratios[ratio_name] = ratio_value
                        return ratios
                    else:
                        return {"Error": "Company ratios section not found"}
                    current_price=soup.find("div",class_="")
                elif response.status_code == 429:
                    # with logs:
                    #     st.sidebar.write(f"Rate limited. Retrying after {backoff_time} seconds. URL: {url}")
                    time.sleep(backoff_time)
                    backoff_time *= 2  # Double the backoff time for the next attempt
                else:
                    return {"Error": f"Failed with status code {response.status_code}"}
            except Exception as e:
                return {"Error": str(e)}
        return {"Error": "Max retries reached"}
    
    def parse_crore_value2(value_str):
        """
        Converts a string like '₹3,05,993Cr' or '₹249239.' into an integer value.

        Args:
            value_str (str): The string representing the value.

        Returns:
            int: The numeric value in integer form, or 0 if the value is invalid.
        """
        if not value_str or value_str.strip() == "":
            return 0  # Return 0 if the value is empty or None

        # Remove currency symbol and suffix, then remove commas
        clean_str = value_str.replace("₹", "").replace("Cr", "").replace(",", "").replace("%","").strip()

        # Remove any trailing periods
        clean_str = clean_str.rstrip(".")

        try:
            # Convert to float to handle decimal values, then to integer
            numeric_value = (float(clean_str) * 1)  # 'Cr' denotes Crores
        except ValueError:
            return 0  # Return 0 if conversion fails

        return numeric_value



    # Function to process DataFrame
    def process_dataframe(df, url_column):
        if url_column not in df.columns:
            st.sidebar.write(f"Column '{url_column}' not found in the DataFrame.")
            return df

        results = []
        progress = st.progress(0)

        def fetch_ratios_for_row(row):
            url = f"https://www.screener.in/company/{row[url_column]}/consolidated"
            ratios = fetch_all_ratios(url)

            # ratios['URL'] = url  # Add URL for reference/debugging
            return ratios

        with ThreadPoolExecutor(max_workers=2) as executor:  # Limit parallel requests
            for idx, result in enumerate(executor.map(fetch_ratios_for_row, df.to_dict('records'))):
                results.append(result)
                progress.progress((idx + 1) / len(df))

        # Combine results into a DataFrame
        result_df = pd.concat([df, pd.DataFrame(results)], axis=1)

        # st.write(result_df.columns)

        # Handle rows with invalid Market Cap
        invalid_cap_rows = result_df[result_df['Market Cap'] == '₹Cr.']
        for idx, row in invalid_cap_rows.iterrows():
            url = f"https://www.screener.in/company/{row[url_column]}"
            with logs:
                st.write(f"Re-fetching data for missing Market Cap at URL: {url}")
            new_ratios = fetch_all_ratios(url)

            # Update the row with newly fetched data
            for key, value in new_ratios.items():
                result_df.at[idx, key] = value

        return result_df

    # Proceed button
    if st.sidebar.button("Proceed"):
        st.divider()
        with st.spinner("Processing..."):
            processed_df = process_dataframe(df, selected_column)
        st.success("Processing complete! Go to Processed data tab to view the data")
        # st.balloons()

        processed_df['PB Ratio']=processed_df["Current Price"].apply(parse_crore_value2)/processed_df["Book Value"].apply(parse_crore_value2)



        with data:
            st.dataframe(processed_df)

        # Convert to Excel for download
        excel_file = BytesIO()
        with pd.ExcelWriter(excel_file, engine='xlsxwriter') as writer:
            processed_df.to_excel(writer, index=False, sheet_name="Sheet1")
        excel_file.seek(0)

        # Download button
        st.sidebar.download_button(
            label="Download Processed File",
            data=excel_file,
            file_name="processed_file.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
else:
    st.sidebar.write("Please upload a file to continue.")
