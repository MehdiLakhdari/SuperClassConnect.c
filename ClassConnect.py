import streamlit as st
import requests
import time

# 1. CONFIGURATION ÉCRAN PRO
st.set_page_config(page_title="Connect Class Algeria", page_icon="⚽", layout="wide")

# 2. DESIGN FIXE (SANS CLIGNOTEMENT)
st.markdown("""
    <style>
    header {visibility: hidden;}
    .stApp { background-color: #0e1117; color: white; }
    
    /* LOGO ORANGE CARRÉ */
    .logo-box {
        background: linear-gradient(135deg, #FF8C00, #FF4500);
        width: 65px; height: 65px; border-radius: 15px;
        display: flex; align-items: center; justify-content: center;
        margin: 0 auto; font-size: 40px; font-weight: bold; color: white;
    }
    .logo-text { font-size: 20px; font-weight: bold; color: #FF8C00; text-align: center; margin-top: 5px; }

    /* BOUTONS ET CARTES */
    .stButton>button { 
        background: linear-gradient(90deg, #FF8C00, #FF4500) !important; 
        color: white !important; border-radius: 10px; border: none; font-weight: bold;
    }
    .msg-card { background: #1c1f26; padding: 15px; border-radius: 12px; border-left: 5px solid #FF8C00; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

# 3. BASE DE DONNÉES
URL_BASE = "https://classconect-f1767-default-rtdb.europe-west1.firebasedatabase.app/"
URL_MSG = f"{URL_BASE}messages.json"
URL_USERS = f"{URL_BASE}utilisateurs.json"

# INITIALISATION DES VARIABLES SANS BUG
if 'user' not in st.session_state: st.session_state.user = None
if 'page' not in st.session_state: st.session_state.page = "Mur"
if 'chat_target' not in st.session_state: st.session_state.chat_target = None

# FONCTION DE CHARGEMENT SÉCURISÉE
def fetch_data(url):
    try:
        r = requests.get(url, timeout=3)
        return r.json() if r.status_code == 200 else {}
    except: return {}

# --- LOGIQUE D'AFFICHAGE ---

# A. SI PAS CONNECTÉ
if st.session_state.user is None:
    data_u = fetch_data(URL_USERS)
    st.markdown("<div class='logo-box'>C</div><div class='logo-text'>Class Connect Algeria</div>", unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["Connexion", "Inscription"])
    with tab1:
        u = st.text_input("Pseudo", key="login_user")
        p = st.text_input("Mdp", type="password", key="login_pass")
        if st.button("ENTRER", key="btn_login"):
            if u in data_u and str(data_u[u].get("mdp")) == str(p):
                st.session_state.user = u
                st.rerun()
            else: st.error("Erreur d'identifiants")
            
    with tab2:
        nu = st.text_input("Nouveau Pseudo", key="reg_user")
        np = st.text_input("Nouveau Mdp", type="password", key="reg_pass")
        club = st.selectbox("Club", ["Paris SG", "Juventus", "Arsenal"], key="reg_club")
        if st.button("CRÉER COMPTE", key="btn_reg"):
            if nu and np:
                requests.patch(URL_USERS, json={nu: {"mdp": np, "club": club, "amis": {}}})
                st.session_state.user = nu
                st.rerun()

# B. SI CONNECTÉ
else:
    me = st.session_state.user
    data_u = fetch_data(URL_USERS)
    my_club = data_u.get(me, {}).get("club", "Fan")

    # SIDEBAR FIXE
    with st.sidebar:
        st.markdown("<div class='logo-box'>C</div>", unsafe_allow_html=True)
        st.write(f"Bonjour **{me}**")
        st.divider()
        if st.button("🏠 MUR MONDIAL", key="nav_mur"): st.session_state.page = "Mur"
        if st.button("💬 MESSAGES PRIVÉS", key="nav_chat"): st.session_state.page = "Chat"
        st.divider()
        st.write("👥 **Amis**")
        mes_amis = data_u.get(me, {}).get("amis", {})
        for ami in mes_amis:
            if st.button(f"👤 {ami}", key=f"btn_chat_{ami}"):
                st.session_state.chat_target = ami
                st.session_state.page = "Chat"
        
        # Ajouter un ami
        new_f = st.text_input("Ajouter un pseudo", key="add_friend_input")
        if st.button("Ajouter", key="btn_add_friend"):
            if new_f in data_u and new_f != me:
                requests.patch(f"{URL_BASE}utilisateurs/{me}/amis.json", json={new_f: True})
                st.rerun()
        
        st.divider()
        if st.button("🚪 Déconnexion", key="btn_logout"):
            st.session_state.user = None
            st.rerun()

    # --- PAGES ---
    if st.session_state.page == "Mur":
        st.title("🏠 Mur Mondial")
        with st.expander("📝 Nouveau Post"):
            txt = st.text_area("Message", key="post_txt")
            img = st.text_input("Lien Image (URL)", key="post_img")
            if st.button("PUBLIER", key="btn_post"):
                requests.post(URL_MSG, json={"u": me, "c": my_club, "m": txt, "i": img, "d": "mondial", "t": time.time()})
                st.rerun()
        
        msgs = fetch_data(URL_MSG)
        if msgs:
            for k in reversed(list(msgs.keys())):
                v = msgs[k]
                if v.get("d") == "mondial":
                    st.markdown(f"<div class='msg-card'><b>{v['u']}</b> ({v.get('c','Fan')})<br>{v.get('m','')}</div>", unsafe_allow_html=True)
                    if v.get("i"): st.image(v["i"], use_container_width=True)

    elif st.session_state.page == "Chat":
        st.title("💬 Messagerie")
        target = st.session_state.chat_target
        if target:
            st.subheader(f"Discussion avec {target}")
            msgs = fetch_data(URL_MSG)
            if msgs:
                for k, v in msgs.items():
                    if (v.get("u") == me and v.get("d") == target) or (v.get("u") == target and v.get("d") == me):
                        align = "right" if v['u'] == me else "left"
                        color = "#FF8C00" if v['u'] == me else "#333"
                        st.markdown(f"<div style='text-align:{align};'><span style='background:{color}; padding:10px; border-radius:10px; display:inline-block; margin:5px;'>{v['m']}</span></div>", unsafe_allow_html=True)
            
            m_in = st.text_input("Écrire...", key="input_chat")
            if st.button("ENVOYER", key="btn_send"):
                requests.post(URL_MSG, json={"u": me, "m": m_in, "d": target, "t": time.time()})
                st.rerun()
        else:
            st.info("Choisis un ami dans la barre latérale pour discuter.")

# RECHARGEMENT TOUTES LES 10 SECONDES (PLUS LENT = PLUS STABLE)
time.sleep(10)
st.rerun()
