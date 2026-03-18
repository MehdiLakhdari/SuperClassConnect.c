import streamlit as st
import requests
import time

# --- 1. CONFIGURATION ---
URL_BASE = "https://classconect-f1767-default-rtdb.europe-west1.firebasedatabase.app/"
URL_MSG = f"{URL_BASE}messages.json"
URL_USERS = f"{URL_BASE}utilisateurs.json"

st.set_page_config(page_title="Connect Class Algeria", page_icon="⚽", layout="wide")

# --- 2. INITIALISATION DES VARIABLES ---
if 'user' not in st.session_state: st.session_state.user = None
if 'page' not in st.session_state: st.session_state.page = "🏠 Mur"
if 'chat_target' not in st.session_state: st.session_state.chat_target = None

# --- 3. FONCTIONS DE CHARGEMENT ---
def charger(url):
    try:
        r = requests.get(url, timeout=5)
        return r.json() if r.status_code == 200 and r.json() else {}
    except: return {}

data_u = charger(URL_USERS)
all_msgs = charger(URL_MSG)

# --- 4. RÉCUPÉRATION DU STYLE DU CLUB ---
user_club = "PSG"
if st.session_state.user and st.session_state.user in data_u:
    user_club = data_u[st.session_state.user].get("club", "PSG")

# Dictionnaire des couleurs officielles
styles = {
    "PSG": {"bg": "#001C3F", "accent": "#E30613", "txt": "white"},
    "Barça": {"bg": "#004D98", "accent": "#A50044", "txt": "#EDBB00"},
    "Juventus": {"bg": "#111111", "accent": "#FFFFFF", "txt": "#000000"}
}
s = styles.get(user_club, styles["PSG"])

# Injection CSS pour les couleurs vives
st.markdown(f"""
    <style>
    .stApp {{ background-color: {s['bg']} !important; color: white !important; }}
    [data-testid="stSidebar"] {{ 
        background-color: rgba(0,0,0,0.9) !important; 
        border-right: 4px solid {s['accent']} !important;
        min-width: 260px !important;
    }}
    .stButton>button {{ 
        background-color: {s['accent']} !important; 
        color: {s['txt']} !important; 
        border: 1px solid white !important;
        font-weight: bold !important;
        text-transform: uppercase;
        border-radius: 10px !important;
    }}
    .msg-card {{ 
        background: rgba(255,255,255,0.15); 
        padding: 15px; border-radius: 12px; 
        border-left: 6px solid {s['accent']}; 
        margin-bottom: 10px;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 5. BARRE LATÉRALE (SIDEBAR) ---
with st.sidebar:
    st.markdown(f"<h1 style='color:white; text-align:center;'>CC</h1>", unsafe_allow_html=True)
    if st.session_state.user:
        st.success(f"Connecté : {st.session_state.user}")
        st.info(f"Club : {user_club}")
        st.divider()
        if st.button("🏠
