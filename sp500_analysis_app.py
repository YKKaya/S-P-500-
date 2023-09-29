{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": 2,
   "id": "be0a71d9",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "[*********************100%%**********************]  503 of 503 completed"
     ]
    },
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "\n",
      "2 Failed downloads:\n",
      "['BRK.B']: Exception('%ticker%: No data found, symbol may be delisted')\n",
      "['BF.B']: Exception('%ticker%: No price data found, symbol may be delisted (period=1y)')\n"
     ]
    },
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "\n"
     ]
    }
   ],
   "source": [
    "# Importing required libraries\n",
    "import streamlit as st\n",
    "import pandas as pd\n",
    "import yfinance as yf\n",
    "\n",
    "# Function to fetch S&P 500 data\n",
    "def fetch_sp500_data(url):\n",
    "    try:\n",
    "        tickers = pd.read_html(url)[0]\n",
    "        return tickers\n",
    "    except Exception as e:\n",
    "        st.error(f\"Error fetching S&P 500 data: {e}\")\n",
    "        return None\n",
    "\n",
    "# Function to download stock data\n",
    "def download_stock_data(Stocks):\n",
    "    try:\n",
    "        Portfolio = yf.download(Stocks , period='1y', interval='1h')\n",
    "        return Portfolio\n",
    "    except Exception as e:\n",
    "        st.error(f\"Error downloading stock data: {e}\")\n",
    "        return None\n",
    "\n",
    "# Function to process data\n",
    "def process_data(Portfolio):\n",
    "    try:\n",
    "        portfolio = Portfolio.stack().reset_index().rename(index=str, columns={\"level_1\": \"Symbol\", \"level_0\": \"Datetime\"})\n",
    "        portfolio['Return'] = (portfolio['Close'] - portfolio['Open']) / portfolio['Open']\n",
    "        return portfolio\n",
    "    except Exception as e:\n",
    "        st.error(f\"Error processing data: {e}\")\n",
    "        return None\n",
    "\n",
    "# Function to merge additional info\n",
    "def merge_additional_info(portfolio, tickers):\n",
    "    try:\n",
    "        company_info = tickers[['Symbol', 'Security', 'GICS Sector', 'GICS Sub-Industry', 'Headquarters Location', 'Date added', 'Founded']]\n",
    "        company_info.columns = ['Symbol', 'Company_Name', 'Industry', 'Sub_Industry', 'Headquarters_Location', 'Date_Added', 'Founded']\n",
    "        portfolio = pd.merge(portfolio, company_info, on='Symbol', how='left')\n",
    "        return portfolio\n",
    "    except Exception as e:\n",
    "        st.error(f\"Error merging additional info: {e}\")\n",
    "        return None\n",
    "\n",
    "# Title and Description\n",
    "st.title(\"S&P 500 Analysis\")\n",
    "st.write(\"\"\"\n",
    "An interactive analysis of S&P 500 companies, allowing users to view historical stock data, returns, and additional company information.\n",
    "\"\"\")\n",
    "\n",
    "# URL for fetching S&P 500 companies data\n",
    "url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'\n",
    "\n",
    "# Fetching the list of S&P 500 companies from Wikipedia\n",
    "tickers = fetch_sp500_data(url)\n",
    "\n",
    "# Selecting the ticker symbols\n",
    "Stocks = tickers.Symbol.to_list()\n",
    "\n",
    "# Downloading historical stock data\n",
    "Portfolio = download_stock_data(Stocks)\n",
    "\n",
    "# Processing the stock data\n",
    "portfolio = process_data(Portfolio)\n",
    "\n",
    "# Merging additional company information\n",
    "portfolio = merge_additional_info(portfolio, tickers)\n",
    "\n",
    "# Cleaning the 'Founded' column by removing year values wrapped in parentheses\n",
    "if portfolio is not None:\n",
    "    portfolio['Founded'] = portfolio['Founded'].str.replace(r'\\(.*?\\)', '', regex=True).str.strip()\n",
    "    # Calculating the dollar value of the return\n",
    "    portfolio['Dollar_Return'] = portfolio['Return'] * portfolio['Adj Close']\n",
    "else:\n",
    "    st.error(\"Portfolio is None.\")\n",
    "\n",
    "# Display Results\n",
    "st.write(\"### Data Table:\")\n",
    "# Display the processed data in a table format\n",
    "st.dataframe(portfolio)\n",
    "\n",
    "# Additional Information\n",
    "st.write(\"### Additional Information:\")\n",
    "st.write(\"Links, resources, or other related information.\")\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "1efa71ca",
   "metadata": {},
   "outputs": [],
   "source": []
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3 (ipykernel)",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.10.9"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 5
}
