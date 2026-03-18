import streamlit as st
import requests
import time

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Connect Class Algeria", page_icon="1", layout="wide")

# DESIGN CSS AMÉLIORÉ (SANS SIDEBAR)
st.markdown("""
    <style>
    header {visibility: hidden;}
    .stApp { background-color: #0e1117; color: white; }
    
    /* LOGO ORANGE */
    .logo-box {
        background: linear-gradient(135deg, #FF8C00, #FF4500);
        width: 70px; height: 70px; border-radius: 15px;
        display: flex; align-items: center; justify-content: center;
        margin: 0 auto; font-size: 45px; font-weight: bold; color: white;
        box-shadow: 0 5px 15px rgba(255, 69, 0, 0.4);
    }
    .logo-text { font-size: 24px; font-weight: bold; color: #FF8C00; text-align: center; margin-top: 10px; }

    /* MENU DE NAVIGATION EN HAUT */
    .nav-container {
        background-color: #1c1f26;
        padding: 10px;
        border-radius: 10px;
        margin-bottom: 20px;
        border-bottom: 3px solid #FF8C00;
        text-align: center;
    }

    /* BOUTONS */
    .stButton>button { 
        background: linear-gradient(90deg, #FF8C00, #FF4500) !important; 
        color: white !important; border-radius: 8px; font-weight: bold; width: 100%; height: 45px;
    }
    .msg-card { background: #1c1f26; padding: 20px; border-radius: 12px; border-left: 6px solid #FF8C00; margin-bottom: 15px; }
    </style>
    """, unsafe_allow_html=True)

URL_BASE = "https://classconect-f1767-default-rtdb.europe-west1.firebasedatabase.app/"
URL_MSG = f"{URL_BASE}messages.json"
URL_USERS = f"{URL_BASE}utilisateurs.json"

if 'user' not in st.session_state: st.session_state.user = None
if 'page' not in st.session_state: st.session_state.page = "Mur"
if 'chat_target' not in st.session_state: st.session_state.chat_target = None

def fetch_db(url):
    try:
        r = requests.get(url, timeout=5)
        return r.json() if r.status_code == 200 else {}
    except: return {}

data_u = fetch_db(URL_USERS)

# --- 2. INTERFACE ---

if st.session_state.user is None:
    st.markdown("<div class='logo-box'>C</div><div class='logo-text'>Class Connect Algeria</div>", unsafe_allow_html=True)
    t1, t2 = st.tabs(["Connexion", "Inscription"])
    with t1:
        u = st.text_input("Pseudo", key="l_u")
        p = st.text_input("Mdp", type="password", key="l_p")
        if st.button("SE CONNECTER"):
            if u in data_u and str(data_u[u].get("mdp")) == str(p):
                st.session_state.user = u
                st.rerun()
    with t2:
        nu = st.text_input("Nouveau Pseudo", key="n_u")
        np = st.text_input("Nouveau Mdp", type="password", key="n_p")
        cl = st.selectbox("Ton Club", ["Paris SG", "Juventus", "Arsenal"])
        if st.button("CRÉER MON COMPTE"):
            if nu and np:
                requests.patch(URL_USERS, json={nu: {"mdp": np, "club": cl, "amis": {}}})
                st.session_state.user = nu
                st.rerun()

else:
    me = st.session_state.user
    my_club = data_u.get(me, {}).get("club", "Fan")

    # --- MENU DE NAVIGATION (REMPLACE LA SIDEBAR) ---
    st.markdown(f"<div class='nav-container'><h3>⚽ Bienvenue {me} ({my_club})</h3></div>", unsafe_allow_html=True)
    
    col_nav1, col_nav2, col_nav3 = st.columns(3)
    with col_nav1:
        if st.button("🏠 MUR MONDIAL"): st.session_state.page = "Mur"
    with col_nav2:
        if st.button("💬 MESSAGES PRIVÉS"): st.session_state.page = "Chat"
    with col_nav3:
        if st.button("🚪 DÉCONNEXION"):
            st.session_state.user = None
            st.rerun()

    st.divider()

    # --- PAGES ---
    if st.session_state.page == "Mur":
        col_post, col_feed = st.columns([1, 2])
        
        with col_post:
            st.subheader("📝 Publier")
            txt = st.text_area("Message", height=100)
            img = st.text_input("Lien Image (URL)")
            if st.button("POSTER 🚀"):
                requests.post(URL_MSG, json={"u": me, "c": my_club, "m": txt, "i": img, "d": "mondial"})
                st.rerun()

        with col_feed:
            st.subheader("🌍 Actualités")
            m_data = fetch_db(URL_MSG)
            if m_data:
                for k in reversed(list(m_data.keys())):
                    v = m_data[k]
                    if v.get("d") == "mondial":
                        st.markdown(f"<div class='msg-card'><b>{v['u']}</b> ({v.get('c','Fan')})<br>{v.get('m','')}</div>", unsafe_allow_html=True)
                        if v.get("i"): st.image(v["i"], use_container_width=True)

    elif st.session_state.page == "Chat":
        col_list, col_chat = st.columns([1, 2])
        
        with col_list:
            st.subheader("👥 Mes Amis")
            amis = data_u.get(me, {}).get("amis", {})
            if amis:
                for a in amis:
                    if st.button(f"👤 {a}", key=f"chat_{a}"):
                        st.session_state.chat_target = a
                        st.rerun()
            
            new_f = st.text_input("Pseudo à ajouter")
            if st.button("Ajouter l'ami"):
                if new_f in data_u and new_f != me:
                    requests.patch(f"{URL_BASE}utilisateurs/{me}/amis.json", json={new_f: True})
                    st.rerun()

        with col_chat:
            target = st.session_state.chat_target
            if target:
                st.subheader(f"Discussion avec {target}")
                m_data = fetch_db(URL_MSG)
                if m_data:
                    for k, v in m_data.items():
                        if (v.get("u") == me and v.get("d") == target) or (v.get("u") == target and v.get("d") == me):
                            side = "right" if v['u'] == me else "left"
                            color = "#FF8C00" if v['u'] == me else "#333"
                            st.markdown(f"<div style='text-align:{side};'><span style='background:{color}; padding:10px; border-radius:10px; display:inline-block; margin:5px;'>{v['m']}</span></div>", unsafe_allow_html=True)
                
                msg_in = st.text_input("Ton message...", key="in_chat")
                if st.button("ENVOYER"):
                    requests.post(URL_MSG, json={"u": me, "m": msg_in, "d": target})
                    st.rerun()
            else:
                st.info("Clique sur un ami à gauche pour discuter.")

# RECHARGEMENT STABLE
time.sleep(10)
st.rerun()
