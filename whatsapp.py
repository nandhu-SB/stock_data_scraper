import streamlit as st
import pandas as  pd
# import re
# Set up the page
st.set_page_config(page_title="MOAT-NEWS ENGINE", page_icon="🐍", layout="wide")
st.title("MOAT-NEWS ENGINE 🐍")
# st.sidebar.header("Moat Stocks")

st.markdown("""
    <style>
    body { font-family: 'Arial', sans-serif; }
    .stTitle { text-align: center; }
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
        height: 350px; /* Set a fixed height for all cards */
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
    .read-more {
        font-size: 0.8rem; color: #007BFF; text-decoration: none;
    }
    .read-more:hover { text-decoration: underline; }


    /* Blur effect */
    .card::after {
        content: "";
        position: absolute;
        bottom: 0;
        left: 0;
        width: 100%;
        height: 50%;
        # background: linear-gradient(to bottom, rgba(255, 215, 0, 0) 80%, rgba(255, 215, 0, 1) 100%);
        pointer-events: none;
    }

    /* Hover effect for cards */
    .card:hover {
        transform: scale(1.02);
        transition: transform 0.2s ease-in-out;
    }
    .highlight {
    background-color: yellow;
    color: black;
            }
    @media (max-width: 768px) {
        .card {
            height: 200px; /* Set a smaller height for mobile devices */
        }
        .card p {
            max-height: 50px; /* Adjust text block height for smaller cards */
        }
    }
    </style>
""", unsafe_allow_html=True)


def highlight_text(text, search_term):
    """
    Highlight a search term in the given text using simple string matching.
    
    Parameters:
        text (str): The text in which to search and highlight the term.
        search_term (str): The term to highlight.
        
    Returns:
        str: The text with the highlighted search term.
    """
    if not text or not search_term:
        return text  # Handle None, empty strings, or empty search term gracefully

    # Case-insensitive highlighting by matching and replacing the term
    lower_text = text.lower()
    lower_search_term = search_term.lower()

    start = 0
    highlighted_text = ""

    while True:
        index = lower_text.find(lower_search_term, start)
        if index == -1:
            highlighted_text += text[start:]
            break

        # Append text up to the match and the highlighted match
        highlighted_text += text[start:index] + f"<span class='highlight'>{text[index:index + len(search_term)]}</span>"
        start = index + len(search_term)

    return highlighted_text



def url_generator(sheet_id,sheet_name):
    return f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv{sheet_name}"
def stock_list_generator(df):
    return df['COMPANY NAME'].unique()
def data_process(df,key,stock_list):
        
        text_search = st.text_input("Search articles", value="", key=f"text_{key}")


        lower_text_search = text_search.strip().lower()

        search_columns = ["title", "description", "title_ent", "description_ent"]
        if lower_text_search:
            df_search=df[df[search_columns].apply(
                lambda col: col.str.contains(lower_text_search, na=False, case=False)
            ).any(axis=1)]
        else:
            df_search = df

        # Show the cards
        N_cards_per_row = 4
        if text_search:
            for n_row, row in df_search.reset_index().iterrows():
                i = n_row%N_cards_per_row
                if i==0:
                    st.write("---")
                    cols = st.columns(N_cards_per_row)
                # draw the card
                with cols[n_row%N_cards_per_row]:
                    st.markdown(f"""
                        <div class="card">
                            <h4>{highlight_text(row['title'], text_search)}</h4>
                            <p>{highlight_text(row['description'], text_search)}</p>
                            <div class="card-footer">
                                <span class="published-date">{row['published_date']}</span>
                                <a href="{row['link']}" class="read-more">Read more</a>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
        else:
            for n_row, row in df.reset_index().iterrows():
                i = n_row%N_cards_per_row
                if i==0:
                    st.write("---")
                    cols = st.columns(N_cards_per_row)
                # draw the card
                with cols[n_row%N_cards_per_row]:
                    st.markdown(f"""
                        <div class="card">
                            <h4>{highlight_text(row['title'], text_search)}</h4>
                            <p>{highlight_text(row['description'], text_search)}</p>
                            <div class="card-footer">
                                <span class="published-date">{row['published_date']}</span>
                                <a href="{row['link']}" class="read-more">Read more</a>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)




# Define the tab options
all_news,moat_news = st.tabs(["All News", "Moat Stocks News"])

# Use the Google Sheets export URL for CSV
url = url_generator("14qjE9EblUbtHjVwQl-Dy9uuZM64MjsxeXg22x2biPmY","&sheet=Sheet1")
moat_url=url_generator("14qjE9EblUbtHjVwQl-Dy9uuZM64MjsxeXg22x2biPmY","&gid=1812473852")
moat_source=url_generator("1CbQQjrLPT25n2xnxuHRdOrI6K6MczA-Kh0BDraguniw","&sheet=Sheet1")

# Read the CSV data from the Google Sheet
all_df = pd.read_csv(url, dtype=str).fillna("")
moat_df=pd.read_csv(moat_url,dtype=str).fillna("")
moat_source=pd.read_csv(moat_source,dtype=str).fillna("")




with all_news:
    data_process(all_df,"all_news",stock_list_generator(moat_source))
    # st.dataframe(all_df)

with moat_news:
    data_process(moat_df,"moat_news",stock_list_generator(moat_source))
    # st.dataframe(moat_df)




    
