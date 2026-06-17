import streamlit as st
import pyttsx3
import webbrowser
import google.generativeai as genai
import os
import hashlib

# [중요] 제미나이 API 키 입력
genai.configure(api_key="AQ.Ab8RN6KhW4lXpeEU8gtmmYCDjliYlBQeUIYhI_dZ0Xxj550oOg")

# 브라우저 기본 설정
st.set_page_config(page_title="궁극의 AI 비서", page_icon="💻", layout="centered")
st.title("💻 궁극의 AI 비서 (기능 대확장 버전)")

# 세션 상태 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []
if "sound_on" not in st.session_state:
    st.session_state.sound_on = True
if "last_audio_id" not in st.session_state:
    st.session_state.last_audio_id = ""

def speak(text):
    if st.session_state.sound_on:
        try:
            engine = pyttsx3.init()
            engine.say(text)
            engine.runAndWait()
        except:
            pass 

def execute_command(text):
    if "유튜브" in text and "열어" in text:
        speak("유튜브를 실행합니다.")
        webbrowser.open("https://youtube.com")
        return "유튜브를 열었습니다! 📺"
    elif "네이버" in text:
        speak("네이버를 엽니다.")
        webbrowser.open("https://naver.com")
        return "네이버를 열었습니다! 🟢"
    return None

# --- 사이드바: AI 및 확장 기능 설정 ---
with st.sidebar:
    st.header("🧠 AI 두뇌 성능 선택")
    model_choice = st.radio(
        "어떤 두뇌를 사용할까요?",
        ["⚡ Flash 모델 (빠르고 가벼움 - 일상용)", "💎 Pro 모델 (느리지만 아주 똑똑함 - 코딩/심층분석용)"]
    )
    
    if "Flash" in model_choice:
        model = genai.GenerativeModel('gemini-2.5-flash')
    else:
        model = genai.GenerativeModel('gemini-2.5-pro')
        
    st.divider()
    
    st.header("⚙️ 비서 모드 설정")
    ai_mode = st.radio(
        "역할을 선택하세요",
        ["🤖 일반 비서 (명령어 지원)", "🐍 파이썬 전문가", "🅒 C언어 전문가", "🌀 AI 섞기 모드 (창의성+논리성 융합)"]
    )
    
    st.divider()
    st.session_state.sound_on = st.toggle("🔊 비서 목소리 켜기", value=st.session_state.sound_on)
    
    st.divider()
    
    # 🌟 기능 1: 비서에게 장기기억 심어주기
    st.header("🔒 비서의 장기 기억")
    memory_file = "memory.txt"
    existing_memory = ""
    if os.path.exists(memory_file):
        with open(memory_file, "r", encoding="utf-8") as f:
            existing_memory = f.read()
            
    user_memory = st.text_area(
        "기억할 정보 입력 (나의 정보/성향)", 
        value=existing_memory,
        placeholder="예) 내 이름은 홍길동이야. 파이썬 초보자니까 코드 위주로 쉽게 설명해줘."
    )
    if user_memory != existing_memory:
        with open(memory_file, "w", encoding="utf-8") as f:
            f.write(user_memory)
        st.success("🧠 기억이 영구 저장되었습니다!")
        st.rerun()

    st.divider()
    
    # 🌟 기능 2: 나만의 코딩 비법 노트로 저장 (대화 내보내기)
    st.header("💾 대화 내보내기")
    if st.session_state.messages:
        chat_export_text = ""
        for msg in st.session_state.messages:
            role_label = "나 (User)" if msg["role"] == "user" else "AI 비서 (Assistant)"
            chat_export_text += f"[{role_label}]\n{msg['content']}\n\n"
            chat_export_text += "="*40 + "\n\n"
            
        st.download_button(
            label="📄 코딩 비법 노트 다운로드 (.txt)",
            data=chat_export_text,
            file_name="coding_secret_note.txt",
            mime="text/plain"
        )
    else:
        st.caption("대화 내용이 아직 없습니다.")

# 장기 기억 프롬프트 반영 설정
memory_context = ""
if os.path.exists(memory_file) and user_memory.strip():
    memory_context = f"[중요 - 기억해야 할 사용자 정보: {user_memory.strip()}]\n너는 답변할 때 이 정보를 기반으로 삼아 친절하게 답해야 해.\n"

