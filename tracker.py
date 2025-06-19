# feeding_tracker.py

import streamlit as st
import pandas as pd
from datetime import datetime
import os
import uuid

CSV_FILE = "feeding_log.csv"

st.set_page_config(page_title="Toddler Feeding Tracker", layout="centered")
st.title("🥣 Toddler Feeding Tracker")

# --- Sidebar ---
st.sidebar.header("Add New Meal Entry")

with st.sidebar.form("meal_form"):
    meal_id = str(uuid.uuid4())
    meal_date = st.date_input("Meal Date", value = datetime.today())
    meal_time = st.time_input("Meal time", value=datetime.now().time())
    meal_datetime = datetime.combine(meal_date, meal_time)
    meal_type = st.selectbox("Meal type", ["Breakfast", "Lunch", "Snack", "Dinner"])
    foods_offered = st.text_input("Foods offered (comma-separated)", help="e.g., banana, rice, yogurt")
    st.markdown("**Amount Offered**")
    amount_offered_grams = st.number_input("Approx. weight (grams)", min_value=0, max_value=500, step=10)
    quantity_unit = st.selectbox(
        "Quantity unit",
        ["", "spoonful", "piece", "slice", "bite", "bowl", "handful", "custom"]
    )
    quantity_value = st.number_input("Quantity count (optional)", min_value=0.0, step=0.5)
    # Combine into one readable string (optional)
    if quantity_value and quantity_unit:
        quantity_offered_str = f"{quantity_value} {quantity_unit}{'s' if quantity_value > 1 else ''}"
    else:
        quantity_offered_str = ""

    amount_eaten = st.selectbox("Amount eaten", ["All", "Half", "Few bites", "None"])
    used_distraction = st.checkbox("Used distraction (cartoon, toy, etc.)")
    notes = st.text_area("Notes (optional)")

    submitted = st.form_submit_button("Save Meal")

    # clear history button
    st.sidebar.markdown("---")
    if st.sidebar.button("🗑️ Clear All Meal Data"):
        if os.path.exists(CSV_FILE):
            os.remove(CSV_FILE)
            st.sidebar.success("Meal history cleared!")
        else:
            st.sidebar.info("No meal data to delete.")

    if submitted:
        new_entry = {
            "meal_id": meal_id,
            "datetime": meal_datetime.strftime("%Y-%m-%d %H:%M:%S"),
            "meal_type": meal_type,
            "foods_offered": foods_offered.strip().lower(),
            "amount_offered_g": amount_offered_grams,
            "quantity_offered": quantity_offered_str,
            "amount_eaten_estimate": amount_eaten.lower(),
            "used_distraction": used_distraction,
            "notes": notes
        }

        df = pd.DataFrame([new_entry])
        if not os.path.isfile(CSV_FILE):
            df.to_csv(CSV_FILE, index=False)
        else:
            df.to_csv(CSV_FILE, mode='a', header=False, index=False)

        st.sidebar.success("Meal saved!")



# --- Main Page ---
st.header("📊 Feeding Insights")

if os.path.exists(CSV_FILE):
    df = pd.read_csv(CSV_FILE)

    # Summary Stats
    st.subheader("Quick Stats")
    st.write(f"🗓️ Total meals logged: {len(df)}")
    st.write(f"🍽️ Meals per type:\n{df['meal_type'].value_counts()}")

    # Food frequency
    st.subheader("🥑 Most Offered Foods")
    food_counts = df["foods_offered"].str.get_dummies(sep=", ").sum().sort_values(ascending=False)
    st.bar_chart(food_counts.head(10))

    # Amount eaten trend
    st.subheader("📈 Meals Over Time")
    df["datetime"] = pd.to_datetime(df["datetime"])
    df["day"] = df["datetime"].dt.date
    daily_counts = df.groupby("day").size()
    st.line_chart(daily_counts)

    # Distraction usage
    st.subheader("🧸 Distraction Use")
    distraction_stats = df["used_distraction"].value_counts()
    st.bar_chart(distraction_stats)
else:
    st.info("No feeding data yet. Add a meal using the sidebar.")

