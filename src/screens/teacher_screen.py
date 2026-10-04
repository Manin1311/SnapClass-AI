import streamlit as st
import numpy as np
import pandas as pd
from datetime import datetime
import time

from src.ui.base_layout import style_background_dashboard
from src.components.header import header_dashboard
from src.components.footer import footer_dashboard
from src.components.subject_card import subject_card
from src.database.db import (
    check_teacher_exists, 
    create_teacher, 
    teacher_login, 
    get_teacher_subjects, 
    get_attendance_for_teacher
)
from src.components.dialog_create_subject import create_subject_dialog
from src.components.dialog_share_subject import share_subject_dialog
from src.components.dialog_add_photo import add_photos_dialog
from src.pipelines.face_pipeline import predict_attendance
from src.components.dialog_attendance_results import attendance_result_dialog
from src.components.dialog_voice_attendance import voice_attendance_dialog
from src.database.config import supabase


def teacher_screen():
    style_background_dashboard()

    if "teacher_data" in st.session_state:
        teacher_dashboard()
    elif 'teacher_login_type' not in st.session_state or st.session_state.teacher_login_type == "login":
        teacher_screen_login()
    elif st.session_state.teacher_login_type == "register":
        teacher_screen_register()


def teacher_dashboard():
    teacher_data = st.session_state.teacher_data
    teacher_id = teacher_data['teacher_id']
    is_dark = (st.session_state.get('theme_mode', 'light') == 'dark')

    name_color = "#F8FAFC" if is_dark else "#0F172A"
    kpi_bg = "rgba(17, 24, 39, 0.7)" if is_dark else "#FFFFFF"
    kpi_border = "rgba(255, 255, 255, 0.08)" if is_dark else "#E2E8F0"
    kpi_shadow = "0 8px 24px -6px rgba(0,0,0,0.3)" if is_dark else "0 4px 12px -2px rgba(0, 0, 0, 0.05)"
    kpi_text = "#F8FAFC" if is_dark else "#0F172A"

    # Top Navigation & Profile Bar
    c1, c2, c3 = st.columns([2.5, 1, 1], vertical_alignment='center')
    with c1:
        header_dashboard()
    with c2:
        from src.components.header import render_theme_toggle
        render_theme_toggle()
    with c3:
        st.markdown(f"""
            <div style="display:flex; justify-content:flex-end; align-items:center; gap:10px;">
                <div style="text-align:right;">
                    <div style="font-weight:700; color:{name_color}; font-size:0.95rem;">{teacher_data['name']}</div>
                    <div style="font-size:0.75rem; color:#4F46E5; font-weight:600;">Faculty</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        if st.button("Sign Out", type='secondary', key='logout_btn', width='stretch'):
            st.session_state['is_logged_in'] = False
            del st.session_state.teacher_data
            st.rerun()

    # Calculate real-time KPIs
    subjects = get_teacher_subjects(teacher_id)
    total_subjects = len(subjects) if subjects else 0
    total_students_enrolled = sum(s.get('total_students', 0) for s in subjects) if subjects else 0
    total_classes_conducted = sum(s.get('total_classes', 0) for s in subjects) if subjects else 0

    # KPI Metric Cards Banner
    st.markdown(f"""
        <div style="display:grid; grid-template-columns:repeat(3, 1fr); gap:1rem; margin:1.5rem 0 2rem 0;">
            <div style="background:{kpi_bg}; border:1px solid {kpi_border}; border-radius:14px; padding:1.2rem; box-shadow:{kpi_shadow};">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span style="font-size:0.8rem; color:#64748B; text-transform:uppercase; font-weight:600; letter-spacing:0.5px;">Active Subjects</span>
                    <span style="font-size:1.2rem;">📚</span>
                </div>
                <div style="font-size:1.8rem; font-weight:800; color:{kpi_text}; margin-top:4px; font-family:'Plus Jakarta Sans';">{total_subjects}</div>
            </div>
            <div style="background:{kpi_bg}; border:1px solid {kpi_border}; border-radius:14px; padding:1.2rem; box-shadow:{kpi_shadow};">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span style="font-size:0.8rem; color:#64748B; text-transform:uppercase; font-weight:600; letter-spacing:0.5px;">Total Students</span>
                    <span style="font-size:1.2rem;">👥</span>
                </div>
                <div style="font-size:1.8rem; font-weight:800; color:#4F46E5; margin-top:4px; font-family:'Plus Jakarta Sans';">{total_students_enrolled}</div>
            </div>
            <div style="background:{kpi_bg}; border:1px solid {kpi_border}; border-radius:14px; padding:1.2rem; box-shadow:{kpi_shadow};">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span style="font-size:0.8rem; color:#64748B; text-transform:uppercase; font-weight:600; letter-spacing:0.5px;">Sessions Conducted</span>
                    <span style="font-size:1.2rem;">⚡</span>
                </div>
                <div style="font-size:1.8rem; font-weight:800; color:#10B981; margin-top:4px; font-family:'Plus Jakarta Sans';">{total_classes_conducted}</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Segmented Tab Navigation
    if "current_teacher_tab" not in st.session_state:
        st.session_state.current_teacher_tab = 'take_attendance'

    tab1, tab2, tab3 = st.columns(3)
    with tab1:
        type1 = "primary" if st.session_state.current_teacher_tab == 'take_attendance' else "secondary"
        if st.button('📸 Take AI Attendance', type=type1, width='stretch'):
            st.session_state.current_teacher_tab = 'take_attendance'
            st.rerun()

    with tab2:
        type2 = "primary" if st.session_state.current_teacher_tab == 'manage_subjects' else "secondary"
        if st.button('📚 Manage Subjects', type=type2, width='stretch'):
            st.session_state.current_teacher_tab = 'manage_subjects'
            st.rerun()

    with tab3:
        type3 = "primary" if st.session_state.current_teacher_tab == 'attendance_records' else "secondary"
        if st.button('📊 Attendance Analytics', type=type3, width='stretch'):
            st.session_state.current_teacher_tab = 'attendance_records'
            st.rerun()

    st.markdown("<div style='margin-bottom:1.5rem;'></div>", unsafe_allow_html=True)

    if st.session_state.current_teacher_tab == "take_attendance":
        teacher_tab_take_attendance(subjects)
    elif st.session_state.current_teacher_tab == "manage_subjects":
        teacher_tab_manage_subjects(subjects)
    elif st.session_state.current_teacher_tab == "attendance_records":
        teacher_tab_attendance_records()

    footer_dashboard()


def teacher_tab_take_attendance(subjects):
    teacher_id = st.session_state.teacher_data['teacher_id']

    st.markdown("""
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:1rem;">
            <div>
                <h2 style="margin:0; font-size:1.45rem;">AI Biometric Attendance Scanner</h2>
                <p style="margin:2px 0 0 0; color:#94A3B8; font-size:0.88rem;">Capture or upload classroom photos. AI performs instant multi-face identification against enrolled rosters.</p>
            </div>
        </div>
    """, unsafe_allow_html=True)

    if 'attendance_images' not in st.session_state:
        st.session_state.attendance_images = []

    if not subjects:
        st.info('ℹ️ You have not created any subjects yet. Please open the "Manage Subjects" tab to set up your first course roster.')
        return

    subject_options = {f"{s['name']} ({s['subject_code']}) - Sec {s.get('section', 'A')}": s['subject_id'] for s in subjects}

    col1, col2 = st.columns([3, 1], vertical_alignment='bottom')
    with col1:
        selected_subject_label = st.selectbox('Select Target Subject', options=list(subject_options.keys()))
    with col2:
        if st.button('➕ Add Photos', type='primary', width='stretch'):
            add_photos_dialog()

    selected_subject_id = subject_options[selected_subject_label]

    st.markdown("<hr style='margin:1.5rem 0;'>", unsafe_allow_html=True)

    # Added Photos Preview Grid
    if st.session_state.attendance_images:
        st.markdown(f"""
            <div style="display:flex; align-items:center; gap:8px; margin-bottom:0.75rem;">
                <span style="font-weight:700; color:#F8FAFC;">Classroom Photos Loaded:</span>
                <span style="background:rgba(99, 102, 241, 0.2); color:#A5B4FC; padding:2px 8px; border-radius:6px; font-size:0.8rem; font-weight:600;">{len(st.session_state.attendance_images)} image(s)</span>
            </div>
        """, unsafe_allow_html=True)
        gallery_cols = st.columns(min(4, len(st.session_state.attendance_images)))
        for idx, img in enumerate(st.session_state.attendance_images):
            with gallery_cols[idx % 4]:
                st.image(img, use_container_width=True, caption=f'Photo #{idx + 1}')

    has_photos = bool(st.session_state.attendance_images)
    c1, c2, c3 = st.columns([1.5, 2, 2])

    with c1:
        if st.button('Clear Queue', width='stretch', type='secondary', disabled=not has_photos):
            st.session_state.attendance_images = []
            st.rerun()

    with c2:
        if st.button('⚡ Execute Face Analysis', width='stretch', type='primary', disabled=not has_photos):
            with st.spinner('AI Engine scanning classroom imagery and matching facial embeddings...'):
                all_detected_ids = {}

                for idx, img in enumerate(st.session_state.attendance_images):
                    img_np = np.array(img.convert('RGB'))
                    detected, _, _ = predict_attendance(img_np)

                    if detected:
                        for sid in detected.keys():
                            student_id = int(sid)
                            all_detected_ids.setdefault(student_id, []).append(f"Photo {idx + 1}")

                enrolled_res = supabase.table('subject_students').select("*, students(*)").eq('subject_id', selected_subject_id).execute()
                enrolled_students = enrolled_res.data

                if not enrolled_students:
                    st.warning('No students are currently enrolled in this subject roster. Share the course code with students first.')
                else:
                    results, attendance_to_log = [], []
                    current_timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

                    for node in enrolled_students:
                        student = node['students']
                        sources = all_detected_ids.get(int(student['student_id']), [])
                        is_present = len(sources) > 0

                        results.append({
                            "Name": student['name'],
                            "Student ID": student['student_id'],
                            "Verification Source": ", ".join(sources) if is_present else "Unmatched",
                            "Status": "✅ Present" if is_present else "❌ Absent"
                        })

                        attendance_to_log.append({
                            'student_id': student['student_id'],
                            'subject_id': selected_subject_id,
                            'timestamp': current_timestamp,
                            'is_present': bool(is_present)
                        })

                    attendance_result_dialog(pd.DataFrame(results), attendance_to_log)

    with c3:
        if st.button('🎙️ Voice Attendance Mode', type='secondary', width='stretch'):
            voice_attendance_dialog(selected_subject_id)


def teacher_tab_manage_subjects(subjects):
    teacher_id = st.session_state.teacher_data['teacher_id']

    col1, col2 = st.columns([3, 1], vertical_alignment='center')
    with col1:
        st.markdown("""
            <div>
                <h2 style="margin:0; font-size:1.45rem;">Course & Roster Management</h2>
                <p style="margin:2px 0 0 0; color:#94A3B8; font-size:0.88rem;">Create new courses, manage sections, and generate instant join links / QR codes for students.</p>
            </div>
        """, unsafe_allow_html=True)
    with col2:
        if st.button('➕ Create New Subject', type='primary', width='stretch'):
            create_subject_dialog(teacher_id)

    st.markdown("<hr style='margin:1.5rem 0;'>", unsafe_allow_html=True)

    if subjects:
        cols = st.columns(2)
        for i, sub in enumerate(subjects):
            stats = [
                ("👥", "Students", sub.get('total_students', 0)),
                ("🗓️", "Classes", sub.get('total_classes', 0)),
            ]
            
            with cols[i % 2]:
                def make_share_btn(s_name, s_code):
                    def callback():
                        if st.button(f"🔗 Share Join Link / QR Code", key=f"share_{s_code}", type='secondary', width='stretch'):
                            share_subject_dialog(s_name, s_code)
                    return callback

                subject_card(
                    name=sub['name'],
                    code=sub['subject_code'],
                    section=sub.get('section', 'A'),
                    stats=stats,
                    footer_callback=make_share_btn(sub['name'], sub['subject_code'])
                )
    else:
        st.info("No courses registered yet. Click 'Create New Subject' above to set up your first class!")


def teacher_tab_attendance_records():
    teacher_id = st.session_state.teacher_data['teacher_id']

    st.markdown("""
        <div>
            <h2 style="margin:0; font-size:1.45rem;">Attendance Analytics & Records</h2>
            <p style="margin:2px 0 0 0; color:#94A3B8; font-size:0.88rem;">Historical log of verified classroom attendance sessions with exportable CSV auditing.</p>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("<hr style='margin:1.5rem 0;'>", unsafe_allow_html=True)

    records = get_attendance_for_teacher(teacher_id)

    if not records:
        st.info("No attendance records logged yet. Run a session in the 'Take Attendance' tab to see analytics here.")
        return

    data = []
    for r in records:
        ts = r.get('timestamp')
        formatted_time = "N/A"
        if ts:
            try:
                formatted_time = datetime.fromisoformat(ts).strftime("%Y-%m-%d  %I:%M %p")
            except Exception:
                formatted_time = ts

        data.append({
            "ts_group": ts.split(".")[0] if ts else "N/A",
            "Session Timestamp": formatted_time,
            "Course Name": r['subjects']['name'],
            "Course Code": r['subjects']['subject_code'],
            "is_present": bool(r.get('is_present', False))
        })

    df = pd.DataFrame(data)

    summary = (
        df.groupby(['ts_group', 'Session Timestamp', 'Course Name', 'Course Code'])
        .agg(
            Present_Count=('is_present', 'sum'),
            Total_Count=('is_present', 'count')
        ).reset_index()
    )

    summary['Attendance Ratio'] = (
        summary['Present_Count'].astype(str) + " / " + summary['Total_Count'].astype(str) + " Students"
    )
    summary['Attendance %'] = (
        (summary['Present_Count'] / summary['Total_Count'] * 100).round(1).astype(str) + "%"
    )

    display_df = summary.sort_values(by='ts_group', ascending=False)[
        ['Session Timestamp', 'Course Name', 'Course Code', 'Attendance Ratio', 'Attendance %']
    ]

    col_df, col_actions = st.columns([4, 1.2], vertical_alignment='bottom')
    with col_actions:
        csv_bytes = display_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Export Report (CSV)",
            data=csv_bytes,
            file_name=f"attendance_report_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            type="primary",
            width='stretch'
        )

    st.dataframe(display_df, use_container_width=True, hide_index=True)


def login_teacher(username, password):
    if not username or not password:
        return False
    teacher = teacher_login(username, password)
    if teacher:
        st.session_state.user_role = 'teacher'
        st.session_state.teacher_data = teacher
        st.session_state.is_logged_in = True
        return True
    return False


def register_teacher(teacher_username, teacher_name, teacher_pass, teacher_pass_confirm):
    if not teacher_username or not teacher_name or not teacher_pass:
        return False, "All fields are required."
    if check_teacher_exists(teacher_username):
        return False, "Username is already registered. Please choose another or login."
    if teacher_pass != teacher_pass_confirm:
        return False, "Passwords do not match."

    try:
        create_teacher(teacher_username, teacher_pass, teacher_name)
        return True, "Profile registered successfully! You may now sign in."
    except Exception as e:
        return False, f"Registration error: {str(e)}"


def teacher_screen_login():
    is_dark = (st.session_state.get('theme_mode', 'light') == 'dark')
    title_color = "#F8FAFC" if is_dark else "#0F172A"
    sub_color = "#94A3B8" if is_dark else "#64748B"

    c1, c2 = st.columns([3, 1], vertical_alignment='center')
    with c1:
        header_dashboard()
    with c2:
        if st.button("← Return to Gateway", type='secondary', key='back_btn'):
            st.session_state['login_type'] = None
            st.rerun()

    _, center_col, _ = st.columns([1, 2.4, 1])
    with center_col:
        with st.container(border=True):
            st.markdown(f"""
                <div style="text-align:center; margin-bottom:1.5rem;">
                    <div style="display:inline-flex; align-items:center; justify-content:center; width:48px; height:48px; border-radius:12px; background:rgba(99, 102, 241, 0.15); border:1px solid rgba(99, 102, 241, 0.3); margin-bottom:0.75rem;">
                        <span style="font-size:1.4rem;">🔐</span>
                    </div>
                    <h2 style="margin:0; font-size:1.55rem; color:{title_color};">Faculty Sign In</h2>
                    <p style="margin:4px 0 0 0; color:{sub_color}; font-size:0.88rem;">Authenticate to manage courses and execute AI attendance</p>
                </div>
            """, unsafe_allow_html=True)

            teacher_username = st.text_input("Username", placeholder='e.g. prof_sharma')
            teacher_pass = st.text_input("Password", type='password', placeholder="Enter your account password")

            st.markdown("<div style='margin-top:1rem;'></div>", unsafe_allow_html=True)
            btn1, btn2 = st.columns(2)
            with btn1:
                if st.button('Sign In →', type='primary', width='stretch'):
                    if login_teacher(teacher_username, teacher_pass):
                        st.toast("Authenticated successfully!", icon="✅")
                        time.sleep(0.5)
                        st.rerun()
                    else:
                        st.error("Invalid username or password.")
            with btn2:
                if st.button('Create Account', type='secondary', width='stretch'):
                    st.session_state.teacher_login_type = 'register'
                    st.rerun()

    footer_dashboard()


def teacher_screen_register():
    is_dark = (st.session_state.get('theme_mode', 'light') == 'dark')
    title_color = "#F8FAFC" if is_dark else "#0F172A"
    sub_color = "#94A3B8" if is_dark else "#64748B"

    c1, c2 = st.columns([3, 1], vertical_alignment='center')
    with c1:
        header_dashboard()
    with c2:
        if st.button("← Return to Gateway", type='secondary', key='back_btn_reg'):
            st.session_state['login_type'] = None
            st.rerun()

    _, center_col, _ = st.columns([1, 2.4, 1])
    with center_col:
        with st.container(border=True):
            st.markdown(f"""
                <div style="text-align:center; margin-bottom:1.5rem;">
                    <div style="display:inline-flex; align-items:center; justify-content:center; width:48px; height:48px; border-radius:12px; background:rgba(16, 185, 129, 0.15); border:1px solid rgba(16, 185, 129, 0.3); margin-bottom:0.75rem;">
                        <span style="font-size:1.4rem;">📝</span>
                    </div>
                    <h2 style="margin:0; font-size:1.55rem; color:{title_color};">Register Faculty Profile</h2>
                    <p style="margin:4px 0 0 0; color:{sub_color}; font-size:0.88rem;">Join the automated biometric attendance system</p>
                </div>
            """, unsafe_allow_html=True)

            teacher_username = st.text_input("Username", placeholder='e.g. dr_verma')
            teacher_name = st.text_input("Full Name", placeholder='e.g. Dr. Rajesh Verma')
            teacher_pass = st.text_input("Password", type='password', placeholder="Create a secure password")
            teacher_pass_confirm = st.text_input("Confirm Password", type='password', placeholder="Re-enter password")

            st.markdown("<div style='margin-top:1rem;'></div>", unsafe_allow_html=True)
            btn1, btn2 = st.columns(2)
            with btn1:
                if st.button('Register Account', type='primary', width='stretch'):
                    success, message = register_teacher(teacher_username, teacher_name, teacher_pass, teacher_pass_confirm)
                    if success:
                        st.success(message)
                        time.sleep(1.2)
                        st.session_state.teacher_login_type = "login"
                        st.rerun()
                    else:
                        st.error(message)
            with btn2:
                if st.button('Back to Sign In', type='secondary', width='stretch'):
                    st.session_state.teacher_login_type = 'login'
                    st.rerun()

    footer_dashboard()