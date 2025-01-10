import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import re

# Streamlit app title
st.title("Screener Ratios Fetcher")

# User input for login credentials
username = st.text_input("Username (Email)", "", type="default")
password = st.text_input("Password", "", type="password")
ticker_list = st.text_area("Enter Ticker Symbols (Comma-separated)")
fetch_button = st.button("Fetch Ratios")

# Initialize session
session = requests.Session()
login_url = "https://www.screener.in/login/"
ratios_df = pd.DataFrame()

# Function to fetch all ratios
def fetch_all_ratios(ticker, url, retries=5):
    headers = {
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "en-US,en;q=0.9,en-IN;q=0.8",
        "Referer": url,
        "Sec-Ch-Ua": "\"Microsoft Edge\";v=\"131\", \"Chromium\";v=\"131\", \"Not_A Brand\";v=\"24\"",
        "Sec-Ch-Ua-Mobile": "?1",
        "Sec-Ch-Ua-Platform": "\"Android\"",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Mobile Safari/537.36 Edg/131.0.0.0",
        "X-Requested-With": "XMLHttpRequest"
    }

    for attempt in range(retries):
        try:
            response = session.get(url, headers=headers)
            soup = BeautifulSoup(response.content, "html.parser")
            ratios = {}

            ratios_div = soup.find("div", class_="company-ratios")
            if ratios_div:
                items = ratios_div.find_all("li", class_="flex flex-space-between")
                ratios["Ticker"] = ticker
                for item in items:
                    ratio_name = item.find("span", class_="name").get_text(strip=True)
                    value_parts = item.find("span", class_="value").stripped_strings
                    ratio_value = " ".join(value_parts)
                    ratios[ratio_name] = ratio_value
                return ratios
            else:
                st.warning(f"No ratios found for {ticker}")
                return None
        except Exception as e:
            st.error(f"Error fetching data for {ticker}: {e}")
            time.sleep(2 ** attempt)
    return None

# Login and fetch data
if fetch_button:
    if username and password and ticker_list:
        # Parse ticker symbols
        TickerList = [ticker.strip() for ticker in ticker_list.split(",")]

        # Fetch CSRF token
        response = session.get(login_url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            csrf_token = soup.find("input", {"name": "csrfmiddlewaretoken"})
            csrf_token = csrf_token["value"] if csrf_token else None

            if csrf_token:
                # Login data
                login_data = {
                    "username": username,
                    "password": password,
                    "csrfmiddlewaretoken": csrf_token
                }

                headers = {
                    "Referer": login_url,
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
                }

                # Send login request
                login_response = session.post(login_url, data=login_data, headers=headers)

                if login_response.status_code == 200:
                    cookies = session.cookies.get_dict()
                    if cookies:
                        st.success("Login successful!")

                        # Fetch ratios for each ticker
                        for ticker in TickerList:
                            st.write(f"Fetching data for {ticker}...")
                            ratios = fetch_all_ratios(ticker, f"https://www.screener.in/company/{ticker}/consolidated/")
                            if ratios:
                                ratios_df = pd.concat([ratios_df, pd.DataFrame([ratios])], ignore_index=True)

                        # Display data
                        if not ratios_df.empty:
                            st.write("### Ratios Data")
                            st.dataframe(ratios_df)

                            # Provide download option
                            csv = ratios_df.to_csv(index=False)
                            st.download_button("Download CSV", csv, "ratios_data.csv", "text/csv")
                        else:
                            st.warning("No data fetched. Please check the ticker symbols.")
                    else:
                        st.error("Login failed. Check your credentials.")
                else:
                    st.error("Login request failed. Verify your username, password, or CSRF token.")
            else:
                st.error("CSRF token not found.")
        else:
            st.error(f"Failed to load login page. Status code: {response.status_code}")
    else:
        st.error("Please fill in all fields.")
