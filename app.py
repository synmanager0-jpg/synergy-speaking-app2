import streamlit as st
import pandas as pd
import os

# 1. 환경 설정
DATA_FILE = "master_data.csv"

# 2. 데이터 불러오기 함수
def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    # 파일이 없으면 샘플 데이터 생성
    return pd.DataFrame({"korean": ["안녕하세요"], "english": ["Hello"]})

# 3. 사이드바 - 관리자 모드 (데이터 동기화 핵심)
st.sidebar.header("🛠️ Admin Controls")
admin_pw = st.sidebar.text_input("관리자 비밀번호", type="password")

if admin_pw == "syn2740582y":
    st.sidebar.success("관리자 인증 완료")
    uploaded_file = st.sidebar.file_uploader("새 엑셀 파일 업로드 (동기화)", type=["xlsx", "csv"])
    
    if uploaded_file:
        if uploaded_file.name.endswith('.xlsx'):
            new_df = pd.read_excel(uploaded_file)
        else:
            new_df = pd.read_csv(uploaded_file)
        
        # 서버 파일 시스템에 직접 저장 (이것이 실시간 동기화의 핵심)
        new_df.to_csv(DATA_FILE, index=False)
        st.sidebar.info("✅ 서버 데이터가 갱신되었습니다. 모든 기기에 반영됩니다.")
        st.rerun()

# 4. 메인 화면 - 학생용 학습 페이지
st.title("🎙️ 시너지영어 스피킹 센터")
current_df = load_data()

st.write(f"현재 총 **{len(current_df)}개**의 문항이 동기화되어 있습니다.")
st.dataframe(current_df, use_container_width=True) # 태블릿에서 보기 편하게 표로 출력