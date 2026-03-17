import streamlit as st
import requests
import time
from datetime import datetime

# --- 1. CONFIGURATION ---
URL_BASE = "https://classconect-f1767-default-rtdb.europe-west1.firebasedatabase.app/"
URL_MSG = f"{URL_BASE}messages.json"
URL_USERS = f"{URL_BASE}utilisateurs.json"

st.set_page_config(page_title="ClassConnect Pro", page_icon="💬", layout="centered")

# --- 2. SESSION ---
if 'theme' not in st.session_state: st.session_state.theme = "sombre"
if 'user' not in st.session_state: st.session_state.user = None
if 'chat_with' not in st.session_state: st.session_state.chat_with = None

# --- 3. STYLE DYNAMIQUE CORRIGÉ ---
if st.session_state.theme == "sombre":
    bg, txt, btn, card, fade = "#0f0f0f", "#ffffff", "#7b1fa2", "#1e1e1e", "#333333"
else:
    # Correction : Texte beaucoup plus foncé (#000000) pour la visibilité
    bg, txt, btn, card, fade = "#ffffff", "#000000", "#d32f2f", "#f0f2f5", "#cccccc"

st.markdown(f"""
    <style>
    .stApp {{ background-color: {bg}; color: {txt}; }}
    .message-card {{ 
        background-color: {card}; padding: 12px; border-radius: 15px; 
        margin-bottom: 10px; border: 1px solid {fade};
    }}
    .profile-pic {{
        width: 40px; height: 40px; border-radius: 50%; 
        object-fit: cover; vertical-align: middle; margin-right: 10px;
    }}
    .contact-btn {{
        display: flex; align-items: center; padding: 10px;
        background-color: {card}; border-radius: 10px; cursor: pointer;
        margin-bottom: 5px; border: 1px solid {fade};
    }}
    .stButton>button {{ border-radius: 20px; font-weight: bold; border:none; }}
    /* Visibilité des textes dans les inputs */
    input {{ color: {txt} !important; }}
    </style>
    """, unsafe_allow_html=True)

# --- 4. FONCTIONS ---
def charger(url):
    try:
        r = requests.get(url)
        return r.json() if r.status_code == 200 and r.json() else {}
    except: return {}

def get_pfp(pseudo, users_data):
    # Récupère la photo de profil ou une image par défaut
    user_info = users_data.get(pseudo, {})
    return user_info.get("pfp", "https://cdn-icons-png.flaticon.com/512/149/149071.png")

# --- 5. AUTHENTIFICATION ---
users_data = charger(URL_USERS)

if st.session_state.user is None:
    st.title("🚀 ClassConnect")
    mode = st.tabs(["Connexion", "Inscription"])
    with mode[0]:
        u = st.text_input("Pseudo")
        p = st.text_input("Mot de passe", type="password")
        if st.button("Se connecter"):
            if u in users_data and str(users_data[u].get("mdp")) == str(p):
                st.session_state.user = u
                st.rerun()
            else: st.error("Pseudo ou mot de passe incorrect.")
    with mode[1]:
        nu = st.text_input("Nouveau Pseudo")
        np = st.text_input("Mot de passe ", type="password")
        if st.button("Créer mon compte"):
            if nu and np:
                requests.patch(URL_USERS, json={nu: {"mdp": np, "pfp": ""}})
                st.success("Compte créé !")

# --- 6. INTERFACE PRINCIPALE ---
else:
    me = st.session_state.user
    my_pfp = get_pfp(me, users_data)

    # SIDEBAR
    st.sidebar.markdown(f"<img src='{my_pfp}' class='profile-pic'> <b>{me}</b>", unsafe_allow_html=True)
    
    st.sidebar.divider()
    menu = st.sidebar.radio("Menu", ["🌍 Mur Mondial", "🔒 Discussions", "⚙️ Mon Profil", "🚪 Quitter"])

    if menu == "🌍 Mur Mondial":
        st.header("🌍 Mur Mondial")
        with st.expander("📝 Poster quelque chose"):
            txt_msg = st.text_area("Message")
            img_msg = st.text_input("Lien Image")
            if st.button("Publier"):
                requests.post(URL_MSG, json={"u": me, "m": txt_msg, "i": img_msg, "d": "mondial", "t": time.time(), "l": 0})
                st.rerun()

        msgs = charger(URL_MSG)
        for k in reversed(list(msgs.keys())):
            v = msgs[k]
            if v.get("d") == "mondial":
                pfp = get_pfp(v['u'], users_data)
                st.markdown(f"""<div class='message-card'>
                    <img src='{pfp}' class='profile-pic'><b>{v['u']}</b><br>
                    <p style='margin-left:50px;'>{v.get('m','')}</p>
                </div>""", unsafe_allow_html=True)
                if v.get("i"): st.image(v["i"])

    elif menu == "🔒 Discussions":
        st.header("🔒 Messages Privés")
        
        # Liste des contacts avec qui on a déjà parlé
        msgs = charger(URL_MSG)
        contacts = set()
        for k in msgs:
            v = msgs[k]
            if v.get("d") != "mondial":
                if v.get("u") == me: contacts.add(v.get("d"))
                if v.get("d") == me: contacts.add(v.get("u"))
        
        st.sidebar.subheader("Contacts récents")
        for c in contacts:
            if st.sidebar.button(f"👤 {c}", key=f"contact_{c}"):
                st.session_state.chat_with = c
        
        target = st.text_input("Chercher un pseudo :", value=st.session_state.chat_with if st.session_state.chat_with else "")
        if target:
            st.session_state.chat_with = target
            pfp_target = get_pfp(target, users_data)
            st.markdown(f"### Discuter avec <img src='{pfp_target}' class='profile-pic'> {target}", unsafe_allow_html=True)
            
            new_p_msg = st.text_input("Ecrire...")
            if st.button("Envoyer"):
                requests.post(URL_MSG, json={"u": me, "m": new_p_msg, "d": target, "t": time.time()})
                st.rerun()
            
            for k in reversed(list(msgs.keys())):
                v = msgs[k]
                if (v.get("u") == me and v.get("d") == target) or (v.get("u") == target and v.get("d") == me):
                    align = "right" if v.get("u") == me else "left"
                    st.markdown(f"<div style='text-align:{align};' class='message-card'><b>{v['u']}</b>: {v['m']}</div>", unsafe_allow_html=True)

    elif menu == "⚙️ Mon Profil":
        st.header("⚙️ Modifier mon profil")
        new_pfp = st.text_input("Lien de ta photo de profil (URL)", value=my_pfp)
        if st.button("Enregistrer les modifs"):
            requests.patch(f"{URL_BASE}utilisateurs/{me}.json", json={"pfp": new_pfp})
            st.success("Profil mis à jour !")
            st.rerun()
            
        st.divider()
        st.subheader("🎨 Thème")
        if st.button("🌙 Mode Sombre"): st.session_state.theme = "sombre"; st.rerun()
        if st.button("☀️ Mode Clair"): st.session_state.theme = "clair"; st.rerun()

    elif menu == "🚪 Quitter":
        st.session_state.user = None
        st.rerun()

    time.sleep(10)
    st.rerun()
