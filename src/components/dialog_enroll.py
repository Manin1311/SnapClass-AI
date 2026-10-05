import streamlit as st
from src.database.db import enroll_student_to_subject
from src.database.config import supabase
import time


@st.dialog("Course Enrollment")
def enroll_dialog():
    is_dark = (st.session_state.get('theme_mode', 'light') == 'dark')
    desc_color = "#94A3B8" if is_dark else "#475569"

    st.markdown(f"""
        <p style="color:{desc_color}; font-size:0.92rem; line-height:1.55; margin-bottom:1.25rem;">
            Enter the unique Course Code provided by your instructor to link your biometric profile to the class roster.
        </p>
    """, unsafe_allow_html=True)

    join_code = st.text_input('Course Code', placeholder='e.g. CS101').strip()

    if st.button('Confirm & Enroll →', type='primary', width='stretch'):
        if join_code:
            res = supabase.table('subjects').select('subject_id, name, subject_code').ilike('subject_code', join_code).execute()
            if res.data:
                subject = res.data[0]
                student_id = st.session_state.student_data['student_id']

                check = supabase.table('subject_students').select('*').eq('subject_id', subject['subject_id']).eq('student_id', student_id).execute()
                if check.data:
                    st.warning(f"You are already registered in {subject['name']}.")
                else:
                    enroll_student_to_subject(student_id, subject['subject_id'])
                    st.success(f"Enrolled successfully in {subject['name']}!")
                    time.sleep(1)
                    st.rerun()
            else:
                st.error("No active course found matching that code. Please check with your instructor.")
        else:
            st.warning('Please enter a course code.')