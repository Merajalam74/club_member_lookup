#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep  1 14:39:57 2025

@author: merajalam
"""

import streamlit as st
import pandas as pd

csv_url = "https://docs.google.com/spreadsheets/d/1ZgOV7SHOX8XzK7EzgVTzDC8okXTPE_sCm1CRCq5Qdjs/gviz/tq?tqx=out:csv&sheet=Form%20responses%201"

df = pd.read_csv(csv_url)

st.title("🎓 College Club Lookup Tool")

# --- Search by Registration Number ---
st.subheader("🔎 Search by Registration Number")
reg_no = st.text_input("Enter Registration Number:")

if reg_no:
    if "Registration Number" in df.columns:
        student_data = df[df["Registration Number"].astype(str) == reg_no]

        if not student_data.empty:
            st.success(f"✅ Found {len(student_data)} record(s)")
            st.dataframe(
                student_data[["Name", "Department", "Phone Number", "Club 1", "Club 2"]],
                use_container_width=True,
                height=(len(student_data) + 1) * 35
            )
        else:
            st.error("❌ No student found with this Registration Number.")
    else:
        st.error("⚠️ Column 'Registration Number' not found. Please check the sheet headers.")


# --- Search by Club ---
st.subheader("🏆 Search by Club")

if "Club 1" in df.columns and "Club 2" in df.columns:
    # Collect unique clubs from both columns
    all_clubs = pd.unique(df[["Club 1", "Club 2"]].values.ravel("K"))
    all_clubs = [c for c in all_clubs if pd.notna(c)]  # remove NaN

    selected_club = st.selectbox("Choose a Club:", ["-- Select Club --"] + sorted(all_clubs))

    if selected_club != "-- Select Club --":
        club_data = df[(df["Club 1"] == selected_club) | (df["Club 2"] == selected_club)]

        if not club_data.empty:
            st.success(f"✅ Found {len(club_data)} student(s) in {selected_club}")
            st.table(club_data[["Name", "Registration Number","Department"]])
            unique_members = club_data.drop_duplicates(subset=["Registration Number"])
            st.info(f"👥 Total Unique Members in **{selected_club}**: {len(unique_members)}")
        else:
            st.warning(f"No students found in {selected_club}.")
