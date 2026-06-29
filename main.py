import sys
import csv
import yfinance as yf
import plotly.graph_objects as go
import streamlit as st
import pandas as pd
from yahooquery import Ticker 
from streamlit_autorefresh import st_autorefresh
import time
import random


def click_button(symbol):
    st.session_state.stock_input = symbol

def main():

    st.markdown(
    """
    <style>
    div.stButton > button[kind="secondary"] {
        background-color: transparent;
        color: #fafafa;
        border: 1px solid #4f9249cc;
    }

    div.stButton > button[kind="secondary"]:hover {
        background-color: #4f92494a;
    }

    div.stButton > button[kind="tertiary"] {
        background-color: transparent;
        color: #fafafa;
        border: 1px solid #924d49;
    }

    div.stButton > button[kind="tertiary"]:hover {
        background-color: #924d494a;
    }
    </style>
    """,
    unsafe_allow_html=True
)

    st.set_page_config(layout="wide")

    #autorefresh timer
    st_autorefresh(interval=30_000, key = "stock_refresh")

    #title of the stocktracker
    st.markdown("# Tickr",text_alignment= "center")

    if "stock_input" not in st.session_state:
        st.session_state.stock_input = ""
    
    if "database_size" not in st.session_state:
        st.session_state.database_size = 100
    
    #Text_input for the name of the stock
    input_col1, input_col2 = st.columns([5,1])
    with input_col1:
        stock_name = st.text_input(
            "Stock symbol", 
            key = "stock_input",
            placeholder = "AAPL"
            )
    with input_col2:
        used_rows = st.number_input(
            "database size",
            key = "database_size",
            placeholder = "100",
            min_value=1,
            max_value=500,
            step = 1,
            value = 100
        )

    #check if input exists
    if not stock_name:
        return 

    ticker = yf.Ticker(stock_name)
    data = ticker.info
    
    buttons_placeholder = st.empty()
    stock_header_placeholder = st.empty()
    menu_placeholder = st.empty()
    chart_placeholder = st.empty()
    
    bottom_col1, bottom_col2, bottom_col3 = st.columns([1,1,1])
    with bottom_col2:
        with st.container(horizontal_alignment="right", border=True):
            st.markdown("created by Royalblueshadow", text_alignment="center")
    with bottom_col3:
        with st.container(horizontal_alignment="right", border=True):
            st.markdown("https://github.com/Royalblueshadow", text_alignment="center")
    with bottom_col1:
        with st.container(horizontal_alignment="right", border=True):
            st.markdown("educational use only", text_alignment="center")


    with menu_placeholder.container():
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
            menu_placeholder.empty()
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
                if change_percentage < 0:
                    st.header(f"$ :red[{round(current_closing_price,2)}]", text_alignment= "right")
                else:
                    st.header(f"$ :green[{round(current_closing_price,2)}]", text_alignment= "right")
        
        col3, col4 = st.columns([5,2])
        with col3:
            st.write(data["longName"])
        with col4:
            with st.container(horizontal = True, horizontal_alignment="right"):
                if change_percentage < 0:
                    st.write(f"$ :red[{round(change_real,2)}]  :red[({round(change_percentage, 2)})]")
                else:
                    st.write(f"$ :green[{round(change_real,2)}]  :green[({round(change_percentage, 2)})]")
    
    with chart_placeholder.container():
        fig = prepare_candle_data(intraday, chart_type, period, change_percentage)
        st.plotly_chart(fig, use_container_width=True)

    with buttons_placeholder.container():
        
    #scraping multiple stockinfos

        tickers_df = pd.read_csv("SP500.csv", nrows = used_rows)

        symbols = tickers_df["Symbol"].tolist()
        
        performance, skipped = get_sp500_performance(symbols)

        if skipped.size > 5:
            detail1, detail2 = st.columns([5,1])
            with detail2:
                st.write("Skipped symbols:", len(skipped))

            with detail1:
                with st.expander("details"):
                    st.write(skipped)
                
        performance = performance.sort_values(by =["Performance"], ascending=False)
        
        #performance = performance.sort_values(by =["Performance"], ascending=False)


        best_performing = performance.head(5)
        #st.write(best_performing)

        worst_performing = performance.tail(5)
        #st.write(worst_performing)

        create_best_performing(best_performing)

        create_worst_performing(worst_performing)


def create_best_performing(dataset):
    with st.container(border=True):
        buttons = st.columns(5)
        i = 0
        for button in buttons:
            symbol = dataset.iloc[i].get("Symbol")
            performance = dataset.iloc[i].get("Performance")
            if button.button(label = f"{symbol}: {performance}", width="stretch", on_click=click_button, args=(symbol,), type = "secondary"):
                st.rerun()
            i+= 1

def create_worst_performing(dataset):
    with st.container(border=True):
        buttons = st.columns(5)
        i = 4
        for button in buttons:
            symbol = dataset.iloc[i].get("Symbol")
            performance = dataset.iloc[i].get("Performance")
            if button.button(label = f"{symbol}: {performance}", width="stretch", on_click=click_button, args=(symbol,), type ="tertiary"):
                st.rerun()
            i-= 1
        
def chunks(lst, size):
    for i in range(0, len(lst), size):
        yield lst[i:i+size]

@st.cache_data(ttl=300)
def get_sp500_performance(symbols, chunk_size=50):
    rows=[]
    skipped = []

    for symbol_chunk in chunks(symbols, chunk_size):
        tickers = Ticker(symbols, asynchronous=True)
        price_data = tickers.price
        

        for symbol in symbol_chunk:
            stock_data = price_data.get(symbol)

            if not isinstance(stock_data, dict):
                skipped.append({
                    "Symbol": symbol,
                    "Reason": "not a dictionary",
                    "Data": str(stock_data)
                })
                continue

            #open_price = stock_data.get("open")
            #previous_close = stock_data.get("previousClose")

            open_price = stock_data.get("regularMarketPrice")
            previous_close = stock_data.get("regularMarketPreviousClose")

            if open_price is None or previous_close in(None, 0):
                skipped.append({
                    "Symbol": symbol,
                    "Reason": "missing regularMarketPrice",
                    "Data": str(stock_data)
                })
                continue
                
            percentage = round(((open_price/previous_close)- 1)*100, 2)

            rows.append({"Symbol": symbol,"Performance": percentage})

        time.sleep(random.randrange(0,3))

    skipped_df = pd.DataFrame(
        skipped,
        columns=["Symbol", "Reason", "Data"]
    )

    return pd.DataFrame(rows), skipped_df


def define_history_window(ticker, selection):
    match selection:
        case "day":
            time_window = "1d"
            interval_window = "2m"
            reference_time = "2d"
            reference_interval = "1d"
        case "week":
            time_window = "7d"
            interval_window = "30m"
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

