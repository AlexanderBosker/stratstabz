import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta

# === Streamlit Setup ===
st.set_page_config(layout="wide")
page = st.sidebar.radio("📁 Select Dashboard Section", [
    "📈 STB Investment Strategy Dashboard",
    "📊 Token Vesting Distribution",
    "📆 Altcoin Season Timeline"
])

# === Section 1: STB Investment Strategy Dashboard ===
if page == "📈 STB Investment Strategy Dashboard":
    main_tokens = 457143
    secondary_tokens = 45834
    total_tokens = main_tokens + secondary_tokens
    initial_token_price = 0.04
    months = np.arange(1, 25)

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

    st.sidebar.markdown("### 📈 Adjust STB Price Curve")
    K_price = st.sidebar.slider("🧮 Max Token Price (K)", 0.5, 10.0, 2.5, step=0.1)
    r_growth = st.sidebar.slider("📈 Growth Rate (r)", 0.01, 1.0, 0.3, step=0.01)
    t_midpoint = st.sidebar.slider("🕒 Inflection Point (Month t₀)", 1, 24, 12)

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

    def logistic_price(t, K, r, t0):
        return K / (1 + np.exp(-r * (t - t0)))

    expected_price = logistic_price(months, K_price, r_growth, t_midpoint)
    projected_profit = np.array(total_tokens_over_time) * expected_price

    def find_nearest_index(arr, target):
        return np.argmin(np.abs(np.array(arr) - target))

    goal_index = find_nearest_index(projected_profit, 1_000_000)
    opt_index = find_nearest_index(projected_profit, 5_000_000)

    st.subheader("📊 Total STB Tokens (Including Rewards)")
    fig_tokens = go.Figure()
    fig_tokens.add_trace(go.Scatter(x=months, y=total_tokens_over_time,
        mode='lines+markers', name='Total STB Tokens',
        hovertemplate='Month %{x}<br>Tokens: %{y:,.0f}<extra></extra>'))
    fig_tokens.update_layout(xaxis_title="Month", yaxis_title="Tokens", hovermode='x unified')
    st.plotly_chart(fig_tokens, use_container_width=True)

    st.subheader("💰 Projected Profit Based on Expected STB Price")
    fig_profit = go.Figure()
    fig_profit.add_trace(go.Scatter(x=months, y=projected_profit,
        mode='lines+markers', name='Projected Profit',
        hovertemplate='Month %{x}<br>Profit: $%{y:,.0f}<extra></extra>'))
    fig_profit.add_trace(go.Scatter(x=[months[goal_index]], y=[projected_profit[goal_index]],
        mode='markers+text', name='Goal $1M', text=["$1M Goal"], textposition="top right",
        marker=dict(size=10, color="orange")))
    fig_profit.add_trace(go.Scatter(x=[months[opt_index]], y=[projected_profit[opt_index]],
        mode='markers+text', name='Optimal $5M', text=["$5M Opt"], textposition="bottom left",
        marker=dict(size=10, color="green")))
    fig_profit.update_layout(xaxis_title="Month", yaxis_title="Profit ($)", hovermode='x unified')
    st.plotly_chart(fig_profit, use_container_width=True)

    st.subheader("📈 Expected STB Price Growth")
    fig_price = go.Figure()
    fig_price.add_trace(go.Scatter(x=months, y=expected_price,
        mode='lines+markers', name='Expected Price',
        hovertemplate='Month %{x}<br>Price: $%{y:.2f}<extra></extra>'))
    fig_price.update_layout(xaxis_title="Month", yaxis_title="STB Price ($)", hovermode='x unified')
    st.plotly_chart(fig_price, use_container_width=True)

    estimated_token_reward = total_tokens_over_time[-1] - total_tokens
    estimated_total_tokens = total_tokens_over_time[-1]

    kpis = [
        ("Main Allocation Tokens", main_tokens),
        ("Secondary Allocation Tokens", secondary_tokens),
        ("Total Tokens Held", total_tokens),
        ("TGE Release % (Main)", "5%"),
        ("TGE Release % (Secondary)", "10%"),
        ("Main Lock Period (Months)", 6),
        ("Main Vesting Period (Months)", 8),
        ("Secondary Vesting Period (Months)", 6),
        ("Staking APY (Estimated)", f"{staking_apy}%"),
        ("Locking APY (Estimated)", f"{locking_apy}%"),
        ("Locking Pool Share (%)", lock_pool_share),
        ("Staking Pool Share (%)", stake_pool_share),
        ("Transaction Fee Rate (%)", fee_rate * 100),
        ("Initial Token Price (USD)", initial_token_price),
        ("Target Sell Price (USD)", target_price),
        ("Max Projected Price (USD)", K_price),
        ("Estimated STB Price (Month 24)", f"${expected_price[-1]:.2f}"),
        ("Estimated Additional Tokens (1Y)", int(estimated_token_reward)),
        ("Estimated Total Tokens (1Y)", int(estimated_total_tokens)),
        ("Estimated Profit at $0.04", int(estimated_total_tokens * 0.04)),
        ("Estimated Profit at $2.00", int(estimated_total_tokens * 2)),
        ("Estimated Profit at $10.00", int(estimated_total_tokens * 10)),
        ("Minimum Profit Goal (USD)", 1_000_000),
        ("Optimal Profit Goal (USD)", 5_000_000),
        ("Target Profit for 2026 (USD)", 900_000),
        ("Expected Altcoin Season Peak", "Summer 2026"),
        ("Secondary Sale Opportunity", "2030 Market Cycle"),
        ("Post-2026 Locking Plan (Months)", 30),
        ("Can Sell Staking Rewards Immediately?", "Yes"),
        ("Can Unstake Anytime?", "Yes"),
        ("Cash Flow Requirements Before 2026?", "No"),
    ]
    st.subheader("📌 Key Performance Indicators (KPI)")
    st.dataframe(pd.DataFrame(kpis, columns=["KPI", "Value"]))

