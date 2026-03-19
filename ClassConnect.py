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
    
    /* BOUTONS NAVIGATION - ORANGE CC */
    div[data-testid="stColumn"] .stButton>button { 
        background: linear-gradient(90deg, #FF8C00, #FF4500) !important; 
        color: white !important; border-radius: 8px; font-weight: bold; height: 50px; border: none;
    }

    /* NOTIF FLASH ROUGE */
    @keyframes blink { 0% {box-shadow: 0 0 5px #FF0000;} 50% {box-shadow: 0 0 20px #FF0000;} 100% {box-shadow: 0 0 5px #FF0000;} }
    .notif-active button { animation: blink 1s infinite !important; border: 1px solid white !important; }

    /* CARTES */
    .msg-card { background: #111; padding: 15px; border-radius: 10px; border-left: 5px solid #D32F2F; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- LIENS FIREBASE ---
URL_BASE = "https://classconect-f1767-default-rtdb.europe-west1.firebasedatabase.app/"
URL_MSG = f"{URL_BASE}messages.json"
URL_USERS = f"{URL_BASE}utilisateurs.json"

# INITIALISATION DES SESSIONS
if 'user' not in st.session_state: st.session_state.user = None
if 'page' not in st.session_state: st.session_state.page = "Mur"
if 'last_count' not in st.session_state: st.session_state.last_count = 0

def get_db(url):
    try:
        r = requests.get(url, timeout=5)
        return r.json() if r.status_code == 200 else {}
    except:
        return {}

# RÉCUPÉRATION DES DONNÉES
data_u = get_db(URL_USERS)
all_m = get_db(URL_MSG)
curr_count = len(all_m) if all_m else 0

# LOGIQUE DE CONNEXION
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
        nu = st.text_input("Choisis un Pseudo").strip()
        np = st.text_input("Choisis un Mdp", type="password").strip()
        if st.button("CRÉER MON COMPTE"):
            if nu and np and nu not in data_u:
                requests.patch(URL_USERS, json={nu: {"mdp": np, "amis": {"Admin": True}}})
                st.success("Compte créé !")
                time.sleep(1
