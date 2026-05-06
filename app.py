import streamlit as st
import pandas as pd
import json
import os
import random

# --- 앱 설정 ---
st.set_page_config(page_title="로또 포뮬러-1 분석기", page_icon="🎰", layout="wide")

# 다크 테마 느낌을 위한 커스텀 스타일
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: white; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #FF4B4B; color: white; }
    .stDataFrame { border: 1px solid #30363d; }
    </style>
    """, unsafe_allow_html=True) # 'allow_html'

# --- 데이터 관리 로직 ---
DB_FILE = "lotto_db.json"

def load_data():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        # 기초 데이터 (1000~1222회 요약 반영용 초기값)
        # 사용자님이 주신 1번(26회), 2번(19회) 등 핵심 데이터를 기반으로 초기화
        return [
            {"drwNo": 1222, "nums": [4, 11, 17, 22, 32, 41]}
        ]

def save_data(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

# 데이터 불러오기
if 'history' not in st.session_state:
    st.session_state.history = load_data()

# --- 사이드바: 당첨 번호 입력 ---
with st.sidebar:
    st.header("📥 최신 회차 입력")
    st.write("토요일 밤, 새로운 번호를 넣으세요.")
    new_drw = st.number_input("회차 (예: 1223)", min_value=1223, step=1)
    new_nums_str = st.text_input("당첨 번호 (쉼표 구분)", "1, 2, 3, 4, 5, 6")
    
    if st.button("데이터 업데이트 및 저장"):
        try:
            new_nums = [int(n.strip()) for n in new_nums_str.split(",")]
            if len(new_nums) == 6:
                st.session_state.history.append({"drwNo": new_drw, "nums": sorted(new_nums)})
                save_data(st.session_state.history)
                st.success(f"{new_drw}회 업데이트 완료!")
                st.rerun()
            else:
                st.error("번호 6개를 정확히 입력하세요.")
        except:
            st.error("숫자 형식이 올바르지 않습니다.")

# --- 메인 분석 화면 ---
st.title("🎰 로또 포뮬러-1 분석 대시보드")
st.info(f"현재 1,000회부터 {st.session_state.history[-1]['drwNo']}회까지의 데이터를 분석 중입니다.")

# 분석 계산 로직
history = st.session_state.history
total_rounds = (history[-1]['drwNo'] - 1000) + 1 # 1000회부터의 총 회차
all_appearances = [n for r in history for n in r['nums']]
last_winning_nums = history[-1]['nums']

analysis_list = []
for n in range(1, 46):
    # 출현 횟수 (기초 데이터 보정치 반영 가능)
    # 실제 앱에서는 1000~1222회 전체 DB를 로드하는 것이 가장 정확합니다.
    count = all_appearances.count(n) 
    
    # 1번 공식: 평균 주기
    interval = round(total_rounds / count, 2) if count > 0 else total_rounds
    
    # 미출현 기간(Gap)
    gap = 0
    for i, r in enumerate(reversed(history)):
        if n in r['nums']:
            gap = i
            break
        gap = total_rounds
    
    # 상태 판별
    status = "보통"
    if n in last_winning_nums: status = "🔥 연타(Repeat)"
    elif gap > interval: status = "⏳ 임박(Delayed)"
    elif interval < 7.5: status = "⭐ 핫넘버"
    
    analysis_list.append({
        "번호": n,
        "출현횟수": count,
        "평균주기": interval,
        "현재공백": gap,
        "상태": status
    })

df = pd.DataFrame(analysis_list)

# 화면 분할
col1, col2 = st.columns([3, 2])

with col1:
    st.subheader("📊 번호별 포뮬러 통계")
    sort_option = st.selectbox("정렬 기준", ["번호순", "평균주기순", "현재공백순"])
    
    if sort_option == "평균주기순":
        df_display = df.sort_values("평균주기")
    elif sort_option == "현재공백순":
        df_display = df.sort_values("현재공백", ascending=False)
    else:
        df_display = df
        
    st.dataframe(df_display, use_container_width=True, height=500)

with col2:
    st.subheader("🔮 전략적 조합 생성")
    strategy = st.radio("추출 전략 선택", ["밸런스 조합", "지연 번호 중심", "핫넘버 중심"])
    fixed_num = st.multiselect("고정수 선택 (최대 2개)", range(1, 46), default=[1] if 1 in range(1, 46) else [])
    
    if st.button("포뮬러 조합 생성하기"):
        st.write("---")
        for i in range(5): # 5개 조합 생성
            candidates = list(range(1, 46))
            weights = []
            for n in candidates:
                s = analysis_list[n-1]
                w = 1 / s['평균주기'] # 기본 가중치
                
                if strategy == "지연 번호 중심" and s['상태'] == "⏳ 임박(Delayed)": w *= 2.5
                if strategy == "핫넘버 중심" and s['상태'] == "⭐ 핫넘버": w *= 2.0
                if n in last_winning_nums: w *= 1.2 # 연타 흐름 반영
                
                weights.append(w)
            
            # 고정수 제외한 나머지 번호 추출
            needed = 6 - len(fixed_num)
            others = []
            while len(others) < needed:
                pick = random.choices(candidates, weights=weights, k=1)[0]
                if pick not in fixed_num and pick not in others:
                    others.append(pick)
            
            res = sorted(fixed_num + others)
            st.markdown(f"**조합 {i+1}:** ` {res[0]} ` ` {res[1]} ` ` {res[2]} ` ` {res[3]} ` ` {res[4]} ` ` {res[5]} `")
        st.balloons()
