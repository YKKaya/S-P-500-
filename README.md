# S&P 500 Analysis Streamlit App
This Streamlit app provides an interactive analysis of S&P 500 companies, allowing users to view and download historical stock data, returns, and additional company information.

## Features
Fetch S&P 500 Data: Retrieves the list of S&P 500 companies from a Wikipedia page.
Download Stock Data: Downloads historical stock data for selected companies.
Data Processing: Processes the downloaded data to calculate returns and merge additional company information.
Data Export: Allows users to download the processed data as a CSV or Excel file.

## How to Use
Select Date Range: Choose a start and end date to filter the stock data.
Select Tickers: Choose one or multiple tickers to view the data for the selected companies.
View Data Table: The data table for the selected tickers and date range will be displayed.
Download Data: Click the buttons to download the data as a CSV or Excel file.
Example
Apple Inc. had its lowest trading price of its stock on Mondays 11:30 and highest trading price of its stock at 15:00 on Thursdays for the selected dates of (date range).

## Functions

fetch_sp500_data(url)

Purpose: Fetches the list of S&P 500 companies from Wikipedia.
Input: URL of the Wikipedia page containing the list of S&P 500 companies.
Output: A pandas DataFrame containing the list of S&P 500 companies.
Operations: Uses pandas.read_html() to scrape tables from the provided URL.

download_stock_data(Stocks)

Purpose: Downloads historical stock data for the provided list of tickers.
Input: List of stock tickers.
Output: A pandas DataFrame containing historical stock data.
Operations: Uses the yfinance library to download stock data for the past year at hourly intervals.

get_esg_data_with_headers_and_error_handling(ticker)

Purpose: Extracts ESG (Environmental, Social, and Governance) data for a given ticker from Yahoo Finance.
Input: Stock ticker.
Output: A dictionary containing ESG risk scores and controversy level.
Operations: Sends a GET request to Yahoo Finance, parses the HTML response using BeautifulSoup, and extracts relevant ESG data.

map_esg_risk_to_level(score)

Purpose: Maps an ESG risk score to a risk level category.
Input: ESG risk score.
Output: Risk level category (e.g., "Very Low", "Low", "Medium", etc.).
Operations: Uses conditional statements to determine the risk level based on the provided score.

process_data(Portfolio)

Purpose: Processes the downloaded stock data to calculate returns.
Input: Portfolio DataFrame containing historical stock data.
Output: A processed DataFrame with calculated returns.
Operations: Calculates the return for each stock based on the difference between the closing and opening prices.

display_esg_data_table(selected_symbols, esg_data_list)

Purpose: Displays consolidated ESG data in a table format.
Input: List of selected symbols and a list of dictionaries containing ESG data.
Output: A Streamlit table displaying ESG data.
Operations: Converts the list of dictionaries to a DataFrame and displays it using Streamlit.

display_risk_levels(tickers, esg_scores)

Purpose: Displays a visualization of ESG risk levels for selected tickers.
Input: List of tickers and their corresponding ESG scores.
Output: A Streamlit bar chart visualizing ESG risk levels.
Operations: Uses Plotly Express to create a bar chart and annotates it with the scores of the selected tickers.

merge_additional_info(portfolio, tickers)

Purpose: Merges additional company information to the portfolio DataFrame.
Input: Portfolio DataFrame and tickers DataFrame containing additional company information.
Output: A merged DataFrame with additional company information.
Operations: Uses pandas.merge() to merge the two DataFrames based on the "Symbol" column.

display_time_series_chart(symbol_data, selected_symbols, start_date, end_date)

Purpose: Displays a time series chart for selected tickers.
Input: Symbol data DataFrame, list of selected symbols, start date, and end date.
Output: A Streamlit line chart visualizing the time series data.
Operations: Filters the data based on the selected symbols and date range, then uses Plotly to create a line chart.

## Main Operations:

Title and Introduction: The app displays a title and a brief introduction about its functionality.
Data Fetching: The app fetches the list of S&P 500 companies from Wikipedia and downloads their historical stock data.
Date Range Selection: Users can select a date range to filter the data.
Ticker Selection: Users can select multiple stock tickers for analysis.
Time Series Chart: The app displays a time series chart for the selected tickers based on the chosen date range.
ESG Data Retrieval: The app retrieves and displays ESG data for the selected tickers.
Data Table: The app displays a data table containing the filtered stock data. Users can also download the data as a CSV or Excel file.

## Requirements
Python
Streamlit
Pandas
yfinance
base64
io
datetime
Installation

License
MIT
