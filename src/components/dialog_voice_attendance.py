import streamlit as st
from datetime import datetime
import pandas as pd

from src.pipelines.voice_pipeline import process_bulk_audio
from src.database.config import supabase
from src.components.dialog_attendance_results import show_attendance_result


@st.dialog('Voice Biometric Verification')
def voice_attendance_dialog(selected_subject_id):
    st.markdown("""
        <p style="color:#94A3B8; font-size:0.88rem; margin-bottom:1rem;">
            Record classroom audio of students stating presence. Deep learning voice encoder splits utterances and matches registered speaker vectors.
        </p>
    """, unsafe_allow_html=True)

    audio_data = st.audio_input("Record Classroom Audio Feed")

    if st.button('⚡ Analyze Speech Biometrics', width='stretch', type='primary'):
        if not audio_data:
            st.warning("Please record audio before analyzing.")
            return

        with st.spinner('Deconvolving audio segments and comparing voice embeddings...'):
            enrolled_res = supabase.table('subject_students').select("*, students(*)").eq('subject_id', selected_subject_id).execute()
            enrolled_students = enrolled_res.data

            if not enrolled_students:
                st.warning('No students are enrolled in this course roster.')
                return

            candidates_dict = {
                s['students']['student_id']: s['students']['voice_embedding'] 
                for s in enrolled_students if s['students'].get('voice_embedding')
            }

            if not candidates_dict:
                st.error('None of the enrolled students have voice embeddings registered yet.')
                return

            audio_bytes = audio_data.read()
            detected_scores = process_bulk_audio(audio_bytes, candidates_dict)

            results, attendance_to_log = [], []
            current_timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

            for node in enrolled_students:
                student = node['students']
                score = detected_scores.get(student['student_id'], 0.0)
                is_present = bool(score > 0)

                results.append({
                    "Name": student['name'],
                    "Student ID": student['student_id'],
                    "Cosine Match Score": f"{score:.3f}" if is_present else "Unmatched",
                    "Status": "✅ Present" if is_present else "❌ Absent"
                })

                attendance_to_log.append({
                    'student_id': student['student_id'],
                    'subject_id': selected_subject_id,
                    'timestamp': current_timestamp,
                    'is_present': bool(is_present)
                })

            st.session_state.voice_attendance_results = (pd.DataFrame(results), attendance_to_log)

    if st.session_state.get('voice_attendance_results'):
        st.markdown("<hr style='margin:1.2rem 0;'>", unsafe_allow_html=True)
        df_results, logs = st.session_state.voice_attendance_results
        show_attendance_result(df_results, logs)
