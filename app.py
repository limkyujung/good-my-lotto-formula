import streamlit as st
import pandas as pd
import json
import os
import random

# --- 앱 설정: 모바일 최적화 ---
st.set_page_config(page_title="레오 로또 시스템", page_icon="🦁", layout="centered")

# 모바일 전용 커스텀 디자인 (CSS)
st.markdown("""
    <style>
    /* 배경 및 기본 폰트 */
    .stApp { background-color: #0b111a; color: #e0e0e0; }
    
    /* 상단 이미지 중앙 정렬 */
    .main-img { display: block; margin: 0 auto; width: 100%; max-width: 350px; border-radius: 20px; box-shadow: 0 10px 20px rgba(0,0,0,0.5); }
    
    /* 모바일 가독성 향상 카드 */
    div[data-testid="stMetric"] {
        background-color: rgba(255, 255, 255, 0.05);
        border-radius: 15px; padding: 10px; border: 1px solid rgba(255, 255, 255, 0.1);
        text-align: center; margin-bottom: 10px;
    }
    
    /* 로또 번호 공 디자인 (모바일 사이즈) */
    .ball {
        display: inline-flex; align-items: center; justify-content: center;
        width: 38px; height: 38px; border-radius: 50%; margin: 3px;
        font-weight: 800; font-size: 0.95rem; color: white;
    }
    .b1 { background: radial-gradient(circle at 30% 30%, #fbc02d, #f57f17); }
    .b2 { background: radial-gradient(circle at 30% 30%, #42a5f5, #1565c0); }
    .b3 { background: radial-gradient(circle at 30% 30%, #ef5350, #b71c1c); }
    .b4 { background: radial-gradient(circle at 30% 30%, #bdbdbd, #616161); }
    .b5 { background: radial-gradient(circle at 30% 30%, #66bb6a, #1b5e20); }

    /* 추출 버튼 (엄지손가락 터치 최적화) */
    .stButton>button {
        width: 100%; border-radius: 15px; height: 60px;
        background: linear-gradient(90deg, #FFD700 0%, #FFA500 100%);
        color: black; font-size: 1.2rem; font-weight: 900; border: none;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 사용자 데이터 (1000~1222회 기초 데이터 유지) ---
BASE_DATA = {
    1: (26, 2, 4), 2: (19, 2, 4), 3: (37, 4, 6), 4: (22, 0, 2), 5: (23, 3, 4),
    6: (39, 5, 12), 7: (37, 5, 7), 8: (26, 3, 1), 9: (27, 4, 5), 10: (23, 2, 5),
    11: (31, 4, 9), 12: (36, 4, 9), 13: (32, 5, 5), 14: (29, 2, 5), 15: (33, 7, 7),
    16: (35, 5, 7), 17: (27, 1, 6), 18: (26, 4, 4), 19: (35, 8, 9), 20: (29, 3, 4),
    21: (30, 4, 3), 22: (30, 4, 3), 23: (26, 3, 7), 24: (29, 3, 5), 25: (23, 3, 4),
    26: (32, 6, 8), 27: (35, 8, 7), 28: (31, 4, 8), 29: (31, 4, 9), 30: (37, 4, 9),
    31: (31, 3, 3), 32: (30, 5, 8), 33: (34, 5, 6), 34: (30, 6, 5), 35: (37, 7, 9),
    36: (29, 2, 8), 37: (32, 1, 12), 38: (36, 6, 13), 39: (22, 2, 4), 40: (31, 6, 4),
    41: (25, 1, 3), 42: (23, 2, 6), 43: (18, 3, 2), 44: (27, 4, 2), 45: (36, 9, 5)
}

DB_FILE = "lotto_db.json"
def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f: return json.load(f)
    return []
if 'history' not in st.session_state: st.session_state.history = load_db()

last_drw = st.session_state.history[-1]['drwNo'] if st.session_state.history else 1222
last_nums = st.session_state.history[-1]['nums'] if st.session_state.history else [4, 11, 17, 22, 32, 41]

analysis = []
for n in range(1, 46):
    b_count, s2, s3 = BASE_DATA[n]
    p_count = sum(1 for r in st.session_state.history if n in r['nums'])
    t_count = b_count + p_count
    energy = (s2 * 1.5) + (s3 * 3.0)
    analysis.append({"번호": n, "총출현": t_count, "연타에너지": energy, "지난주": n in last_nums})
df = pd.DataFrame(analysis)

# --- [1] 상단 이미지 & 타이틀 ---
# 캐릭터 이미지를 상단에 표시합니다. (파일명이 다르면 해당 파일명으로 수정 필요)
image_path = "Gemini_Generated_Image_n1yenqn1yenqn1ye.png"
if os.path.exists(image_path):
    st.image(image_path, use_column_width=True)
else:
    st.markdown('<h1 style="text-align:center;">🦁 레오 로또 시스템</h1>', unsafe_allow_html=True)

# --- [2] 번호 생성기 (터치 중심) ---
with st.container():
    st.markdown("### 🔮 레오 추천 번호")
    if st.button("🔥 지금 행운의 번호 추출"):
        for i in range(5):
            cand = list(range(1, 46))
            weights = [ (a['연타에너지'] + 10) for a in analysis ]
            res = sorted(random.choices(cand, weights=weights, k=6))
            while len(set(res)) < 6: res = sorted(random.choices(cand, weights=weights, k=6))
            
            ball_html = ""
            for num in res:
                cls = "b1" if num <= 10 else "b2" if num <= 20 else "b3" if num <= 30 else "b4" if num <= 40 else "b5"
                ball_html += f'<div class="ball {cls}">{num}</div>'
            st.markdown(f'<div style="display:flex; justify-content:center; margin-bottom:10px;">{ball_html}</div>', unsafe_allow_html=True)
        st.balloons()

# --- [3] 시스템 지표 (2열 모바일 그리드) ---
st.markdown("---")
c1, c2 = st.columns(2)
c1.metric("분석 회차", f"{last_drw}회")
c2.metric("최대 에너지", f"{df.sort_values('연타에너지').iloc[-1]['번호']}번")
c3, c4 = st.columns(2)
c3.metric("최다 출현", f"{df.sort_values('총출현').iloc[-1]['번호']}번")
c4.metric("시스템", "🦁 Active")

# --- [4] 데이터 리포트 (모바일은 가로 스크롤 방지) ---
st.markdown("---")
st.subheader("📊 에너지 랭킹 Top 5")
top_5 = df.sort_values("연타에너지", ascending=False).head(5)
st.table(top_5[['번호', '총출현', '연타에너지']]) # 모바일은 table이 가독성이 더 좋습니다.

# --- 관리 메뉴 (숨김 처리) ---
with st.expander("🛠️ 데이터 관리"):
    new_drw_input = st.number_input("업데이트 회차", value=last_drw+1)
    new_nums_input = st.text_input("당첨 번호 (쉼표 구분)")
    if st.button("갱신"):
        st.toast("저장 완료")
