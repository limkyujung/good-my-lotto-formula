import streamlit as st
import pandas as pd
import json
import os
import random

# --- 앱 설정 ---
st.set_page_config(page_title="레오 로또 시스템", page_icon="🦁", layout="centered")

# 디자인 설정 (글자색 밝게 유지)
st.markdown("""
    <style>
    .stApp { background-color: #0b111a; color: #ffffff !important; }
    h1, h2, h3, h4, h5, h6, p, span, label { color: #ffffff !important; }
    div[data-testid="stMetric"] {
        background-color: rgba(255, 255, 255, 0.1);
        border-radius: 15px; padding: 12px; border: 1px solid rgba(255, 255, 255, 0.2);
        text-align: center;
    }
    .ball {
        display: inline-flex; align-items: center; justify-content: center;
        width: 38px; height: 38px; border-radius: 50%; margin: 3px;
        font-weight: 800; font-size: 0.95rem; color: white !important;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.5);
    }
    .b1 { background: radial-gradient(circle at 30% 30%, #fbc02d, #f57f17); }
    .b2 { background: radial-gradient(circle at 30% 30%, #42a5f5, #1565c0); }
    .b3 { background: radial-gradient(circle at 30% 30%, #ef5350, #b71c1c); }
    .b4 { background: radial-gradient(circle at 30% 30%, #bdbdbd, #616161); }
    .b5 { background: radial-gradient(circle at 30% 30%, #66bb6a, #1b5e20); }

    .stButton>button {
        width: 100%; border-radius: 15px; height: 60px;
        background: linear-gradient(90deg, #FFD700 0%, #FFA500 100%);
        color: #000000 !important; font-size: 1.25rem; font-weight: 900; border: none;
    }
    /* 멀티셀렉트/셀렉트박스 글자색 보정 */
    .stMultiSelect div, .stSelectbox div { color: #000000 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 기초 데이터 (기존과 동일) ---
BASE_STATS = {
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
    b_count, s2, s3 = BASE_STATS[n]
    p_count = sum(1 for r in st.session_state.history if n in r['nums'])
    t_count = b_count + p_count
    energy = round((s2 * 1.5) + (s3 * 3.0), 1)
    analysis.append({"번호": n, "총출현": t_count, "연타에너지": energy, "지난주": n in last_nums})
df = pd.DataFrame(analysis)

# --- [1] 상단 이미지 ---
if os.path.exists("leo_main.png"):
    st.image("leo_main.png", use_container_width=True)
else:
    st.markdown('<h1 style="text-align:center; color:#FFD700;">🦁 레오 로또 시스템</h1>', unsafe_allow_html=True)

# --- [2] 번호 필터링 옵션 (추가된 기능) ---
st.markdown("### ⚙️ 번호 필터 설정")
col_f1, col_f2 = st.columns(2)

with col_f1:
    exclude_nums = st.multiselect("배제할 숫자 (1~5개)", range(1, 46), max_selections=5)

with col_f2:
    fixed_num = st.selectbox("고정할 숫자 (1개)", [None] + list(range(1, 46)))

# --- [3] 번호 생성기 ---
st.markdown("---")
if st.button("🚀 레오 추천 조합 생성"):
    for i in range(5):
        # 전체 1~45번 중 배제할 숫자 제거
        candidates = [n for n in range(1, 46) if n not in exclude_nums]
        
        # 고정수가 있다면 후보군에서 제외 (나중에 합치기 위해)
        if fixed_num and fixed_num in candidates:
            candidates.remove(fixed_num)
        
        # 가중치 계산 (배제된 번호 제외)
        weights = []
        for n in candidates:
            idx = n - 1
            w = (analysis[idx]['총출현'] * 0.5 + analysis[idx]['연타에너지'] + 5)
            weights.append(w)
        
        # 고정수를 제외한 나머지 번호 추출
        needed_count = 5 if fixed_num else 6
        res_others = random.choices(candidates, weights=weights, k=needed_count)
        
        # 중복 방지 로직
        while len(set(res_others)) < needed_count:
            res_others = random.choices(candidates, weights=weights, k=needed_count)
            
        # 고정수와 합쳐서 최종 6개 만들기
        final_res = sorted(res_others + ([fixed_num] if fixed_num else []))
        
        # 공 모양 시각화
        ball_html = ""
        for num in final_res:
            cls = "b1" if num <= 10 else "b2" if num <= 20 else "b3" if num <= 30 else "b4" if num <= 40 else "b5"
            ball_html += f'<div class="ball {cls}">{num}</div>'
        st.markdown(f'<div style="display:flex; justify-content:center; margin-bottom:12px;">{ball_html}</div>', unsafe_allow_html=True)
    st.balloons()

# --- [4] 요약 지표 및 리포트 ---
st.markdown("---")
c1, c2 = st.columns(2)
c1.metric("분석 회차", f"{last_drw}회")
c2.metric("에너지 1위", f"{df.sort_values('연타에너지').iloc[-1]['번호']}번")
st.table(df.sort_values("연타에너지", ascending=False).head(5)[['번호', '총출현', '연타에너지']])
