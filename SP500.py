# Importing required libraries
import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta

# Function to fetch S&P 500 data
@st.cache  # Adding caching here
def fetch_sp500_data(url):
    try:
        tickers = pd.read_html(url)[0]
        return tickers
    except Exception as e:
        st.error(f"Error fetching S&P 500 data: {e}")
        return None

# Function to download stock data
@st.cache  # Adding caching here
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

# Function to merge additional info
def merge_additional_info(portfolio, tickers):
    try:
        company_info = tickers[['Symbol', 'Security', 'GICS Sector', 'GICS Sub-Industry', 'Headquarters Location', 'Date added', 'Founded']]
        company_info.columns = ['Symbol', 'Company_Name', 'Industry', 'Sub_Industry', 'Headquarters_Location', 'Date_Added', 'Founded']
        portfolio = pd.merge(portfolio, company_info, on='Symbol', how='left')
        return portfolio
    except Exception as e:
        return None

st.title("S&P 500 Analysis")
st.write("""
An interactive analysis of S&P 500 companies, allowing users to view historical stock data, returns, and additional company information.
""")


url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'

tickers = fetch_sp500_data(url)
Stocks = tickers.Symbol.to_list()
Portfolio = download_stock_data(Stocks)
portfolio = process_data(Portfolio)
portfolio = merge_additional_info(portfolio, tickers)

if portfolio is not None:
    portfolio['Founded'] = portfolio['Founded'].str.replace(r'\(.*?\)', '', regex=True).str.strip()
    portfolio['Dollar_Return'] = portfolio['Return'] * portfolio['Adj Close']

    
    yesterday = datetime.now() - timedelta(days=1)  # Changed this line
    selected_date = st.date_input("Select Date:", yesterday)
    filtered_portfolio = portfolio[portfolio['Datetime'].dt.date == selected_date]

    # Ticker selection
    selected_symbol = st.selectbox("Ticker:", filtered_portfolio['Symbol'].unique())

    # Filter the data for the selected symbol
    symbol_data = filtered_portfolio[filtered_portfolio['Symbol'] == selected_symbol]

    # Check if symbol_data is not None and not empty before setting the index
    if symbol_data is not None and not symbol_data.empty:
        symbol_data.set_index('Datetime', inplace=True)
        st.write("### Data Table:")
        st.dataframe(symbol_data)
    else:
        st.error("No data available for the selected symbol.")
