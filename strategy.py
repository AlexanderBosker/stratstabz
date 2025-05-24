import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta

# === Utility Function ===
def generate_token_distribution_chart():
    main_tokens = 457143
    secondary_tokens = 45834
    initial_token_price = 0.04
    months_range = 24
    altseason_start = 18
    altseason_duration = 4

    start_date = datetime.today()
    months = np.arange(1, months_range + 1)
    date_labels = [(start_date + timedelta(days=30 * i)).strftime("%b %y") for i in range(months_range)]

    K_price = 2.5
    r_growth = 0.3
    t_midpoint = 12
    expected_price = K_price / (1 + np.exp(-r_growth * (months - t_midpoint)))

    locked_tokens = []
    staked_tokens = []
    cumulative_rewards = []
    reward_value_usd = []

    cum_reward = 0
    goal_usd = 1_000_000
    goal_fulfilled = False

    for month in months:
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
        monthly_reward_tokens = 4000 + (month * 300)
        cum_reward += monthly_reward_tokens
        reward_value_usd.append(monthly_reward_tokens * expected_price[month - 1])
        cumulative_rewards.append(cum_reward)

        total_with_rewards = vested_total + cum_reward

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

    top_overlay = [max(l, s) + r for l, s, r in zip(locked_tokens, staked_tokens, cumulative_rewards)]

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=date_labels, y=locked_tokens, name="🔒 Locked Tokens", mode="lines+markers",
                             hovertemplate="Month %{x}<br>Locked: %{y:,.0f} STB"))
    fig.add_trace(go.Scatter(x=date_labels, y=staked_tokens, name="📥 Staked Tokens (vested)", mode="lines+markers",
                             hovertemplate="Month %{x}<br>Staked: %{y:,.0f} STB"))
    fig.add_trace(go.Scatter(x=date_labels, y=top_overlay, name="💰 Cumulative Rewards (on top)", mode="lines+markers",
                             hovertemplate="Month %{x}<br>Total: %{y:,.0f} STB"))

    fig.update_layout(
        title="📈 Strategic Token Distribution Timeline with Reward Overlay",
        xaxis_title="Month",
        yaxis_title="Token Count",
        hovermode='x unified',
        legend=dict(orientation="h", y=-0.2),
        margin=dict(t=60, b=80)
    )
    return fig

# === Streamlit App ===
st.set_page_config(layout="wide")
page = st.sidebar.radio("📁 Select Dashboard Section", [
    "📆 Altcoin Season Timeline"
])

# === Section: Altcoin Season Timeline ===
if page == "📆 Altcoin Season Timeline":
    st.title("📆 STB Strategy Timeline")

    altseason_start_month = st.sidebar.slider("Month Altcoin Season Starts", 1, 24, 18)
    altseason_duration = st.sidebar.slider("Duration of Altcoin Season (Months)", 1, 6, 4)

    start_date = datetime.today()
    months_range = 24
    dates = [start_date + timedelta(days=30 * i) for i in range(months_range)]

    lock_period = []
    altseason_period = []
    post_season = []

    for i in range(months_range):
        if i < altseason_start_month:
            lock_period.append(1)
            altseason_period.append(0)
            post_season.append(0)
        elif altseason_start_month <= i < altseason_start_month + altseason_duration:
            lock_period.append(0)
            altseason_period.append(1)
            post_season.append(0)
        else:
            lock_period.append(0)
            altseason_period.append(0)
            post_season.append(1)

    timeline_df = pd.DataFrame({
        "Date": dates,
        "Locking Phase": lock_period,
        "Altcoin Season": altseason_period,
        "Post Season": post_season
    })

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=timeline_df["Date"], y=timeline_df["Locking Phase"], name="Locking", stackgroup='one', mode='none'))
    fig.add_trace(go.Scatter(x=timeline_df["Date"], y=timeline_df["Altcoin Season"], name="Altcoin Season", stackgroup='one', mode='none'))
    fig.add_trace(go.Scatter(x=timeline_df["Date"], y=timeline_df["Post Season"], name="Post Season", stackgroup='one', mode='none'))

    fig.update_layout(
        title="📆 STB Strategy Timeline (Lock → Altseason → Post)",
        xaxis_title="Date",
        yaxis_title="Phase",
        yaxis=dict(showticklabels=False),
        hovermode='x unified'
    )

    st.plotly_chart(fig, use_container_width=True)

    # Add strategic token distribution timeline chart
    st.subheader("📊 Strategic Token Distribution Timeline With Reward Overlay")
    fig_distribution = generate_token_distribution_chart()
    st.plotly_chart(fig_distribution, use_container_width=True)
