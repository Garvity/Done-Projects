import streamlit as st
import yfinance as yf
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import Dense, LSTM
import matplotlib.pyplot as plt
import pickle
import os

st.title("Stock Price Prediction with LSTM & Buy/Sell Signals")

# --- Helper functions ---

def download_and_prepare(ticker, period):
    data = yf.download(ticker, period=period)[['Close', 'Volume']]
    data['MA20'] = data['Close'].rolling(window=20).mean()
    data.dropna(inplace=True)
    return data

def prepare_data(df, features, n_steps, scaler=None):
    if scaler is None:
        scaler = MinMaxScaler(feature_range=(0,1))
        scaled_data = scaler.fit_transform(df[features])
    else:
        scaled_data = scaler.transform(df[features])
    X, y = [], []
    for i in range(n_steps, len(scaled_data)):
        X.append(scaled_data[i-n_steps:i, :])
        y.append(scaled_data[i, 0])
    return np.array(X), np.array(y), scaler

def build_and_train_model(X_train, y_train):
    model = Sequential([
        LSTM(50, return_sequences=True, input_shape=(X_train.shape[1], X_train.shape[2])),
        LSTM(50),
        Dense(1)
    ])
    model.compile(optimizer='adam', loss='mean_squared_error')
    model.fit(X_train, y_train, epochs=10, batch_size=32)
    return model

def generate_signals(actual, predicted):
    return ['Buy' if p > a else 'Sell' for p, a in zip(predicted, actual)]

def plot_results(actual, predicted, ticker):
    fig, ax = plt.subplots(figsize=(12,6))
    ax.plot(actual, label='Actual Close Price')
    ax.plot(predicted, label='Predicted Close Price')
    ax.set_title(f'{ticker} Stock Price Prediction')
    ax.set_xlabel('Time')
    ax.set_ylabel('Price')
    ax.legend()
    st.pyplot(fig)

# --- Streamlit UI ---

ticker = st.text_input("Enter Stock Ticker", value="AAPL").upper()
period_train = st.selectbox("Select Training Data Period", options=["1y", "2y", "5y", "10y"], index=2)
period_pred = st.selectbox("Select Prediction Data Period", options=["1mo", "3mo", "6mo", "1y"], index=3)
n_steps = st.slider("Number of past days to consider (LSTM timesteps)", 20, 100, 60)

if st.button("Train Model and Predict"):
    with st.spinner("Downloading and preparing data..."):
        data_train = download_and_prepare(ticker, period_train)
        features = ['Close', 'Volume', 'MA20']
        X, y, scaler = prepare_data(data_train, features, n_steps)
        train_size = int(len(X)*0.8)
        X_train, y_train = X[:train_size], y[:train_size]

    with st.spinner("Training model..."):
        model = build_and_train_model(X_train, y_train)

    with st.spinner("Downloading new data for prediction..."):
        data_pred = download_and_prepare(ticker, period_pred)
        X_pred, y_pred, _ = prepare_data(data_pred, features, n_steps, scaler)

    with st.spinner("Predicting..."):
        preds = model.predict(X_pred)
        pad_zeros = np.zeros((preds.shape[0], len(features)-1))
        preds_inv = scaler.inverse_transform(np.hstack([preds, pad_zeros]))[:,0]
        y_pred_inv = scaler.inverse_transform(np.hstack([y_pred.reshape(-1,1), pad_zeros]))[:,0]

    signals = generate_signals(y_pred_inv, preds_inv)

    st.subheader(f"Buy/Sell Signals for {ticker}")
    for i, sig in enumerate(signals[-10:], 1):
        st.write(f"Day -{10 - i + 1}: {sig}")

    plot_results(y_pred_inv, preds_inv, ticker)
