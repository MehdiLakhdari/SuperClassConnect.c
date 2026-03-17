import streamlit as st
import requests
import time
from datetime import datetime

# --- 1. CONFIGURATION ---
URL_BASE = "https://classconect-f1767-default-rtdb.europe-west1.firebasedatabase.app/"
URL_MSG = f"{URL_BASE}messages.json"
URL_USERS = f"{URL_BASE}utilisateurs.json"

st.set_page_config(page_title="ClassConnect Official", page_icon="🛡️", layout="centered")

# --- 2. GESTION DES THÈMES & SESSION ---
if 'theme' not in st.session_state:
    st.session_state.theme = "sombre"
if 'user' not in st.session_state:
    st.session_state.user = None
if 'last_msg_count' not in st.session_state:
    st.session_state.last_msg_count = 0

# --- 3. STYLE DYNAMIQUE (VIOLET/NOIR vs ROUGE/BLANC) ---
if st.session_state.theme == "sombre":
    bg, txt, btn, card = "#0f0f0f", "#e0e0e0", "#6200ee", "#1e1e1e" # Violet & Noir
else:
    bg, txt, btn, card = "#ffffff", "#1a1a1a", "#d32f2f", "#f8f9fa" # Rouge & Blanc

st.markdown(f"""
    <style>
    .stApp {{ background-color: {bg}; color: {txt}; }}
    .message-card {{ 
        background-color: {card}; padding: 15px; border-radius: 12px; 
        border-left: 5px solid {btn}; margin-bottom: 10px; box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
    }}
    .stButton>button {{ background-color: {btn}; color: white; border-radius: 20px; font-weight: bold; width: 100%; border:none; }}
    </style>
    """, unsafe_allow_html=True)

# --- 4. FONCTIONS ---
def charger(url):
    try:
        r = requests.get(url)
        return r.json() if r.status_code == 200 and r.json() else {}
    except: return {}

# --- 5. SYSTÈME DE NOTIFICATIONS DIRECTES ---
def verifier_notifs():
    if st.session_state.user:
        data = charger(URL_MSG)
        current_count = len(data) if data else 0
        if current_count > st.session_state.last_msg_count:
            # Vérifier si le dernier message est pour moi
            last_key = list(data.keys())[-1]
            last_v = data[last_key]
            if last_v.get("d") == st.session_state.user:
                st.toast(f"🔔 Nouveau message de {last_v['u']} !", icon="💬")
            st.session_state.last_msg_count = current_count

# --- 6. AUTHENTIFICATION ---
if st.session_state.user is None:
    st.title("🛡️ ClassConnect Official")
    mode = st.tabs(["Connexion", "Inscription"])
    with mode[0]:
        u = st.text_input("Pseudo")
        p = st.text_input("Mot de passe", type="password")
        if st.button("Se connecter"):
            users = charger(URL_USERS)
            if u in users and str(users[u].get("mdp")) == str(p):
                st.session_state.user = u
                st.rerun()
            else: st.error("Erreur d'accès")
    with mode[1]:
        nu = st.text_input("Pseudo d'élève")
        np = st.text_input("Mot de passe", type="password")
        if st.button("Créer mon compte"):
            if nu and np:
                requests.patch(URL_USERS, json={nu: {"mdp": np, "t": time.time()}})
                st.success("Compte validé !")

# --- 7. INTERFACE PRINCIPALE ---
else:
    verifier_notifs()
    
    # Sidebar avec sélecteur de thème
    st.sidebar.title(f"👤 {st.session_state.user}")
    
    st.sidebar.subheader("🎨 Apparence")
    if st.sidebar.button("🌙 Mode Sombre"):
        st.session_state.theme = "sombre"
        st.rerun()
    if st.sidebar.button("☀️ Mode Clair"):
        st.session_state.theme = "clair"
        st.rerun()
    
    st.sidebar.divider()
    menu = st.sidebar.radio("Navigation", ["🌍 Mur Mondial", "🔒 Messages Privés", "🚪 Déconnexion"])

    if menu == "🌍 Mur Mondial":
        st.header("🌍 Mur Mondial")
        with st.expander("➕ Nouveau Post"):
            txt = st.text_area("Ton message...")
            img = st.text_input("Lien d'une photo (URL)")
            if st.button("Publier"):
                requests.post(URL_MSG, json={"u": st.session_state.user, "m": txt, "i": img, "d": "mondial", "t": time.time(), "l": 0})
                st.rerun()

        data = charger(URL_MSG)
        if data:
            for k in reversed(list(data.keys())):
                v = data[k]
                if v.get("d") == "mondial":
                    st.markdown(f"<div class='message-card'><b>{v['u']}</b><br>{v.get('m','')}", unsafe_allow_html=True)
                    if v.get("i"): st.image(v["i"])
                    
                    likes = v.get("l", 0)
                    if st.button(f"❤️ {likes}", key=k):
                        requests.patch(f"{URL_BASE}messages/{k}.json", json={"l": likes + 1})
                        st.rerun()
                    st.markdown("</div>", unsafe_allow_html=True)

    elif menu == "🔒 Messages Privés":
        ami = st.text_input("Discuter avec :")
        if ami:
            msg_p = st.text_input("Message...")
            if st.button("Envoyer"):
                requests.post(URL_MSG, json={"u": st.session_state.user, "m": msg_p, "d": ami, "t": time.time()})
                st.rerun()
            
            data = charger(URL_MSG)
            if data:
                for k in reversed(list(data.keys())):
                    v = data[k]
                    if (v.get("u") == st.session_state.user and v.get("d") == ami) or (v.get("u") == ami and v.get("d") == st.session_state.user):
                        st.info(f"**{v['u']}**: {v['m']}")

    elif menu == "🚪 Déconnexion":
        st.session_state.user = None
        st.rerun()

    time.sleep(10)
    st.rerun()
