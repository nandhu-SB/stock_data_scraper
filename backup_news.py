import spacy
from bs4 import BeautifulSoup
import pandas as pd
import requests
import streamlit as st
import yfinance as yf
import re


# Load spaCy model
nlp = spacy.load("en_core_web_md")

# Streamlit Title
st.title("STOCK NEWS :zap:")


def extract_text_from_rss(urls):
    """
    Parses the RSS XML feed and extracts titles.
    """
    headings = []
    for url in urls:
        try:
            r = requests.get(url)
            if r.status_code == 200:
                soup = BeautifulSoup(r.content, features="xml")
                items = soup.find_all("item")  # RSS feed items
                for item in items:
                    title = item.find("title").text  # Extract titles
                    headings.append(title)
        except Exception as e:
            st.error(f"Error parsing RSS feed: {e}")
    return headings




def generate_stock_info(headings):
    """
    Processes headings to extract company stock information.
    """
    pattern = r"[\'’]"
    pattern2 = r"&amp;"
    df=pd.DataFrame()

    # Load stock data
    try:
        stocks_df = pd.read_csv("data/ind_nifty500list.csv")  # Fixed path issue
    except FileNotFoundError:
        st.error("Stock list CSV file not found!")
        return pd.DataFrame()

    # Process each heading
    for title in headings:

        cleaned_text = re.sub(pattern, " ", title)
        cleaned_text = re.sub(pattern2, "&", cleaned_text)
        doc = nlp(cleaned_text)

        for ent in doc.ents:
            if ent.label_=="ORG" or ent.label_=="PERSON":





                try:

                    match = stocks_df['Company Name'].str.contains(ent.text, case=False, na=False)
                    if match.sum():
                        symbols=stocks_df[match]['Symbol']
                        df = pd.concat([df, stocks_df[stocks_df['Symbol'].isin(symbols)]], ignore_index=True)
                        st.write(cleaned_text)
                        st.write(doc.ents)
                        st.write("--------")
                        break
                        
                except:
                    pass

    df['Weight'] = df.groupby('Symbol')['Symbol'].transform('count')
    df=df.drop_duplicates(['Symbol'])
    df = df.sort_values(['Weight'], ascending=False)
    return df   

url_list=[
    "https://economictimes.indiatimes.com/prime/money-and-markets/rssfeeds/62511286.cms",
    "https://www.moneycontrol.com/rss/buzzingstocks.xml","https://in.investing.com/rss/market_overview_Fundamental.rss","https://in.investing.com/rss/news_357.rss"
]

fin_headings = extract_text_from_rss(url_list)
if fin_headings:
    output_df = generate_stock_info(fin_headings)
    st.sidebar.header("stocks in news")
    st.sidebar.dataframe(output_df)

else:
    st.warning("No headings were found in the RSS feed.")