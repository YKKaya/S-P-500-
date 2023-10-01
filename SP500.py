import streamlit as st
import pandas as pd
import yfinance as yf
import base64
import io
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

# Function to get the last weekday
def last_weekday():
    today = datetime.now()
    offset = 1
    while (today - timedelta(days=offset)).weekday() > 4:  # 0=Monday, 1=Tuesday, ..., 4=Friday
        offset += 1
    last_working_day = today - timedelta(days=offset)
    st.write(f"Last Working Day: {last_working_day}")  # Add this line for debugging
    return last_working_day

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
    portfolio['Founded'] = portfolio['Founded'].str.replace(r'\(.*?\)', '', regex=True).str.strip()
    portfolio['Dollar_Return'] = portfolio['Return'] * portfolio['Adj Close']

    # Date range selection
    st.write("Select Date Range:")
    start_date = st.date_input(
        "Start Date",
        value=last_weekday() - timedelta(days=30),  # Default value is 30 days ago
        min_value=datetime.now() - timedelta(days=365),  # Min value is one year ago
        max_value=last_weekday(),  # Max value is the last working day
    )
    end_date = st.date_input(
        "End Date",
        value=last_weekday(),  # Default value is the last working day
        min_value=datetime.now() - timedelta(days=365),  # Min value is one year ago
        max_value=last_weekday(),  # Max value is the last working day
    )

    filtered_portfolio = portfolio[(portfolio['Datetime'].dt.date >= start_date) & (portfolio['Datetime'].dt.date <= end_date)]

    # Ticker selection
    selected_symbols = st.multiselect("Tickers:", filtered_portfolio['Symbol'].unique(), default=['AAPL'])

    # Filter the data for the selected symbols
    symbol_data = filtered_portfolio[filtered_portfolio['Symbol'].isin(selected_symbols)]
    
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
