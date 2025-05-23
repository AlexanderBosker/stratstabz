import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# --- Constants ---
main_tokens = 457143
secondary_tokens = 45834
total_tokens = main_tokens + secondary_tokens
initial_token_price = 0.04

# --- Sidebar Config ---
st.set_page_config(layout="wide")
st.title("📈 STB Investment Strategy Dashboard")
st.sidebar.header("🔧 Adjust Assumptions")

target_price = st.sidebar.number_input("🎯 Target Sell Price ($)", 0.1, 20.0, value=2.0)
lock_pool_share = st.sidebar.slider("🔐 Lock Pool Share (%)", 0.001, 1.0, value=0.5)
stake_pool_share = st.sidebar.slider("📥 Staking Pool Share (%)", 0.001, 1.0, value=0.5)
staking_apy = st.sidebar.slider("📈 Staking APY (%)", 0, 200, value=50)
locking_apy = st.sidebar.slider("🔒 Locking APY (%)", 0, 300, value=100)
fee_rate = st.sidebar.slider("💰 Transaction Fee Rate (%)", 0.001, 0.5, value=0.1) / 100
volume_start = st.sidebar.number_input("📊 Start DEX Volume ($M/day)", 10, 1000, value=100) * 1_000_000
volume_end = st.sidebar.number_input("📈 End-Year DEX Volume ($M/day)", 10, 1000, value=300) * 1_000_000

# --- Token and Reward Simulation ---
months = np.arange(1, 25)
reward_usd, reward_tokens, total_tokens_over_time = [], [], []
cumulative_rewards = 0

for month in months:
    volume = volume_start + (volume_end - volume_start) * (month / 24)
    monthly_fee = volume * fee_rate * 30
    lock_rewards = monthly_fee * 0.14 * (lock_pool_share / 100)
    stake_rewards = monthly_fee * 0.86 * (stake_pool_share / 100)
    reward_total = lock_rewards + stake_rewards
    reward_token_amount = reward_total / initial_token_price
    cumulative_rewards += reward_token_amount
    reward_usd.append(reward_total)
    reward_tokens.append(reward_token_amount)
    total_tokens_over_time.append(total_tokens + cumulative_rewards)

# --- Logistic Token Price ---
def logistic_price(t, K=2.5, r=0.3, t0=12):
    return K / (1 + np.exp(-r * (t - t0)))

expected_price = logistic_price(months)
projected_profit = np.array(total_tokens_over_time) * expected_price

def find_nearest_index(arr, target):
    return np.argmin(np.abs(np.array(arr) - target))

goal_index = find_nearest_index(projected_profit, 1_000_000)
opt_index = find_nearest_index(projected_profit, 5_000_000)

# --- Charts ---
st.subheader("📊 Total STB Tokens (Including Rewards)")
fig_tokens = go.Figure()
fig_tokens.add_trace(go.Scatter(
    x=months, y=total_tokens_over_time,
    mode='lines+markers',
    name='Total STB Tokens',
    hovertemplate='Month %{x}<br>Tokens: %{y:,.0f}<extra></extra>'
))
fig_tokens.update_layout(
    xaxis_title="Month", yaxis_title="Tokens",
    hovermode='x unified'
)
st.plotly_chart(fig_tokens, use_container_width=True)

st.subheader("💰 Projected Profit Based on Expected STB Price")
fig_profit = go.Figure()
fig_profit.add_trace(go.Scatter(
    x=months, y=projected_profit,
    mode='lines+markers',
    name='Projected Profit',
    hovertemplate='Month %{x}<br>Profit: $%{y:,.0f}<extra></extra>'
))
fig_profit.add_trace(go.Scatter(
    x=[months[goal_index]], y=[projected_profit[goal_index]],
    mode='markers+text', name='Goal $1M',
    text=["$1M Goal"], textposition="top right",
    marker=dict(size=10, color="orange")
))
fig_profit.add_trace(go.Scatter(
    x=[months[opt_index]], y=[projected_profit[opt_index]],
    mode='markers+text', name='Optimal $5M',
    text=["$5M Opt"], textposition="bottom left",
    marker=dict(size=10, color="green")
))
fig_profit.update_layout(
    xaxis_title="Month", yaxis_title="Profit ($)",
    hovermode='x unified'
)
st.plotly_chart(fig_profit, use_container_width=True)

st.subheader("📈 Expected STB Price Growth")
fig_price = go.Figure()
fig_price.add_trace(go.Scatter(
    x=months, y=expected_price,
    mode='lines+markers',
    name='Expected Price',
    hovertemplate='Month %{x}<br>Price: $%{y:.2f}<extra></extra>'
))
fig_price.update_layout(
    xaxis_title="Month", yaxis_title="STB Price ($)",
    hovermode='x unified'
)
st.plotly_chart(fig_price, use_container_width=True)

# --- KPI Table ---
st.subheader("📌 Key Performance Indicators")
kpis = [
    ("Initial Tokens", total_tokens),
    ("Lock Pool Share (%)", lock_pool_share),
    ("Stake Pool Share (%)", stake_pool_share),
    ("Transaction Fee Rate (%)", fee_rate * 100),
    ("Projected Tokens in 2 Years", int(total_tokens_over_time[-1])),
    ("Projected Profit ($, end)", f"${projected_profit[-1]:,.0f}"),
    ("Expected Token Price (end)", f"${expected_price[-1]:.2f}")
]
st.dataframe(pd.DataFrame(kpis, columns=["KPI", "Value"]))
