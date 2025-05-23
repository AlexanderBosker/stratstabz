import streamlit as st
import pandas as pd
import numpy as np
import datetime
import matplotlib.pyplot as plt

# ---- Sidebar Inputs ----
st.set_page_config(layout="wide")
st.title("📈 STB Investment Strategy Dashboard")

st.sidebar.header("🔧 Adjust Assumptions")

# Token Allocation
main_tokens = 457143
secondary_tokens = 45834
total_tokens = main_tokens + secondary_tokens

# User Adjustables
initial_price = st.sidebar.number_input("Initial Token Price ($)", 0.01, 5.0, value=0.04)
target_price = st.sidebar.number_input("Target Sell Price ($)", 0.1, 20.0, value=2.0)
lock_pool_share = st.sidebar.slider("Lock Pool Share (%)", 0.1, 5.0, value=0.5)
staking_apy = st.sidebar.slider("Staking APY (%)", 0, 200, value=50)
locking_apy = st.sidebar.slider("Locking APY (%)", 0, 300, value=100)
volume_start = st.sidebar.number_input("Start DEX Volume ($M/day)", 10, 1000, value=100) * 1_000_000
volume_end = st.sidebar.number_input("End-Year DEX Volume ($M/day)", 10, 1000, value=300) * 1_000_000

# Constants
fee_rate = 0.001  # 0.1%
vesting_start_main = 7
vesting_period_main = 8
vesting_period_secondary = 6

# ---- Simulation ----
months = np.arange(1, 25)
locked, vested, staked, rewards = [], [], [], []

for month in months:
    locked_amt = 0
    vested_amt = 0
    staked_amt = 0
    reward_amt = 0

    # Main Vesting
    if month <= 6:
        locked_amt = main_tokens * 0.95
        vested_amt += secondary_tokens * 0.10 + (secondary_tokens * 0.90) * (month / vesting_period_secondary)
    elif 7 <= month <= 14:
        locked_amt = main_tokens * 0.95 - ((month - 6) * (main_tokens * 0.95) / vesting_period_main)
        vested_amt += (main_tokens * 0.95) * ((month - 6) / vesting_period_main)
        vested_amt += secondary_tokens
    else:
        vested_amt = main_tokens * 0.95 + secondary_tokens

    # Staked estimate = All vested tokens
    staked_amt = vested_amt

    # Volume ramp
    vol = volume_start + ((volume_end - volume_start) / 24) * month
    total_fee = vol * fee_rate * 30  # monthly

    lock_reward_pool = total_fee * 0.14
    stake_reward_pool = total_fee * 0.86 / 25  # assume 1/25th in stb staking pool

    reward_amt = (lock_reward_pool * (lock_pool_share / 100)) + stake_reward_pool

    locked.append(locked_amt)
    vested.append(vested_amt)
    staked.append(staked_amt)
    rewards.append(reward_amt)

df = pd.DataFrame({
    "Month": months,
    "Locked": locked,
    "Vested": vested,
    "Staked": staked,
    "Monthly Rewards ($)": rewards,
    "Cumulative Rewards ($)": np.cumsum(rewards)
})

# ---- KPI Display ----
st.subheader("📌 Key Performance Indicators")
kpis = {
    "Total Tokens": total_tokens,
    "Initial Token Price ($)": initial_price,
    "Target Sell Price ($)": target_price,
    "Lock Pool Share (%)": lock_pool_share,
    "Staking APY (%)": staking_apy,
    "Locking APY (%)": locking_apy,
    "Start Volume ($/day)": volume_start,
    "End Volume ($/day)": volume_end,
    "Altcoin Season Target": "Summer 2026",
    "Next Sale Cycle": "2030"
}
st.dataframe(pd.DataFrame(kpis.items(), columns=["KPI", "Value"]))

# ---- Charts ----
st.subheader("📊 Token Distribution Over Time")
fig1, ax1 = plt.subplots()
ax1.plot(df["Month"], df["Locked"], label="Locked")
ax1.plot(df["Month"], df["Vested"], label="Vested")
ax1.plot(df["Month"], df["Staked"], label="Staked")
ax1.set_xlabel("Month")
ax1.set_ylabel("Token Amount")
ax1.set_title("Token Lifecycle")
ax1.legend()
st.pyplot(fig1)

st.subheader("💸 Reward Accumulation")
fig2, ax2 = plt.subplots()
ax2.plot(df["Month"], df["Monthly Rewards ($)"], label="Monthly Rewards")
ax2.plot(df["Month"], df["Cumulative Rewards ($)"], label="Cumulative Rewards", linestyle="--")
ax2.set_xlabel("Month")
ax2.set_ylabel("Rewards ($)")
ax2.set_title("Reward Growth from Platform Fees")
ax2.legend()
st.pyplot(fig2)

# ---- Task Manager ----
st.subheader("📅 Key Milestones & Task Tracker")
tasks = [
    {"Task": "🗓 Daily: Claim staking & locking rewards", "Due": "Daily"},
    {"Task": "🔁 Reinvest unlocked rewards if STB < $2", "Due": "Monthly"},
    {"Task": "🔓 Month 7: Begin receiving vested tokens (Main)", "Due": "Month 7"},
    {"Task": "📊 Month 24: Lock remaining tokens post-2026", "Due": "Month 24"},
    {"Task": "💰 Summer 2026: Liquidate up to $1M at STB > $2", "Due": "Q2-Q3 2026"},
    {"Task": "🔒 Post-2026: Lock remaining tokens for 2030", "Due": "Late 2026"}
]
st.table(pd.DataFrame(tasks))
