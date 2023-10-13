import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup

# Function to fetch S&P 500 data
@st.cache_data
def fetch_sp500_data(url):
    try:
        tickers = pd.read_html(url)[0]
        return tickers
    except Exception as e:
        st.error(f"Error fetching S&P 500 data: {e}")
        return None

# Function to download stock data
@st.cache_data
def download_stock_data(Stocks):
    try:
        Portfolio = yf.download(Stocks, period='1y', interval='1h')
        Portfolio = Portfolio.stack(level=0).rename_axis(['Date', 'Symbol']).reset_index(level=1)
        return Portfolio
    except Exception as e:
        st.error(f"Error downloading stock data: {e}")
        return None

# Function to extract ESG
@st.cache_data
def get_esg_data_with_headers_and_error_handling(ticker):
    # ... [same code as before] ...

# Main part of the code
st.title("S&P 500 Companies Hourly Returns and ESG Data")

# ESG Data Retrieval
st.write("### Retrieve ESG Data")
user_input_ticker = st.text_input("Enter a ticker symbol for ESG data (e.g., AAPL):")
if user_input_ticker:
    esg_data = get_esg_data_with_headers_and_error_handling(user_input_ticker)
    if esg_data:
        st.write(f"### ESG Data for {user_input_ticker}:")
        st.write(esg_data)
    else:
        st.write(f"No ESG data available for {user_input_ticker}.")

url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
tickers = fetch_sp500_data(url)
Stocks = tickers.Symbol.to_list()
Portfolio = download_stock_data(Stocks)

# Date range selection
st.write("Select Date Range:")
start_date = st.date_input("Start Date", value=datetime.now() - timedelta(days=30), max_value=datetime.now())
end_date = st.date_input("End Date", value=datetime.now(), max_value=datetime.now())
filtered_portfolio = Portfolio[(Portfolio['Date'].dt.date >= start_date) & (Portfolio['Date'].dt.date <= end_date)]

# Ticker selection
default_ticker = ['AAPL']
selected_symbols = st.multiselect("Tickers:", filtered_portfolio['Symbol'].unique(), default=default_ticker)

# Filter the data for the selected symbols
symbol_data = filtered_portfolio[filtered_portfolio['Symbol'].isin(selected_symbols)]

# Display the time series chart for selected tickers
if selected_symbols:  # Check if at least one ticker is selected
    # ... [rest of your Streamlit app code here] ...
else:
    st.warning("Please select at least one ticker for comparison.")


    # Display the time series chart for selected tickers
    if selected_symbols:  # Check if at least one ticker is selected
        display_time_series_chart(symbol_data, selected_symbols, start_date, end_date)
    else:
        st.warning("Please select at least one ticker for comparison.")
   
    # Call the display_high_low function here
    display_high_low(symbol_data, selected_symbols, start_date, end_date)
      
    # Now display the data table
    if 'Datetime' in symbol_data.columns:
        symbol_data.set_index('Datetime', inplace=True)
        st.write("### Data Table:")
        st.dataframe(symbol_data)

        if st.button("Download data as CSV"):
            tmp_download_link = download_link(symbol_data, 'your_data.csv', 'Click here to download your data as CSV!')
            st.markdown(tmp_download_link, unsafe_allow_html=True)

        if st.button("Download data as Excel"):
            towrite = io.BytesIO()
            downloaded_file = symbol_data.to_excel(towrite, index=False, sheet_name='Sheet1')
            towrite.seek(0)
            b64 = base64.b64encode(towrite.read()).decode()
            tmp_download_link = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="your_data.xlsx">Download excel file</a>'
            st.markdown(tmp_download_link, unsafe_allow_html=True)
    else:
        st.error("Datetime column not found in the data.")
else:
    st.error("No data available for the selected symbol.")
