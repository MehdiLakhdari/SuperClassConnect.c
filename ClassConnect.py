import streamlit as st
import requests
import time
from datetime import datetime

# --- 1. CONFIGURATION ---
URL_BASE = "https://classconect-f1767-default-rtdb.europe-west1.firebasedatabase.app/"
URL_MSG = f"{URL_BASE}messages.json"
URL_USERS = f"{URL_BASE}utilisateurs.json"

st.set_page_config(page_title="ClassConnect Fast", page_icon="⚡", layout="centered")

# --- 2. DESIGN DARK & FLUIDE ---
st.markdown("""
    <style>
    .stApp { background-color: #0d1117; color: #c9d1d9; }
    .message-card { 
        background-color: #161b22; padding: 15px; border-radius: 12px; 
        border: 1px solid #30363d; margin-bottom: 15px;
    }
    .stButton>button { border-radius: 20px; font-weight: bold; transition: 0.2s; }
    .stButton>button:hover { transform: scale(1.02); background-color: #03DAC6; color: black; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. SESSION ---
if 'user' not in st.session_state:
    st.session_state.user = None

def charger(url):
    try:
        r = requests.get(url)
        return r.json() if r.status_code == 200 and r.json() else {}
    except: return {}

# --- 4. AUTHENTIFICATION ---
if st.session_state.user is None:
    st.title("⚡ ClassConnect Fast")
    mode = st.tabs(["🔑 Connexion", "📝 Inscription"])
    with mode[0]:
        u = st.text_input("Pseudo", key="login_u")
        p = st.text_input("Mot de passe", type="password", key="login_p")
        if st.button("Se connecter"):
            users = charger(URL_USERS)
            if u in users and str(users[u].get("mdp")) == str(p):
                st.session_state.user = u
                st.rerun()
            else: st.error("Identifiants incorrects.")
    with mode[1]:
        nu = st.text_input("Nouveau Pseudo")
        np = st.text_input("Nouveau Mot de passe", type="password")
        if st.button("Créer mon compte"):
            if nu and np:
                requests.patch(URL_USERS, json={nu: {"mdp": np, "t": time.time()}})
                st.success("Compte créé !")

# --- 5. INTERFACE PRINCIPALE ---
else:
    u_curr = st.session_state.user
    st.sidebar.title(f"⚽ {u_curr}")
    
    # Notifications
    data_all = charger(URL_MSG)
    nb_notifs = sum(1 for k in data_all if data_all[k].get("d") == u_curr)
    label_prive = f"🔒 Privé ({nb_notifs})" if nb_notifs > 0 else "🔒 Privé"
    
    menu = st.sidebar.radio("Navigation", ["🌍 Mur Mondial", label_prive, "🚪 Déconnexion"])

    if menu == "🌍 Mur Mondial":
        st.header("🌍 Mur Mondial")
        
        # --- SECTION POSTER (TEXTE + GIF/IMAGE) ---
        with st.expander("➕ Nouveau Post (Texte, Photo ou GIF)"):
            txt = st.text_area("Ton message...")
            media_url = st.text_input("Lien de l'image ou du GIF")
            
            st.write("Réactions rapides (GIFs) :")
            c1, c2, c3 = st.columns(3)
            # GIF Facepalm (se frappe la tête)
            if c1.button("🤦‍♂️ Facepalm"): 
                media_url = "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExM2I1eHlyZzR4ZzR4ZzR4ZzR4ZzR4ZzR4ZzR4ZzR4ZzR4ZzR4JmVwPXYxX2ludGVybmFsX2dpZl9ieV9pZCZjdD1n/3og0INyCmHLYS35ps4/giphy.gif"
            # GIF Choqué
            if c2.button("😲 QUOI ?"): 
                media_url = "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExM2I1eHlyZzR4ZzR4ZzR4ZzR4ZzR4ZzR4ZzR4ZzR4ZzR4ZzR4JmVwPXYxX2ludGVybmFsX2dpZl9ieV9pZCZjdD1n/26ufdipLGQpD8F9kY/giphy.gif"
            # GIF Bravo
            if c3.button("👏 Bravo"): 
                media_url = "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExM2I1eHlyZzR4ZzR4ZzR4ZzR4ZzR4ZzR4ZzR4ZzR4ZzR4ZzR4JmVwPXYxX2ludGVybmFsX2dpZl9ieV9pZCZjdD1n/l3q2XhfQ8oCkm1Ts4/giphy.gif"

            if st.button("PUBLIER 🚀"):
                if txt or media_url:
                    requests.post(URL_MSG, json={
                        "u": u_curr, "m": txt, "i": media_url, 
                        "d": "mondial", "t": time.time(), "l": 0
                    })
                    st.rerun()

        st.divider()
        
        # --- AFFICHAGE ---
        if data_all:
            for k in reversed(list(data_all.keys())):
                v = data_all[k]
                if v.get("d") == "mondial":
                    with st.container():
                        st.markdown(f"<div class='message-card'>", unsafe_allow_html=True)
                        st.write(f"👤 **{v['u']}**")
                        if v.get("m"): st.write(v["m"])
                        
                        # Affichage Image ou GIF
                        if v.get("i"):
                            st.image(v["i"], use_container_width=True)
                        
                        likes = v.get("l", 0)
                        if st.button(f"❤️ {likes}", key=k):
                            requests.patch(f"{URL_BASE}messages/{k}.json", json={"l": likes + 1})
                            st.rerun()
                        st.markdown("</div>", unsafe_allow_html=True)

    elif "🔒 Privé" in menu:
        st.header("💬 Messages Privés")
        ami = st.text_input("Pseudo de l'ami :")
        if ami:
            msg_p = st.text_input("Ton message...")
            if st.button("Envoyer 🔒"):
                requests.post(URL_MSG, json={"u": u_curr, "m": msg_p, "d": ami, "t": time.time()})
                st.rerun()
            
            for k in reversed(list(data_all.keys())):
                v = data_all[k]
                if (v.get("u") == u_curr and v.get("d") == ami) or (v.get("u") == ami and v.get("d") == u_curr):
                    st.info(f"**{v['u']}**: {v['m']}")

    elif menu == "🚪 Déconnexion":
        st.session_state.user = None
        st.rerun()

    time.sleep(10) # Rafraîchissement toutes les 10 secondes
    st.rerun()
