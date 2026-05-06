import streamlit as st
import pandas as pd
import json
import os
import random
import plotly.express as px

# --- 앱 설정 및 레이아웃 ---
st.set_page_config(page_title="LOTTO F-1 DASHBOARD", page_icon="📈", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0b0e14; color: #e0e0e0; }
    div[data-testid="stMetric"] {
        background-color: rgba(255, 255, 255, 0.05);
        border-radius: 15px;
        padding: 20px;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    .ball {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 45px;
        height: 45px;
        border-radius: 50%;
        margin: 5px;
        font-weight: 800;
        font-size: 1.1rem;
        color: white;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.3);
    }
    .b1 { background: radial-gradient(circle at 30% 30%, #fbc02d, #f57f17); }
    .b2 { background: radial-gradient(circle at 30% 30%, #42a5f5, #1565c0); }
    .b3 { background: radial-gradient(circle at 30% 30%, #ef5350, #b71c1c); }
    .b4 { background: radial-gradient(circle at 30% 30%, #bdbdbd, #616161); }
    .b5 { background: radial-gradient(circle at 30% 30%, #66bb6a, #1b5e20); }

    .stButton>button {
        background: linear-gradient(90deg, #FF4B4B 0%, #FF2E2E 100%);
        border: none;
        color: white;
        padding: 15px 32px;
        font-size: 20px;
        font-weight: bold;
        border-radius: 12px;
        transition: all 0.3s;
        box-shadow: 0 4px 15px rgba(255, 75, 75, 0.3);
    }
    .stButton>button:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(255, 75, 75, 0.5); }
    
    /* 생성기 박스 강조 */
    .generator-box {
        background-color: rgba(255, 255, 255, 0.03);
        padding: 30px;
        border-radius: 20px;
        border: 1px dashed rgba(255, 255, 255, 0.2);
        margin-bottom: 30px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 사용자 데이터 (동일하게 유지) ---
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

# --- 분석 데이터 생성 ---
last_drw = st.session_state.history[-1]['drwNo'] if st.session_state.history else 1222
last_nums = st.session_state.history[-1]['nums'] if st.session_state.history else [4, 11, 17, 22, 32, 41]

analysis = []
for n in range(1, 46):
    b_count, s2, s3 = BASE_DATA[n]
    p_count = sum(1 for r in st.session_state.history if n in r['nums'])
    t_count = b_count + p_count
    energy = (s2 * 1.5) + (s3 * 3.0)
    analysis.append({
        "번호": n, "총출현": t_count, "연타에너지": energy,
        "성향": "🔥 폭발형" if s3 > 8 else ("🏃 연속형" if s2 > 6 else "⚪ 일반"),
        "지난주": n in last_nums
    })
df = pd.DataFrame(analysis)

# --- [레이아웃 변경] 맨 위: 타이틀 및 요약 ---
st.title("🛡️ LOTTO FORMULA-1 DASHBOARD")
m1, m2, m3, m4 = st.columns(4)
m1.metric("최종 분석 회차", f"{last_drw}회")
m2.metric("최대 에너지 번호", f"{df.sort_values('연타에너지').iloc[-1]['번호']}번")
m3.metric("최다 출현 번호", f"{df.sort_values('총출현').iloc[-1]['번호']}번")
m4.metric("시스템 상태", "Stable")

st.markdown("---")

# --- [레이아웃 변경] 맨 위쪽 중앙: 스마트 번호 생성기 ---
st.markdown("### 🔮 스마트 번호 생성기")
with st.container():
    st.markdown('<div class="generator-box">', unsafe_allow_html=True)
    col_a, col_b = st.columns([1, 2])
    with col_a:
        strategy = st.radio("알고리즘 전략", ["에너지 집중형", "균형잡힌 추출", "최근 흐름 중시"])
    with col_b:
        if st.button("🚀 지금 번호 추출하기"):
            for i in range(5):
                cand = list(range(1, 46))
                weights = [ (a['연타에너지'] + 10) for a in analysis ]
                res = sorted(random.choices(cand, weights=weights, k=6))
                while len(set(res)) < 6: res = sorted(random.choices(cand, weights=weights, k=6))
                
                ball_html = ""
                for num in res:
                    cls = "b1" if num <= 10 else "b2" if num <= 20 else "b3" if num <= 30 else "b4" if num <= 40 else "b5"
                    ball_html += f'<div class="ball {cls}">{num}</div>'
                st.markdown(f'<div style="display:flex; margin-bottom:10px; align-items:center;"><b style="margin-right:20px;">SET {i+1}</b>{ball_html}</div>', unsafe_allow_html=True)
            st.balloons()
    st.markdown('</div>', unsafe_allow_html=True)

# --- [레이아웃 변경] 하단: 상세 데이터 리포트 ---
st.markdown("---")
col1, col2 = st.columns([2, 1])
with col1:
    st.subheader("📋 전체 데이터 상세 리포트")
    st.dataframe(df.sort_values("연타에너지", ascending=False), use_container_width=True, height=400)
with col2:
    st.subheader("📈 에너지 랭킹 Top 10")
    top_10 = df.sort_values("연타에너지", ascending=False).head(10)
    fig = px.bar(top_10, x='번호', y='연타에너지', color='연타에너지', color_continuous_scale='Reds', template='plotly_dark')
    fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', margin=dict(l=0, r=0, t=0, b=0), height=350)
    st.plotly_chart(fig, use_container_width=True)

# --- 관리 메뉴 ---
with st.expander("🛠️ 데이터 관리"):
    new_drw_no = st.number_input("회차", value=last_drw+1)
    new_nums_input = st.text_input("당첨 번호 (쉼표 구분)")
    if st.button("동기화"):
        st.toast("저장 중...")
