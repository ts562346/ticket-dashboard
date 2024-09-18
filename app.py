import streamlit as st
import pandas as pd
from datetime import datetime

# Function to process the data
def process_data(df):
    df['Date/Time Logged'] = pd.to_datetime(df['Date/Time Logged']).dt.date
    today = datetime.today().date()  # Keep only the date, not time
    df['days_diff'] = (today - df['Date/Time Logged']).apply(lambda x: x.days)

    bins = [-1, 0, 5, 15, 30, 60, 90, float('inf')]
    labels = ['Same Day', '1-5', '6-15', '16-30', '31-60', '61-90', 'Over 91']
    df['bucket'] = pd.cut(df['days_diff'], bins=bins, labels=labels)

    df['assigned_status'] = df['Assigned User Name'].apply(lambda x: 'Unassigned' if pd.isna(x) else 'Assigned')
    bucket_counts = df.groupby(['bucket', 'assigned_status']).size().unstack(fill_value=0)

    bucket_counts = bucket_counts.reindex(labels).fillna(0)
    result = pd.DataFrame({
        'Bucket': bucket_counts.index,
        'Ticket Count': bucket_counts.sum(axis=1),
        'Assigned Tickets': bucket_counts['Assigned'],
        'Unassigned Tickets': bucket_counts['Unassigned']
    })

    total_row = pd.DataFrame({
        'Bucket': ['Total Tickets'],
        'Ticket Count': [result['Ticket Count'].sum()],
        'Assigned Tickets': [result['Assigned Tickets'].sum()],
        'Unassigned Tickets': [result['Unassigned Tickets'].sum()]
    })

    result = pd.concat([result, total_row], ignore_index=True)
    
    return result

st.title("Ticket Analysis App")
uploaded_file = st.file_uploader("Upload an Excel file", type=["xls", "xlsx"])

if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)
    st.write("### Data Preview")
    st.write(df.head())

    if st.button("Run Analysis"):
        result = process_data(df)
        st.write("### Analysis Results")
        st.write(result)
