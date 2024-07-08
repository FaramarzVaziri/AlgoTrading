import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import warnings

warnings.filterwarnings("ignore")

# Function to analyze strategies
def analyze_strategies(initial_cash, start_date_test, end_date_test, long_window, short_window, symbol):
    # Load test data
    data_test = yf.download(symbol, start=start_date_test, end=end_date_test)

    # Moving Average Crossover Strategy
    def moving_average_crossover(data, short_window, long_window):
        data['Short_MA'] = data['Close'].rolling(window=short_window, min_periods=1).mean()
        data['Long_MA'] = data['Close'].rolling(window=long_window, min_periods=1).mean()
        data['Signal_MA'] = 0.0
        data['Signal_MA'][short_window:] = np.where(data['Short_MA'][short_window:] > data['Long_MA'][short_window:], 1.0, 0.0)
        data['Position_MA'] = data['Signal_MA'].diff()
        return data

    # Apply strategies
    data_test = moving_average_crossover(data_test, short_window=short_window, long_window=long_window)

    # Calculate returns and portfolio value for Moving Average Crossover
    cash_ma = initial_cash
    position_ma = 0
    data_test['Portfolio_MA'] = np.nan

    for i in range(len(data_test)):
        if data_test['Position_MA'].iloc[i] == 1.0:  # Buy signal
            action = 'buy all or keep shares if already bought'
            if cash_ma > 0:  # Ensure we only buy if we have cash
                position_ma = cash_ma / data_test['Close'].iloc[i]
                cash_ma = 0
        elif data_test['Position_MA'].iloc[i] == -1.0:  # Sell signal
            action = 'sell all shares or hold on if already sold'
            if position_ma > 0:  # Ensure we only sell if we have a position
                cash_ma = position_ma * data_test['Close'].iloc[i]
                position_ma = 0
        data_test['Portfolio_MA'].iloc[i] = cash_ma + position_ma * data_test['Close'].iloc[i]

    final_value_MA = cash_ma + position_ma * data_test['Close'].iloc[-1]
    return_MA = (final_value_MA - initial_cash) / initial_cash * 100

    # Print the results
    st.write(f"End Date's Action: {action}")
    st.write(f"Moving Average Crossover Strategy Return for {symbol}: {return_MA:.2f}%")
    st.write(f"Final Portfolio Value for {symbol}: {final_value_MA:.2f}")

    # Plot the results
    st.subheader(f'{symbol} - Strategy Comparison')
    fig, ax = plt.subplots(figsize=(14, 7))
    ax.plot(data_test['Close'], label='Close Price')
    ax.plot(data_test['Short_MA'], label=f'Short MA ({short_window} days)')
    ax.plot(data_test['Long_MA'], label=f'Long MA ({long_window} days)')
    ax.plot(data_test[data_test['Position_MA'] == 1.0].index, data_test['Short_MA'][data_test['Position_MA'] == 1.0], '^', markersize=10, color='g', lw=0, label='Buy Signal MA')
    ax.plot(data_test[data_test['Position_MA'] == -1.0].index, data_test['Short_MA'][data_test['Position_MA'] == -1.0], 'v', markersize=10, color='r', lw=0, label='Sell Signal MA')
    ax.legend()
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    st.pyplot(fig)

    # Plot portfolio values
    st.subheader(f'{symbol} - Portfolio Values Over Time')
    fig, ax = plt.subplots(figsize=(14, 7))
    ax.plot(data_test.index, data_test['Portfolio_MA'], label='Portfolio Value MA', color='blue')
    ax.legend()
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    st.pyplot(fig)

    return final_value_MA

# Streamlit app
st.title("Daily Monitor - Moving Average Crossover Strategy - ")

# Input fields
today = datetime.today().strftime('%Y-%m-%d')
three_months_ago = (datetime.today() - timedelta(days=31)).strftime('%Y-%m-%d')

initial_cash = st.number_input("Initial Cash", value=10000)
start_date_test = st.date_input("Start Date", value=pd.to_datetime(three_months_ago))
end_date_test = st.date_input("End Date", value=pd.to_datetime(today))
long_window = st.number_input("Long Window", value=7)
short_window = st.number_input("Short Window", value=3)
symbol = st.text_input("Stock Symbol", value="AAPL")

# Run analysis button
if st.button("Run Analysis"):
    final_value = analyze_strategies(initial_cash, start_date_test, end_date_test, long_window, short_window, symbol)
    st.write(f"Final Portfolio Value: {final_value}")


# Author and Link
st.markdown("### Author: Faramarz Jabbarvaziri")
st.markdown("[Embarking on My AlgoTrading Journey](https://www.linkedin.com/pulse/embarking-my-algotrading-journey-faramarz-jabbarvaziri-9ltpc/?trackingId=RRdkLYdVTrKmOYOOVUV6Bg%3D%3D)")
