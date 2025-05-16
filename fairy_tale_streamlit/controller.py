import os
import openai
import tempfile
from playsound import playsound
import asyncio
from dotenv import load_dotenv
import streamlit as st
from openai import OpenAI

load_dotenv()  # .env 파일에서 환경변수 로드

# OpenAI API 키 가져오기
#openai_api_key = os.getenv('OPENAI_API_KEY')

# 1. 변수에 값 할당하기
openai_api_key = st.secrets["OpenAI"]["OPENAI_API_KEY"]

# 2. 값이 없으면 에러 처리
if not openai_api_key:
    raise ValueError("환경변수 'OPENAI_API_KEY'가 설정되지 않았습니다.")

# 3. openai에 API 키 등록
openai.api_key = openai_api_key

client = OpenAI(api_key=openai_api_key)

# 동화 생성 함수
def generate_fairy_tale(thema):
    prompt = (
        f"너는 동화 작가야. '{thema}'을 주제로 하는 길고 풍부한 동화를 생성해줘. "
        "등장인물, 배경, 사건 등의 디테일을 포함하고, 엄마가 아이에게 읽어주듯 친절한 말투로 써줘."
    )
    try:
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=4096,
            temperature=0.5
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"동화 생성 중 오류 발생: {e}"


# 비동기 음성 재생 함수
async def play_openai_voice(text, voice_name="alloy", speed=1):
    tmp_path = None

    try:
        # OpenAI TTS API 호출
        response = client.audio.speech.create(
            model="tts-1",
            voice=voice_name,
            input=text
        )

        # 임시 MP3 파일 생성
        if hasattr(response, 'content') and response.content:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
                tmp_file.write(response.content)
                tmp_path = tmp_file.name

            # playsound는 blocking이므로 executor로 실행
            loop = asyncio.get_running_loop()
            await loop.run_in_executor(None, playsound, tmp_path)
        else:
            print("TTS 응답이 비어있습니다.")
    except Exception as e:
        print(f"음성 생성/재생 중 오류: {e}")
    finally:
        if tmp_path and os.path.exists(tmp_path):
            await asyncio.sleep(1)
            try:
                os.remove(tmp_path)
            except Exception as e:
                print(f"파일 삭제 중 오류 발생: {e}")


# 비동기 이미지 생성 함수
async def generate_image_from_fairy_tale(fairy_tale_text):
    prompt = f"동화 속 장면을 묘사하는 그림을 그려줘: {fairy_tale_text[:300]}"
    try:
        response = openai.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            n=1
        )

        if hasattr(response, "data") and response.data and len(response.data) > 0:
            return response.data[0].url
        else:
            print("이미지 생성 실패: 응답이 비어 있거나 형식이 잘못됨.")
            return None
    except Exception as e:
        print(f"이미지 생성 중 오류: {e}")
        return None
