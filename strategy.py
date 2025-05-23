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

# --- Sidebar Inputs ---
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
total_tokens_over_time = []

for month in months:
    volume = volume_start + (volume_end - volume_start) * (month / 24)
    monthly_fee = volume * fee_rate * 30
    lock_pool_usd = monthly_fee * 0.14 * (lock_pool_share / 100)
    stake_pool_usd = monthly_fee * 0.86 * (stake_pool_share / 100)
    total_reward_usd = lock_pool_usd + stake_pool_usd
    tokens_from_rewards = total_reward_usd / initial_token_price
    reward_usd.append(total_reward_usd)
    reward_tokens.append(tokens_from_rewards)

reward_tokens_cum = np.cumsum(reward_tokens)
total_tokens_over_time = total_tokens + reward_tokens_cum

# --- Expected Price Curve & Profit ---
expected_price = np.concatenate([
    np.linspace(0.04, 1.0, 12),
    np.linspace(1.0, 2.5, 12)
])
projected_profit = total_tokens_over_time * expected_price

# --- Interactive Token Accumulation Chart ---
st.subheader("📊 Total STB Tokens (Including Rewards)")
token_chart = go.Figure()
token_chart.add_trace(go.Scatter(
    x=months,
    y=total_tokens_over_time,
    mode='lines+markers',
    name='Total STB Tokens',
    hovertemplate='Month %{x}<br>Tokens: %{y:,.0f}<extra></extra>'
))
token_chart.update_layout(
    xaxis_title="Month",
    yaxis_title="Tokens",
    hovermode='x unified',
    margin=dict(l=40, r=40, t=40, b=40)
)
st.plotly_chart(token_chart, use_container_width=True)

# --- Projected Profit Chart ---
st.subheader("💰 Projected Profit Based on Expected STB Price")
profit_chart = go.Figure()
profit_chart.add_trace(go.Scatter(
    x=months,
    y=projected_profit,
    mode='lines+markers',
    name='Projected Profit ($)',
    hovertemplate='Month %{x}<br>Profit: $%{y:,.0f}<extra></extra>'
))
profit_chart.add_hline(y=1_000_000, line_dash='dash', line_color='orange', annotation_text='Goal: $1M')
profit_chart.add_hline(y=5_000_000, line_dash='dash', line_color='green', annotation_text='Optimal: $5M')
profit_chart.update_layout(
    xaxis_title="Month",
    yaxis_title="Profit ($)",
    hovermode='x unified',
    margin=dict(l=40, r=40, t=40, b=40)
)
st.plotly_chart(profit_chart, use_container_width=True)

# --- Expected Token Price Growth Chart ---
st.subheader("📈 Expected STB Price Growth (Next 2 Years)")
price_chart = px.line(
    x=months,
    y=expected_price,
    labels={'x': 'Month', 'y': 'Expected STB Price ($)'},
    title="Projected Token Price Over 2 Years"
)
price_chart.update_traces(mode='lines+markers', hovertemplate='Month %{x}<br>Price: $%{y:.2f}<extra></extra>')
price_chart.update_layout(hovermode='x unified')
st.plotly_chart(price_chart, use_container_width=True)

# --- KPI Summary Table ---
st.subheader("📌 Key Performance Indicators (KPI)")
kpis = [
    ("Main Allocation Tokens", main_tokens),
    ("Secondary Allocation Tokens", secondary_tokens),
    ("Total Tokens Held", total_tokens),
    ("Locking Pool Share (%)", lock_pool_share),
    ("Staking Pool Share (%)", stake_pool_share),
    ("Staking APY (%)", staking_apy),
    ("Locking APY (%)", locking_apy),
    ("Transaction Fee Rate (%)", fee_rate * 100),
    ("Initial Token Price ($)", initial_token_price),
    ("Target Sell Price ($)", target_price),
    ("Expected STB Price End Year", expected_price[-1]),
    ("Projected Tokens in 2 Years", int(total_tokens_over_time[-1])),
    ("Projected Profit at End Price ($)", f"${projected_profit[-1]:,.0f}"),
]
st.dataframe(pd.DataFrame(kpis, columns=["KPI", "Value"]))
