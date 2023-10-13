import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup
import plotly.graph_objects as go
import matplotlib.pyplot as plt

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
        
# Function to extract esg data        
@st.cache
def get_esg_data_with_headers_and_error_handling(ticker):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    url = f"https://uk.finance.yahoo.com/quote/{ticker}/sustainability?p={ticker}"
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print(f"Failed to fetch data for {ticker}. Status code: {response.status_code}")
        return None

    soup = BeautifulSoup(response.content, 'html.parser')
    result = {}

    try:
        total_esg_risk_score = soup.find("div", {"class": "Fz(36px) Fw(600) D(ib) Mend(5px)"}).text
        result["Total ESG risk score"] = float(total_esg_risk_score)
    except:
        result["Total ESG risk score"] = None

    scores = soup.find_all("div", {"class": "D(ib) Fz(23px) smartphone_Fz(22px) Fw(600)"})
    try:
        result["Environment risk score"] = float(scores[0].text)
    except:
        result["Environment risk score"] = None

    try:
        result["Social risk score"] = float(scores[1].text)
    except:
        result["Social risk score"] = None

    try:
        result["Governance risk score"] = float(scores[2].text)
    except:
        result["Governance risk score"] = None

    try:
        controversy_level = soup.find("div", {"class": "D(ib) Fz(36px) Fw(500)"}).text
        result["Controversy level"] = int(controversy_level)
    except:
        result["Controversy level"] = None

    return result

# Function to map ESG risk score to risk level
def map_esg_risk_to_level(score):
    if score < 10:
        return "Very Low"
    elif 10 <= score < 20:
        return "Low"
    elif 20 <= score < 30:
        return "Medium"
    elif 30 <= score < 40:
        return "High"
    else:
        return "Severe"
        
# Function to process data
def process_data(Portfolio):
    try:
        portfolio = Portfolio.stack().reset_index().rename(index=str, columns={"level_1": "Symbol", "level_0": "Datetime"})
        portfolio['Return'] = (portfolio['Close'] - portfolio['Open']) / portfolio['Open']
        return portfolio
    except Exception as e:
        st.error(f"Error processing data: {e}")
        return None
        
# Display the risk levels in a static table
def display_risk_levels(ticker, ticker_esg_score):
    st.write("### ESG Risk Levels:")
    
    risk_levels = ["Very Low", "Low", "Medium", "High", "Severe"]
    colors = ["#FFEDCC", "#FFDB99", "#FFC266", "#FF9900", "#FF6600"]  # Shades of orange from light to dark
    
    # Determine the position of the ticker's ESG score on the scale
    score_position = risk_levels.index(map_esg_risk_to_level(ticker_esg_score))
    
    # Highlight the cell corresponding to the ticker's ESG score
    cell_colors = [['#2e2e2e'] * 5 for _ in range(5)]
    cell_colors[score_position][0] = colors[score_position]
    
    fig = go.Figure(data=[go.Table(
        header=dict(values=["Risk Level", "Score Range"],
                    fill_color='#2e2e2e',
                    line_color='#2e2e2e',
                    align='center',
                    font=dict(color='white', size=14)),
        cells=dict(values=[risk_levels, ["0-10", "10-20", "20-30", "30-40", "40+"]],
                   fill_color=cell_colors,
                   line_color='#2e2e2e',
                   align='center',
                   font=dict(color='white', size=12))
    )])
    
    # Add a text annotation to display the ticker's ESG score
    fig.add_annotation(
        x=1.1,  # Adjusted position to the right outside of the figure
        y=score_position/4.5,  # Adjusted y position relative to the height of the figure
        xref="paper",
        yref="paper",
        text=f"{ticker}'s Score: {ticker_esg_score}",
        showarrow=False,
        font=dict(color='white', size=12)
    )
    
    fig.update_layout(
        width=600,
        height=300,
        paper_bgcolor='#2e2e2e',
        plot_bgcolor='#2e2e2e',
        margin=dict(l=0, r=0, b=0, t=0)
    )
    
    st.plotly_chart(fig)


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
    
                
    # Filter the data for the selected symbols
    symbol_data = filtered_portfolio[filtered_portfolio['Symbol'].isin(selected_symbols)]

   # Display the time series chart for selected tickers
    if selected_symbols:  # Check if at least one ticker is selected
        display_time_series_chart(symbol_data, selected_symbols, start_date, end_date)
    else:
        st.warning("Please select at least one ticker for comparison.")
   
    # Call the display_high_low function here
    display_high_low(symbol_data, selected_symbols, start_date, end_date)
    

   
    # ESG Data Retrieval and Display
    for symbol in selected_symbols:
        esg_data = get_esg_data_with_headers_and_error_handling(symbol)
        if esg_data:
            total_esg_score = esg_data.get("Total ESG risk score", None)
            risk_level = map_esg_risk_to_level(total_esg_score) if total_esg_score is not None else "N/A"
            
            st.write(f"### ESG Data for {symbol}:")
            st.markdown(f"""
            - **Total ESG risk score:** {total_esg_score} ({risk_level})
            - **Environment risk score:** {esg_data.get("Environment risk score", "N/A")}
            - **Social risk score:** {esg_data.get("Social risk score", "N/A")}
            - **Governance risk score:** {esg_data.get("Governance risk score", "N/A")}
            - **Controversy level:** {esg_data.get("Controversy level", "N/A")}
            """)

            # Display the risk levels table
            if total_esg_score:
                display_risk_levels(symbol, total_esg_score)
            else:
                st.error("Unable to fetch ESG score for the selected ticker.")
            
            st.write("This data is sourced from Yahoo Finance and risk ratings are conducted by Sustainalytics.")
            st.markdown("[More information on Sustainalytics ESG Data](https://www.sustainalytics.com/esg-data)")
            st.video("https://www.youtube.com/embed/bJgMM31wiRs?autoplay=1")
            
        else:
            st.write(f"No ESG data available for {symbol}.")
      
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
