import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

# --- Constants ---
main_tokens = 457143
secondary_tokens = 45834
total_tokens = main_tokens + secondary_tokens
initial_token_price = 0.04

# --- Sidebar ---
st.set_page_config(layout="wide")
st.title("📈 STB Investment Strategy Dashboard")
st.sidebar.header("🔧 Adjust Assumptions")

target_price = st.sidebar.number_input("🎯 Target Sell Price ($)", 0.1, 20.0, value=2.0)
lock_pool_share = st.sidebar.slider("🔐 Lock Pool Share (%)", 0.1, 5.0, value=0.5)
stake_pool_share = st.sidebar.slider("📥 Staking Pool Share (%)", 0.1, 10.0, value=4.0)
staking_apy = st.sidebar.slider("📈 Staking APY (%)", 0, 200, value=50)
locking_apy = st.sidebar.slider("🔒 Locking APY (%)", 0, 300, value=100)
fee_rate = st.sidebar.slider("💰 Transaction Fee Rate (%)", 0.01, 0.5, value=0.1) / 100
volume_start = st.sidebar.number_input("📊 Start DEX Volume ($M/day)", 10, 1000, value=100) * 1_000_000
volume_end = st.sidebar.number_input("📈 End-Year DEX Volume ($M/day)", 10, 1000, value=300) * 1_000_000

# --- Simulated Rewards & Tokens ---
months = np.arange(1, 25)
reward_usd = []
reward_tokens = []
accumulated_tokens = []
total_tokens_over_time = []

cumulative_rewards = 0
for month in months:
    volume = volume_start + (volume_end - volume_start) * (month / 24)
    monthly_fee = volume * fee_rate * 30
    lock_pool_usd = monthly_fee * 0.14 * (lock_pool_share / 100)
    stake_pool_usd = monthly_fee * 0.86 * (stake_pool_share / 100)
    reward = lock_pool_usd + stake_pool_usd
    tokens = reward / initial_token_price
    cumulative_rewards += tokens
    reward_usd.append(reward)
    reward_tokens.append(tokens)
    accumulated_tokens.append(cumulative_rewards)
    total_tokens_over_time.append(total_tokens + cumulative_rewards)

# --- Expected Token Price Curve (Logistic) ---
def logistic_price(t, K=2.5, r=0.3, t0=12):
    return K / (1 + np.exp(-r * (t - t0)))

expected_price = logistic_price(months)
projected_profit = np.array(total_tokens_over_time) * expected_price

# --- Find Goal Intersections for Markers ---
def find_nearest_index(arr, target):
    return np.argmin(np.abs(np.array(arr) - target))

goal_index = find_nearest_index(projected_profit, 1_000_000)
opt_index = find_nearest_index(projected_profit, 5_000_000)

# --- Charts ---
# Token Accumulation Chart
st.subheader("📊 Total STB Tokens (Including Rewards)")
token_chart = go.Figure()
token_chart.add_trace(go.Scatter(
    x=months, y=total_tokens_over_time,
    mode='lines+markers',
    name='Total STB Tokens',
    hovertemplate='Month %{x}<br>Tokens: %{y:,.0f}<extra></extra>'
))
token_chart.update_layout(
    xaxis_title="Month", yaxis_title="Tokens",
    hovermode='x unified',
    margin=dict(l=40, r=40, t=40, b=40)
)
st.plotly_chart(token_chart, use_container_width=True)

# Projected Profit Chart
st.subheader("💰 Projected Profit Based on Expected STB Price")
profit_chart = go.Figure()
profit_chart.add_trace(go.Scatter(
    x=months, y=projected_profit,
    mode='lines+markers',
    name='Projected Profit ($)',
    hovertemplate='Month %{x}<br>Profit: $%{y:,.0f}<extra></extra>'
))
profit_chart.add_trace(go.Scatter(
    x=[months[goal_index]], y=[projected_profit[goal_index]],
    mode='markers+text', name='Goal ($1M)',
    text=["$1M Goal"], textposition="top right",
    marker=dict(size=10, color="orange")
))
profit_chart.add_trace(go.Scatter(
    x=[months[opt_index]], y=[projected_profit[opt_index]],
    mode='markers+text', name='Optimal ($5M)',
    text=["$5M Optimal"], textposition="top left",
    marker=dict(size=10, color="green")
))
profit_chart.update_layout(
    xaxis_title="Month", yaxis_title="Profit ($)",
    hovermode='x unified',
    margin=dict(l=40, r=40, t=40, b=40)
)
st.plotly_chart(profit_chart, use_container_width=True)

# Expected Price Growth Chart
st.subheader("📈 Expected STB Price Growth (Logistic Growth Curve)")
price_chart = go.Figure()
price_chart.add_trace(go.Scatter(
    x=months, y=expected_price,
    mode='lines+markers',
    name='Expected Price',
    hovertemplate='Month %{x}<br>Price: $%{y:.2f}<extra></extra>'
))
price_chart.update_layout(
    xaxis_title="Month", yaxis_title="Price ($)",
    hovermode='x unified',
    margin=dict(l=40, r=40, t=40, b=40)
)
st.plotly_chart(price_chart, use_container_width=True)

# KPI Table
st.subheader("📌 Key Performance Indicators (KPI)")
kpis = [
    ("Total Tokens Held", total_tokens),
    ("Lock Pool Share (%)", lock_pool_share),
    ("Stake Pool Share (%)", stake_pool_share),
    ("Transaction Fee Rate (%)", fee_rate * 100),
    ("Initial Token Price ($)", initial_token_price),
    ("Target Sell Price ($)", target_price),
    ("Projected Tokens in 2 Years", int(total_tokens_over_time[-1])),
    ("Projected Profit (End of 2 Years)", f"${projected_profit[-1]:,.0f}"),
    ("Expected Price at End", f"${expected_price[-1]:.2f}")
]
st.dataframe(pd.DataFrame(kpis, columns=["KPI", "Value"]))
