import sys
import csv
import yfinance as yf
import plotly.graph_objects as go
import streamlit as st
import pandas as pd
from streamlit_autorefresh import st_autorefresh

def main():
    #autorefresh timer
    st_autorefresh(interval=30_000, key = "stock_refresh")

    #title of the stocktracker
    st.title("Stocktracker",text_alignment= "center")

    #Text_input for the name of the stock
    stock_name = st.text_input("Name of Stock", placeholder="AAPL")

    #check if input exists
    if not stock_name:
        return 

    ticker = yf.Ticker(stock_name)
    data = ticker.info

    #ticker history for the day with intervals of 1min

    #intraday = ticker.history(period = "1d", interval = "5m")

    #pill buttons for time selection
    #options = ["day", "week", "month", "year", "5 years", "max"]
    #selection = st.segmented_control("",options, default = "day", selection_mode="single")
    

    stock_header_placeholder = st.empty()
    
    col5, col6 = st.columns([1,2])
    with col5:
        options = ["Line", "Candlestick"]
        chart_type =st.segmented_control("", options, default = "Line", selection_mode="single")
    with col6:
        with st.container(horizontal_alignment="right"):
            options = ["day", "week", "month", "year", "5 years", "max"]
            selection = st.segmented_control("",options, default = "day", selection_mode="single")

    with stock_header_placeholder.container():
        intraday, period, reference_history = define_history_window(ticker,selection)
        #throw error, when no price for the day is found
        if intraday.empty:
            st.error("No data found.")
            return

        #values for the price difference within a timespan
        
        change_real, change_percentage = calculate_daily_difference(reference_history, intraday)
        current_closing_price = ticker.info.get("regularMarketPrice")

        col1, col2 = st.columns([1,1])
        with col1:  
            st.header(data["symbol"])
        with col2:
            with st.container(horizontal_alignment="right", vertical_alignment= "bottom"):
                st.header(f"${round(current_closing_price,2)}", text_alignment= "right")
        
        col3, col4 = st.columns([5,2])
        with col3:
            st.write(data["longName"])
        with col4:
            with st.container(horizontal = True, horizontal_alignment="right"):
                st.write(f"${round(change_real,2)}: ({round(change_percentage, 2)})")
    
    fig = prepare_candle_data(intraday, chart_type, period, change_percentage)
    st.plotly_chart(fig, use_container_width=True)

    

def define_history_window(ticker, selection):
    match selection:
        case "day":
            time_window = "1d"
            interval_window = "5m"
            reference_time = "2d"
            reference_interval = "1d"
        case "week":
            time_window = "7d"
            interval_window = "60m"
            reference_time = "1wk"
            reference_interval = "1wk"
        case "month":
            time_window = "1mo"
            interval_window = "1d"
            reference_time = "2mo"
            reference_interval = "1mo"
        case "year":
            time_window = "1y"
            interval_window = "1wk"
            reference_time = "1y"
            reference_interval = "3mo"
        case "5 years":
            time_window = "5y"
            interval_window = "1mo"
            reference_time = "5y"
            reference_interval = "3mo"
        case "max":
            time_window = "max"
            interval_window = "3mo"
            reference_time = time_window
            reference_interval = interval_window
        case _:
            time_window ="1d"
            interval_window = "5m"
            reference_time = "2d"
            reference_interval = "1d"
            

    history = ticker.history(period = time_window, interval = interval_window, prepost=False)
    reference_history = ticker.history(period = reference_time, interval = reference_interval)
    return history, time_window, reference_history

def prepare_candle_data(data, type, period, change):

    fig = go.Figure()

    if change >= 0:
        color = "green"
    else: 
        color = "red"

    if type == "Candlestick":
        fig.add_trace(
            go.Candlestick(
                x = data.index,
                open = data["Open"],
                high = data["High"],
                low = data["Low"],
                close = data["Close"],
                name = "OHLC"
            )
        )
        

    elif type == "Line":
        fig.add_trace(
            go.Scatter(
                x = data.index,
                y = data["Close"],
                mode = "lines",
                name = "Close",
                line_color = color
            )
        )
        

    fig.update_layout(
        xaxis_title="Time",
        yaxis_title="Price",
        xaxis_rangeslider_visible=False,
        height = 600
    )

    fig.update_xaxes(
        rangebreaks = get_rangebreaks(period)
    ) 

    return fig

def get_rangebreaks(period):
    period_week = ["1d", "7d"]
    period_max = ["1y", "5y", "max"]

    if period in period_week:
        return [
            dict(bounds = ["sat", "mon"]),
            dict(bounds = [16, 9.5], pattern = "hour")
        ]
    elif period in period_max:
        return []

    return [
        dict(bounds = ["sat", "mon"])
    ]

def calculate_daily_difference(daily, intraday):
    previous_close = daily["Close"].iloc[0]
    current_closing_price = intraday["Close"].iloc[-1]

    change_real = (current_closing_price - previous_close)
    change_percentage = (current_closing_price/previous_close - 1) * 100

    return change_real.round(2), change_percentage.round(2)
    

if __name__ == "__main__":
    main()  

