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

# === Section 3: Altcoin Season Timeline ===
if page == "📆 Altcoin Season Timeline":
    st.title("📆 Strategic Token Distribution Timeline")

    # Token and Strategy Settings
    main_tokens = 457143
    secondary_tokens = 45834
    initial_token_price = 0.04
    months_range = 24
    altseason_start = 18
    altseason_duration = 4

    start_date = datetime.today()
    dates = [start_date + timedelta(days=30 * i) for i in range(months_range)]
    months = np.arange(1, months_range + 1)

    # Expected Token Price Forecast (Logistic Growth)
    K_price = 2.5
    r_growth = 0.3
    t_midpoint = 12
    expected_price = K_price / (1 + np.exp(-r_growth * (months - t_midpoint)))

    # Token Generation and Distribution Simulation
    locked_tokens = []
    staked_tokens = []
    generated_token_rewards = []
    overlay_rewards = []
    reward_value_usd = []

    cumulative_rewards = 0
    goal_usd = 1_000_000
    goal_fulfilled = False

    for month in months:
        # Vesting logic
        if month <= 6:
            mv = 0
            sv = secondary_tokens * (0.10 + (0.90 * month / 6))
        elif 7 <= month <= 14:
            mv = ((month - 6) / 8) * (main_tokens * 0.95)
            sv = secondary_tokens
        else:
            mv = main_tokens * 0.95
            sv = secondary_tokens
        vested_total = main_tokens * 0.05 + mv + sv

        # Monthly rewards
        monthly_reward_tokens = 4000 + (month * 300)
        cumulative_rewards += monthly_reward_tokens
        reward_value_usd.append(monthly_reward_tokens * expected_price[month - 1])
        generated_token_rewards.append(cumulative_rewards)

        total_available = vested_total
        total_with_rewards = vested_total + cumulative_rewards

        # Token allocation logic across time
        if month < altseason_start:
            locked = total_with_rewards
            staked = 0
        elif altseason_start <= month < altseason_start + altseason_duration:
            if not goal_fulfilled and total_with_rewards * expected_price[month - 1] >= goal_usd:
                goal_fulfilled = True
                staked = total_with_rewards - (goal_usd / expected_price[month - 1])
                locked = 0
            else:
                staked = total_with_rewards
                locked = 0
        else:
            locked = total_with_rewards
            staked = 0

        locked_tokens.append(locked)
        staked_tokens.append(staked)
        overlay_rewards.append(cumulative_rewards + max(locked, staked))

    date_labels = [d.strftime("%b %y") for d in dates]

    # Plotly Multi-Line Chart
    st.subheader("📈 Strategic Token Distribution Timeline with Reward Overlay")
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=date_labels, y=locked_tokens, name="🔒 Locked Tokens",
        mode="lines+markers",
        hovertemplate="Month %{x}<br>Locked: %{y:,.0f} STB"
    ))

    fig.add_trace(go.Scatter(
        x=date_labels, y=staked_tokens, name="📥 Staked Tokens (vested)",
        mode="lines+markers",
        hovertemplate="Month %{x}<br>Staked: %{y:,.0f} STB"
    ))

    fig.add_trace(go.Scatter(
        x=date_labels, y=overlay_rewards, name="💰 Cumulative Rewards (on top)",
        mode="lines+markers",
        hovertemplate="Month %{x}<br>Total: %{y:,.0f} STB"
    ))

    fig.update_layout(
        title="📊 Token Distribution & Rewards Forecast with Altcoin Strategy",
        xaxis_title="Month",
        yaxis_title="Token Count",
        hovermode='x unified',
        legend=dict(orientation="h", y=-0.2),
        margin=dict(t=60, b=80)
    )

    st.plotly_chart(fig, use_container_width=True)
