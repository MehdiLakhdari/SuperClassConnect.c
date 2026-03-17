import streamlit as st
import requests
import time

# --- 1. CONFIGURATION ---
URL_BASE = "https://classconect-f1767-default-rtdb.europe-west1.firebasedatabase.app/"
URL_MSG = f"{URL_BASE}messages.json"
URL_USERS = f"{URL_BASE}utilisateurs.json"

st.set_page_config(page_title="Connect Class Algeria", page_icon="🇩🇿", layout="wide")

# --- 2. ÉTAT DE LA SESSION ---
if 'user' not in st.session_state: st.session_state.user = None
if 'page' not in st.session_state: st.session_state.page = "🏠 Mur Mondial"
if 'chat_target' not in st.session_state: st.session_state.chat_target = None

# --- 3. STYLE ROUGE STARTUP ---
st.markdown("""
    <style>
    [data-testid="stSidebar"] { background-color: #300000; border-right: 2px solid #ff0000; }
    .stApp { background-color: #1a0000; color: white; }
    .stButton>button { background-color: #ff0000; color: white; border-radius: 8px; width: 100%; border: none; font-weight: bold; height: 45px; margin-bottom: 10px; }
    .logo-text { font-size: 24px; font-weight: bold; color: white; text-align: center; padding: 20px; border-bottom: 1px solid #444; }
    .msg-card { background: rgba(255,255,255,0.05); padding: 15px; border-radius: 10px; border-left: 4px solid #ff0000; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. CHARGEMENT DONNÉES ---
def charger(url):
    try:
        r = requests.get(url)
        return r.json() if r.status_code == 200 and r.json() else {}
    except: return {}

data_u = charger(URL_USERS)

# --- 5. INTERFACE ---

# SI NON CONNECTÉ
if st.session_state.user is None:
    st.markdown("<h1 style='text-align:center;'>CONNECT CLASS ALGERIA</h1>", unsafe_allow_html=True)
    t1, t2 = st.tabs(["Connexion", "Inscription"])
    with t1:
        u = st.text_input("Pseudo", key="login_u")
        p = st.text_input("Mot de passe", type="password", key="login_p")
        if st.button("SE CONNECTER"):
            if u in data_u and str(data_u[u].get("mdp")) == str(p):
                st.session_state.user = u
                st.rerun()
            else: st.error("Identifiants incorrects")
    with t2:
        nu = st.text_input("Choisis un Pseudo", key="new_u")
        np = st.text_input("Choisis un MDP", type="password", key="new_p")
        if st.button("CRÉER COMPTE"):
            requests.patch(URL_USERS, json={nu: {"mdp": np, "pfp": ""}})
            st.success("Compte créé ! Connecte-toi.")

# SI CONNECTÉ
else:
    me = st.session_state.user
    
    # BARRE LATÉRALE (SIDEBAR) - TOUJOURS LÀ
    with st.sidebar:
        st.markdown("<div class='logo-text'>CONNECT CLASS</div>", unsafe_allow_html=True)
        st.write(f"Bonjour, **{me}** 💼")
        st.divider()
        
        # BOUTONS DE NAVIGATION
        if st.button("🏠 Mur Mondial"): st.session_state.page = "🏠 Mur Mondial"
        if st.button("💬 Messages Privés"): st.session_state.page = "💬 Messages Privés"
        if st.button("⚙️ Paramètres"): st.session_state.page = "⚙️ Paramètres"
        
        st.divider()
        if st.button("🚪 Déconnexion"):
            st.session_state.user = None
            st.rerun()

    # --- CONTENU DES PAGES ---
    
    if st.session_state.page == "🏠 Mur Mondial":
        st.title("🏠 Mur Mondial")
        with st.expander("📝 Publier un message"):
            m_txt = st.text_area("Ton message...")
            m_img = st.text_input("URL Image (optionnel)")
            if st.button("POSTER MAINTENANT"):
                requests.post(URL_MSG, json={"u": me, "m": m_txt, "i": m_img, "d": "mondial", "t": time.time()})
                st.rerun()
        
        msgs = charger(URL_MSG)
        if msgs:
            for k in reversed(list(msgs.keys())):
                v = msgs[k]
                if v.get("d") == "mondial":
                    st.markdown(f"<div class='msg-card'><b>{v['u']}</b> : {v.get('m','')}</div>", unsafe_allow_html=True)
                    if v.get("i"): st.image(v["i"])

    elif st.session_state.page == "💬 Messages Privés":
        st.title("💬 Messages Privés")
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.subheader("Contacts")
            target = st.text_input("Pseudo de l'ami")
            if st.button("Ouvrir Chat"):
                if target in data_u: st.session_state.chat_target = target
                else: st.error("Inconnu")

        with col2:
            if st.session_state.chat_target:
                dest = st.session_state.chat_target
                st.subheader(f"Chat avec {dest}")
                
                # Flux messages
                msgs = charger(URL_MSG)
                if msgs:
                    for k, v in msgs.items():
                        if (v.get("u") == me and v.get("d") == dest) or (v.get("u") == dest and v.get("d") == me):
                            align = "right" if v['u'] == me else "left"
                            color = "#ff4b4b" if v['u'] == me else "#444"
                            st.markdown(f"<div style='text-align:{align};'><span style='background:{color}; padding:8px 12px; border-radius:10px; display:inline-block; margin:2px;'>{v['m']}</span></div>", unsafe_allow_html=True)
                
                # Envoi
                msg_in = st.text_input("Message...", key="chat_in")
                if st.button("ENVOYER 🚀"):
                    if msg_in:
                        requests.post(URL_MSG, json={"u": me, "m": msg_in, "d": dest, "t": time.time()})
                        st.rerun()

    elif st.session_state.page == "⚙️ Paramètres":
        st.title("⚙️ Paramètres")
        st.write("Gestion de ton compte Startup.")
        pfp_url = st.text_input("URL de ta photo")
        if st.button("Mettre à jour"):
            requests.patch(f"{URL_BASE}utilisateurs/{me}.json", json={"pfp": pfp_url})
            st.success("Profil mis à jour !")

# Refresh auto
time.sleep(10)
st.rerun()
