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
    
    /* 상단 이미지 디자인 */
    .main-img { 
        display: block; 
        margin: 0 auto; 
        width: 100%; 
        border-radius: 20px; 
        box-shadow: 0 8px 16px rgba(0,0,0,0.4);
        margin-bottom: 20px;
    }
    
    /* 카드형 메트릭 디자인 */
    div[data-testid="stMetric"] {
        background-color: rgba(255, 255, 255, 0.05);
        border-radius: 15px; 
        padding: 12px; 
        border: 1px solid rgba(255, 255, 255, 0.1);
        text-align: center;
    }
    
    /* 로또 번호 공 디자인 (모바일 사이즈 최적화) */
    .ball {
        display: inline-flex; 
        align-items: center; 
        justify-content: center;
        width: 38px; 
        height: 38px; 
        border-radius: 50%; 
        margin: 3px;
        font-weight: 800; 
        font-size: 0.95rem; 
        color: white;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.5);
    }
    .b1 { background: radial-gradient(circle at 30% 30%, #fbc02d, #f57f17); }
    .b2 { background: radial-gradient(circle at 30% 30%, #42a5f5, #1565c0); }
    .b3 { background: radial-gradient(circle at 30% 30%, #ef5350, #b71c1c); }
    .b4 { background: radial-gradient(circle at 30% 30%, #bdbdbd, #616161); }
    .b5 { background: radial-gradient(circle at 30% 30%, #66bb6a, #1b5e20); }

    /* 추출 버튼 (스마트폰 터치 중심) */
    .stButton>button {
        width: 100%; 
        border-radius: 15px; 
        height: 60px;
        background: linear-gradient(90deg, #FFD700 0%, #FFA500 100%);
        color: black; 
        font-size: 1.25rem; 
        font-weight: 900; 
        border: none;
        box-shadow: 0 4px 15px rgba(255, 215, 0, 0.3);
    }
    </style>
    """, unsafe_allow_html=True)

# --- 사용자 데이터 (1000~1222회 데이터) ---
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
    analysis.append({"번호": n, "총출현": t_count, "연타에너지": energy})
df = pd.DataFrame(analysis)

# --- [1] 상단 캐릭터 이미지 표시 ---
# 파일 이름이 leo_main.png 인지 확인하세요.
if os.path.exists("leo_main.png"):
    st.image("leo_main.png", use_column_
