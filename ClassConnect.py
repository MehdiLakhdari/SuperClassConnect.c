import streamlit as st
import requests
import time
import random

# --- 1. CONFIGURATION ---
URL_BASE = "https://classconect-f1767-default-rtdb.europe-west1.firebasedatabase.app/"
URL_MSG = f"{URL_BASE}messages.json"
URL_USERS = f"{URL_BASE}utilisateurs.json"

st.set_page_config(page_title="ClassConnect Startup", page_icon="⚽", layout="wide")

# --- 2. ÉTAT DE LA SESSION ---
if 'user' not in st.session_state: st.session_state.user = None
if 'chat_with' not in st.session_state: st.session_state.chat_with = None
if 'temp_code' not in st.session_state: st.session_state.temp_code = None

# --- 3. DESIGN "RED DARK" ---
st.markdown("""
    <style>
    #MainMenu, footer, header {visibility: hidden;}
    .stApp { background: linear-gradient(180deg, #300000 0%, #000000 100%); color: #ffffff; }
    
    /* Logo en haut à gauche */
    .logo-sidebar {
        background: linear-gradient(135deg, #ff0000, #8b0000);
        width: 50px; height: 50px; border-radius: 12px;
        display: flex; align-items: center; justify-content: center;
        font-size: 30px; font-weight: bold; color: white;
        box-shadow: 0 0 15px rgba(255, 0, 0, 0.5);
        margin-bottom: 20px;
    }

    .pfp-nav { width: 50px; height: 50px; border-radius: 50%; object-fit: cover; border: 2px solid #ff4b4b; }
    .bubble { padding: 12px; border-radius: 15px; margin-bottom: 8px; max-width: 80%; }
    .me { background-color: #28a745; float: right; clear: both; }
    .them { background-color: #6f42c1; float: left; clear: both; }
    
    /* Bouton Appel Vidéo Stylé */
    .call-btn {
        background-color: #007bff !important;
        color: white !important;
        font-weight: bold !important;
        border-radius: 20px !important;
        border: 2px solid white !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 4. FONCTIONS ---
def charger(url):
    try:
        r = requests.get(url)
        return r.json() if r.status_code == 200 and r.json() else {}
    except: return {}

def get_pfp(pseudo, users_data):
    u_info = users_data.get(pseudo, {})
    url = u_info.get("pfp")
    return url if url and url.startswith("http") else "https://cdn-icons-png.flaticon.com/512/149/149071.png"

# --- 5. LOGIQUE DE NAVIGATION ---
users_data = charger(URL_USERS)

# ON VIDE TOUT AVANT DE DESSINER
placeholder = st.empty()

with placeholder.container():
    if st.session_state.user is None:
        # --- ECRAN AUTHENTIFICATION ---
        st.markdown("<center><div class='logo-sidebar' style='margin:auto;'>C</div><h1>CLASS CONNECT</h1></center>", unsafe_allow_html=True)
        t1, t2 = st.tabs(["Connexion", "Inscription"])
        with t1:
            u = st.text_input("Pseudo", key="l_u")
            p = st.text_input("Mdp", type="password", key="l_p")
            if st.button("SE CONNECTER"):
                if u in users_data and str(users_data[u].get("mdp")) == str(p):
                    st.session_state.user = u
                    st.rerun()
        with t2:
            nu = st.text_input("Pseudo Unique", key="r_u")
            nm = st.text_input("Email", key="r_m")
            np = st.text_input("Mdp", type="password", key="r_p")
            if st.button("VÉRIFIER"):
                if nu in users_data: st.error("Déjà pris")
                else:
                    st.session_state.temp_code = random.randint(1111, 9999)
                    st.info(f"CODE : {st.session_state.temp_code}")
            if st.session_state.temp_code:
                c = st.text_input("Entrez le code")
                if st.button("VALIDER"):
                    if str(c) == str(st.session_state.temp_code):
                        requests.patch(URL_USERS, json={nu: {"mdp": np, "mail": nm, "pfp": "", "amis": {}}})
                        st.success("Compte OK !")
                        st.session_state.temp_code = None

    else:
        # --- INTERFACE CONNECTÉE ---
        me = st.session_state.user
        pfp_me = get_pfp(me, users_data)
        
        # LOGO EN HAUT À GAUCHE
        st.sidebar.markdown("<div class='logo-sidebar'>C</div>", unsafe_allow_html=True)
        st.sidebar.image(pfp_me, width=60)
        st.sidebar.write(f"**{me}**")
        
        # Navigation
        choice = st.sidebar.radio("Navigation", ["🏠 Mur Mondial", "💬 Messages", "⚙️ Paramètres"], key="nav_main")

        # --- PAGE MUR ---
        if choice == "🏠 Mur Mondial":
            st.header("🏠 Mur Mondial")
            with st.expander("📝 Publier"):
                txt = st.text_area("Message")
                img = st.text_input("Lien Image")
                if st.button("Diffuser"):
                    requests.post(URL_MSG, json={"u": me, "m": txt, "i": img, "d": "mondial", "t": time.time()})
                    st.rerun()
            
            msgs = charger(URL_MSG)
            for k in reversed(list(msgs.keys())):
                v = msgs[k]
                if v.get("d") == "mondial":
                    st.markdown(f"<div style='background:rgba(255,255,255,0.05); padding:10px; border-radius:10px; margin-bottom:10px;'><b>{v['u']}</b>: {v.get('m','')}</div>", unsafe_allow_html=True)
                    if v.get("i"): st.image(v["i"])

        # --- PAGE MESSAGES ---
        elif choice == "💬 Messages":
            st.header("💬 Messages Privés")
            search = st.text_input("Rechercher un pseudo...")
            if st.button("Lancer le chat"):
                if search in users_data and search != me:
                    st.session_state.chat_with = search
                    requests.patch(f"{URL_BASE}utilisateurs/{me}/amis.json", json={search: True})
                    st.rerun()

            # Contacts récents
            amis = users_data.get(me, {}).get("amis", {})
            if amis:
                st.sidebar.write("---")
                for ami in amis.keys():
                    if st.sidebar.button(f"👤 {ami}", key=f"chat_{ami}"):
                        st.session_state.chat_with = ami
                        st.rerun()

            if st.session_state.chat_with:
                target = st.session_state.chat_with
                
                # LA ZONE D'APPEL VIDÉO (LOGO ET BOUTON)
                st.write("---")
                c1, c2 = st.columns([3, 1])
                c1.subheader(f"Conversation avec {target}")
                if c2.button("📞 APPEL VIDÉO", key="video_call_btn"):
                    room = f"ClassConnect-{min(me, target)}-{max(me, target)}"
                    st.markdown(f'<iframe src="https://meet.jit.si/{room}" allow="camera; microphone; fullscreen" style="height: 500px; width: 100%; border-radius:15px; border: 2px solid #ff0000;"></iframe>', unsafe_allow_html=True)

                # Messages
                msgs = charger(URL_MSG)
                for k in list(msgs.keys()):
                    v = msgs[k]
                    if (v.get("u") == me and v.get("d") == target) or (v.get("u") == target and v.get("d") == me):
                        cls = "me" if v['u'] == me else "them"
                        st.markdown(f"<div class='bubble {cls}'><b>{v['u']}:</b> {v['m']}</div>", unsafe_allow_html=True)
                
                m_in = st.text_input("Écrire...", key="msg_input")
                if st.button("ENVOYER 🚀"):
                    if m_in:
                        requests.post(URL_MSG, json={"u": me, "m": m_in, "d": target, "t": time.time()})
                        st.rerun()

        # --- PAGE PARAMÈTRES ---
        elif choice == "⚙️ Paramètres":
            st.header("⚙️ Paramètres")
            pfp_input = st.text_input("URL Photo de profil", value=pfp_me)
            if st.button("Sauvegarder"):
                requests.patch(f"{URL_BASE}utilisateurs/{me}.json", json={"pfp": pfp_input})
                st.success("OK !")
            if st.button("🚪 Déconnexion"):
                st.session_state.user = None
                st.rerun()

# Auto-refresh
time.sleep(10)
st.rerun()
