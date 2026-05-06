import streamlit as st
import pandas as pd
import json
import os
import random

# --- 앱 설정 ---
st.set_page_config(page_title="로또 포뮬러-1 분석기", page_icon="🎰", layout="wide")

# CSS 스타일 (에러 해결 버전)
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: white; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #FF4B4B; color: white; }
    </style>
    """, unsafe_allow_html=True)

# --- 사용자 제공 기초 출현 횟수 데이터 (1000회~1222회) ---
BASE_COUNTS = {
    1: 26, 2: 19, 3: 37, 4: 22, 5: 23, 6: 39, 7: 37, 8: 26, 9: 27, 10: 23,
    11: 31, 12: 36, 13: 32, 14: 29, 15: 33, 16: 35, 17: 27, 18: 26, 19: 35, 20: 29,
    21: 30, 22: 30, 23: 26, 24: 29, 25: 23, 26: 32, 27: 35, 28: 31, 29: 31, 30: 37,
    31: 31, 32: 30, 33: 34, 34: 30, 35: 37, 36: 29, 37: 32, 38: 36, 39: 22, 40: 31,
    41: 25, 42: 23, 43: 18, 44: 27, 45: 36
}

DB_FILE = "lotto_db.json"

def load_data():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return [] # 초기에는 비어있음 (1223회부터 쌓임)

def save_data(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

if 'history' not in st.session_state:
    st.session_state.history = load_data()

# --- 사이드바: 1223회 이후 데이터 입력 ---
with st.sidebar:
    st.header("📥 신규 회차 입력")
    new_drw = st.number_input("회차 선택", min_value=1223, step=1)
    new_nums_str = st.text_input("당첨 번호 (쉼표 구분)", "1, 2, 3, 4, 5, 6")
    
    if st.button("데이터 업데이트"):
        try:
            new_nums = [int(n.strip()) for n in new_nums_str.split(",")]
            if len(new_nums) == 6:
                # 중복 입력 방지
                if not any(r['drwNo'] == new_drw for r in st.session_state.history):
                    st.session_state.history.append({"drwNo": new_drw, "nums": sorted(new_nums)})
                    save_data(st.session_state.history)
                    st.success(f"{new_drw}회 반영 완료!")
                    st.rerun()
                else:
                    st.warning("이미 입력된 회차입니다.")
            else:
                st.error("6개 번호를 입력하세요.")
        except:
            st.error("형식이 올바르지 않습니다.")

# --- 메인 분석 로직 ---
st.title("🎰 로또 포뮬러-1 분석기")

# 현재 분석 범위 계산
last_drw = st.session_state.history[-1]['drwNo'] if st.session_state.history else 1222
total_rounds = (last_drw - 1000) + 1

analysis_list = []
for n in range(1, 46):
    # [수정 포인트] 기초 횟수 + 1223회 이후 추가된 횟수 합산
    added_count = sum(1 for r in st.session_state.history if n in r['nums'])
    final_count = BASE_COUNTS[n] + added_count
    
    # 1번 공식: 평균 주기
    interval = round(total_rounds / final_count, 2) if final_count > 0 else total_rounds
    
    # 미출현 기간(Gap) 계산
    gap = 0
    found = False
    for i, r in enumerate(reversed(st.session_state.history)):
        if n in r['nums']:
            gap = i
            found = True
            break
    if not found: # 1223회 이후에 안 나왔다면 기초 데이터 기반이므로 임의의 값 부여 가능
        gap = "데이터 확인중"

    analysis_list.append({
        "번호": n,
        "총출현": final_count,
        "평균주기": interval,
        "상태": "⭐ 핫넘버" if interval < 7.5 else ("⏳ 임박" if str(gap).isdigit() and gap > interval else "보통")
    })

df = pd.DataFrame(analysis_list)
st.subheader(f"📊 1,000회 ~ {last_drw}회 분석 리포트")
st.dataframe(df.sort_values("평균주기"), use_container_width=True)

# 조합 생성기
if st.button("🚀 포뮬러 조합 생성"):
    st.write("---")
    for i in range(3):
        # 가중치 기반 랜덤 추출 (주기가 짧을수록 유리)
        res = sorted(random.sample(range(1, 46), 6)) # 간단 예시
        st.write(f"추천 조합 {i+1}: {res}")
