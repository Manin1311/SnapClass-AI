import streamlit as st
from src.database.db import enroll_student_to_subject
from src.database.config import supabase
import time


@st.dialog("Course Invitation")
def auto_enroll_dialog(subject_code):
    student_id = st.session_state.student_data['student_id']

    res = supabase.table('subjects').select('subject_id, name, subject_code').ilike('subject_code', subject_code.strip()).execute()
    if not res.data:
        st.error(f"Course code '{subject_code}' not found in active rosters.")
        if st.button('Close'):
            st.query_params.clear()
            st.rerun()
        return

    subject = res.data[0]

    check = supabase.table('subject_students').select('*').eq('subject_id', subject['subject_id']).eq('student_id', student_id).execute()
    if check.data:
        st.info(f"You are already registered in **{subject['name']}**.")
        if st.button('Continue to Dashboard →', type='primary'):
            st.query_params.clear()
            st.rerun()
        return

    is_dark = (st.session_state.get('theme_mode', 'light') == 'dark')
    card_bg = "rgba(255,255,255,0.03)" if is_dark else "#F1F5F9"
    card_border = "rgba(255,255,255,0.08)" if is_dark else "#E2E8F0"
    title_col = "#F8FAFC" if is_dark else "#0F172A"
    desc_col = "#94A3B8" if is_dark else "#475569"

    st.markdown(f"""
        <div style="background:{card_bg}; border:1px solid {card_border}; border-radius:12px; padding:1.25rem; margin-bottom:1.25rem;">
            <div style="font-size:0.75rem; text-transform:uppercase; color:#6366F1; font-weight:700;">Invited Course</div>
            <h3 style="margin:4px 0 0 0; color:{title_col}; font-size:1.25rem;">{subject['name']}</h3>
            <span style="font-family:'JetBrains Mono', monospace; font-size:0.85rem; color:#4F46E5; font-weight:600;">Code: {subject['subject_code']}</span>
        </div>
        <p style="color:{desc_col}; font-size:0.9rem; line-height:1.5;">Would you like to enroll and associate your facial biometrics with this course roster?</p>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        if st.button('Decline', width='stretch', type='secondary'):
            st.query_params.clear()
            st.rerun()
    with col2:
        if st.button('Accept & Enroll →', type='primary', width='stretch'):
            enroll_student_to_subject(student_id, subject['subject_id'])
            st.success(f"Enrolled successfully in {subject['name']}!")
            st.query_params.clear()
            time.sleep(1)
            st.rerun()
