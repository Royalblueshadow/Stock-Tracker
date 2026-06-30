# Stock Tracker

A Streamlit-based stock tracking web app that allows users to search for stock tickers, view current price information, and display historical price charts using Yahoo Finance data.

URL: https://github.com/Royalblueshadow/Stock-Tracker](https://stock-tracker-jxprylb6sjqnwkmav9cwq8.streamlit.app/

## Overview

Stock Tracker is a Python web application built with Streamlit. It lets users enter any supported stock ticker and view price data across different timeframes, including daily, weekly, monthly, yearly, and longer-term views.

The app uses Yahoo Finance data through Python finance libraries and visualizes the results with interactive Plotly charts.

## Features

- Search for individual stock tickers
- Display current stock price
- Show daily price change and percentage change
- View historical price charts
- Switch between line charts and candlestick charts
- Select different chart timeframes
- Display best-performing stocks from an S&P 500 list
- Click stock buttons to quickly load another ticker
- Interactive Plotly charts
- Streamlit-based web interface
- Custom Streamlit theme configuration

## Tech Stack

- Python
- Streamlit
- Plotly
- yfinance
- yahooquery
- pandas

## Installation

Clone the repository:

```bash
git clone https://github.com/Royalblueshadow/Stock-Tracker.git
cd Stock-Tracker
```

Create and activate a virtual environment:

```bash
python -m venv .venv
```

On Windows:

```bash
.venv\Scripts\activate
```

On macOS/Linux:

```bash
source .venv/bin/activate
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

## Running the App Locally

Start the Streamlit app with:

```bash
streamlit run main.py
```

Then open the local URL shown in the terminal, usually:

```text
http://localhost:8501
```

## Requirements

The project dependencies are listed in `requirements.txt`.

Typical dependencies include:

```text
streamlit
pandas
plotly
yfinance
yahooquery
```

## Data Source

Stock price and market data are retrieved from Yahoo Finance through Python libraries such as `yfinance` and `yahooquery`.

The app uses this data to display:

- Current stock prices
- Previous closing prices
- Daily price changes
- Historical chart data
- Line charts
- Candlestick charts
- S&P 500 stock performance information

Because the app relies on unofficial Yahoo Finance access, data availability and request behavior may vary. Stock data may be delayed, incomplete, or temporarily unavailable.

## Notes on Rate Limits

Yahoo Finance may temporarily limit requests if too many queries are made in a short period of time. This can especially happen when loading data for many S&P 500 stocks at once.

Possible signs of rate limiting include:

- Some tickers return missing data
- Only part of the S&P 500 list loads successfully
- Current price or previous close values are missing
- The app works with fewer tickers but fails with many tickers
- Re-running the app immediately gives inconsistent results

To reduce the risk of rate limits, the app can use:

- Caching with Streamlit
- Smaller request batches
- Delays between larger data requests
- Fewer automatic refreshes
- Fallback checks for missing ticker data

Example caching strategy:

```python
@st.cache_data(ttl=300)
def get_stock_data(...):
    ...
```

This keeps downloaded data for a limited time and avoids sending the same request repeatedly.

## Disclaimer

This project is for educational and informational purposes only. It is not financial advice. Stock data may be delayed, incomplete, or temporarily unavailable. Always verify financial information from reliable sources before making investment decisions.

## Author

Created by [Royalblueshadow](https://github.com/Royalblueshadow).
