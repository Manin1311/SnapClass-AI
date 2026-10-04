import streamlit as st
from src.database.db import create_attendance


def show_attendance_result(df, logs):
    present_count = df[df['Status'].str.contains('Present')].shape[0] if 'Status' in df.columns else 0
    total_count = len(df)
    absent_count = total_count - present_count
    pct = (present_count / total_count * 100) if total_count > 0 else 0

    st.markdown(f"""
        <div style="background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.08); border-radius:12px; padding:1rem; margin-bottom:1rem; display:flex; justify-content:space-between; align-items:center;">
            <div>
                <div style="font-size:0.75rem; color:#94A3B8; text-transform:uppercase; font-weight:700;">Detection Summary</div>
                <div style="font-size:1.3rem; font-weight:800; color:#F8FAFC; margin-top:2px;">
                    {present_count} <span style="font-size:0.9rem; color:#64748B;">/ {total_count}</span> <span style="color:#10B981; font-size:1rem;">({pct:.0f}%)</span>
                </div>
            </div>
            <div style="display:flex; gap:8px;">
                <span style="background:rgba(16, 185, 129, 0.15); border:1px solid rgba(16, 185, 129, 0.3); color:#34D399; padding:4px 10px; border-radius:6px; font-size:0.8rem; font-weight:600;">✅ {present_count} Present</span>
                <span style="background:rgba(244, 63, 94, 0.15); border:1px solid rgba(244, 63, 94, 0.3); color:#FB7185; padding:4px 10px; border-radius:6px; font-size:0.8rem; font-weight:600;">❌ {absent_count} Absent</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.dataframe(df, hide_index=True, use_container_width=True)

    col1, col2 = st.columns(2)

    with col1:
        if st.button('Discard Session', width='stretch', type='secondary'):
            st.session_state.voice_attendance_results = None
            st.session_state.attendance_images = []
            st.rerun()

    with col2:
        if st.button('Confirm & Commit to Cloud →', width='stretch', type='primary'):
            try:
                create_attendance(logs)
                st.toast("Attendance successfully recorded to Supabase!", icon="✅")
                st.session_state.attendance_images = []
                st.session_state.voice_attendance_results = None
                st.rerun()
            except Exception as e:
                st.error(f'Sync failed: {str(e)}')


@st.dialog("Review Attendance Verification")
def attendance_result_dialog(df, logs):
    show_attendance_result(df, logs)
