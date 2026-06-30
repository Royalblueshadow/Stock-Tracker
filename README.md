# Stock Tracker

A Streamlit-based stock tracking web app that allows users to search for stock tickers, view current price information, and display historical price charts using Yahoo Finance data.

Repository: https://github.com/Royalblueshadow/Stock-Tracker

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

## Project Structure

```text
Stock-Tracker/
├── .streamlit/
│   └── config.toml
├── SP500.csv
├── main.py
├── requirements.txt
└── README.md
