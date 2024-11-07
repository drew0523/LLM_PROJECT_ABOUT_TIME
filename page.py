import streamlit as st
import time
import base64
from api import *
def get_base64_image(image_path):
    with open(image_path, "rb") as image_file:
        encoded = base64.b64encode(image_file.read()).decode()
    return encoded

# 입력 페이지 함수
def input_page():
    image_path = "main.png"
    encoded_image = get_base64_image(image_path)
    st.markdown(
    f"""
    <style>
    .stApp {{
        background-image: url("data:image/jpeg;base64,{encoded_image}");
        background-attachment: fixed;
        background-size: cover;
    }}
    h1 {{
        font-size: 5em;  /* 제목 크기 조정 */
        color: white;    /* 제목 색상 조정 */
        text-align: center;  /* 제목 정렬 */
        margin-top: 20px; /* 제목 상단 여백 */
    }}
    </style>
    """,
    unsafe_allow_html=True
    )

    st.title("어바웃 타임")
    st.write("상대방과의 대화 내역과 특별한 정보를 입력하세요.")

    uploaded_file = st.file_uploader("상대방과의 대화 내역 (txt 파일)", type="txt")
    special_info = st.text_area("사용자가 알고 있는 특별한 정보")

    if st.button("챗봇 생성"):
        if uploaded_file is not None and special_info:
            name, chat_log= parse(uploaded_file)
            st.session_state.name = name
            st.session_state.uploaded_file = chat_log
            st.session_state.special_info = special_info
            st.session_state.isload = False
            st.session_state.page = "chatbot"
            st.rerun() 
        else:
            st.error("모든 정보를 입력해 주세요.")

# 챗봇 페이지 함수
def chatbot_page():
    logo_path = "logo.png"
    encoded_logo = get_base64_image(logo_path)
    st.markdown(
        f"""
        <div style="text-align: center; margin-bottom: 30px;">
            <img src="data:image/png;base64,{encoded_logo}" alt="Logo" style="width: 2000px; height: auto;">
        </div>
        """,
        unsafe_allow_html=True
    )
    if(st.session_state.isload == False):
        with st.spinner("챗봇 생성중..."):
            st.session_state.persona=make_persona(st.session_state)
            st.session_state.summary_log = summarey(st.session_state)
            st.session_state.tips_log = tips(st.session_state)
            st.session_state.date_course = date_course(st.session_state)
            st.session_state.isload = True

    st.title(f"{st.session_state.name}님의 특징!")
    st.write(st.session_state.summary_log)
    st.title("연애 팁!")
    st.write(st.session_state.tips_log)
    st.title("데이트 코스 추천!")
    st.write(st.session_state.date_course)

    chat_input = st.text_input("다음 답장 입력:")

    if st.button("평가"):
        st.session_state.chat_input = chat_input
        st.write(evaluate(st.session_state))