# === Section 2: Token Vesting Distribution ===
elif page == "📆 Altcoin Season Timeline":
    st.title("📊 Strategic Token Distribution Timeline with Reward Overlay")

    # --- User Inputs ---
    altseason_start_month = st.sidebar.slider("Month Altcoin Season Starts", 1, 24, 18)
    altseason_duration = st.sidebar.slider("Duration of Altcoin Season (Months)", 1, 6, 4)

    # --- Token Setup ---
    main_tokens = 457143
    secondary_tokens = 45834
    total_tokens = main_tokens + secondary_tokens
    initial_token_price = 0.04

    months_range = 24
    months = np.arange(1, months_range + 1)
    start_date = datetime(2025, 5, 1)
    dates = [start_date + timedelta(days=30 * i) for i in range(months_range)]

    # --- Vesting Simulation ---
    vested_tokens = []
    for month in months:
        if month <= 6:
            mv = main_tokens * 0.05
            sv = secondary_tokens * (0.10 + (0.90 * month / 6))
        else:
            mv = main_tokens * 0.05 + ((month - 6) / 8) * (main_tokens * 0.95)
            sv = secondary_tokens
        vested_tokens.append(mv + sv)

    # --- Distribution & Rewards ---
    locked_tokens, staked_tokens, reward_tokens, top_line = [], [], [], []
    cumulative_rewards = 0

    for i, month in enumerate(months):
        vested = vested_tokens[i]

        # Locking vs Staking Dynamics
        if month < altseason_start_month:
            lock = vested
            stake = total_tokens - lock
        elif altseason_start_month <= month < altseason_start_month + altseason_duration:
            lock = 0
            stake = vested
        else:
            lock = vested
            stake = 0

        # Simulated reward growth
        monthly_reward_tokens = 10000 + i * 5000
        cumulative_rewards += monthly_reward_tokens

        locked_tokens.append(lock)
        staked_tokens.append(stake)
        reward_tokens.append(cumulative_rewards)
        top_line.append((lock if lock > 0 else stake) + cumulative_rewards)

    # --- Create Chart ---
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=dates, y=locked_tokens,
        mode='lines+markers',
        name='🔒 Locked Tokens',
        line=dict(color='orange'),
        hovertemplate='%{x|%b %y}<br>🔒 Locked: %{y:,.0f} STB ($%{customdata:,.0f})<extra></extra>',
        customdata=np.array(locked_tokens) * initial_token_price
    ))

    fig.add_trace(go.Scatter(
        x=dates, y=staked_tokens,
        mode='lines+markers',
        name='📥 Staked Tokens (vested)',
        line=dict(color='goldenrod'),
        hovertemplate='%{x|%b %y}<br>📥 Staked: %{y:,.0f} STB ($%{customdata:,.0f})<extra></extra>',
        customdata=np.array(staked_tokens) * initial_token_price
    ))

    fig.add_trace(go.Scatter(
        x=dates, y=top_line,
        mode='lines+markers',
        name='📈 Cumulative Rewards (on top)',
        line=dict(color='deeppink'),
        hovertemplate='%{x|%b %y}<br>📈 Total: %{y:,.0f} STB ($%{customdata:,.0f})<extra></extra>',
        customdata=np.array(top_line) * initial_token_price
    ))

    fig.update_layout(
        title="📈 Strategic Token Distribution Timeline with Reward Overlay",
        xaxis_title="Month",
        yaxis_title="STB Tokens",
        hovermode='x unified'
    )

    st.plotly_chart(fig, use_container_width=True)

