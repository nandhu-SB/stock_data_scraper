import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd



conn=st.connection("gsheets",type=GSheetsConnection)

df=conn.read()

for row in df.itertuples():
    st.write(f"{row.Name}")
