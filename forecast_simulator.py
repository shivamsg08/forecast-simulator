import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# ---- Simulate Replenishment Logic ---- #
def calculate_replenishment(forecast, lead_time=2, min_stock=20):
    replenishment_orders = []
    current_stock = 100  # initial stock
    
    for day_forecast in forecast:
        if current_stock - day_forecast < min_stock:
            order_qty = (min_stock + day_forecast + lead_time * np.mean(forecast)) - current_stock
            replenishment_orders.append(order_qty)
            current_stock += order_qty
        else:
            replenishment_orders.append(0)
        
        current_stock -= day_forecast
        
    return replenishment_orders

# ---- Streamlit UI ---- #
st.title("📦 Daily Forecast & Replenishment Simulator")

# User Input
num_days = st.slider("Number of Days to Simulate", 7, 30, 14)

# Default Forecast Values
default_forecast = [50 + np.random.randint(-10, 10) for _ in range(num_days)]
forecast = []

st.subheader("🔢 Adjust Forecast per Day")
for i in range(num_days):
    val = st.number_input(f"Day {i+1} Forecast", min_value=0, value=int(default_forecast[i]), key=f"forecast_{i}")
    forecast.append(val)

# Replenishment Calculation
replenishment = calculate_replenishment(forecast)

# ---- Display Tables ---- #
df = pd.DataFrame({
    "Day": list(range(1, num_days + 1)),
    "Forecast": forecast,
    "Replenishment Order": replenishment
})

st.subheader("📊 Forecast vs Replenishment Table")
st.dataframe(df)

# ---- Plotting ---- #
st.subheader("📈 Forecast and Replenishment Trend")

fig = px.line(df, x="Day", y=["Forecast", "Replenishment Order"], markers=True)
st.plotly_chart(fig, use_container_width=True)
