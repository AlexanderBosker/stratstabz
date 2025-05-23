import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

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
total_tokens_over_time = []

for month in months:
    volume = volume_start + (volume_end - volume_start) * (month / 24)
    monthly_fee = volume * fee_rate * 30
    lock_pool_usd = monthly_fee * 0.14 * (lock_pool_share / 100)
    stake_pool_usd = monthly_fee * 0.86 * (stake_pool_share / 100)
    reward = lock_pool_usd + stake_pool_usd
    reward_usd.append(reward)

reward_cumulative = np.cumsum(reward_usd)
reward_tokens = [usd / initial_token_price for usd in reward_usd]
reward_tokens_cum = np.cumsum(reward_tokens)
total_tokens_over_time = [total_tokens + r for r in reward_tokens_cum]

# --- KPI Table ---
kpis = [
    {"KPI Name": "Main Allocation Tokens", "Value": main_tokens},
    {"KPI Name": "Secondary Allocation Tokens", "Value": secondary_tokens},
    {"KPI Name": "Total Tokens Held", "Value": total_tokens},
    {"KPI Name": "TGE Release % (Main)", "Value": "5%"},
    {"KPI Name": "TGE Release % (Secondary)", "Value": "10%"},
    {"KPI Name": "Main Lock Period (Months)", "Value": 6},
    {"KPI Name": "Main Vesting Period (Months)", "Value": 8},
    {"KPI Name": "Secondary Vesting Period (Months)", "Value": 6},
    {"KPI Name": "Staking APY (Estimated)", "Value": f"{staking_apy}%"},
    {"KPI Name": "Locking APY (Estimated)", "Value": f"{locking_apy}%"},
    {"KPI Name": "Locking Pool Share (%)", "Value": lock_pool_share},
    {"KPI Name": "Staking Pool Share (%)", "Value": stake_pool_share},
    {"KPI Name": "Transaction Fee Rate (%)", "Value": fee_rate * 100},
    {"KPI Name": "Initial DEX Volume (USD/day)", "Value": int(volume_start)},
    {"KPI Name": "Expected DEX Volume in 1 Year (USD/day)", "Value": int(volume_end)},
    {"KPI Name": "Initial Token Price (USD)", "Value": initial_token_price},
    {"KPI Name": "Target Sell Price (USD)", "Value": target_price},
    {"KPI Name": "Upper Sell Price Potential (USD)", "Value": 10.0},
    {"KPI Name": "Minimum Profit Goal (USD)", "Value": 1_000_000},
    {"KPI Name": "Optimal Profit Goal (USD)", "Value": 5_000_000},
    {"KPI Name": "Target Profit for 2026 (USD)", "Value": 900_000},
    {"KPI Name": "Expected Altcoin Season Peak", "Value": "Summer 2026"},
    {"KPI Name": "Secondary Sale Opportunity", "Value": "2030 Market Cycle"},
    {"KPI Name": "Post-2026 Locking Plan (Months)", "Value": 30},
    {"KPI Name": "Estimated STB Tokens in 1 Year", "Value": int(total_tokens_over_time[-1])},
    {"KPI Name": "Can Sell Staking Rewards Immediately?", "Value": "Yes"},
    {"KPI Name": "Can Unstake Anytime?", "Value": "Yes"},
    {"KPI Name": "Cash Flow Requirements Before 2026?", "Value": "No"},
]
st.subheader("📌 Key Performance Indicators")
st.dataframe(pd.DataFrame(kpis))

# --- Token Growth Graph ---
st.subheader("📊 Estimated STB Token Accumulation Over Time")
fig1, ax1 = plt.subplots()
ax1.plot(months, total_tokens_over_time, label="Total Tokens Accumulated", color='blue')
ax1.set_xlabel("Month")
ax1.set_ylabel("Tokens")
ax1.set_title("Total STB Tokens (Including Rewards)")
st.pyplot(fig1)

# --- Profit Potential Graph ---
st.subheader("💰 Projected Profit Based on STB Price")
token_range = np.linspace(0.01, 12, 300)
profits = (total_tokens_over_time[-1]) * token_range
fig2, ax2 = plt.subplots()
ax2.plot(token_range, profits, label="Projected Profit ($)")
ax2.axhline(1_000_000, color='orange', linestyle='--', label="Min Goal ($1M)")
ax2.axhline(5_000_000, color='green', linestyle='--', label="Optimal Goal ($5M)")
ax2.set_xlabel("STB Token Price ($)")
ax2.set_ylabel("Profit ($)")
ax2.set_title("Profit vs. STB Price")
ax2.legend()
st.pyplot(fig2)

# --- Altcoin Cycle Timeline ---
st.subheader("🕒 Strategic Altcoin Cycle Timeline")
timeline_data = pd.DataFrame({
    "Event": ["TGE", "Main Vesting Start", "Target Sell Window", "2030 Cycle Prep"],
    "Month": [0, 6, 18, 60],
    "Description": ["TGE Complete", "Vesting Begins", "Peak Sale Strategy", "Next Cycle Opportunity"]
})
st.dataframe(timeline_data)

st.markdown("""
**🗓 Recommendations:**
- Accumulate until Summer 2026 (expected alt season)
- Prepare sell strategy for STB at ≥ $2
- Re-lock remaining tokens post-2026 for 2030 run
""")
