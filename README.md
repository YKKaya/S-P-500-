#S&P 500 Analysis Streamlit App
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