# 화면에 이전 대화 내역 그리기
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

user_input = None

# 🌟 기능 3: 타이핑 없이 말로 질문하기 (음성 입력 창)
audio_value = st.audio_input("🎤 말로 질문하기 (녹음 버튼을 누르고 대화해 보세요)")
if audio_value:
    audio_bytes = audio_value.read()
    audio_id = hashlib.md5(audio_bytes).hexdigest()
    
    # 중복 분석을 방지하기 위한 안전장치
    if st.session_state.last_audio_id != audio_id:
        st.session_state.last_audio_id = audio_id
        with st.spinner("🎙️ 음성을 분석하여 받아쓰는 중..."):
            try:
                transcribe_prompt = "이 오디오 파일의 한국어 음성을 글자로 그대로 받아써줘. 어떤 설명도 없이 오직 받아쓴 결과 텍스트만 한 줄로 출력해줘."
                transcribe_res = model.generate_content([
                    transcribe_prompt,
                    {"mime_type": "audio/wav", "data": audio_bytes}
                ])
                user_input = transcribe_res.text.strip()
            except Exception as e:
                st.error(f"음성 변환 실패: {e}")

# 만약 음성 입력이 없었다면 일반 텍스트 입력창 활성화
if not user_input:
    user_input = st.chat_input(f"{ai_mode}에게 질문하기...")

# 실제 대화 작동 로직
if user_input:
    with st.chat_message("user"):
        st.markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        
        # 1. 일반 비서 모드
        if ai_mode == "🤖 일반 비서 (명령어 지원)":
            response_placeholder.markdown("🤖 생각 중...")
            command_result = execute_command(user_input)
            if command_result:
                ai_response = command_result
            else:
                prompt = memory_context + user_input if memory_context else user_input
                response = model.generate_content(prompt)
                ai_response = response.text
            response_placeholder.markdown(ai_response)
            speak(ai_response)

        # 2. 파이썬 / C언어 전문가 모드
        elif ai_mode in ["🐍 파이썬 전문가", "🅒 C언어 전문가"]:
            response_placeholder.markdown(f"🤖 코드 분석 중...")
            base_prompt = "너는 파이썬 최고 개발자야. 코드 위주로 설명해." if "파이썬" in ai_mode else "너는 C언어 최고 전문가야. 원리와 코드를 명확히 설명해."
            prompt = memory_context + base_prompt + " 질문: " + user_input
            response = model.generate_content(prompt)
            ai_response = response.text
            response_placeholder.markdown(ai_response)
            speak("전문가 답변을 작성했습니다.")

        # 3. AI 섞기 모드
        elif ai_mode == "🌀 AI 섞기 모드 (창의성+논리성 융합)":
            try:
                with st.status("🧠 융합 AI 가동 중...", expanded=True) as status:
                    st.write("🔮 장기 기억과 시각을 융합하는 중입니다...")
                    
                    fusion_prompt = f"""
                    {memory_context}
                    너는 지금부터 '창의성 대장'과 '논리성 대장'의 능력을 모두 가진 '융합형 AI 최고 의사결정권자'야.
                    사용자의 질문에 대해 반드시 아래의 3가지 서식에 맞춰서 답변을 나누어 작성해줘.
                    
                    ### 🎨 1. 창의적 관점의 아이디어
                    (기발하고 자유로운 상상력을 발휘한 답변)
                    
                    ### 🧐 2. 논리적 관점의 분석
                    (비판적이고 현실적이며 데이터 중심의 분석)
                    
                    ### 🤝 3. 최종 융합 결론
                    (두 상반된 관점의 장점만 뽑아 하나로 합친 완벽한 최종 답변)
                    
                    사용자의 질문: {user_input}
                    """
                    response = model.generate_content(fusion_prompt)
                    ai_response = response.text
                    status.update(label="✨ AI 융합 완료!", state="complete", expanded=False)
                
                response_placeholder.markdown(ai_response)
                speak("여러 시각을 융합한 답변을 도출했습니다.")
                
            except Exception as e:
                ai_response = f"❌ 에러 발생: {e}"
                response_placeholder.markdown(ai_response)
                
    st.session_state.messages.append({"role": "assistant", "content": ai_response})
    st.rerun()