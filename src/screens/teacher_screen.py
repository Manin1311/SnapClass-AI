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

    # Top Navigation & Profile Bar — theme toggle in top-right next to Sign Out
    c1, c3 = st.columns([2.5, 1.5], vertical_alignment='center')
    with c1:
        header_dashboard()
    with c3:
        from src.components.header import render_theme_toggle
        tgl_col, info_col = st.columns([1, 3], vertical_alignment='center')
        with tgl_col:
            render_theme_toggle(compact=True, key="theme_toggle_dash")
        with info_col:
            st.markdown(f"""
                <div style="display:flex; flex-direction:column; align-items:flex-end; gap:2px; padding-right:4px;">
                    <div style="font-weight:700; color:{name_color}; font-size:0.9rem; line-height:1;">{teacher_data['name']}</div>
                    <div style="font-size:0.72rem; color:#4F46E5; font-weight:700; letter-spacing:0.3px;">Faculty</div>
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
    is_dark = (st.session_state.get('theme_mode', 'light') == 'dark')

    # Theme tokens
    text_primary = "#F8FAFC" if is_dark else "#0F172A"
    text_secondary = "#94A3B8" if is_dark else "#475569"
    text_muted = "#64748B"
    card_bg = "rgba(17, 24, 39, 0.7)" if is_dark else "#FFFFFF"
    card_border = "rgba(255, 255, 255, 0.08)" if is_dark else "#E2E8F0"
    card_shadow = "0 10px 25px -5px rgba(0,0,0,0.5)" if is_dark else "0 4px 12px -2px rgba(0,0,0,0.05)"
    row_bg = "rgba(255,255,255,0.03)" if is_dark else "#F8FAFC"
    row_border = "rgba(255,255,255,0.06)" if is_dark else "#E2E8F0"
    badge_bg = "rgba(79,70,229,0.12)" if is_dark else "#EEF2FF"
    badge_color = "#818CF8" if is_dark else "#4338CA"
    present_color = "#34D399" if is_dark else "#16A34A"
    present_bg = "rgba(16,185,129,0.12)" if is_dark else "#DCFCE7"
    absent_color = "#FC8181" if is_dark else "#DC2626"
    absent_bg = "rgba(239,68,68,0.1)" if is_dark else "#FEF2F2"

    col1, col2 = st.columns([3, 1], vertical_alignment='center')
    with col1:
        st.markdown(f"""
            <div>
                <h2 style="margin:0; font-size:1.45rem; color:{text_primary};">Course &amp; Roster Management</h2>
                <p style="margin:2px 0 0 0; color:{text_secondary}; font-size:0.88rem;">Create courses, manage sections, view enrolled student rosters &amp; attendance statistics.</p>
            </div>
        """, unsafe_allow_html=True)
    with col2:
        if st.button('+ Create New Subject', type='primary', width='stretch'):
            create_subject_dialog(teacher_id)

    st.markdown("<hr style='margin:1.5rem 0;'>", unsafe_allow_html=True)

    if not subjects:
        st.info("No courses registered yet. Click 'Create New Subject' above to set up your first class!")
        return

    for sub in subjects:
        subject_id = sub['subject_id']
        total_s = sub.get('total_students', 0)
        total_c = sub.get('total_classes', 0)

        # ── Subject Header ──
        hcol1, hcol2 = st.columns([4, 1.4], vertical_alignment='center')
        with hcol1:
            st.markdown(f"""
                <div style="background:{card_bg}; border:1px solid {card_border}; border-radius:14px; padding:1.1rem 1.4rem; box-shadow:{card_shadow}; position:relative; overflow:hidden; margin-bottom:0.35rem;">
                    <div style="position:absolute; top:0; left:0; width:100%; height:3px; background:linear-gradient(90deg, #4F46E5, #38BDF8);"></div>
                    <div style="display:flex; align-items:center; gap:10px; flex-wrap:wrap;">
                        <h3 style="margin:0; color:{text_primary}; font-size:1.1rem; font-weight:800;">{sub['name']}</h3>
                        <span style="background:{badge_bg}; border:1px solid rgba(79,70,229,0.25); color:{badge_color}; font-family:'JetBrains Mono', monospace; font-weight:700; font-size:0.78rem; padding:1px 8px; border-radius:5px;">{sub['subject_code']}</span>
                        <span style="color:{text_muted}; font-size:0.8rem;">Sec {sub.get('section', 'A')}</span>
                        <span style="color:{text_muted}; font-size:0.8rem;">·</span>
                        <span style="color:{text_muted}; font-size:0.8rem;">👥 {total_s} students</span>
                        <span style="color:{text_muted}; font-size:0.8rem;">·</span>
                        <span style="color:{text_muted}; font-size:0.8rem;">🗓️ {total_c} sessions</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)

        with hcol2:
            sc1, sc2 = st.columns(2)
            with sc1:
                if st.button("🔗 QR", key=f"qr_{subject_id}", type='secondary', help="Share Join Link / QR Code", width='stretch'):
                    share_subject_dialog(sub['name'], sub['subject_code'])
            with sc2:
                expand_key = f"expand_roster_{subject_id}"
                if expand_key not in st.session_state:
                    st.session_state[expand_key] = False
                btn_label = "▲ Hide" if st.session_state[expand_key] else "👥 Roster"
                if st.button(btn_label, key=f"roster_btn_{subject_id}", type='secondary', width='stretch'):
                    st.session_state[expand_key] = not st.session_state[expand_key]
                    st.rerun()

        # ── Student Roster (expandable) ──
        if st.session_state.get(f"expand_roster_{subject_id}", False):
            enrolled_res = supabase.table('subject_students').select("*, students(*)").eq('subject_id', subject_id).execute()
            enrolled = enrolled_res.data or []

            att_res = supabase.table('attendance_logs').select("student_id, is_present, timestamp").eq('subject_id', subject_id).execute()
            att_logs = att_res.data or []

            from collections import defaultdict
            student_att = defaultdict(lambda: {'present': 0, 'total': 0})
            seen_sessions = defaultdict(set)
            for log in att_logs:
                sid = log['student_id']
                ts = log.get('timestamp', '')
                session_key = ts.split('.')[0] if ts else ts
                if session_key not in seen_sessions[sid]:
                    seen_sessions[sid].add(session_key)
                    student_att[sid]['total'] += 1
                    if log.get('is_present'):
                        student_att[sid]['present'] += 1

            st.markdown(f"""
                <div style="margin:0.2rem 0 0.5rem 0; padding:0.5rem 1rem; background:{badge_bg}; border:1px solid rgba(79,70,229,0.2); border-radius:8px;">
                    <span style="font-size:0.73rem; font-weight:700; color:{badge_color}; text-transform:uppercase; letter-spacing:0.5px;">
                        Student Roster — {len(enrolled)} Enrolled
                    </span>
                </div>
            """, unsafe_allow_html=True)

            if not enrolled:
                st.markdown(f"""
                    <div style="background:{row_bg}; border:1px solid {row_border}; border-radius:10px; padding:1.25rem; text-align:center; color:{text_muted}; font-size:0.9rem; margin-bottom:1rem;">
                        No students enrolled yet. Share the QR code so students can join!
                    </div>
                """, unsafe_allow_html=True)
            else:
                for node in enrolled:
                    student = node.get('students', {})
                    if not student:
                        continue
                    sid = student.get('student_id')
                    sname = student.get('name', 'Unknown')
                    att = student_att[sid]
                    present = att['present']
                    total = att['total']
                    pct = round(present / total * 100) if total > 0 else 0
                    pct_color = present_color if pct >= 75 else absent_color
                    pct_bg_val = present_bg if pct >= 75 else absent_bg
                    status_icon = "✅" if pct >= 75 else "⚠️"
                    status_tip = "Eligible" if pct >= 75 else "Below 75%"

                    rcol1, rcol2 = st.columns([6, 1], vertical_alignment='center')
                    with rcol1:
                        st.markdown(f"""
                            <div style="background:{row_bg}; border:1px solid {row_border}; border-radius:10px; padding:0.6rem 1rem; margin-bottom:6px; display:flex; align-items:center; gap:0; flex-wrap:wrap;">
                                <div style="flex:2; min-width:120px;">
                                    <span style="font-weight:700; color:{text_primary}; font-size:0.92rem;">{status_icon} {sname}</span>
                                </div>
                                <div style="flex:1.5; min-width:80px;">
                                    <span style="font-family:'JetBrains Mono', monospace; font-size:0.78rem; color:{badge_color}; font-weight:600;">#{sid}</span>
                                </div>
                                <div style="flex:0.8; min-width:50px;">
                                    <span style="font-weight:700; color:{present_color}; font-size:0.9rem;">{present}</span>
                                    <span style="color:{text_muted}; font-size:0.8rem;">/{total}</span>
                                </div>
                                <div style="flex:1; min-width:70px;">
                                    <span style="background:{pct_bg_val}; color:{pct_color}; font-weight:800; font-size:0.82rem; padding:2px 9px; border-radius:20px;">{pct}% · {status_tip}</span>
                                </div>
                            </div>
                        """, unsafe_allow_html=True)
                    with rcol2:
                        if st.button("🗑️", key=f"remove_{subject_id}_{sid}", type='secondary', width='stretch', help=f"Remove {sname} from this course"):
                            from src.database.db import unenroll_student_to_subject
                            unenroll_student_to_subject(sid, subject_id)
                            st.toast(f"Removed {sname} from roster.", icon="🗑️")
                            st.rerun()

            st.markdown("<div style='margin-bottom:0.75rem;'></div>", unsafe_allow_html=True)

        st.markdown("<div style='margin-bottom:1.25rem;'></div>", unsafe_allow_html=True)


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