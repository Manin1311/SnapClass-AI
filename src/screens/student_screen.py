import streamlit as st
import numpy as np
from PIL import Image
import time

from src.ui.base_layout import style_background_dashboard
from src.components.header import header_dashboard, render_theme_toggle
from src.components.footer import footer_dashboard
from src.pipelines.face_pipeline import predict_attendance, get_face_embeddings, train_classifier
from src.pipelines.voice_pipeline import get_voice_embedding
from src.database.db import (
    get_all_students, 
    create_student, 
    get_student_subjects, 
    get_student_attendance, 
    unenroll_student_to_subject
)
from src.components.dialog_enroll import enroll_dialog
from src.components.subject_card import subject_card


def student_screen():
    style_background_dashboard()

    if "student_data" in st.session_state:
        student_dashboard()
        return

    is_dark = (st.session_state.get('theme_mode', 'light') == 'dark')
    title_color = "#F8FAFC" if is_dark else "#0F172A"
    sub_color = "#94A3B8" if is_dark else "#64748B"

    # Top Navigation Bar with Theme Switcher
    c1, c2, c3 = st.columns([3, 1, 1], vertical_alignment='center')
    with c1:
        header_dashboard()
    with c2:
        render_theme_toggle()
    with c3:
        if st.button("← Return to Gateway", type='secondary', key='back_btn_stud', width='stretch'):
            st.session_state['login_type'] = None
            st.rerun()

    # Biometric FaceID Viewfinder Card
    st.markdown(f"""
        <div style="max-width:540px; margin:1.25rem auto 1.25rem auto; text-align:center;">
            <div style="display:inline-flex; align-items:center; gap:8px; padding:6px 14px; border-radius:30px; background:rgba(16, 185, 129, 0.1); border:1px solid rgba(16, 185, 129, 0.25); margin-bottom:0.75rem;">
                <span style="display:inline-block; width:8px; height:8px; border-radius:50%; background:#10B981; box-shadow:0 0 8px #10B981;"></span>
                <span style="font-size:0.75rem; font-weight:700; color:#059669; letter-spacing:0.5px; text-transform:uppercase;">Biometric Sensor Active</span>
            </div>
            <h2 style="margin:0; font-size:1.6rem; color:{title_color};">FaceID Biometric Authentication</h2>
            <p style="margin:6px 0 1.25rem 0; color:{sub_color}; font-size:0.9rem;">
                Align your face within the frame. AI instantly matches your facial embeddings to authenticate you.
            </p>
        </div>
    """, unsafe_allow_html=True)

    show_registration = False

    # Centered & Compact Camera Viewfinder Container
    col_cam_left, col_cam_center, col_cam_right = st.columns([1, 2.2, 1])
    with col_cam_center:
        photo_source = st.camera_input("Biometric Camera Scanner")

    if photo_source:
        img = np.array(Image.open(photo_source))

        with st.spinner('AI analyzing facial vector coordinates...'):
            detected, all_ids, num_faces = predict_attendance(img)

            if num_faces == 0:
                st.warning('⚠️ No face detected. Please ensure proper lighting and face the camera directly.')
            elif num_faces > 1:
                st.warning('⚠️ Multiple faces detected in frame. Please ensure only one student is in view.')
            else:
                if detected:
                    student_id = list(detected.keys())[0]
                    all_students = get_all_students()
                    student = next((s for s in all_students if s['student_id'] == student_id), None)

                    if student:
                        st.session_state.is_logged_in = True
                        st.session_state.user_role = 'student'
                        st.session_state.student_data = student
                        st.toast(f"Face Verified! Welcome, {student['name']}", icon="✅")
                        time.sleep(0.8)
                        st.rerun()
                else:
                    st.info('💡 Face recognized as new. Complete your profile registration below.')
                    show_registration = True

    # One-Time Registration Form inside Centered Container
    if show_registration:
        _, center_col, _ = st.columns([1, 2.4, 1])
        with center_col:
            with st.container(border=True):
                st.markdown(f"""
                    <div style="text-align:center; margin-bottom:1.25rem;">
                        <div style="font-size:1.5rem; margin-bottom:4px;">👤</div>
                        <h3 style="margin:0; font-size:1.3rem; color:{title_color};">Register Student Biometric Profile</h3>
                        <p style="color:{sub_color}; font-size:0.85rem; margin-top:2px;">Associate your facial embeddings with your student record</p>
                    </div>
                """, unsafe_allow_html=True)

                new_name = st.text_input("Full Name", placeholder='e.g. Akash Sharma')

                st.markdown(f"""
                    <div style="margin-top:1.2rem; margin-bottom:0.5rem;">
                        <span style="font-size:0.85rem; font-weight:600; color:{title_color};">🎙️ Voice Enrollment (Optional)</span>
                        <p style="color:{sub_color}; font-size:0.78rem; margin:2px 0 0 0;">Record a voice sample to enable multimodal voice attendance verification.</p>
                    </div>
                """, unsafe_allow_html=True)

                audio_data = None
                try:
                    audio_data = st.audio_input('Record phrase: "I am present, my name is..."')
                except Exception:
                    pass

                if st.button('✨ Complete Biometric Registration', type='primary', width='stretch'):
                    if new_name:
                        with st.spinner('Extracting vector descriptors and training neural classifier...'):
                            img = np.array(Image.open(photo_source))
                            encodings = get_face_embeddings(img)
                            if encodings:
                                face_emb = encodings[0].tolist()
                                voice_emb = None
                                if audio_data:
                                    voice_emb = get_voice_embedding(audio_data.read())

                                response_data = create_student(new_name, face_embedding=face_emb, voice_embedding=voice_emb)

                                if response_data:
                                    train_classifier()
                                    st.session_state.is_logged_in = True
                                    st.session_state.user_role = 'student'
                                    st.session_state.student_data = response_data[0]
                                    st.toast(f"Profile created successfully! Welcome, {new_name}", icon="🎉")
                                    time.sleep(1)
                                    st.rerun()
                            else:
                                st.error('Could not extract facial feature coordinates. Please capture a clearer front-facing photo.')
                    else:
                        st.warning('Please enter your full name to proceed.')

    footer_dashboard()


