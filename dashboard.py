import pandas as pd
import streamlit as st
import yfinance as yf
import plotly.express as px
import numpy as np
import plotly.graph_objects as go
from alpha_vantage.fundamentaldata import FundamentalData
from stocknews import StockNews
#my code

st.title("Stock Dasboard")
market=st.sidebar.selectbox("Choose Market",options=("NSE","Global"))
ticker=st.sidebar.text_input("Ticker")
start_date=st.sidebar.date_input("Start Date")
end_date=st.sidebar.date_input("End Date")

if not ticker:
    st.write("Enter the Ticker Name")
else:
    charts,pricing_data,fundamental_data,news=st.tabs(["Charts","Pricing Data","Fundamental Data","News"])
    try:
        if market=="NSE":
            ticker=ticker+".NS"
            # st.write(ticker)
        data=yf.download(ticker,start_date,end_date)
        # stock=yf.Ticker(ticker)
        # current_price=stock.info['currentPrice']
        if data.empty:
            st.error("No data available for the provided ticker and dates")
        else:
            with charts:

                if isinstance(data.columns, pd.MultiIndex):
                    data.columns = data.columns.droplevel(1)
                #price=st.write(yf.Ticker(ticker).history(period="1d")['Close'][0] )  
                fig = px.line(data, x=data.index, y=data['Adj Close'], title=f"{ticker} Stock Prices ")
                       

                
                st.plotly_chart(fig)


                candlestick_fig = go.Figure(data=[go.Candlestick(
                                x=data.index,
                                open=data['Open'],
                                high=data['High'],
                                low=data['Low'],
                                close=data['Close'])])
                candlestick_fig.update_layout(title=f"{ticker} Candlestick Chart",xaxis_title="Date",yaxis_title="Price")
                st.plotly_chart(candlestick_fig)


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


    except Exception as e:
            st.error(f"An error occured {e}")



















