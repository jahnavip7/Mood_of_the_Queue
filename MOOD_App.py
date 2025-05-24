import streamlit as st
import gspread
from datetime import datetime
import pandas as pd
import plotly.express as px
import json
from oauth2client.service_account import ServiceAccountCredentials

# Google Sheets Setup
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds_dict = json.loads(st.secrets["GOOGLE_CREDENTIALS"])
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)
sheet = client.open("MoodLog").sheet1 

# Streamlit UI 
st.set_page_config(page_title="Mood of the Queue", layout="centered")
st.title("Mood of the Queue")

with st.form("log_form"):
    st.subheader("Log a Mood")
    mood = st.radio("How's the vibe?", ["😊", "😠", "😕", "🎉"], horizontal=True)
    note = st.text_input("Add a short note (optional)")
    submitted = st.form_submit_button("Submit")

    if submitted:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        sheet.append_row([timestamp, mood, note])
        st.success("✅ Mood logged!")

# Mood Chart 
st.markdown("---")
st.subheader("Today's Mood Trend")

records = sheet.get_all_records()
if records:
    df = pd.DataFrame(records)
    df.columns = df.columns.str.strip().str.lower()  
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    today = datetime.now().date()
    df_today = df[df["timestamp"].dt.date == today]

    if not df_today.empty and "mood" in df_today.columns:
        mood_counts = df_today["mood"].value_counts().reset_index()
        mood_counts.columns = ["Mood", "Count"]
        fig = px.bar(mood_counts, x="Mood", y="Count", title="Mood Counts for Today", text="Count")
        st.plotly_chart(fig, use_container_width=True, key="today_mood_chart")
    else:
        st.info("No moods logged yet today.")
else:
    st.info("No data found in the sheet.")
