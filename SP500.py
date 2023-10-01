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

# Function to find highest and lowest return and corresponding times
def find_high_low_prices(symbol_data, selected_symbols, start_date, end_date):
    if symbol_data.empty:
        st.error("The symbol data is empty. Cannot find high and low prices.")
        return

    if 'High' not in symbol_data.columns or 'Low' not in symbol_data.columns:
        st.error("The 'High' or 'Low' column is not found in the symbol data.")
        return

    try:
        for symbol in selected_symbols:
            single_symbol_data = symbol_data[symbol_data['Symbol'] == symbol]
            single_symbol_data = single_symbol_data.loc[start_date:end_date]
            highest_price_row = single_symbol_data[single_symbol_data['High'] == single_symbol_data['High'].max()]
            lowest_price_row = single_symbol_data[single_symbol_data['Low'] == single_symbol_data['Low'].min()]
            highest_price = highest_price_row['High'].values[0]
            lowest_price = lowest_price_row['Low'].values[0]
            highest_datetime = highest_price_row.index[0]
            lowest_datetime = lowest_price_row.index[0]
            text = f"{symbol} had its lowest trading price of ${lowest_price:.2f} on {lowest_datetime.strftime('%A, %B %d, %Y at %H:%M')} and highest trading price of ${highest_price:.2f} on {highest_datetime.strftime('%A, %B %d, %Y at %H:%M')} for the selected dates of {start_date} to {end_date}."
            st.write(text)
    except Exception as e:
        st.error(f"An error occurred while finding high and low prices: {e}")

st.title("S&P 500 Analysis")
st.write("""
An interactive analysis of S&P 500 companies, allowing users to view and download historical stock data, returns, 
additional company information. The dataset provides 1 year of historical data, recorded at hourly intervals. 
""")

url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'

tickers = fetch_sp500_data(url)
Stocks = tickers.Symbol.to_list()
Portfolio = download_stock_data(Stocks)
portfolio = process_data(Portfolio)

if portfolio is not None:
    portfolio['Datetime'] = pd.to_datetime(portfolio['Datetime'])
    portfolio.set_index('Datetime', inplace=True)
    portfolio['Dollar_Return'] = portfolio['Return'] * portfolio['Adj Close']

    # Date range selection
    st.write("Select Date Range:")
    start_date = st.date_input(
        "Start Date",
        value=last_weekday() - timedelta(days=30),
        min_value=datetime.now() - timedelta(days=365),
        max_value=last_weekday(),
    )
    end_date = st.date_input(
        "End Date",
        value=last_weekday(),
        min_value=datetime.now() - timedelta(days=365),
        max_value=last_weekday(),
    )

    filtered_portfolio = portfolio.loc[start_date:end_date]

    # Ticker selection
    selected_symbols = st.multiselect("Tickers:", filtered_portfolio['Symbol'].unique(), default=['AAPL'])

    # Filter the data for the selected symbols
    symbol_data = filtered_portfolio[filtered_portfolio['Symbol'].isin(selected_symbols)]

   # After filtering the symbol_data DataFrame based on the selected symbols and date range, call the function:
    find_high_low_prices(symbol_data, selected_symbols, start_date, end_date)

    if not symbol_data.empty:
        st.write("### Data Table:")
        st.dataframe(symbol_data)

        if st.button("Download data as CSV"):
            tmp_download_link = download_link(symbol_data, 'your_data.csv', 'Click here to download your data as CSV!')
            st.markdown(tmp_download_link, unsafe_allow_html=True)

        if st.button("Download data as Excel"):
            towrite = io.BytesIO()
            downloaded_file = symbol_data.to_excel(towrite, index=True, sheet_name='Sheet1')
            towrite.seek(0)
            b64 = base64.b64encode(towrite.read()).decode()
            tmp_download_link = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="your_data.xlsx">Download excel file</a>'
            st.markdown(tmp_download_link, unsafe_allow_html=True)
    else:
        st.error("No data available for the selected symbol.")
