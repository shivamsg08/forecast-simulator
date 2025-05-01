# Install these first in your environment:
# pip install streamlit pandas plotly numpy

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# --------------------------------
# 1. Setup Simulation Parameters
# --------------------------------
LEAD_TIME_DAYS = 2
SAFETY_STOCK_DAYS = 3
ORDER_CYCLE_DAYS = 1  # daily replenishment
MOQ = 10  # Minimum Order Quantity
ROUNDING_MULTIPLE = 5  # Round to nearest 5 units

# --------------------------------
# 2. Generate Sample Forecast & Stock Data
# --------------------------------
def load_sample_data():
    dates = pd.date_range(start=pd.Timestamp.today().normalize(), periods=14)
    base_forecast = np.random.randint(80, 120, size=14)
    df = pd.DataFrame({
        'Date': dates,
        'Base_Forecast': base_forecast,
        'Adjusted_Forecast': base_forecast.copy(),
    })
    return df

# --------------------------------
# 3. Replenishment Engine
# --------------------------------
def simulate_replenishment(df, opening_stock):
    replen_list = []
    stock_list = []
    current_stock = opening_stock

    for i in range(len(df)):
        day_forecast = df.loc[i, 'Adjusted_Forecast']
        safety_stock = df['Adjusted_Forecast'].rolling(SAFETY_STOCK_DAYS, min_periods=1).mean().iloc[i] * SAFETY_STOCK_DAYS

        # Projected Stock after sales
        projected_stock = current_stock - day_forecast
        stock_list.append(projected_stock)

        # Replenishment logic
        if i % ORDER_CYCLE_DAYS == 0:
            target_stock = (LEAD_TIME_DAYS * day_forecast) + safety_stock
            replen_qty = max(0, target_stock - projected_stock)

            # Apply MOQ and rounding rules
            if replen_qty > 0:
                replen_qty = max(MOQ, ROUNDING_MULTIPLE * round(replen_qty / ROUNDING_MULTIPLE))
            else:
                replen_qty = 0
        else:
            replen_qty = 0

        replen_list.append(replen_qty)
        current_stock = projected_stock + replen_qty  # After receiving replen

    df['Replenishment_Qty'] = replen_list
    df['Projected_Stock'] = stock_list
    return df

# --------------------------------
# 4. Streamlit App
# --------------------------------
def main():
    st.title("📦 Forecast-Replenishment Impact Simulator")

    # Load data
    df = load_sample_data()
    opening_stock = st.number_input("Enter opening stock (units)", min_value=100, max_value=1000, value=500)

    st.subheader("🔧 Adjust Daily Forecast")
    for i in range(len(df)):
        df.loc[i, 'Adjusted_Forecast'] = st.slider(
            label=f"{df.loc[i, 'Date'].strftime('%Y-%m-%d')}",
            min_value=int(df.loc[i, 'Base_Forecast'] * 0.5),
            max_value=int(df.loc[i, 'Base_Forecast'] * 1.5),
            value=int(df.loc[i, 'Base_Forecast']),
            step=5
        )

    # Simulate
    df_result = simulate_replenishment(df, opening_stock)

    # --------------------------
    # Charts
    # --------------------------
    st.subheader("📊 Forecast Comparison")
    df_chart1 = df_result.melt(id_vars='Date', value_vars=['Base_Forecast', 'Adjusted_Forecast'], var_name='Type', value_name='Forecast')
    fig1 = px.line(df_chart1, x='Date', y='Forecast', color='Type', markers=True)
    st.plotly_chart(fig1)

    st.subheader("📦 Replenishment Plan")
    fig2 = px.bar(df_result, x='Date', y='Replenishment_Qty', labels={'Replenishment_Qty': 'Replenishment Qty'})
    fig2.add_scatter(x=df_result['Date'], y=df_result['Projected_Stock'], mode='lines+markers', name='Projected Stock Level')
    st.plotly_chart(fig2)

    st.subheader("📄 Detailed Plan")
    st.dataframe(df_result.style.format({
        "Base_Forecast": "{:.0f}", 
        "Adjusted_Forecast": "{:.0f}", 
        "Replenishment_Qty": "{:.0f}", 
        "Projected_Stock": "{:.0f}"
    }))

if __name__ == "__main__":
    main()
