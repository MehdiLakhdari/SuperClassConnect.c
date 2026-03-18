import streamlit as st
import requests
import time

# --- 1. CONFIGURATION DE FORCE ---
st.set_page_config(
    page_title="Connect Class", 
    page_icon="⚽", 
    layout="wide",
    initial_sidebar_state="expanded"  # FORCE L'OUVERTURE DE LA BARRE LATERALE
)

# DESIGN CSS
st.markdown("""
    <style>
    header {visibility: hidden;}
    .stApp { background-color: #0e1117; color: white; }
    [data-testid="stSidebar"] { background-color: #1c1f26 !important; border-right: 2px solid #FF8C00; }
    .logo-box {
        background: linear-gradient(135deg, #FF8C00, #FF4500);
        width: 60px; height: 60px; border-radius: 12px;
        display: flex; align-items: center; justify-content: center;
        margin: 0 auto; font-size: 40px; font-weight: bold; color: white;
    }
    .stButton>button { 
        background: linear-gradient(90deg, #FF8C00, #FF4500) !important; 
        color: white !important; border-radius: 8px; font-weight: bold; width: 100%;
    }
    .msg-card { background: #1c1f26; padding: 15px; border-radius: 12px; border-left: 5px solid #FF8C00; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

URL_BASE = "https://classconect-f1767-default-rtdb.europe-west1.firebasedatabase.app/"
URL_MSG = f"{URL_BASE}messages.json"
URL_USERS = f"{URL_BASE}utilisateurs.json"

# --- 2. GESTION DE LA SESSION ---
if 'user' not in st.session_state: st.session_state.user = None
if 'page' not in st.session_state: st.session_state.page = "Mur"
if 'chat_target' not in st.session_state: st.session_state.chat_target = None

def fetch_db(url):
    try:
        r = requests.get(url, timeout=5)
        return r.json() if r.status_code == 200 else {}
    except: return {}

data_u = fetch_db(URL_USERS)

# --- 3. INTERFACE ---

# CAS A : NON CONNECTÉ
if st.session_state.user is None:
    st.markdown("<div class='logo-box'>C</div><h2 style='text-align:center;'>Class Connect Algeria</h2>", unsafe_allow_html=True)
    t1, t2 = st.tabs(["Connexion", "Inscription"])
    with t1:
        u = st.text_input("Pseudo", key="login_u")
        p = st.text_input("Mdp", type="password", key="login_p")
        if st.button("SE CONNECTER"):
            if u in data_u and str(data_u[u].get("mdp")) == str(p):
                st.session_state.user = u
                st.rerun()
    with t2:
        nu = st.text_input("Nouveau Pseudo", key="new_u")
        np = st.text_input("Nouveau Mdp", type="password", key="new_p")
        cl = st.selectbox("Club", ["Paris SG", "Juventus", "Arsenal"])
        if st.button("CRÉER COMPTE"):
            if nu and np:
                requests.patch(URL_USERS, json={nu: {"mdp": np, "club": cl, "amis": {}}})
                st.session_state.user = nu
                st.rerun()

# CAS B : CONNECTÉ (BARRE LATERALE GARANTIE)
else:
    me = st.session_state.user
    my_club = data_u.get(me, {}).get("club", "Fan")

    # BARRE LATERALE SANS CONDITION
    with st.sidebar:
        st.markdown("<div class='logo-box'>C</div>", unsafe_allow_html=True)
        st.markdown(f"<h3 style='text-align:center;'>@{me}</h3>", unsafe_allow_html=True)
        st.write(f"⚽ {my_club}")
        st.divider()
        
        # NAVIGATION
        if st.button("🏠 MUR MONDIAL", key="nav_1"): 
            st.session_state.page = "Mur"
            st.rerun()
        if st.button("💬 MESSAGES PRIVÉS", key="nav_2"): 
            st.session_state.page = "Chat"
            st.rerun()
        
        st.divider()
        st.write("👥 **CONTACTS**")
        amis = data_u.get(me, {}).get("amis", {})
        if amis:
            for a in amis:
                if st.button(f"👤 {a}", key=f"contact_{a}"):
                    st.session_state.chat_target = a
                    st.session_state.page = "Chat"
                    st.rerun()
        
        new_f = st.text_input("Ajouter un pseudo", key="add_input")
        if st.button("Ajouter à ma liste", key="add_btn"):
            if new_f in data_u and new_f != me:
                requests.patch(f"{URL_BASE}utilisateurs/{me}/amis.json", json={new_f: True})
                st.rerun()
        
        st.divider()
        if st.button("🚪 DÉCONNEXION", key="logout_btn"):
            st.session_state.user = None
            st.rerun()

    # PAGES
    if st.session_state.page == "Mur":
        st.title("🏠 Mur Mondial")
        with st.expander("📝 Publier"):
            txt = st.text_area("Ton message")
            img = st.text_input("Lien Image URL")
            if st.button("POSTER 🚀"):
                requests.post(URL_MSG, json={"u": me, "c": my_club, "m": txt, "i": img, "d": "mondial"})
                st.rerun()
        
        m_data = fetch_db(URL_MSG)
        if m_data:
            for k in reversed(list(m_data.keys())):
                v = m_data[k]
                if v.get("d") == "mondial":
                    st.markdown(f"<div class='msg-card'><b>{v['u']}</b> ({v.get('c','Fan')})<br>{v.get('m','')}</div>", unsafe_allow_html=True)
                    if v.get("i"): st.image(v["i"], use_container_width=True)

    elif st.session_state.page == "Chat":
        target = st.session_state.chat_target
        if target:
            st.title(f"💬 Chat avec {target}")
            m_data = fetch_db(URL_MSG)
            if m_data:
                for k, v in m_data.items():
                    if (v.get("u") == me and v.get("d") == target) or (v.get("u") == target and v.get("d") == me):
                        side = "right" if v['u'] == me else "left"
                        color = "#FF8C00" if v['u'] == me else "#333"
                        st.markdown(f"<div style='text-align:{side};'><span style='background:{color}; padding:10px; border-radius:10px; display:inline-block; margin:5px;'>{v['m']}</span></div>", unsafe_allow_html=True)
            
            msg_in = st.text_input("Écrire...", key="in_chat")
            if st.button("ENVOYER"):
                requests.post(URL_MSG, json={"u": me, "m": msg_in, "d": target})
                st.rerun()
        else:
            st.info("Sélectionne un ami dans la liste à gauche.")

# STABILISATION
time.sleep(10)
st.rerun()
