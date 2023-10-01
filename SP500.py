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

def display_high_low(symbol_data, selected_symbols, start_date, end_date):
    try:
        for symbol in selected_symbols:
            single_symbol_data = symbol_data[symbol_data['Symbol'] == symbol]
            single_symbol_data['Datetime'] = pd.to_datetime(single_symbol_data['Datetime'])  # Ensure Datetime is in datetime format
            if single_symbol_data.empty:
                st.error(f"No data available for {symbol} in the selected date range.")
                continue
            min_return_row = single_symbol_data.loc[single_symbol_data['Low'].idxmin()]  # Get the row with the minimum 'Low' value
            max_return_row = single_symbol_data.loc[single_symbol_data['High'].idxmax()]  # Get the row with the maximum 'High' value
            text = f"For the dates **{start_date} to {end_date}**, **{symbol}** recorded its lowest trading price of **${min_return_row['Low']:.2f}** on **{min_return_row['Datetime'].strftime('%A, %B %d at %H:%M')}** and its peak trading price of **${max_return_row['High']:.2f}** on **{max_return_row['Datetime'].strftime('%A, %B %d at %H:%M')}**."
            st.markdown(text)
    except Exception as e:
        st.error(f"An error occurred: {e}")

# Function to create download link
def download_link(object_to_download, download_filename, download_link_text):
    if isinstance(object_to_download, pd.DataFrame):
        object_to_download = object_to_download.to_csv(index=False)

    b64 = base64.b64encode(object_to_download.encode()).decode()
    download_link = f'<a href="data:file/csv;base64,{b64}" download="{download_filename}">{download_link_text}</a>'
    return download_link

# Main part of the code
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
    # Date range selection
    st.write("Select Date Range:")
    start_date = st.date_input("Start Date", value=datetime.now() - timedelta(days=30), max_value=datetime.now())
    end_date = st.date_input("End Date", value=datetime.now(), max_value=datetime.now())
    filtered_portfolio = portfolio[(portfolio['Datetime'].dt.date >= start_date) & (portfolio['Datetime'].dt.date <= end_date)]

    # Ticker selection
    default_ticker = ['AAPL']
    selected_symbols = st.multiselect("Tickers:", filtered_portfolio['Symbol'].unique(), default=default_ticker)


    # Filter the data for the selected symbols
    symbol_data = filtered_portfolio[filtered_portfolio['Symbol'].isin(selected_symbols)]

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
