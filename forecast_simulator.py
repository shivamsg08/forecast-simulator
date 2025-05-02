# Install first:
# pip install streamlit pandas plotly numpy

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objs as go

# ---------------------------
# 1. Simulation Parameters
# ---------------------------
LEAD_TIME_DAYS = 2
SAFETY_STOCK_DAYS = 3
ORDER_CYCLE_DAYS = 1
MOQ = 10
ROUNDING_MULTIPLE = 5

# ---------------------------
# 2. Sample Forecast & Stock Data
# ---------------------------
@st.cache_data
def load_sample_data():
    dates = pd.date_range(start=pd.Timestamp.today().normalize(), periods=14)
    base_forecast = np.random.randint(80, 120, size=14)
    df = pd.DataFrame({
        'Date': dates,
        'Base_Forecast': base_forecast,
        'Adjusted_Forecast': base_forecast.copy(),
    })
    return df

# ---------------------------
# 3. Replenishment Engine
# ---------------------------
def simulate_replenishment(df, opening_stock):
    replen_list = []
    stock_list = []
    current_stock = opening_stock

    for i in range(len(df)):
        day_forecast = df.loc[i, 'Adjusted_Forecast']
        safety_stock = df['Adjusted_Forecast'].rolling(SAFETY_STOCK_DAYS, min_periods=1).mean().iloc[i] * SAFETY_STOCK_DAYS

        projected_stock = current_stock - day_forecast
        stock_list.append(projected_stock)

        if i % ORDER_CYCLE_DAYS == 0:
            target_stock = (LEAD_TIME_DAYS * day_forecast) + safety_stock
            replen_qty = max(0, target_stock - projected_stock)

            if replen_qty > 0:
                replen_qty = max(MOQ, ROUNDING_MULTIPLE * round(replen_qty / ROUNDING_MULTIPLE))
            else:
                replen_qty = 0
        else:
            replen_qty = 0

        replen_list.append(replen_qty)
        current_stock = projected_stock + replen_qty

    df['Replenishment_Qty'] = replen_list
    df['Projected_Stock'] = stock_list
    return df

# ---------------------------
# 4. Streamlit App
# ---------------------------
def main():
    st.title("📦 Forecast-Replenishment Impact Simulator")

    # Session state to preserve user-adjustments
    if 'df' not in st.session_state:
        st.session_state.df = load_sample_data()

    df = st.session_state.df

    # Opening Stock input
    opening_stock = st.number_input("Enter opening stock (units)", min_value=100, max_value=1000, value=500)

    # Reset button
    if st.button("🔄 Reset Adjusted Forecast to Base Forecast"):
        df['Adjusted_Forecast'] = df['Base_Forecast']

    # Adjust Forecast Sliders
    st.subheader("🔧 Adjust Daily Forecast (Adjusted Forecast)")
    for i in range(len(df)):
        adjusted_value = st.slider(
            label=f"{df.loc[i, 'Date'].strftime('%Y-%m-%d')}",
            min_value=int(df.loc[i, 'Base_Forecast'] * 0.5),
            max_value=int(df.loc[i, 'Base_Forecast'] * 2.0),  # wider range 0.5x to 2x
            value=int(df.loc[i, 'Adjusted_Forecast']),
            step=5,
            key=f"slider_{i}"
        )
        df.loc[i, 'Adjusted_Forecast'] = adjusted_value

    # Simulate
    df_result = simulate_replenishment(df.copy(), opening_stock)

    # --------------------------
    # Charts
    # --------------------------
    st.subheader("📊 Forecast Comparison")
    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(x=df_result['Date'], y=df_result['Base_Forecast'], name="Base Forecast", mode='lines+markers'))
    fig1.add_trace(go.Scatter(x=df_result['Date'], y=df_result['Adjusted_Forecast'], name="Adjusted Forecast", mode='lines+markers'))
    st.plotly_chart(fig1, use_container_width=True)

    st.subheader("📦 Replenishment Plan")
    fig2 = go.Figure()
    fig2.add_trace(go.Bar(x=df_result['Date'], y=df_result['Replenishment_Qty'], name="Replenishment Qty"))
    fig2.add_trace(go.Scatter(x=df_result['Date'], y=df_result['Projected_Stock'], name="Projected Stock Level", mode='lines+markers'))
    st.plotly_chart(fig2, use_container_width=True)

    st.subheader("📄 Detailed Plan")
    st.dataframe(df_result.style.format({
        "Base_Forecast": "{:.0f}",
        "Adjusted_Forecast": "{:.0f}",
        "Replenishment_Qty": "{:.0f}",
        "Projected_Stock": "{:.0f}"
    }))

if __name__ == "__main__":
    main()
