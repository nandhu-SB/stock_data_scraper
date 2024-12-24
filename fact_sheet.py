import pandas as pd
import streamlit as st



st.button(label="Button")
file_uploader=st.sidebar.file_uploader("Upload Excel File",type=["xlsx","xls"])
if file_uploader:
    df=pd.read_excel(file_uploader)
    st.caption("Loaded Data")
    st.write(df)
    # df=pd.read_excel(r"C:\Users\nandh\Downloads\Copy of  NEW MOAT SCHEME  WISE EXCEL .xlsx")
    # print(df.head())
    # print(df.info())
    sum_of_portfolio_wt=sum(df['Portfoilo Wt.'])
    wt_of_market_cap=sum(df['Market cap(Cr)']*df['Portfoilo Wt.'])/sum_of_portfolio_wt
    wt_of_pe=sum(df['P/E ratio']*df['Portfoilo Wt.'])/sum_of_portfolio_wt
    total_equity=sum(df["Market Value"])
    print(wt_of_market_cap)
    print(wt_of_pe)
    st.write(f"Weighted Average Market Cap: {wt_of_market_cap}")
    st.write(f"Weighted Average PE:{ wt_of_pe}")
    st.write(f"Total Equity: {total_equity}")

