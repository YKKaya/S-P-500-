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
def find_high_low_return(symbol_data, selected_symbols):
    if not symbol_data.empty:
        highest_return_row = symbol_data[symbol_data['Return'] == symbol_data['Return'].max()]
        lowest_return_row = symbol_data[symbol_data['Return'] == symbol_data['Return'].min()]
        highest_time = highest_return_row.index[0].time()
        highest_day = highest_return_row.index[0].strftime('%A')
        lowest_time = lowest_return_row.index[0].time()
        lowest_day = lowest_return_row.index[0].strftime('%A')
        for symbol in selected_symbols:
            text = f"{symbol} had its lowest trading price of its stock on {lowest_day} {lowest_time} and highest trading price of its stock at {highest_time} on {highest_day} for the selected dates."
            st.write(text)

# ... rest of the code remains unchanged

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

    # Call the function to find highest and lowest return and display the text
    find_high_low_return(symbol_data, selected_symbols)

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
