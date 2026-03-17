import streamlit as st
import requests
import time
from datetime import datetime

# --- 1. CONFIGURATION ---
URL_BASE = "https://classconect-f1767-default-rtdb.europe-west1.firebasedatabase.app/"
URL_MSG = f"{URL_BASE}messages.json"
URL_USERS = f"{URL_BASE}utilisateurs.json"

st.set_page_config(page_title="ClassConnect Pro +", page_icon="🔔", layout="centered")

# --- 2. DESIGN SOMBRE & NOTIFICATIONS ---
st.markdown("""
    <style>
    .stApp { background-color: #0d1117; color: #c9d1d9; }
    .message-card { 
        background-color: #161b22; padding: 15px; border-radius: 12px; 
        border: 1px solid #30363d; margin-bottom: 10px;
    }
    .stButton>button { border-radius: 8px; font-weight: bold; width: 100%; }
    .stTextInput>div>div>input { background-color: #21262d; color: white; }
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
    
    # Menu avec notifications
    label_prive = f"🔒 Messages Privés"
    if nb_notifs > 0:
        label_prive += f" ({nb_notifs})"

    st.sidebar.title(f"👤 {u_curr}")
    menu = st.sidebar.radio("Navigation", ["🌍 Mur Mondial", label_prive, "🚪 Déconnexion"])

    if menu == "🌍 Mur Mondial":
        st.header("🌍 Mur Mondial")
        
        # --- SECTION POSTER (AVEC IMAGE) ---
        with st.expander("➕ Nouveau Post (Texte ou Image)"):
            txt = st.text_area("Ton message...")
            img_url = st.text_input("Lien d'une image (ex: https://...)")
            if st.button("Publier 🚀"):
                if txt or img_url:
                    requests.post(URL_MSG, json={
                        "u": u_curr, "m": txt, "i": img_url, 
                        "d": "mondial", "t": time.time(), "l": 0
                    })
                    st.rerun()

        st.divider()
        
        # --- AFFICHAGE DU MUR ---
        data = charger(URL_MSG)
        if data:
            for k in reversed(list(data.keys())):
                v = data[k]
                if v.get("d") == "mondial":
                    with st.container():
                        st.markdown(f"<div class='message-card'>", unsafe_allow_html=True)
                        st.write(f"👤 **{v['u']}**")
                        if v.get("m"):
                            st.write(v["m"])
                        if v.get("i"): # ICI : Affichage de l'image
                            st.image(v["i"], use_container_width=True)
                        
                        # Bouton Like
                        likes = v.get("l", 0)
                        if st.button(f"❤️ {likes}", key=k):
                            requests.patch(f"{URL_BASE}messages/{k}.json", json={"l": likes + 1})
                            st.rerun()
                        st.markdown("</div>", unsafe_allow_html=True)

    elif "🔒 Messages Privés" in menu:
        st.header("💬 Tes Discussions Privées")
        if nb_notifs > 0:
            st.warning(f"Tu as {nb_notifs} message(s) non lus !")
            
        ami = st.text_input("Pseudo de l'ami :")
        if ami:
            msg_p = st.text_input("Ton message privé...", key="p_msg")
            if st.button("Envoyer en privé"):
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
                    if (v.get("u") == u_curr and v.get("d") == ami) or (v.get("u") == ami and v.get("d") == u_curr):
                        st.info(f"**{v['u']}**: {v['m']}")

    elif menu == "🚪 Déconnexion":
        st.session_state.user = None
        st.rerun()

    # AUTO-REFRESH (Toutes les 12 secondes pour les notifs et messages)
    time.sleep(12)
    st.rerun()