def student_dashboard():
    student_data = st.session_state.student_data
    student_id = student_data['student_id']
    is_dark = (st.session_state.get('theme_mode', 'light') == 'dark')

    name_color = "#F8FAFC" if is_dark else "#0F172A"
    card_bg = "rgba(17, 24, 39, 0.7)" if is_dark else "#FFFFFF"
    card_border = "rgba(255, 255, 255, 0.08)" if is_dark else "#E2E8F0"
    card_shadow = "0 8px 24px -6px rgba(0,0,0,0.3)" if is_dark else "0 4px 12px -2px rgba(0, 0, 0, 0.05)"

    # Top Student Header
    c1, c2, c3 = st.columns([2.5, 1, 1], vertical_alignment='center')
    with c1:
        header_dashboard()
    with c2:
        render_theme_toggle()
    with c3:
        st.markdown(f"""
            <div style="display:flex; justify-content:flex-end; align-items:center; gap:10px;">
                <div style="text-align:right;">
                    <div style="font-weight:700; color:{name_color}; font-size:0.95rem;">{student_data['name']}</div>
                    <div style="font-size:0.75rem; color:#10B981; font-weight:600;">ID: #{student_id} • Student</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        if st.button("Sign Out", type='secondary', key='logout_student', width='stretch'):
            st.session_state['is_logged_in'] = False
            del st.session_state.student_data
            st.rerun()

    with st.spinner('Syncing academic course records...'):
        subjects = get_student_subjects(student_id)
        logs = get_student_attendance(student_id)

    stats_map = {}
    for log in logs:
        sid = log['subject_id']
        if sid not in stats_map:
            stats_map[sid] = {"total": 0, "attended": 0}
        stats_map[sid]['total'] += 1
        if log.get('is_present'):
            stats_map[sid]['attended'] += 1

    # Calculate overall campus attendance stats
    overall_total = sum(s['total'] for s in stats_map.values())
    overall_attended = sum(s['attended'] for s in stats_map.values())
    overall_pct = (overall_attended / overall_total * 100) if overall_total > 0 else 100.0

    # 75% Attendance Criteria Gauge Banner
    if overall_pct >= 75.0:
        badge_bg = "rgba(16, 185, 129, 0.12)" if is_dark else "#ECFDF5"
        badge_border = "rgba(16, 185, 129, 0.3)" if is_dark else "#A7F3D0"
        badge_color = "#34D399" if is_dark else "#047857"
        status_label = "SAFE ZONE • ELIGIBLE FOR EXAMS (≥ 75%)"
        progress_color = "#10B981"
    elif overall_pct >= 65.0:
        badge_bg = "rgba(245, 158, 11, 0.12)" if is_dark else "#FFFBEB"
        badge_border = "rgba(245, 158, 11, 0.3)" if is_dark else "#FDE68A"
        badge_color = "#FBBF24" if is_dark else "#B45309"
        status_label = "WARNING • BORDERLINE ATTENDANCE"
        progress_color = "#F59E0B"
    else:
        badge_bg = "rgba(244, 63, 94, 0.12)" if is_dark else "#FFF1F2"
        badge_border = "rgba(244, 63, 94, 0.3)" if is_dark else "#FECDD3"
        badge_color = "#FB7185" if is_dark else "#BE123C"
        status_label = "CRITICAL ALERT • ATTENDANCE SHORTAGE (< 75%)"
        progress_color = "#F43F5E"

    st.markdown(f"""
        <div style="background:{card_bg}; border:1px solid {card_border}; border-radius:14px; padding:1.5rem; margin:1.5rem 0 2rem 0; box-shadow:{card_shadow};">
            <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px;">
                <div>
                    <div style="display:inline-flex; align-items:center; gap:6px; padding:4px 10px; border-radius:6px; background:{badge_bg}; border:1px solid {badge_border}; font-size:0.75rem; font-weight:700; color:{badge_color};">
                        <span>●</span> {status_label}
                    </div>
                    <div style="font-size:1.6rem; font-weight:800; color:{name_color}; margin-top:6px; font-family:'Plus Jakarta Sans';">
                        {overall_pct:.1f}% <span style="font-size:0.95rem; font-weight:400; color:#64748B;">Campus Cumulative Attendance</span>
                    </div>
                </div>
                <div style="text-align:right;">
                    <div style="font-size:1.25rem; font-weight:700; color:{name_color};">{overall_attended} <span style="color:#94A3B8;">/</span> {overall_total}</div>
                    <div style="font-size:0.78rem; color:#64748B;">Lectures Attended</div>
                </div>
            </div>
            <div style="width:100%; height:8px; background:rgba(0,0,0,0.06); border-radius:4px; margin-top:14px; overflow:hidden;">
                <div style="width:{min(100, max(0, overall_pct))}%; height:100%; background:{progress_color}; border-radius:4px; transition:width 0.5s ease;"></div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Enrolled Courses Bar
    c1, c2 = st.columns([3, 1], vertical_alignment='center')
    with c1:
        st.markdown(f"""
            <div>
                <h2 style="margin:0; font-size:1.35rem; color:{name_color};">Enrolled Subject Rosters</h2>
                <p style="margin:2px 0 0 0; color:#64748B; font-size:0.85rem;">View course lecture breakdown and manage course enrollments.</p>
            </div>
        """, unsafe_allow_html=True)
    with c2:
        if st.button('➕ Enroll in Subject', type='primary', width='stretch'):
            enroll_dialog()

    st.markdown("<hr style='margin:1.2rem 0;'>", unsafe_allow_html=True)

    if subjects:
        cols = st.columns(2)
        for i, sub_node in enumerate(subjects):
            sub = sub_node['subjects']
            sid = sub['subject_id']
            stats = stats_map.get(sid, {"total": 0, "attended": 0})
            sub_pct = (stats['attended'] / stats['total'] * 100) if stats['total'] > 0 else 100.0

            def make_unenroll_button(course_name, course_id):
                def callback():
                    if st.button("🗑️ Drop Course", key=f"unenroll_{course_id}", type='secondary', width='stretch'):
                        unenroll_student_to_subject(student_id, course_id)
                        st.toast(f"Unenrolled from {course_name}", icon="ℹ️")
                        time.sleep(0.5)
                        st.rerun()
                return callback

            with cols[i % 2]:
                subject_card(
                    name=sub['name'],
                    code=sub['subject_code'],
                    section=sub.get('section', 'A'),
                    stats=[
                        ('📅', 'Lectures Held', stats['total']),
                        ('✅', 'Attended', stats['attended']),
                        ('📊', 'Rate', f"{sub_pct:.0f}%"),
                    ],
                    footer_callback=make_unenroll_button(sub['name'], sid)
                )
    else:
        st.info("You are not currently enrolled in any academic courses. Click 'Enroll in Subject' above to join your teacher's class!")

    footer_dashboard()