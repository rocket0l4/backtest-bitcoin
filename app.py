




import pandas as pd
import numpy as np
import plotly.graph_objects as go
import streamlit as st
import pickle

# Load data from pickle file
with open("data.pkl", "rb") as f:
    data = pickle.load(f)

# Ensure the date column is set as the index
data.set_index('Date', inplace=True)

# Debugging: Show dataset range
st.sidebar.header("Data Range")
st.sidebar.write(f"Minimum Close Price: {data['Close'].min()}")
st.sidebar.write(f"Maximum Close Price: {data['Close'].max()}")

# Input parameters from the user
st.sidebar.header("Filters and Parameters")
min_price = st.sidebar.number_input("Minimum Price", min_value=0, value=25000, step=100)
max_price = st.sidebar.number_input("Maximum Price", min_value=0, value=40000, step=100)

# Trading strategy parameters
window_size = st.sidebar.slider("Moving Average Window (days)", min_value=5, max_value=50, value=10)
starting_capital = st.sidebar.number_input("Starting Capital", min_value=0, value=100000, step=1000)

# Filter data based on user input
filtered_data = data[(data['Close'] >= min_price) & (data['Close'] <= max_price)]

# Handle empty dataset scenario
if filtered_data.empty:
    st.error(f"No data available for the price range {min_price}-{max_price}. Please adjust the range.")
    st.write("Showing entire dataset as fallback:")
    st.write(data)
    st.stop()

# Generate Buy/Sell signals
filtered_data['Rolling_Mean'] = filtered_data['Close'].rolling(window_size).mean()
filtered_data['Buy_Entry'] = np.where(filtered_data['Close'] > filtered_data['Rolling_Mean'], 1, 0)
filtered_data['Sell_Entry'] = np.where(filtered_data['Close'] < filtered_data['Rolling_Mean'], 1, 0)

# Backtesting Logic
capital = starting_capital
position = 0  # Current position (amount of stock held)
cash = capital  # Initial cash
pnl = []  # Portfolio value over time

for i in range(len(filtered_data)):
    close_price = filtered_data['Close'].iloc[i]

    # Buy signal
    if filtered_data['Buy_Entry'].iloc[i] == 1 and position == 0:
        position = cash / close_price  # Buy with all available cash
        cash = 0

    # Sell signal
    elif filtered_data['Sell_Entry'].iloc[i] == 1 and position > 0:
        cash = position * close_price  # Sell all positions
        position = 0

    # Calculate current portfolio value
    portfolio_value = cash + (position * close_price)
    pnl.append(portfolio_value)

# Add PnL to the DataFrame
filtered_data['PnL'] = pnl

# Performance Metrics
total_return = (pnl[-1] - capital) / capital
drawdown = min(pnl) - capital
sharpe_ratio = (np.mean(np.diff(pnl)) / np.std(np.diff(pnl))) * np.sqrt(252) if len(pnl) > 1 else 0

# Display Metrics
st.sidebar.header("Performance Metrics")
st.sidebar.write(f"Total Return: {total_return:.2%}")
st.sidebar.write(f"Max Drawdown: {drawdown:.2f}")
st.sidebar.write(f"Sharpe Ratio: {sharpe_ratio:.2f}")

# Plot Interactive Line Chart
st.title(f"Price Chart with Buy/Sell Signals ({min_price}-{max_price})")
line_fig = go.Figure()

line_fig.add_trace(go.Scatter(
    x=filtered_data.index,
    y=filtered_data['Close'],
    mode='lines',
    name='Close Price',
    line=dict(color='royalblue', width=2)
))

line_fig.add_trace(go.Scatter(
    x=filtered_data[filtered_data['Buy_Entry'] == 1].index,
    y=filtered_data[filtered_data['Buy_Entry'] == 1]['Close'],
    mode='markers',
    name='Buy Signal',
    marker=dict(color='green', symbol='triangle-up', size=12, line=dict(color='black', width=2))
))

line_fig.add_trace(go.Scatter(
    x=filtered_data[filtered_data['Sell_Entry'] == 1].index,
    y=filtered_data[filtered_data['Sell_Entry'] == 1]['Close'],
    mode='markers',
    name='Sell Signal',
    marker=dict(color='red', symbol='triangle-down', size=12, line=dict(color='black', width=2))
))

line_fig.update_layout(
    title="Price Chart with Buy/Sell Signals",
    xaxis_title="Date",
    yaxis_title="Price",
    template='plotly_dark',
    xaxis=dict(showgrid=True, gridcolor='gray', zeroline=False),
    yaxis=dict(showgrid=True, gridcolor='gray', zeroline=False),
    font=dict(size=12)
)

st.plotly_chart(line_fig)

# Plot Portfolio Equity Curve
st.title("Portfolio Equity Curve")
equity_fig = go.Figure()
equity_fig.add_trace(go.Scatter(
    x=filtered_data.index,
    y=filtered_data['PnL'],
    mode='lines',
    name='Equity Curve',
    line=dict(color='gold', width=3)
))

equity_fig.update_layout(
    title="Portfolio Equity Curve",
    xaxis_title="Date",
    yaxis_title="Portfolio Value",
    template='plotly_dark',
    xaxis=dict(showgrid=True, gridcolor='gray', zeroline=False),
    yaxis=dict(showgrid=True, gridcolor='gray', zeroline=False),
    font=dict(size=12)
)

st.plotly_chart(equity_fig)

# Plot Candlestick Chart
st.title("Candlestick Chart")
candlestick_fig = go.Figure()
candlestick_fig.add_trace(go.Candlestick(
    x=filtered_data.index,
    open=filtered_data['Open'],
    high=filtered_data['High'],
    low=filtered_data['Low'],
    close=filtered_data['Close'],
    name='Candlestick',
    increasing_line_color='green',
    decreasing_line_color='red'
))

candlestick_fig.update_layout(
    title="Bitcoin Candlestick Chart",
    xaxis_title="Date",
    yaxis_title="Price",
    template='plotly_dark',
    xaxis=dict(showgrid=True, gridcolor='gray', zeroline=False),
    yaxis=dict(showgrid=True, gridcolor='gray', zeroline=False),
    font=dict(size=12),
)

st.plotly_chart(candlestick_fig)
