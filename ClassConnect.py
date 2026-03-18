import streamlit as st
import requests
import time

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Connect Class Algeria", page_icon="😊", layout="wide")

st.markdown("""
    <style>
    header {visibility: hidden;}
    .stApp { background-color: #0e1117; color: white; }
    .logo-box {
        background: linear-gradient(135deg, #FF8C00, #FF4500);
        width: 60px; height: 60px; border-radius: 12px;
        display: flex; align-items: center; justify-content: center;
        margin: 0 auto; font-size: 35px; font-weight: bold; color: white;
    }
    .stButton>button { 
        background: linear-gradient(90deg, #FF8C00, #FF4500) !important; 
        color: white !important; border-radius: 10px; font-weight: bold; width: 100%; height: 50px;
    }
    .msg-card { background: #1c1f26; padding: 15px; border-radius: 12px; border-left: 5px solid #FF8C00; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

URL_BASE = "https://classconect-f1767-default-rtdb.europe-west1.firebasedatabase.app/"
URL_MSG = f"{URL_BASE}messages.json"
URL_USERS = f"{URL_BASE}utilisateurs.json"

# --- 2. ÉTAT DE LA SESSION ---
if 'user' not in st.session_state: st.session_state.user = None
if 'page' not in st.session_state: st.session_state.page = "Mur"

# Fonction de récupération ultra-légère
def rapide_fetch(url):
    try:
        return requests.get(url, timeout=3).json()
    except:
        return {}

# --- 3. INTERFACE ---

if st.session_state.user is None:
    st.markdown("<div class='logo-box'>C</div><h3 style='text-align:center;'>Class Connect Algeria 😊</h3>", unsafe_allow_html=True)
    
    t1, t2 = st.tabs(["Connexion", "Inscription"])
    
    with t1:
        u_input = st.text_input("Pseudo", key="login_u").strip()
        p_input = st.text_input("Mdp", type="password", key="login_p").strip()
        
        if st.button("🚀 SE CONNECTER MAINTENANT"):
            if not u_input or not p_input:
                st.warning("Remplis tous les champs !")
            else:
                with st.spinner("Vérification en cours..."):
                    # On ne récupère les users QUE quand on clique sur le bouton
                    all_users = rapide_fetch(URL_USERS)
                    if u_input in all_users:
                        db_pass = str(all_users[u_input].get("mdp"))
                        if db_pass == p_input:
                            st.session_state.user = u_input
                            st.success("Connexion réussie !")
                            time.sleep(0.5)
                            st.rerun()
                        else:
                            st.error("Mot de passe incorrect")
                    else:
                        st.error("Ce pseudo n'existe pas")

    with t2:
        nu = st.text_input("Nouveau Pseudo", key="n_u").strip()
        np = st.text_input("Nouveau Mdp", type="password", key="n_p").strip()
        cl = st.selectbox("Club", ["Paris SG", "Juventus", "Arsenal"])
        if st.button("CRÉER MON COMPTE"):
            if nu and np:
                with st.spinner("Création..."):
                    requests.patch(URL_USERS, json={nu: {"mdp": np, "club": cl, "amis": {}}})
                    st.session_state.user = nu
                    st.rerun()

else:
    # --- INTERFACE CONNECTÉE ---
    me = st.session_state.user
    
    # Barre de navigation simple
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("🏠 MUR"): st.session_state.page = "Mur" ; st.rerun()
    with c2:
        if st.button("💬 MESSAGES"): st.session_state.page = "Chat" ; st.rerun()
    with c3:
        if st.button("🚪 QUITTER"): st.session_state.user = None ; st.rerun()

    st.divider()

    if st.session_state.page == "Mur":
        st.subheader("🌍 Mur")
        txt = st.text_area("Ton message")
        if st.button("POSTER"):
            if txt:
                requests.post(URL_MSG, json={"u": me, "m": txt, "d": "mondial", "t": time.time()})
                st.rerun()
        
        # Affichage
        msgs = rapide_fetch(URL_MSG)
        if msgs:
            for k in reversed(list(msgs.keys())):
                v = msgs[k]
                if v.get("d") == "mondial":
                    st.markdown(f"<div class='msg-card'><b>{v['u']}</b><br>{v['m']}</div>", unsafe_allow_html=True)

    elif st.session_state.page == "Chat":
        st.subheader("💬 Messagerie")
        # Ici tu peux remettre ton code de chat précédent
        st.info("Ajoute tes amis pour discuter !")
