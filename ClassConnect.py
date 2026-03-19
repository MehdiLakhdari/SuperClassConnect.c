import streamlit as st
import requests
import time

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Connect Class", page_icon="😊", layout="wide")

st.markdown("""
    <style>
    header {visibility: hidden;}
    .stApp { background-color: #050505; color: white; }
    .nav-bar { background: #111; padding: 10px; border-radius: 10px; border-bottom: 3px solid #D32F2F; margin-bottom: 20px; text-align:center; }
    
    div[data-testid="stColumn"] .stButton>button { 
        background: linear-gradient(90deg, #FF8C00, #FF4500) !important; 
        color: white !important; border-radius: 8px; font-weight: bold; height: 50px; border: none;
    }

    @keyframes blink { 0% {box-shadow: 0 0 5px #FF0000;} 50% {box-shadow: 0 0 20px #FF0000;} 100% {box-shadow: 0 0 5px #FF0000;} }
    .notif-active button { animation: blink 1s infinite !important; border: 1px solid white !important; }

    .msg-card { background: #111; padding: 15px; border-radius: 10px; border-left: 5px solid #D32F2F; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

URL_BASE = "https://classconect-f1767-default-rtdb.europe-west1.firebasedatabase.app/"
URL_MSG = f"{URL_BASE}messages.json"
URL_USERS = f"{URL_BASE}utilisateurs.json"

if 'user' not in st.session_state: st.session_state.user = None
if 'page' not in st.session_state: st.session_state.page = "Mur"
if 'last_count' not in st.session_state: st.session_state.last_count = 0

def get_db(url):
    try:
        r = requests.get(url, timeout=5)
        return r.json() if r.status_code == 200 else {}
    except:
        return {}

data_u = get_db(URL_USERS)
all_m = get_db(URL_MSG)
curr_count = len(all_m) if all_m else 0

if st.session_state.user is None:
    st.markdown("<h2 style='text-align:center; color:#FF8C00;'>Connect Class Algeria 😊</h2>", unsafe_allow_html=True)
    t1, t2 = st.tabs(["🔴 CONNEXION", "🟠 INSCRIPTION"])
    
    with t1:
        u = st.text_input("Pseudo").strip()
        p = st.text_input("Mdp", type="password").strip()
        if st.button("ENTRER"):
            if u in data_u and str(data_u[u].get("mdp")) == str(p):
                st.session_state.user = u
                st.session_state.last_count = curr_count
                st.rerun()
    
    with t2:
        nu = st.text_input("Nouveau Pseudo").strip()
        np = st.text_input("Nouveau Mdp", type="password").strip()
        if st.button("CRÉER MON COMPTE"):
            if nu and np and nu not in data_u:
                requests.patch(URL_USERS, json={nu: {"mdp": np, "amis": {"Admin": True}}})
                st.success("Compte créé !")
                time.sleep(1) # PARENTHÈSE CORRIGÉE ICI ✅
                st.rerun()
else:
    me = st.session_state.user
    user_info = data_u.get(me, {})
    mes_amis = list(user_info.get("amis", {}).keys()) if "amis" in user_info else []

    inc_list = []
    if all_m:
        for k, v in all_m.items():
            exp = v.get("u")
            if v.get("d") == me and exp not in mes_amis:
                if exp not in inc_list:
                    inc_list.append(exp)
    nb_inc = len(set(inc_list))

    st.markdown(f"<div class='nav-bar'>🟠 <b>@{me}</b></div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    
    with c1:
        if st.button("🏠 MUR"):
            st.session_state.page = "Mur"
            st.rerun()
    with c2:
        label_chat = f"💬 CHAT ({nb_inc})" if nb_inc > 0 else "💬 CHAT"
        div_class = "notif-active" if nb_inc > 0 else ""
        st.markdown(f"<div class='{div_class}'>", unsafe_allow_html=True)
        if st.button(label_chat):
            st.session_state.page = "Chat"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    with c3:
        if st.button("🚪 QUITTER"):
            st.session_state.user = None
            st.rerun()

    if st.session_state.page == "Mur":
        with st.form("p_mur"):
            t = st.text_area("Message...")
            i = st.text_input("URL Image")
            if st.form_submit_button("PUBLIER"):
                requests.post(URL_MSG, json={"u": me, "m": t, "i": i, "d": "mondial", "t": time.time()})
                st.rerun()
        if all_m:
            for k in reversed(list(all_m.keys())):
                v = all_m[k]
                if v.get("d") == "mondial":
                    st.markdown(f"<div class='msg-card'><b>@{v['u']}</b><br>{v.get('m','')}</div>", unsafe_allow_html=True)
                    if v.get("i"): st.image(v["i"], use_container_width=True)

    elif st.session_state.page == "Chat":
        ta_a, ta_i = st.tabs(["👥 AMIS
