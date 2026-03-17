import streamlit as st
import requests
import time
from datetime import datetime

# --- 1. CONFIGURATION ---
URL_BASE = "https://classconect-f1767-default-rtdb.europe-west1.firebasedatabase.app/"
URL_MSG = f"{URL_BASE}messages.json"
URL_USERS = f"{URL_BASE}utilisateurs.json"

st.set_page_config(page_title="ClassConnect Pro", page_icon="📱", layout="centered")

# --- 2. DESIGN SOMBRE & PRO ---
st.markdown("""
    <style>
    .stApp { background-color: #0d1117; color: #c9d1d9; }
    .message-card { 
        background-color: #161b22; padding: 15px; border-radius: 10px; 
        border: 1px solid #30363d; margin-bottom: 10px;
    }
    .stButton>button { 
        background-color: #238636; color: white; border-radius: 8px; 
        font-weight: bold; border: none; width: 100%;
    }
    .post-btn>button { background-color: #f0b90b !important; color: black !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. SESSION ---
if 'user' not in st.session_state:
    st.session_state.user = None

# --- 4. FONCTIONS ---
def charger(url):
    try:
        r = requests.get(url)
        return r.json() if r.json() else {}
    except: return {}

# --- 5. PAGE DE CONNEXION ---
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
            else: st.error("Pseudo ou mot de passe faux !")

    with mode[1]:
        nu = st.text_input("Pseudo", key="reg_u")
        ne = st.text_input("Email", key="reg_e")
        np = st.text_input("Mot de passe", type="password", key="reg_p")
        col1, col2 = st.columns(2)
        sex = col1.selectbox("Sexe", ["Homme", "Femme"])
        age = col2.number_input("Âge", 10, 99)
        if st.button("Créer mon compte"):
            if nu and np:
                requests.patch(URL_USERS, json={nu: {"mdp": np, "email": ne, "sexe": sex, "age": age}})
                st.success("Compte créé ! Connecte-toi.")

# --- 6. INTERFACE PRINCIPALE ---
else:
    st.sidebar.title(f"👤 {st.session_state.user}")
    menu = st.sidebar.radio("Aller vers :", ["🌍 Mur Mondial", "🔒 Messages Privés", "🚪 Déconnexion"])

    if menu == "🌍 Mur Mondial":
        st.header("🌍 Mur Mondial")
        
        # --- BOUTON POST DIRECT ---
        with st.expander("➕ NOUVEAU POST (Clique ici)", expanded=False):
            txt = st.text_area("Ton message...")
            url_img = st.text_input("Lien d'une photo (optionnel)")
            if st.button("PUBLIER MAINTENANT 🚀"):
                if txt or url_img:
                    requests.post(URL_MSG, json={
                        "u": st.session_state.user, "m": txt, "i": url_img,
                        "d": "mondial", "t": time.time(), "l": 0
                    })
                    st.success("Posté !")
                    time.sleep(1)
                    st.rerun()

        st.divider()
        
        # AFFICHAGE
        data = charger(URL_MSG)
        if data:
            for k in reversed(list(data.keys())):
                v = data[k]
                if v.get("d") == "mondial":
                    with st.container():
                        st.markdown(f"<div class='message-card'><b>{v['u']}</b><br>{v.get('m','')}", unsafe_allow_html=True)
                        if v.get("i"): st.image(v["i"])
                        
                        # Bouton Like
                        likes = v.get("l", 0)
                        if st.button(f"❤️ {likes}", key=k):
                            requests.patch(f"{URL_BASE}messages/{k}.json", json={"l": likes + 1})
                            st.rerun()
                        st.markdown("</div>", unsafe_allow_html=True)
        
        # Auto-refresh toutes les 15 secondes
        time.sleep(15)
        st.rerun()

    elif menu == "🔒 Messages Privés":
        ami = st.text_input("Nom de l'ami :")
        if ami:
            msg_p = st.text_input("Message privé...")
            if st.button("Envoyer"):
                requests.post(URL_MSG, json={"u": st.session_state.user, "m": msg_p, "d": ami, "t": time.time(), "l": 0})
                st.rerun()
            
            data = charger(URL_MSG)
            if data:
                for k in reversed(list(data.keys())):
                    v = data[k]
                    if (v.get("u")==st.session_state.user and v.get("d")==ami) or (v.get("u")==ami and v.get("d")==st.session_state.user):
                        st.info(f"**{v['u']}**: {v['m']}")

    elif menu == "🚪 Déconnexion":
        st.session_state.user = None
        st.rerun()
