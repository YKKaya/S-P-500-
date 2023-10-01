import streamlit as st
import pandas as pd
import yfinance as yf
import base64
import io
from datetime import datetime, timedelta


def display_high_low_return_info(symbol_data, selected_symbols, start_date, end_date):
    symbol_data['Hour'] = symbol_data.index.hour
    symbol_data['Day'] = symbol_data.index.day_name()
    min_return_row = symbol_data[symbol_data['Return'] == symbol_data['Return'].min()]
    max_return_row = symbol_data[symbol_data['Return'] == symbol_data['Return'].max()]

    min_return_hour = min_return_row['Hour'].iloc[0]
    min_return_day = min_return_row['Day'].iloc[0]
    max_return_hour = max_return_row['Hour'].iloc[0]
    max_return_day = max_return_row['Day'].iloc[0]

    st.write(f"{selected_symbols[0]} had its lowest trading price of its stock on {min_return_day}s {min_return_hour}:00 and highest trading price of its stock at {max_return_hour}:00 on {max_return_day}s for the selected dates of ({start_date} to {end_date})")


@st.cache
def fetch_sp500_data(url):
    try:
        tickers = pd.read_html(url)[0]
        return tickers
    except Exception as e:
        st.error(f"Error fetching S&P 500 data: {e}")
        return None


@st.cache
def download_stock_data(Stocks):
    try:
        Portfolio = yf.download(Stocks, period='1y', interval='1h')
        return Portfolio
    except Exception as e:
        st.error(f"Error downloading stock data: {e}")
        return None


def process_data(Portfolio):
    try:
        portfolio = Portfolio.stack().reset_index().rename(index=str, columns={"level_1": "Symbol", "level_0": "Datetime"})
        portfolio['Return'] = (portfolio['Close'] - portfolio['Open']) / portfolio['Open']
        return portfolio
    except Exception as e:
        st.error(f"Error processing data: {e}")
        return None


def merge_additional_info(portfolio, tickers):
    try:
        company_info = tickers[['Symbol', 'Security', 'GICS Sector', 'GICS Sub-Industry', 'Headquarters Location', 'Date added', 'Founded']]
        company_info.columns = ['Symbol', 'Company_Name', 'Industry', 'Sub_Industry', 'Headquarters_Location', 'Date_Added', 'Founded']
        portfolio = pd.merge(portfolio, company_info, on='Symbol', how='left')
        return portfolio
    except Exception as e:
        return None


def download_link(object_to_download, download_filename, download_link_text):
    if isinstance(object_to_download, pd.DataFrame):
        object_to_download = object_to_download.to_csv(index=False)

    b64 = base64.b64encode(object_to_download.encode()).decode()
    download_link = f'<a href="data:file/txt;base64,{b64}" download="{download_filename}">{download_link_text}</a>'
    return download_link


def last_weekday():
    today = datetime.now()
    offset = 1
    while (today - timedelta(days=offset)).weekday() > 4:
        offset += 1
    last_working_day = today - timedelta(days=offset)
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
portfolio = merge_additional_info(portfolio, tickers)

if portfolio is not None:
    portfolio['Founded'] = portfolio['Founded'].str.replace(r'\(.*?\)', '', regex=True).str.strip()
    portfolio['Dollar_Return'] = portfolio['Return'] * portfolio['Adj Close']

    start_date = st.date_input("Start Date", value=last_weekday() - timedelta(days=1), min_value=datetime.now() - timedelta(days=365), max_value=last_weekday())
    end_date = st.date_input("End Date", value=last_weekday(), min_value=datetime.now() - timedelta(days=365), max_value=last_weekday())

    filtered_portfolio = portfolio[(portfolio['Datetime'].dt.date >= start_date) & (portfolio['Datetime'].dt.date <= end_date)]

    selected_symbols = st.multiselect("Tickers:", filtered_portfolio['Symbol'].unique(), default=['AAPL'])

    symbol_data = filtered_portfolio[filtered_portfolio['Symbol'].isin(selected_symbols)]

    if symbol_data is not None and not symbol_data.empty:
        if 'Datetime' in symbol_data.columns:
            symbol_data.set_index('Datetime', inplace=True)
            display_high_low_return_info(symbol_data, selected_symbols, start_date, end_date)
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
