import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path


@st.cache_data
def load_data():
    """Load query results from outputs folder."""
    outputs_dir = Path('data/outputs')
    return {
        'daily_revenue': pd.read_csv(outputs_dir / 'daily_revenue.csv'),
        'truck_performance': pd.read_csv(outputs_dir / 'truck_performance.csv'),
        'payment_methods': pd.read_csv(outputs_dir / 'payment_methods.csv'),
        'hourly_patterns': pd.read_csv(outputs_dir / 'hourly_patterns.csv'),
        'day_of_week_patterns': pd.read_csv(outputs_dir / 'day_of_week_patterns.csv')
    }


def display_kpis(data):
    """Display key performance indicator metrics."""
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Revenue",
                f"£{data['daily_revenue']['total_revenue'].sum():,.0f}")
    col2.metric("Transactions",
                f"{data['daily_revenue']['transaction_count'].sum():,}")
    col3.metric("Avg Transaction",
                f"£{data['daily_revenue']['avg_transaction_value'].mean():.2f}")
    col4.metric("Active Trucks", len(data['truck_performance']))


def display_daily_revenue(data):
    """Display daily revenue trend line chart."""
    st.subheader("Daily Revenue")
    fig = px.line(data['daily_revenue'], x='date',
                  y='total_revenue', markers=True)
    st.plotly_chart(fig, use_container_width=True)


def display_truck_performance(data):
    """Display truck revenue performance bar chart."""
    st.subheader("Truck Performance")
    fig = px.bar(data['truck_performance'], x='truck_name',
                 y='total_revenue', color='fsa_rating')
    fig.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)


def display_payment_methods(data):
    """Display payment method distribution pie chart."""
    st.subheader("Payment Methods")
    fig = px.pie(data['payment_methods'], values='total_revenue',
                 names='payment_method', hole=0.4)
    st.plotly_chart(fig, use_container_width=True)


def display_hourly_patterns(data):
    """Display hourly revenue patterns bar chart."""
    st.subheader("Hourly Pattern")
    fig = px.bar(data['hourly_patterns'], x='hour_of_day', y='total_revenue')
    st.plotly_chart(fig, use_container_width=True)


def display_day_of_week(data):
    """Display day of week revenue patterns bar chart."""
    st.subheader("Day of Week")
    days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    dow = data['day_of_week_patterns'].copy()
    dow['day'] = dow['day_of_week'].apply(lambda x: days[int(x) - 1])
    fig = px.bar(dow, x='day', y='total_revenue')
    st.plotly_chart(fig, use_container_width=True)


def main():
    """Main dashboard layout and orchestration."""
    st.set_page_config(page_title="T3 Food Trucks",
                       page_icon="🚚", layout="wide")
    st.title("🚚 T3 Food Trucks Dashboard")

    data = load_data()

    display_kpis(data)
    st.divider()
    display_daily_revenue(data)

    col1, col2 = st.columns(2)
    with col1:
        display_truck_performance(data)
    with col2:
        display_payment_methods(data)

    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        display_hourly_patterns(data)
    with col2:
        display_day_of_week(data)


if __name__ == "__main__":
    main()
