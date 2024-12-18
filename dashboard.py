import pandas as pd
import streamlit as st
import yfinance as yf
import plotly.express as px
import numpy as np


st.title("Stock Dasboard")
ticker=st.sidebar.text_input("Ticker")
start_date=st.sidebar.date_input("Start Date")
end_date=st.sidebar.date_input("End Date")

data=yf.download(ticker,start_date,end_date)
charts,pricing_data,fundamental_data,news=st.tabs(["Charts","Pricing Data","Fundamental Data","News"])
with charts:
    if data.empty:
        st.error("No data available for the given ticker and date range.")
    else:
        # Proceed with processing and plotting
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.droplevel(1)

        fig = px.line(data, x=data.index, y=data['Adj Close'], title=f"{ticker} Stock Prices")
        st.plotly_chart(fig)

        import plotly.graph_objects as go

        fig = go.Figure(data=[go.Candlestick(x=data.index,
                        open=data['Open'],
                        high=data['High'],
                        low=data['Low'],
                        close=data['Close'])])

        st.plotly_chart(fig)



with pricing_data:
    st.header("Price Movements")
    data2=data
    data2["% Change"]=data2['Adj Close']/data2['Adj Close'].shift(1)-1
    st.write(data2)
    annual_return=data["% Change"].mean()*252*100
    stdev=np.std(data2['% Change'])*np.sqrt(252)
    risk_adj_return=annual_return/(stdev*100)
    st.write(f"Annual Returns : {annual_return} %")
    st.write(f"Standard Deviation : {stdev*100} %")
    st.write(f"Risk Adj Return : {risk_adj_return}")


from alpha_vantage.fundamentaldata import FundamentalData

with fundamental_data:
    st.write("Fundamentals")
    # key="BAFM8AIBPOT38186"
    key="U8UCXZQWWNMPHRTW"
    fd=FundamentalData(key,output_format="pandas")


    st.subheader('Balance Sheet')
    balance_sheet=fd.get_balance_sheet_annual(ticker)[0]
    bs=balance_sheet.T[2:]
    bs.columns=list(balance_sheet.T.iloc[0])
    st.write(bs)

    st.subheader('Income Statement')
    income_statement=fd.get_income_statement_annual(ticker)[0]
    is1=income_statement.T[2:]
    is1.columns=list(income_statement.T.iloc[0])
    st.write(is1)

    st.subheader("Cash Flow Statement")
    cash_flow=fd.get_cash_flow_annual(ticker)[0]
    cs=cash_flow.T[2:]
    cs.columns=list(cash_flow.T.iloc[0])
    st.write(cs)

from stocknews import StockNews

with news:
    st.header(f"News of {ticker}")
    sn=StockNews(ticker,save_news=False)
    df_news=sn.read_rss()
    for i in range(10):
        st.subheader(f'News {i+1}')
        st.write(df_news['published'][i])
        st.write(df_news['title'][i])
        st.write(df_news['summary'][i])
        title_sentiment=df_news['sentiment_title'][i]
        st.write(f'Title Sentiment {title_sentiment}')
        news_sentiment=df_news['sentiment_summary'][i]
        st.write(f'News Sentiment {news_sentiment}')





