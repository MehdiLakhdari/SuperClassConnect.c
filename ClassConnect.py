import streamlit as st
import requests
import time
import random

# --- 1. CONFIGURATION ---
URL_BASE = "https://classconect-f1767-default-rtdb.europe-west1.firebasedatabase.app/"
URL_MSG = f"{URL_BASE}messages.json"
URL_USERS = f"{URL_BASE}utilisateurs.json"

st.set_page_config(page_title="Connect Class Algeria", page_icon="🇩🇿", layout="wide")

# --- 2. INITIALISATION DU SESSION STATE ---
if 'user' not in st.session_state: st.session_state.user = None
if 'chat_with' not in st.session_state: st.session_state.chat_with = None
if 'temp_code' not in st.session_state: st.session_state.temp_code = None
if 'menu_option' not in st.session_state: st.session_state.menu_option = "🏠 Mur Mondial"

# --- 3. DESIGN ---
st.markdown("""
    <style>
    #MainMenu, footer, header {visibility: hidden;}
    .stApp { background: linear-gradient(180deg, #300000 0%, #000000 100%); color: #ffffff; }
    .logo-sidebar {
        background: linear-gradient(135deg, #ff0000, #8b0000);
        width: 50px; height: 50px; border-radius: 12px;
        display: flex; align-items: center; justify-content: center;
        font-size: 25px; font-weight: bold; color: white; margin-bottom: 20px;
    }
    .bubble { padding: 12px; border-radius: 15px; margin-bottom: 8px; max-width: 80%; display: inline-block; }
    .me { background-color: #28a745; float: right; clear: both; }
    .them { background-color: #6f42c1; float: left; clear: both; }
    .stButton>button { background: #ff0000; color: white; border-radius: 10px; width: 100%; border:none; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. FONCTIONS ---
def charger(url):
    try:
        r = requests.get(url)
        return r.json() if r.status_code == 200 and r.json() else {}
    except: return {}

def get_pfp(pseudo, u_data):
    url = u_data.get(pseudo, {}).get("pfp")
    return url if url and url.startswith("http") else "https://cdn-icons-png.flaticon.com/512/149/149071.png"

# --- 5. LOGIQUE ---
u_data = charger(URL_USERS)

if st.session_state.user is None:
    # --- PAGE CONNEXION ---
    st.markdown("<center><div class='logo-sidebar' style='margin:auto;'>C</div><h1>CONNECT CLASS ALGERIA</h1></center>", unsafe_allow_html=True)
    t1, t2 = st.tabs(["Connexion", "Inscription"])
    with t1:
        u = st.text_input("Pseudo", key="l_u")
        p = st.text_input("Mdp", type="password", key="l_p")
        if st.button("SE CONNECTER"):
            if u in u_data and str(u_data[u].get("mdp")) == str(p):
                st.session_state.user = u
                st.rerun()
    with t2:
        nu = st.text_input("Pseudo", key="r_u")
        np = st.text_input("Mdp", type="password", key="r_p")
        if st.button("CREER COMPTE"):
            requests.patch(URL_USERS, json={nu: {"mdp": np, "pfp": "", "amis": {}}})
            st.success("Compte OK ! Connecte-toi.")

else:
    # --- INTERFACE CONNECTÉE ---
    me = st.session_state.user
    pfp_me = get_pfp(me, u_data)
    
    # Barre Latérale (Sidebar)
    st.sidebar.markdown("<div class='logo-sidebar'>C</div>", unsafe_allow_html=True)
    st.sidebar.image(pfp_me, width=80)
    st.sidebar.write(f"💼 **{me}**")
    
    # Navigation forcée par session_state
    st.session_state.menu_option = st.sidebar.radio("Navigation", ["🏠 Mur Mondial", "💬 Direct Messages", "⚙️ Paramètres"], index=["🏠 Mur Mondial", "💬 Direct Messages", "⚙️ Paramètres"].index(st.session_state.menu_option))

    # --- SECTION : MUR ---
    if st.session_state.menu_option == "🏠 Mur Mondial":
        st.header("🏠 Mur Mondial")
        with st.expander("📝 Publier"):
            msg = st.text_area("Message")
            img = st.text_input("URL Image")
            if st.button("Diffuser"):
                requests.post(URL_MSG, json={"u": me, "m": msg, "i": img, "d": "mondial", "t": time.time()})
                st.rerun()
        
        msgs = charger(URL_MSG)
        for k in reversed(list(msgs.keys())):
            v = msgs[k]
            if v.get("d") == "mondial":
                st.markdown(f"**{v['u']}** : {v.get('m','')}")
                if v.get('i'): st.image(v['i'], use_container_width=True)
                st.divider()

    # --- SECTION : MESSAGES ---
    elif st.session_state.menu_option == "💬 Direct Messages":
        st.header("💬 Messages Privés")
        target = st.text_input("Rechercher un pseudo")
        if st.button("Lancer"):
            if target in u_data:
                st.session_state.chat_with = target
                requests.patch(f"{URL_BASE}utilisateurs/{me}/amis.json", json={target: True})
                st.rerun()

        if st.session_state.chat_with:
            t = st.session_state.chat_with
            st.subheader(f"Chat avec {t}")
            
            # APPEL VIDÉO
            if st.button("📞 APPEL VIDÉO"):
                room = f"CC-{min(me, t)}-{max(me, t)}"
                st.markdown(f'<iframe src="https://meet.jit.si/{room}" allow="camera; microphone; fullscreen" style="height:400px; width:100%; border-radius:10px;"></iframe>', unsafe_allow_html=True)

            m_msgs = charger(URL_MSG)
            for k, v in m_msgs.items():
                if (v.get("u")==me and v.get("d")==t) or (v.get("u")==t and v.get("d")==me):
                    side = "me" if v['u'] == me else "them"
                    st.markdown(f"<div class='bubble {side}'><b>{v['u']}:</b> {v['m']}</div>", unsafe_allow_html=True)
            
            m_in = st.text_input("Message...", key="m_in")
            if st.button("Envoyer"):
                requests.post(URL_MSG, json={"u": me, "m": m_in, "d": t, "t": time.time()})
                st.rerun()

    # --- SECTION : PARAMÈTRES ---
    elif st.session_state.menu_option == "⚙️ Paramètres":
        st.header("⚙️ Paramètres")
        new_pfp = st.text_input("Lien Photo", value=pfp_me)
        if st.button("Sauvegarder"):
            requests.patch(f"{URL_BASE}utilisateurs/{me}.json", json={"pfp": new_pfp})
            st.rerun()
        if st.button("Déconnexion"):
            st.session_state.user = None
            st.rerun()

time.sleep(10)
st.rerun()
