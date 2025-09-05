"""
College Club Management Tool - Modern UI with Graphs
"""

import streamlit as st
import pandas as pd

# ---------------------- CONFIG ----------------------
st.set_page_config(
    page_title="🎓 College Club Tool",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------- CUSTOM CSS ----------------------
st.markdown("""
<style>
.stApp { background-color: #f9f9fb; }

/* Headings */
h1, h2, h3 {
    color: #2c3e50;
    font-weight: 600;
}

/* Metric card */
div[data-testid="stMetric"] {
    background: #ffffff;
    padding: 20px;
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    text-align: center;
    margin: 5px;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: #f0f3f7;
}
</style>
""", unsafe_allow_html=True)

# ---------------------- DATA LOAD ----------------------
# Responses sheet (Google Form output)
csv_url = "https://docs.google.com/spreadsheets/d/1ZgOV7SHOX8XzK7EzgVTzDC8okXTPE_sCm1CRCq5Qdjs/gviz/tq?tqx=out:csv&sheet=Form%20responses%201"
df = pd.read_csv(csv_url)
df.columns = df.columns.str.strip()

# Master student list
all_students_link = "https://docs.google.com/spreadsheets/d/1iXn5B9vmizIpOp_1LAjKjLxyTiEf67b1/gviz/tq?tqx=out:csv&sheet=Form%20responses%201"
all_students_df = pd.read_csv(all_students_link)
all_students_df.columns = all_students_df.columns.str.strip()

# ---------------------- OWNER CONFIG ----------------------
OWNER_PIN = "1234"
OWNER_ACTIVITY_FORM_URL = "https://forms.gle/uWH3JUhz1jMh8t4PA"

# ---------------------- SIDEBAR MENU ----------------------
menu = st.sidebar.radio(
    "📌 Navigation",
    [
        "🏠 Dashboard",
        "🔎 Search by Registration Number",
        "🏆 Search by Club",
        "✅ Students Joined At Least One Club",
        "🚫 Students Who Have Not Responded",
        "🛠️ Club Owner Panel"
    ]
)

# ---------------------- DASHBOARD ----------------------
if menu == "🏠 Dashboard":
    st.title("🎓 College Club Dashboard")
    st.markdown("Welcome to the **College Club Management Tool**!")

    total_responses = len(df)
    total_students = len(all_students_df) if not all_students_df.empty else 0
    total_not_responded = total_students - total_responses

    # ----- Colorful cards -----
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📥 Joined Any Club", total_responses)
    with col2:
        st.metric("👥 Total Students", total_students)
    with col3:
        st.metric("🚫 Not Responded", total_not_responded if total_not_responded >= 0 else 0)

    # ----- Club participation bar chart -----
    st.subheader("📊 Club Participation Comparison")

    if "Club 1" in df.columns and "Club 2" in df.columns:
        clubs = pd.concat([df["Club 1"], df["Club 2"]]).dropna()
        club_counts = clubs.value_counts().reset_index()
        club_counts.columns = ["Club", "Count"]

        st.bar_chart(club_counts.set_index("Club"))
    else:
        st.warning("⚠️ Club columns not found in the sheet.")

    # ----- Latest responses -----
    st.subheader("🕒 Latest Responses")
    st.dataframe(df.tail(5), use_container_width=True)

# ---------------------- SEARCH BY REG NO ----------------------
elif menu == "🔎 Search by Registration Number":
    st.title("🔎 Search by Registration Number")
    reg_no = st.text_input("Enter Registration Number:")

    if st.button("🔍 Search"):
        if reg_no:
            student_data = df[df["Registration Number"].astype(str) == reg_no]
            if not student_data.empty:
                st.success(f"✅ Found {len(student_data)} record(s)")
                st.dataframe(
                    student_data[["Name", "Department", "Phone Number", "Club 1", "Club 2"]],
                    use_container_width=True
                )
            else:
                st.error("❌ No student found with this Registration Number.")
        else:
            st.warning("⚠️ Please enter a Registration Number.")

# ---------------------- SEARCH BY CLUB ----------------------
elif menu == "🏆 Search by Club":
    st.title("🏆 Search by Club")
    if "Club 1" in df.columns and "Club 2" in df.columns:
        all_clubs = pd.unique(df[["Club 1", "Club 2"]].values.ravel("K"))
        all_clubs = [c for c in all_clubs if pd.notna(c)]

        selected_club = st.selectbox("Choose a Club:", ["-- Select Club --"] + sorted(all_clubs))

        if selected_club != "-- Select Club --":
            club_data = df[(df["Club 1"] == selected_club) | (df["Club 2"] == selected_club)]
            if not club_data.empty:
                st.dataframe(club_data[["Name", "Registration Number", "Department"]],
                             use_container_width=True)
                unique_members = club_data.drop_duplicates(subset=["Registration Number"])
                st.info(f"👥 Total Unique Members in **{selected_club}**: {len(unique_members)}")
            else:
                st.warning(f"No students found in {selected_club}.")

# ---------------------- JOINED AT LEAST ONE CLUB ----------------------
elif menu == "✅ Students Joined At Least One Club":
    st.title("✅ Students Joined At Least One Club")
    joined = df[(df["Club 1"].notna()) | (df["Club 2"].notna())]
    if not joined.empty:
        st.dataframe(joined[["Name", "Registration Number", "Department", "Club 1", "Club 2"]],
                     use_container_width=True)
        st.info(f"👥 Total Students Joined At Least One Club: {len(joined)}")
    else:
        st.warning("No students have joined any club.")

# ---------------------- NOT RESPONDED ----------------------
elif menu == "🚫 Students Who Have Not Responded":
    st.title("🚫 Students Who Have Not Responded")
    if not all_students_df.empty and "Registration Number" in all_students_df.columns:
        responded_reg_nos = df["Registration Number"].astype(str).unique()
        non_responded = all_students_df[
            ~all_students_df["Registration Number"].astype(str).isin(responded_reg_nos)
        ]

        if not non_responded.empty:
            st.dataframe(non_responded[["Name", "Registration Number", "Department"]],
                         use_container_width=True)
            st.info(f"👥 Total Students Not Responded: {len(non_responded)}")

            csv = non_responded.to_csv(index=False).encode("utf-8")
            st.download_button("📥 Download Non-Responded List", data=csv,
                               file_name="non_responded_students.csv", mime="text/csv")
        else:
            st.success("🎉 All students have responded!")

# ---------------------- CLUB OWNER PANEL ----------------------
elif menu == "🛠️ Club Owner Panel":
    st.title("🛠️ Club Owner Panel")

    pin = st.text_input("Enter Owner PIN", type="password")
    if pin == OWNER_PIN:
        st.success("✅ Authenticated as Club Owner")

        col1, col2 = st.columns(2)
        with col1:
            st.info("📌 Use this form to submit new activity updates.")
        with col2:
            st.markdown(f"[📝 Open Activity Form]({OWNER_ACTIVITY_FORM_URL})", unsafe_allow_html=True)

    elif pin:
        st.error("❌ Incorrect PIN")
    else:
        st.warning("Enter PIN to access the Owner Panel.")
