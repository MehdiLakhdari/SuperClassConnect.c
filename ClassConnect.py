import streamlit as st
import requests
import time
from datetime import datetime

# --- 1. CONFIGURATION ---
URL_BASE = "https://classconect-f1767-default-rtdb.europe-west1.firebasedatabase.app/"
URL_MSG = f"{URL_BASE}messages.json"
URL_USERS = f"{URL_BASE}utilisateurs.json"

st.set_page_config(page_title="ClassConnect Pro +", page_icon="🔔", layout="centered")

# --- 2. DESIGN AVEC NOTIFICATIONS ---
st.markdown("""
    <style>
    .stApp { background-color: #0d1117; color: #c9d1d9; }
    .message-card { 
        background-color: #161b22; padding: 12px; border-radius: 10px; 
        border: 1px solid #30363d; margin-bottom: 8px;
    }
    .notif-badge {
        background-color: #ff4b4b; color: white; border-radius: 50%;
        padding: 2px 8px; font-size: 12px; font-weight: bold; margin-left: 10px;
    }
    .stButton>button { border-radius: 8px; font-weight: bold; width: 100%; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. SESSION & CHARGEMENT ---
if 'user' not in st.session_state:
    st.session_state.user = None

def charger(url):
    try:
        r = requests.get(url)
        return r.json() if r.status_code == 200 and r.json() else {}
    except: return {}

# --- 4. LOGIQUE DES NOTIFICATIONS ---
def compter_notifs(pseudo):
    data = charger(URL_MSG)
    count = 0
    if data:
        for k in data:
            v = data[k]
            # On compte les messages privés destinés à l'utilisateur
            if v.get("d") == pseudo:
                count += 1
    return count

# --- 5. AUTHENTIFICATION ---
if st.session_state.user is None:
    st.title("🚀 ClassConnect")
    mode = st.tabs(["Connexion", "Inscription"])
    
    with mode[0]:
        u = st.text_input("Pseudo", key="login_u")
        p = st.text_input("Mot de passe", type="password", key="login_p")
        if st.button("Se connecter"):
            users = charger(URL_USERS)
            if u in users and str(users[u].get("mdp")) == str(p):
                st.session_state.user = u
                st.rerun()
            else: st.error("Pseudo ou mot de passe incorrect.")

    with mode[1]:
        nu = st.text_input("Pseudo", key="reg_u")
        np = st.text_input("Mot de passe", type="password", key="reg_p")
        if st.button("Créer mon compte"):
            if nu and np:
                requests.patch(URL_USERS, json={nu: {"mdp": np, "t": time.time()}})
                st.success("Compte créé !")

# --- 6. INTERFACE PRINCIPALE ---
else:
    u_curr = st.session_state.user
    nb_notifs = compter_notifs(u_curr)
    
    # Affichage des notifs dans la sidebar
    label_prive = f"🔒 Messages Privés"
    if nb_notifs > 0:
        label_prive += f" ({nb_notifs})"

    st.sidebar.title(f"👤 {u_curr}")
    menu = st.sidebar.radio("Navigation", ["🌍 Mur Mondial", label_prive, "🚪 Déconnexion"])

    if "🔒 Messages Privés" in menu:
        st.header("💬 Tes Discussions")
        if nb_notifs > 0:
            st.warning(f"Tu as {nb_notifs} message(s) dans ta boîte !")
            
        ami = st.text_input("Discuter avec (Pseudo) :")
        if ami:
            msg_p = st.text_input("Ton message privé...", key="p_msg")
            if st.button("Envoyer 🔒"):
                if msg_p:
                    requests.post(URL_MSG, json={
                        "u": u_curr, "m": msg_p, "d": ami, "t": time.time(), "l": 0
                    })
                    st.rerun()
            
            st.divider()
            data = charger(URL_MSG)
            if data:
                for k in reversed(list(data.keys())):
                    v = data[k]
                    # Afficher la discussion entre les deux
                    if (v.get("u") == u_curr and v.get("d") == ami) or (v.get("u") == ami and v.get("d") == u_curr):
                        st.info(f"**{v['u']}**: {v['m']}")

    elif menu == "🌍 Mur Mondial":
        st.header("🌍 Mur Mondial")
        with st.expander("➕ Nouveau Post"):
            txt = st.text_area("Message...")
            if st.button("Publier"):
                requests.post(URL_MSG, json={
                    "u": u_curr, "m": txt, "d": "mondial", "t": time.time(), "l": 0
                })
                st.rerun()

        data = charger(URL_MSG)
        if data:
            for k in reversed(list(data.keys())):
                v = data[k]
                if v.get("d") == "mondial":
                    st.markdown(f"<div class='message-card'><b>{v['u']}</b><br>{v.get('m','')}</div>", unsafe_allow_html=True)

    elif menu == "🚪 Déconnexion":
        st.session_state.user = None
        st.rerun()

    # AUTO-REFRESH (Toutes les 12 secondes)
    time.sleep(12)
    st.rerun()
