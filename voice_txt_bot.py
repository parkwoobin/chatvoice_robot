import streamlit as st
from audiorecorder import audiorecorder
import openai
import os
from datetime import datetime
from gtts import gTTS
import base64


##### 기능 구현 함수 #####
def STT(audio, apikey):
    # 파일 저장
    filename='input.mp3'
    audio.export(filename, format="mp3")

    # 음원 파일 열기
    audio_file = open(filename, "rb")
    # Whisper 모델을 활용해 텍스트 얻기
    client = openai.OpenAI(api_key = apikey)
    respons = client.audio.transcriptions.create(model = "whisper-1", file = audio_file)
    audio_file.close()
    # 파일 삭제
    os.remove(filename)
    return respons. text

def voice_ask_gpt(prompt, model, apikey):
    client = openai.OpenAI(api_key = apikey)
    voice_response = client.chat.completions.create(model=model, messages=prompt)
    voice_gptResponse = voice_response.choices[0].message.content
    return voice_gptResponse

def txt_ask_gpt(prompt, model, apikey):
    client = openai.OpenAI(api_key = apikey)
    txt_response = client.chat.completions.create(model=model, messages=prompt)
    txt_gptResponse = txt_response.choices[0].message.content
    return txt_gptResponse

    
def main():
    st.set_page_config(
        page_title="음성 진우 프로그램", layout="wide")

# 제목
    st.header("음성 진우 프로그램")

# 구분선
    st.markdown(" --- ")

# 기본 설명
    with st.expander("음성진우 프로그램에 관하여", expanded=True):
        st.write(
        """
        - 음성진우 프로그램의 UI는 스트림릿을 활용하여 만들었습니다.
        - STT(Speech-To-Text)는 OpenAI의 Whisper AI를 활용하였습니다.
        - 답변은 OpenAI의 GPT 모델을 활용하였습니다.
        - TTS(Text-To-Speech)는 구글의 Google Translate TTS를 활용하였습니다.
        - 이 프로그램은 이승우, 박우빈이 공동으로 제작하였습니다.
        """)

        st.markdown("---")


        # session state 초기화
        if "chat" not in st.session_state:
            st.session_state["chat"] = []

        if "OPENAI_API" not in st.session_state:
            st.session_state["OPENAI_API"] = ""

        if "messages" not in st.session_state:
            st.session_state["messages"] = [{"role": "assistant", "content": "You are Jinwoo Park who goes to Gangnam University, Speak informally in Korean."}]

        if "check_audio" not in st.session_state:
            st.session_state["check_reset"] = False

    with st.sidebar:
        st.session_state["OPENAI_API"] = st.text_input(label="OPENAI API 키", placeholder="Enter your api", value="", type="password")
        st.markdown(" --- ")
        # GPT 모델 선택하기 위한 라디오 버튼 생성
        model = st.radio(label="GPT 모델", options=["gpt-4","gpt-3.5-turbo"])
        st.markdown(" --- ")

        # 리셋 버튼 생성
        if st.button(label="초기화"):
        # 리셋 코드
            st.session_state["chat"] = []
            st.session_state["messages"] = [{"role": "assistant", "content": "You are Jinwoo Park who goes to Gangnam University, Speak informally in Korean."}]
            st.session_state["check_reset"] = True

        
    #기능 구현 공간
    col1, col2 = st.columns(2)
    with col1: # 왼쪽 영역 작성
        #question_type = st.radio("질문 유형", ["음성", "텍스트"])

        #if question_type == "음성":
            st.subheader("음성 질문")
            audio = audiorecorder("음성 질문", "녹음 중 ... ")
            if (audio.duration_seconds > 0) and (st.session_state["check_reset"] == False):
                # 음성 재생
                st.audio(audio.export().read())
                # 음원 파일에서 텍스트 추출
                question = STT(audio, st.session_state["OPENAI_API"])

                # 채팅을 시각화하기 위해 질문 내용 저장
                now = datetime.now().strftime("%H:%M")
                st.session_state["chat"] = st.session_state["chat"]+[("user",now, question)]
                # GPT 모델에 넣을 프롬프트를 위해 질문 내용 저장
                st.session_state["messages"] = st.session_state["messages"]+[{"role": "user", "content": question}]

        #elif question_type == "텍스트":
            st.subheader("텍스트 질문")
            user_question = st.text_input(label="질문을 입력하세요")
            now = datetime.now().strftime("%H:%M")
            if st.button("질문하기"):
                if user_question:
                    st.session_state["chat"] = st.session_state["chat"]+[("user", now, user_question)]
                    st.session_state["messages"] = st.session_state["messages"]+[{"role":"user","content": user_question}]
        

    with col2: # 오른쪽 영역 작성
        st.subheader("답변")
        voice_response = txt_response = None

        if (audio.duration_seconds > 0) and (not st.session_state["check_reset"]):
            voice_response = voice_ask_gpt(st.session_state["messages"], model, st.session_state["OPENAI_API"])
            if voice_response:
                now = datetime.now().strftime("%H:%M")
                st.session_state["chat"] = st.session_state["chat"] + [("bot", now, voice_response)]
                st.session_state["messages"] = st.session_state["messages"] + [{"role": "system", "content": voice_response}]
                
                for sender, time, message in st.session_state["chat"]:
                    if sender == "user":
                        st.write(f'<div style="display:flex;align-items:center;"><div style="background-color:#007AFF;color:white;border-radius:12px;padding:8px 12px;margin-right:8px;">{message}</div><div style="font-size:0.8rem;color:gray;">{time}</div></div>', unsafe_allow_html=True)
                        st.write("")                  
                    else:
                        st.write(f'<div style="display:flex;align-items:center;justify-content:flex-end;"><div style="font-size:0.8rem;color:gray;">{time}</div><div style="background-color:lightgray;border-radius:12px;padding:8px 12px;margin-left:8px;">{message}</div></div>', unsafe_allow_html=True)
                        st.write("")

        elif user_question and (not st.session_state["check_reset"]):
            txt_response = txt_ask_gpt(st.session_state["messages"], model, st.session_state["OPENAI_API"])
            if txt_response:
            # ChatGPT에게 답변 얻기
                now = datetime.now().strftime("%H:%M")
                st.session_state["chat"] = st.session_state["chat"] + [("bot", now, txt_response)]
                st.session_state["messages"] = st.session_state["messages"] + [{"role": "system", "content": txt_response}]
                
                for sender, time, message in st.session_state["chat"]:
                    if sender == "user":
                        st.write(f'<div style="display:flex;align-items:center;"><div style="background-color:#007AFF;color:white;border-radius:12px;padding:8px 12px;margin-right:8px;">{message}</div><div style="font-size:0.8rem;color:gray;">{time}</div></div>', unsafe_allow_html=True)
                        st.write("")                  
                    else:
                        st.write(f'<div style="display:flex;align-items:center;justify-content:flex-end;"><div style="font-size:0.8rem;color:gray;">{time}</div><div style="background-color:lightgray;border-radius:12px;padding:8px 12px;margin-left:8px;">{message}</div></div>', unsafe_allow_html=True)
                        st.write("")
                
        

if __name__=="__main__":
    main()