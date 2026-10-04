import streamlit as st
from src.database.db import create_subject


@st.dialog("Create Academic Subject")
def create_subject_dialog(teacher_id):
    st.markdown("""
        <p style="color:#94A3B8; font-size:0.88rem; margin-bottom:1rem;">
            Configure course parameters and section designations to initialize attendance tracking rosters.
        </p>
    """, unsafe_allow_html=True)

    sub_id = st.text_input("Course Code", placeholder="e.g. CS101, PHY201").strip().upper()
    sub_name = st.text_input("Course Title", placeholder="e.g. Data Structures & Algorithms").strip()
    sub_section = st.text_input("Section / Batch", placeholder="e.g. Section A, Lab Batch 1").strip()

    if st.button("Initialize Course Roster →", type='primary', width='stretch'):
        if sub_id and sub_name:
            section_val = sub_section if sub_section else "A"
            try:
                create_subject(sub_id, sub_name, section_val, teacher_id)
                st.toast("Course created successfully!", icon="✅")
                st.rerun()
            except Exception as e:
                st.error(f"Failed to create subject: {str(e)}")
        else:
            st.warning("Please provide both a Course Code and Course Title.")
