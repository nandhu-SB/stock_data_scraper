import os
import spacy
from bs4 import BeautifulSoup
import pandas as pd
import requests
import streamlit as st
import re
from fuzzywuzzy import process

# Load spaCy model
nlp = spacy.load("en_core_web_md")

# Streamlit Title
st.title("STOCK NEWS :zap:")

@st.cache_data
def extract_text_from_rss(urls):
    """
    Parses the RSS XML feed and extracts titles.
    """
    headings = []
    for url in urls:
        try:
            r = requests.get(url, timeout=10)
            if r.status_code == 200:
                soup = BeautifulSoup(r.content, features="xml")
                items = soup.find_all("item")  # RSS feed items
                for item in items:
                    title = item.find("title").text  # Extract titles
                    link = item.find("link").text if item.find("link") else ""
                    headings.append({"title": title, "link": link})
        except Exception as e:
            st.error(f"Error parsing RSS feed: {e}")
    return headings

@st.cache_data
def load_stock_data():
    """
    Load stock data from CSV file.
    """
    csv_path = "data/ind_nifty500list.csv"
    if not os.path.exists(csv_path):
        st.error("Stock list CSV file is missing!")
        return pd.DataFrame()
    return pd.read_csv(csv_path)

def generate_stock_info(headings, stocks_df):
    """
    Processes headings to extract company stock information.
    """
    from fuzzywuzzy import fuzz  # Ensure fuzz is explicitly imported
    pattern = r"[\'’]"
    pattern2 = r"&amp;"
    stock_news_map = {}

    for item in headings:
        title = item["title"]
        link = item["link"]
        cleaned_text = re.sub(pattern, " ", title)
        cleaned_text = re.sub(pattern2, "&", cleaned_text)
        doc = nlp(cleaned_text)

        for ent in doc.ents:
            if ent.label_ in ["ORG", "PERSON"]:
                match, score = process.extractOne(ent.text, stocks_df['Company Name'].tolist(), scorer=fuzz.ratio)
                if score >= 80:  # Threshold for fuzzy matching
                    matched_row = stocks_df[stocks_df['Company Name'] == match]
                    for _, row in matched_row.iterrows():
                        stock_name = row['Company Name']

                        # Update stock-news mapping
                        if stock_name not in stock_news_map:
                            stock_news_map[stock_name] = []
                        stock_news_map[stock_name].append({"Title": title, "Link": link})
                    break



    # Create a DataFrame for sidebar listing
    stock_matches = [
        {"Company Name": stock, "Title": news["Title"], "Link": news["Link"]}
        for stock, news_list in stock_news_map.items()
        for news in news_list
    ]

    return pd.DataFrame(stock_matches), stock_news_map

# Define RSS feed URLs
url_list = [
    "https://economictimes.indiatimes.com/prime/money-and-markets/rssfeeds/62511286.cms",
    "https://www.moneycontrol.com/rss/buzzingstocks.xml",
    "https://in.investing.com/rss/market_overview_Fundamental.rss",
    "https://in.investing.com/rss/news_357.rss"
]

# Load and process data
stocks_df = load_stock_data()
if not stocks_df.empty:
    fin_headings = extract_text_from_rss(url_list)
    if fin_headings:
        output_df, stock_news_map = generate_stock_info(fin_headings, stocks_df)

        # Display results
        if not output_df.empty:
            st.sidebar.header("Stocks in News")
            selected_stock = st.sidebar.selectbox("Select a Stock", ["All"] + list(stock_news_map.keys()))

            if selected_stock and selected_stock != "All":
                st.subheader(f"News related to {selected_stock}")
                for news in stock_news_map[selected_stock]:
                    st.write(f"- [{news['Title']}]({news['Link']})")
            else:
                st.subheader("All News")
                for _, row in output_df.iterrows():
                    st.write(f"- [{row['Title']}]({row['Link']})")
        else:
            st.warning("No stock matches found in the news headlines.")
    else:
        st.warning("No headings were found in the RSS feed.")
else:
    st.error("Unable to load stock data. Ensure the CSV file is available.")
