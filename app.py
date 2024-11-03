import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt

# Connect to SQLite database (or create it if it doesn't exist)
conn = sqlite3.connect("expenses.db")
c = conn.cursor()

# Create table if it doesn't exist, with a 'type' column to track income, expense, or savings
c.execute('''
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY,
        amount REAL,
        comment TEXT,
        type TEXT,
        date TEXT,
        time TEXT
    )
''')
conn.commit()

# Streamlit app title
st.title("Income, Expense, and Savings Tracker")

# Input section for new transaction
st.header("Add a New Transaction")
with st.form("transaction_form"):
    transaction_type = st.selectbox("Type", ["Expense", "Income", "Savings"])  # Choose between Expense, Income, and Savings
    amount = st.number_input("Amount", min_value=0.01, format="%.2f")
    comment = st.text_input("Comment")
    date = datetime.now().strftime("%Y-%m-%d")
    time = datetime.now().strftime("%H:%M:%S")
    submitted = st.form_submit_button("Add Transaction")

    # Insert data into SQLite database
    if submitted:
        c.execute("INSERT INTO transactions (amount, comment, type, date, time) VALUES (?, ?, ?, ?, ?)", 
                  (amount, comment, transaction_type, date, time))
        conn.commit()
        st.success("Transaction added successfully!")

# Display and visualize data
st.header("Transaction History")

# Fetch data from database
c.execute("SELECT * FROM transactions ORDER BY date DESC, time DESC")
data = c.fetchall()

# Display data in a table
if data:
    df = pd.DataFrame(data, columns=["ID", "Amount", "Comment", "Type", "Date", "Time"])
    st.dataframe(df[["Amount", "Comment", "Type", "Date", "Time"]])

    # Calculate and display totals
    total_income = df[df["Type"] == "Income"]["Amount"].sum()
    total_expense = df[df["Type"] == "Expense"]["Amount"].sum()
    total_savings = df[df["Type"] == "Savings"]["Amount"].sum()  # Total savings calculation
    st.write(f"**Total Income:** RS-{total_income:,.2f}")
    st.write(f"**Total Expenses:** RS-{total_expense:,.2f}")
    st.write(f"**Total Savings:** RS-{total_savings:,.2f}")  # Display total savings
    st.write(f"**Net Balance (Income - Expenses):** RS-{total_income - total_savings-  total_expense :,.2f}")

    # Visualization: Income, Expenses, and Savings over time
    st.header("Income, Expenses, and Savings Over Time")
    daily_totals = df.groupby(["Date", "Type"])["Amount"].sum().unstack(fill_value=0)
    fig, ax = plt.subplots()
    daily_totals.plot(kind="bar", stacked=True, ax=ax)
    ax.set_ylabel("Total Amount")
    ax.set_title("Daily Income, Expenses, and Savings")
    st.pyplot(fig)
else:
    st.info("No transactions recorded yet.")

# Close database connection
conn.close()
