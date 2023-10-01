import streamlit as st
import pandas as pd
import yfinance as yf
import base64
import io
from datetime import datetime, timedelta

# Function to fetch S&P 500 data
@st.cache
def fetch_sp500_data(url):
    try:
        tickers = pd.read_html(url)[0]
        return tickers
    except Exception as e:
        st.error(f"Error fetching S&P 500 data: {e}")
        return None

# Function to download stock data
@st.cache
def download_stock_data(Stocks):
    try:
        Portfolio = yf.download(Stocks, period='1y', interval='1h')
        return Portfolio
    except Exception as e:
        st.error(f"Error downloading stock data: {e}")
        return None

# Function to process data
def process_data(Portfolio):
    try:
        portfolio = Portfolio.stack().reset_index().rename(index=str, columns={"level_1": "Symbol", "level_0": "Datetime"})
        portfolio['Return'] = (portfolio['Close'] - portfolio['Open']) / portfolio['Open']
        return portfolio
    except Exception as e:
        st.error(f"Error processing data: {e}")
        return None

# Function to display high and low return text
def display_high_low(data, symbols, start_date, end_date):
    for symbol in symbols:
        symbol_data = data[data['Symbol'] == symbol]
        min_return_row = symbol_data[symbol_data['Return'] == symbol_data['Return'].min()]
        max_return_row = symbol_data[symbol_data['Return'] == symbol_data['Return'].max()]
        st.write(f"{symbol} had its lowest trading price of its stock on {min_return_row['Datetime'].dt.strftime('%A %H:%M').values[0]} and highest trading price of its stock at {max_return_row['Datetime'].dt.strftime('%A %H:%M').values[0]} for the selected dates of {start_date} to {end_date}")

# Main code
st.title("S&P 500 Analysis")
url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
tickers = fetch_sp500_data(url)
Stocks = tickers.Symbol.to_list()
Portfolio = download_stock_data(Stocks)
portfolio = process_data(Portfolio)

if portfolio is not None:
    start_date = st.date_input("Start Date", value=datetime.now() - timedelta(days=30))
    end_date = st.date_input("End Date", value=datetime.now())
    filtered_portfolio = portfolio[(portfolio['Datetime'].dt.date >= start_date) & (portfolio['Datetime'].dt.date <= end_date)]
    selected_symbols = st.multiselect("Tickers:", filtered_portfolio['Symbol'].unique(), default=['AAPL'])
    symbol_data = filtered_portfolio[filtered_portfolio['Symbol'].isin(selected_symbols)]

    # Call to the display_high_low function
    display_high_low(symbol_data, selected_symbols, start_date, end_date)

    if symbol_data is not None and not symbol_data.empty:
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
