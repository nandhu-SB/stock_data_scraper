import streamlit as st
import pandas as pd
import re
from datetime import datetime
# Set up the page
st.set_page_config(page_title="MOAT-NEWS ENGINE", layout="wide", initial_sidebar_state="collapsed")
st.title("MOAT-NEWS ENGINE")
st.sidebar.header("Moat Stocks")

# Retained and optimized CSS styling
st.markdown("""
    <style>
    body { font-family: 'Arial', sans-serif; }
    .stTitle { text-align: center; }
    #MainEnu{visibility:hidden;}
    #footer{visibility:hidden;}
    .card {
        border: 1px solid #D4AF37;
        border-radius: 15px;
        padding: 15px;
        margin: 10px;
        box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
        display: flex;
        flex-direction: column;
        justify-content: left;
        text-align: center;
        position: relative;
        overflow: hidden;
        height: 350px;
    }
    .card h4 { font-size: 1.2rem; font-weight: bold; margin-bottom: 10px; }
    .card p {
        font-size: 1rem;
        margin-bottom: 20px;
        max-height: 80px;
        overflow: hidden;
        text-overflow: ellipsis;
        display: -webkit-box;
        -webkit-line-clamp: 3;
        -webkit-box-orient: vertical;
    }
    .card-footer {
        position: absolute;
        bottom: 10px;
        left: 15px;
        right: 15px;
        display: flex;
        justify-content: space-around;
    }
    .published-date { font-size: 0.8rem; color: #777; }
    .read-more { font-size: 0.8rem; color: #007BFF; text-decoration: none; }
    .read-more:hover { text-decoration: underline; }
    .card:hover { transform: scale(1.02); transition: transform 0.2s ease-in-out; }
    .highlight { background-color: yellow; color: black; }
    @media (max-width: 768px) {
        .card { height: 200px; }
        .card p { max-height: 50px; }
    }
    [data-testid="stSidebar"] { min-width: 200px; max-width: 200px; }
    [data-testid="stSidebar"] * { font-size: 14px; }
    [data-testid="stSidebar"] button[kind="secondary"] {
        border: 1px solid #D4AF37;
        border-radius: 10px;
        padding: 8px 16px;
        font-size: 14px;
        font-weight: bold;
        margin: 5px 0;
        cursor: pointer;
        width: 100%;
        display: block;
        text-align: center;
    }
    [data-testid="stSidebar"] button[kind="secondary"]:hover {
        background-color: #D4AF37;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)
def generate_cache_key():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Generate a new cache key for each page refresh
cache_key = generate_cache_key()

@st.cache_data(show_spinner=False)
def load_data(sheet_id, sheet_name,cache_key):
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv{sheet_name}"
    return pd.read_csv(url, dtype=str).fillna("")




def highlight_text(text, search_term):
    if not text or not search_term:
        return text
    pattern = re.compile(re.escape(search_term), re.IGNORECASE)
    return pattern.sub(lambda match: f"<span class='highlight'>{match.group(0)}</span>", text)

def stock_list_generator(df):
    return df['COMPANY NAME'].unique()

def data_process(df, key, stock_list):
    search_key = "text_search"
    if search_key not in st.session_state:
        st.session_state[search_key] = ""

    text_search = st.text_input("Search articles", value=st.session_state[search_key], key=f"text_{key}")

    for stock in stock_list:
        if st.sidebar.button(stock, key=f"{stock}_button_{key}"):  # Made key unique by adding tab key
            st.session_state[search_key] = stock
            text_search = stock

    search(df, text_search)

def search(df, term=""):
    search_columns = ["title", "description", "title_ent", "description_ent"]
    if term.strip():
        df_search = df[df[search_columns].apply(lambda col: col.str.contains(term, case=False, na=False)).any(axis=1)]
    else:
        df_search = df

    N_cards_per_row = 4
    for n_row, row in df_search.reset_index().iterrows():
        if n_row % N_cards_per_row == 0:
            cols = st.columns(N_cards_per_row)
        with cols[n_row % N_cards_per_row]:
            st.markdown(f"""
                <div class="card">
                    <h4>{highlight_text(row['title'], term)}</h4>
                    <p>{highlight_text(row['description'], term)}</p>
                    <div class="card-footer">
                        <span class="published-date">{row['published_date']}</span>
                        <a href="{row['link']}" target="_blank" class="read-more">Read more</a>
                    </div>
                </div>
            """, unsafe_allow_html=True)

all_df = load_data("14qjE9EblUbtHjVwQl-Dy9uuZM64MjsxeXg22x2biPmY", "&sheet=Sheet1",cache_key)  
moat_df = load_data("14qjE9EblUbtHjVwQl-Dy9uuZM64MjsxeXg22x2biPmY", "&gid=1812473852",cache_key)
moat_source = load_data("1CbQQjrLPT25n2xnxuHRdOrI6K6MczA-Kh0BDraguniw", "&sheet=Sheet1",cache_key)

all_news, moat_news = st.tabs(["All News", "Moat Stocks News"])

with all_news:
    data_process(all_df, "all_news", stock_list_generator(moat_source))

with moat_news:
    data_process(moat_df, "moat_news", stock_list_generator(moat_source))
