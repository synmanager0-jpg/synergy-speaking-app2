import streamlit as st
import json
import os
import random
import google.generativeai as genai
import pandas as pd

# --- [1. 스타일 및 레이아웃 설정] ---
st.set_page_config(page_title="시너지영어 Speaking", page_icon="🎙️", layout="centered")

# CSS로 React 앱 느낌의 디자인과 애니메이션 적용
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Pretendard:wght@400;700;900&display=swap');
    
    * { font-family: 'Pretendard', sans-serif; }
    
    .stButton>button { 
        width: 100%; border-radius: 16px; height: 4.5rem; 
        font-weight: 800; font-size: 1.25rem; margin-bottom: 12px; 
        transition: all 0.2s; border: none; background: #f1f5f9; color: #1e293b;
    }
    .stButton>button:hover { 
        transform: translateY(-3px); box-shadow: 0 10px 20px rgba(0,0,0,0.1); 
        background: linear-gradient(90deg, #6366f1, #8b5cf6); color: white;
    }
    .main-header { 
        font-size: 3rem; font-weight: 900; text-align: center; 
        background: linear-gradient(to right, #6366f1, #a855f7, #ec4899); 
        -webkit-background-clip: text; -webkit-text-fill-color: transparent; 
        margin-bottom: 0.5rem; 
    }
    .sub-header { font-size: 1.1rem; text-align: center; color: #64748b; margin-bottom: 2.5rem; }
    .question-card { 
        background: white; padding: 3.5rem; border-radius: 32px; 
        border: 1px solid #e2e8f0; text-align: center; 
        box-shadow: 0 25px 50px -12px rgba(0,0,0,0.08); margin: 2rem 0; 
    }
    .korean-text { font-size: 2.2rem; font-weight: 900; color: #0f172a; margin-bottom: 1rem; }
    .progress-label { font-size: 0.8rem; font-weight: 700; color: #6366f1; text-transform: uppercase; }
    </style>
""", unsafe_allow_html=True)

# --- [2. 초기 커리큘럼 데이터 (initialData.ts 내용 기반)] ---
INITIAL_COURSES = [
    {
        "id": 1, "name": "스피킹 연습",
        "classes": [
            {
                "id": 101, "name": "Phonics",
                "subClasses": [
                    {"id": 1011, "name": "[Lv 0] Phonics 1", "activities": [{"id": 1001, "name": "Speaking", "questions": [{"korean": "사과", "english": "apple"}, {"korean": "바나나", "english": "banana"}, {"korean": "고양이", "english": "cat"}, {"korean": "강아지", "english": "dog"}]}]},
                    {"id": 1012, "name": "[Lv 0] Phonics 2", "activities": [{"id": 1002, "name": "Speaking", "questions": [{"korean": "버스", "english": "bus"}, {"korean": "컵", "english": "cup"}]}]}
                ]
            },
            {
                "id": 102, "name": "Logos",
                "subClasses": [
                    {"id": 1021, "name": "Logos 1-1", "activities": [{"id": 2101, "name": "Market Expressions", "questions": [{"korean": "이거 얼마예요?", "english": "How much is this?"}, {"korean": "너무 비싸요.", "english": "It's too expensive."}]}]}
                ]
            },
            {
                "id": 103, "name": "IDEA",
                "subClasses": [
                    {"id": 1031, "name": "IDEA 6-1", "activities": [{"id": 3001, "name": "Speaking", "questions": [{"korean": "당신의 의견은 무엇인가요?", "english": "What is your opinion?"}, {"korean": "동의합니다.", "english": "I agree with you."}]}]}
                ]
            }
        ]
    }
]

# --- [3. 데이터 영구 저장 시스템] ---
DATA_FILE = "synergy_data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return INITIAL_COURSES

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

if "user_courses" not in st.session_state:
    st.session_state.user_courses = load_data()
if "view" not in st.session_state:
    st.session_state.view = "MAIN"
if "auth" not in st.session_state:
    st.session_state.auth = False

# --- [4. Gemini AI 자동 문제 생성] ---
def generate_ai_content(count=5):
    api_key = st.secrets.get("API_KEY")
    if not api_key: return None
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    prompt = f"일상 영어 회화 문장 {count}개를 JSON 형식으로 생성해줘. 형식: {{'questions': [{{'korean': '한글뜻', 'english': 'English'}}]}}"
    try:
        response = model.generate_content(prompt, generation_config={"response_mime_type": "application/json"})
        return json.loads(response.text).get("questions", [])
    except: return None

# --- [5. 화면 렌더링 함수들] ---

def render_main():
    st.markdown('<div class="main-header">Synergy English</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">시너지영어학원 스피킹 센터에 오신 것을 환영합니다.</div>', unsafe_allow_html=True)
    for course in st.session_state.user_courses:
        if st.button(f"📘 {course['name']}"):
            st.session_state.current_course = course
            st.session_state.view = "CLASS_LIST"; st.rerun()

def render_class_list():
    st.markdown(f'<div class="main-header">{st.session_state.current_course["name"]}</div>', unsafe_allow_html=True)
    if st.button("← 메인 메뉴"): st.session_state.view = "MAIN"; st.rerun()
    for cls in st.session_state.current_course["classes"]:
        if st.button(f"📂 {cls['name']}"):
            st.session_state.current_class = cls
            st.session_state.view = "SUBCLASS_LIST"; st.rerun()

def render_subclass_list():
    st.markdown(f'<div class="main-header">{st.session_state.current_class["name"]}</div>', unsafe_allow_html=True)
    if st.button("← 뒤로가기"): st.session_state.view = "CLASS_LIST"; st.rerun()
    for sub in st.session_state.current_class["subClasses"]:
        if st.button(f"📖 {sub['name']}"):
            st.session_state.current_subclass = sub
            st.session_state.view = "ACTIVITY_LIST"; st.rerun()

def render_activity_list():
    st.markdown(f'<div class="main-header">{st.session_state.current_subclass["name"]}</div>', unsafe_allow_html=True)
    if st.button("← 뒤로가기"): st.session_state.view = "SUBCLASS_LIST"; st.rerun()
    for act in st.session_state.current_subclass["activities"]:
        if st.button(f"🎙️ {act['name']} 연습 시작"):
            st.session_state.questions = act["questions"]
            st.session_state.q_idx = 0
            st.session_state.view = "PRACTICE"; st.rerun()

def render_practice():
    questions = st.session_state.questions
    if not questions:
        st.error("문제가 없습니다."); st.button("돌아가기", on_click=lambda: st.session_state.update({"view": "MAIN"}))
        return

    q = questions[st.session_state.q_idx]
    st.markdown(f'<p class="progress-label">Question {st.session_state.q_idx + 1} / {len(questions)}</p>', unsafe_allow_html=True)
    st.progress((st.session_state.q_idx + 1) / len(questions))
    
    if st.button("종료하기", key="exit_btn"): st.session_state.view = "MAIN"; st.rerun()

    st.markdown(f'<div class="question-card"><div class="korean-text">"{q["korean"]}"</div><p style="color:#94a3b8;">영어로 어떻게 말할까요?</p></div>', unsafe_allow_html=True)
    
    ans = st.text_input("여기에 입력하세요", key=f"ans_{st.session_state.q_idx}").strip()
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("정답 확인 ✅"):
            if ans.lower().replace(".","") == q["english"].lower().replace(".",""):
                st.success("정답입니다! 잘하셨어요."); st.balloons()
            else: st.error(f"아쉬워요! 정답은: {q['english']}")
    with col2:
        if st.button("다음 문제 ➡️"):
            if st.session_state.q_idx < len(questions) - 1:
                st.session_state.q_idx += 1; st.rerun()
            else: st.success("축하합니다! 모든 연습을 마쳤습니다.")

# --- [6. 메인 실행 흐름 제어] ---
with st.sidebar:
    st.markdown("### 🛠️ 관리자 센터")
    if not st.session_state.auth:
        pw = st.text_input("비밀번호", type="password")
        if st.button("로그인"):
            if pw == "syn2740582y": st.session_state.auth = True; st.rerun()
            else: st.error("비밀번호가 틀렸습니다.")
    else:
        st.success("관리자 인증 완료")
        if st.button("로그아웃"): st.session_state.auth = False; st.rerun()
        st.divider()
        if st.button("💾 서버에 전체 저장 (모든 기기 동기화)"):
            save_data(st.session_state.user_courses)
            st.toast("서버 동기화가 완료되었습니다!")
        if st.button("🤖 AI 문제 생성 및 추가"):
            new_qs = generate_ai_content()
            if new_qs: 
                st.session_state.user_courses[0]["classes"][0]["subClasses"][0]["activities"][0]["questions"].extend(new_qs)
                st.success("AI 문제가 첫 번째 코스에 추가되었습니다.")

if st.session_state.view == "MAIN": render_main()
elif st.session_state.view == "CLASS_LIST": render_class_list()
elif st.session_state.view == "SUBCLASS_LIST": render_subclass_list()
elif st.session_state.view == "ACTIVITY_LIST": render_activity_list()
elif st.session_state.view == "PRACTICE": render_practice()

st.divider()
st.caption("© 2026 Synergy English Academy • All data synced via Streamlit Cloud")
