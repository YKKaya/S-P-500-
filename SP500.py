import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
import yesg

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
# Function to get ESG score
@st.cache
def get_esg_score(ticker):
    try:
        esg = Esg(ticker)
        score = esg.get_score()
        return score
    except Exception as e:
        st.error(f"Error fetching ESG score for {ticker}: {e}")
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
            
            company_name = single_symbol_data['Company_Name'].values[0]  # Get the Company_Name from the dataset
            
            st.write(f"For the dates {start_date} to {end_date}, {company_name} recorded its:") 
            st.write(f"Lowest trading price: ${min_return_row['Low']:.2f} on {min_return_row['Datetime'].strftime('%A, %B %d at %H:%M')}")
            st.write(f"Highest trading price: ${max_return_row['High']:.2f} on {max_return_row['Datetime'].strftime('%A, %B %d at %H:%M')}")
    except Exception as e:
        st.error(f"An error occurred: {e}")

        
# Function to display the time series chart for selected tickers using Plotly
def display_time_series_chart(symbol_data, selected_symbols, start_date, end_date):
    try:
        filtered_data = symbol_data[
            (symbol_data['Symbol'].isin(selected_symbols)) &
            (symbol_data['Datetime'].dt.date >= start_date) &
            (symbol_data['Datetime'].dt.date <= end_date)
        ]

        if filtered_data.empty:
            st.error("No data available for the selected symbols in the selected date range.")
        else:
            selected_tickers = ', '.join(selected_symbols)  # Join selected tickers with commas
            
            # Create a Plotly line chart
            fig = go.Figure()  # Create a new Plotly figure
            
            # Customize the chart with explicit light colors
            light_colors = ['#FF5733', '#FFBD33', '#33FF57', '#339CFF', '#FF33D1']  # Light colors
            color_mapping = {symbol: light_colors[i % len(light_colors)] for i, symbol in enumerate(selected_symbols)}
            
            for symbol in selected_symbols:
                symbol_data = filtered_data[filtered_data['Symbol'] == symbol]
                # Add trace only once for each unique symbol
                if symbol not in fig.data:
                    fig.add_trace(
                        go.Scatter(
                            x=symbol_data['Datetime'],
                            y=symbol_data['High'],
                            mode='lines',
                            name=symbol,
                            line=dict(color=color_mapping[symbol], width=2)
                        )
                    )
            
            # Set chart title
            fig.update_layout(
                title=f"Time Series Chart for {selected_tickers} Tickers",
                xaxis_title="Date",
                yaxis_title="Highest Price"
            )
            
            # Show the chart
            st.plotly_chart(fig)
    except Exception as e:
        st.error(f"An error occurred: {e}")
        
# Main part of the code
st.title("S&P 500 Companies Hourly Returns")
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
    # Date range selection
    st.write("Select Date Range:")
    start_date = st.date_input("Start Date", value=datetime.now() - timedelta(days=30), max_value=datetime.now())
    end_date = st.date_input("End Date", value=datetime.now(), max_value=datetime.now())
    filtered_portfolio = portfolio[(portfolio['Datetime'].dt.date >= start_date) & (portfolio['Datetime'].dt.date <= end_date)]

    # Ticker selection
    default_ticker = ['AAPL']
    selected_symbols = st.multiselect("Tickers:", filtered_portfolio['Symbol'].unique(), default=default_ticker)
    
   
    # Fetch and display ESG score
    if selected_symbols:
        for symbol in selected_symbols:
            esg_score = get_esg_score(symbol)
            if esg_score is not None:
                st.write(f"### ESG Score for {symbol}:")
                st.write(f"Total ESG Score: {esg_score['total']}")
                st.write(f"Environment Score: {esg_score['environment']}")
                st.write(f"Social Score: {esg_score['social']}")
                st.write(f"Governance Score: {esg_score['governance']}")
            else:
                st.write(f"No ESG score available for {symbol}.")


    # Filter the data for the selected symbols
    symbol_data = filtered_portfolio[filtered_portfolio['Symbol'].isin(selected_symbols)]

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
