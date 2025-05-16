import streamlit as st
import asyncio
from controller import generate_fairy_tale, play_openai_voice, generate_image_from_fairy_tale

# 초기 상태 설정
if 'fairy_tale_text' not in st.session_state:
    st.session_state.fairy_tale_text = ""

if 'image_url' not in st.session_state:
    st.session_state.image_url = None

# Streamlit 앱 설정
title = "태교 동화 생성봇"
st.markdown("# 인공지능 비서 동글이입니다.")
st.subheader("태아를 위한 동화를 생성해 드립니다.")

# 속도 버튼
speed = st.slider("속도를 선택해 주세요", 0, 2, 1) # 최소, 최대, 기본값값
st.write("선택한 속도:", speed)

# 테마 버튼
thema = st.selectbox("테마를 선택해 주세요", ["자연", "모험", "가족", "사랑", "우정", "교훈", "동물"])
st.write("선택한 테마:", thema)

# 목소리 선택
voice_choices = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
voice = st.selectbox("목소리를 선택해 주세요", voice_choices)
st.write("선택한 목소리:", voice)

# 동화 생성 버튼
if st.button("동화 생성"):
    st.session_state.fairy_tale_text = generate_fairy_tale(thema)  # 동화 생성
    st.success("동화가 생성되었습니다!")  # 사용자 피드백

# 동화 내용 표시
st.text_area("생성된 동화:", st.session_state.fairy_tale_text, height=300)

# 음성으로 듣기 버튼 (비동기로 실행)
if st.button("음성으로 듣기"):
    if st.session_state.fairy_tale_text:
        asyncio.run(play_openai_voice(
            st.session_state.fairy_tale_text, voice, speed
        ))
    else:
        st.warning("먼저 동화를 생성해주세요.")

# 이미지 생성 버튼 (동기 함수 내부에서 비동기 함수 실행)
if st.button("동화 이미지 생성"):
    if st.session_state.fairy_tale_text:
        async def load_image():
            image_url = await generate_image_from_fairy_tale(st.session_state.fairy_tale_text)
            if image_url:
                st.session_state.image_url = image_url
                st.success("이미지가 생성되었습니다!")
            else:
                st.warning("이미지 생성 중 오류가 발생했습니다.")

        asyncio.run(load_image())
    else:
        st.warning("먼저 동화를 생성해주세요.")

# 이미지 표시
if st.session_state.image_url:
    st.image(st.session_state.image_url, caption="동화 이미지", use_container_width=True)
