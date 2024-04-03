import streamlit as st
from audiorecorder import audiorecorder
import openai
import os
from datetime import datetime

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
    return respons.text

def ask_gpt(prompt, model, apikey):
    client = openai.OpenAI(api_key = apikey)
    response = client.chat.completions.create(model=model, messages=prompt)
    gptResponse = response.choices[0].message.content
    return gptResponse


def main():
    st.set_page_config(page_title="AI 진우 챗봇", page_icon="🐼")
    

    # 제목
    st.header("🐼 AI 진우 챗봇")
    st.caption("A streamlit chatbot powered by OpenAI ParkWB & LeeSW")

    # 기본 설명
    with st.expander("AI 진우 프로그램에 관하여", expanded=False):
        
        st.write(
            """
            - AI 진우 프로젝트 OpenAI API를 사용하였습니다.
            - GPT 모델의 선택이 가능합니다.(gpt-3.5-turbo, gpt-4)
            - STT(Speech-To-Text)는 OpenAI의 Whisper AI를 활용하였습니다.
            - Chat GPT API key를 입력하지 않으면 작동이 되지 않으니 주의 바랍니다.
            - 채팅 질문은 답변 아래에서, 음성 질문은 사이드바에서 가능합니다.
            """)
        st.markdown(" --- ")
        st.write(
            """
            - 강남대학교 박진우 학생을 모티브로 제작되었습니다.
            - 이 프로그램은 강남대학교 박우빈, 이승우 학생이 공동으로 제작하였습니다.
            """)

        # session state 초기화
        if "chat" not in st.session_state:
            st.session_state["chat"] = []

        if "OPENAI_API" not in st.session_state:
            st.session_state["OPENAI_API"] = ""

        if "messages" not in st.session_state:
            st.session_state["messages"] = [{"role": "assistant", "content": "나는 강남대학교에 다니는 박진우 chat bot이야"}]

        if "check_audio" not in st.session_state:
            st.session_state["check_reset"] = False

    with st.sidebar:

        st.session_state["OPENAI_API"] = st.text_input(label="OPENAI API 키", placeholder="Enter your API key", value="", type="password")
        st.markdown("""<style>div[class*="stTextInput"] > label > div[data-testid="stMarkdownContainer"] > p {font-size: 20px; font-weight: bold;}</style>""", unsafe_allow_html=True)
        

        st.markdown(" --- ")


        # GPT 모델 선택하기 위한 라디오 버튼 생성
        model = st.radio(label="GPT 모델", options=["gpt-3.5-turbo", "gpt-4"])
        st.markdown("""<style>div[class*="stRadio"] > label > div[data-testid="stMarkdownContainer"] > p {font-size: 20px; font-weight: bold;}</style>""", unsafe_allow_html=True)


        st.markdown(" --- ")


        st.markdown('<p style="font-size: 20px; font-weight: bold;">음성 질문</p>', unsafe_allow_html=True)
        if st.session_state["OPENAI_API"]:
            audio = audiorecorder("🎙️음성 질문", "🔴녹음 중 ... ")
            if (audio.duration_seconds > 0) and (st.session_state["check_reset"] == False):
                # 음성 재생
                st.audio(audio.export().read())
                # 음원 파일에서 텍스트 추출
                question = STT(audio, st.session_state["OPENAI_API"])
            

        st.markdown(" --- ")


        # 리셋 버튼 생성
        if st.button(label="초기화"):
            # 리셋 코드
            st.session_state["chat"] = []
            st.session_state["messages"] = [{"role": "assistant", "content": "나는 강남대학교에 다니는 박진우 chat bot이야"}]
            st.session_state["check_reset"] = True
        
       
        st.markdown("")
        st.markdown("")
        st.markdown("")
        st.markdown("")
        st.markdown("")
        st.markdown("")
        st.markdown("")
        st.markdown("")
        st.markdown("")
        st.markdown("")
        st.markdown("")
        st.subheader("참고 자료")
        "[Get an OpenAI API key](https://platform.openai.com/api-keys)"
        "[View the Source Code](https://github.com/parkwoobin/chatvoice_robot/blob/main/voice_txt_bot.py)"
        "[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/parkwoobin/chatvoice_robot)"


    
    if not st.session_state["OPENAI_API"]:
            st.info("⚠️ Please add your OpenAI API key!")
            st.stop()

    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])


    if response := st.chat_input():
        client = openai.OpenAI(api_key=st.session_state["OPENAI_API"])
        st.session_state.messages.append({"role": "user", "content": response})
        st.chat_message("user").write(response)
        response = client.chat.completions.create(model = model, messages=st.session_state.messages)
        msg = response.choices[0].message.content
        st.session_state.messages.append({"role": "assistant", "content": msg})
        st.chat_message("assistant").write(msg)

    elif (audio.duration_seconds > 0) and (st.session_state["check_reset"] == False):
        client = openai.OpenAI(api_key=st.session_state["OPENAI_API"])
        # 채팅을 시각화하기 위해 질문 내용 저장
        st.session_state["messages"].append({"role": "user", "content": question})
        st.chat_message("user").write(question)

        # GPT 모델을 통해 대답 생성

        gpt_response = client.chat.completions.create(model = model,messages=st.session_state.messages)
        msg1 = gpt_response.choices[0].message.content

        # 생성된 대답을 시각화하기 위해 대화 내용에 추가
        st.session_state["messages"].append({"role": "assistant", "content": msg1})
        st.chat_message("assistant").write(msg1)
    
    

if __name__=="__main__":
    main()
