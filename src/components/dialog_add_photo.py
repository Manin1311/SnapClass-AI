import streamlit as st
from PIL import Image


@st.dialog("Classroom Imagery Ingestion")
def add_photos_dialog():
    is_dark = (st.session_state.get('theme_mode', 'light') == 'dark')
    desc_color = "#94A3B8" if is_dark else "#475569"

    st.markdown(f"""
        <p style="color:{desc_color}; font-size:0.92rem; line-height:1.55; margin-bottom:1.25rem;">
            Provide classroom photos containing student faces. AI will detect and run multi-face embeddings simultaneously.
        </p>
    """, unsafe_allow_html=True)

    if 'photo_tab' not in st.session_state:
        st.session_state.photo_tab = 'camera'

    t1, t2 = st.columns(2)

    with t1:
        type_camera = "primary" if st.session_state.photo_tab == 'camera' else 'secondary'
        if st.button('📷 Live Camera Snap', type=type_camera, width='stretch'):
            st.session_state.photo_tab = 'camera'
            st.rerun()

    with t2:
        type_upload = "primary" if st.session_state.photo_tab == 'upload' else 'secondary'
        if st.button('📁 Upload Image Files', type=type_upload, width='stretch'):
            st.session_state.photo_tab = 'upload'
            st.rerun()

    st.markdown("<div style='margin-top:1rem;'></div>", unsafe_allow_html=True)

    if st.session_state.photo_tab == 'camera':
        cam_photo = st.camera_input('Capture Classroom Frame', key='dialog_cam')
        if cam_photo:
            st.session_state.attendance_images.append(Image.open(cam_photo))
            st.toast('Classroom snapshot added to queue!', icon="📸")
            st.rerun()

    if st.session_state.photo_tab == 'upload':
        uploaded_files = st.file_uploader(
            'Upload classroom images (JPG, PNG)', 
            type=['jpg', 'png', 'jpeg'], 
            accept_multiple_files=True, 
            key='dialog_upload'
        )

        if uploaded_files:
            for f in uploaded_files:
                st.session_state.attendance_images.append(Image.open(f))
            st.toast(f"{len(uploaded_files)} photo(s) queued for AI analysis!", icon="📁")
            st.rerun()

    st.markdown("<hr style='margin:1.2rem 0;'>", unsafe_allow_html=True)
    if st.button('Done & Review Queue →', type='primary', width='stretch'):
        st.rerun()
