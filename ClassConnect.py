import streamlit as st
import requests
import time

# --- 1. CONFIGURATION ---
URL_BASE = "https://classconect-f1767-default-rtdb.europe-west1.firebasedatabase.app/"
URL_MSG = f"{URL_BASE}messages.json"
URL_USERS = f"{URL_BASE}utilisateurs.json"

st.set_page_config(page_title="Connect Class Algeria", page_icon="⚽", layout="wide")

# --- 2. SESSION STATE ---
if 'user' not in st.session_state: st.session_state.user = None
if 'page' not in st.session_state: st.session_state.page = "🏠 Mur"
if 'chat_target' not in st.session_state: st.session_state.chat_target = None

# --- 3. FONCTIONS ---
def charger(url):
    try:
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            return r.json() if r.json() else {}
    except: pass
    return {}

# --- 4. CHARGEMENT INITIAL ---
data_u = charger(URL_USERS)
all_msgs = charger(URL_MSG)

# --- 5. STYLE DYNAMIQUE (PSG, BARÇA, JUVE) ---
user_club = "PSG" # Par défaut
if st.session_state.user and st.session_state.user in data_u:
    user_club = data_u[st.session_state.user].get("club", "PSG")

styles = {
    "PSG": {"bg": "#001C3F", "accent": "#E30613", "txt": "white"},
    "Barça": {"bg": "#004D98", "accent": "#A50044", "txt": "#EDBB00"},
    "Juventus": {"bg": "#000000", "accent": "#FFFFFF", "txt": "#000000"}
}
s = styles.get(user_club, styles["PSG"])

st.markdown(f"""
    <style>
    .stApp {{ background-color: {s['bg']} !important; color: white !important; }}
    [data-testid="stSidebar"] {{ background-color: rgba(0,0,0,0.8) !important; border-right: 3px solid {s['accent']} !important; }}
    .stButton>button {{ 
        background-color: {s['accent']} !important; color: {s['txt']} !important; 
        border-radius: 8px; font-weight: bold; border: 1px solid white; width: 100%;
    }}
    .msg-card {{ background: rgba(255,255,255,0.1); padding: 12px; border-radius: 10px; border-left: 5px solid {s['accent']}; margin-bottom: 8px; }}
    </style>
    """, unsafe_allow_html=True)

# --- 6. INTERFACE ---

if st.session_state.user is None:
    st.markdown("<h1 style='text-align:center; color:white;'>CC - ALGERIA</h1>", unsafe_allow_html=True)
    t1, t2 = st.tabs(["CONNEXION", "INSCRIPTION"])
    
    with t1:
        u_in = st.text_input("Pseudo", key="login_u")
        p_in = st.text_input("Mot de passe", type="password", key="login_p")
        if st.button("SE CONNECTER"):
            # On recharge la data juste avant de vérifier
            data_check = charger(URL_USERS)
            if u_in in data_check and str(data_check[u_in].get("mdp")) == str(p_in):
                st.session_state.user = u_in
                st.rerun()
            else:
                st.error("❌ Identifiants incorrects") # LE MESSAGE EST ICI

    with t2:
        nu = st.text_input("Choisis un Pseudo", key="reg_u")
        np = st.text_input("Crée un Mdp", type="password", key="reg_p")
        nclub = st.selectbox("Ton Club", ["PSG", "Barça", "Juventus"])
        if st.button("CRÉER MON COMPTE"):
            if nu and np:
                requests.patch(URL_USERS, json={nu: {"mdp": np, "club": nclub, "pfp": ""}})
                st.success("Compte créé ! Connecte-toi maintenant.")
            else:
                st.warning("Remplis tous les champs !")

else:
    me = st.session_state.user
    
    # --- AUTO-DETECTION MESSAGES ---
    notifs = []
    if all_msgs:
        for m in all_msgs.values():
            if m.get("d") == me and m["u"] not in notifs:
                notifs.append(m["u"])

    # --- SIDEBAR ---
    with st.sidebar:
        st.markdown(f"<h2 style='color:{s['accent']}; text-align:center;'>{user_club}</h2>", unsafe_allow_html=True)
        st.write(f"Utilisateur : **{me}**")
        st.divider()
        if st.button("🏠 LE MUR"): st.session_state.page = "Mur"
        msg_label = f"💬 MESSAGES ({len(notifs)})" if notifs else "💬 MESSAGES"
        if st.button(msg_label): st.session_state.page = "Messages"
        st.divider()
        if st.button("🚪 DÉCONNEXION"):
            st.session_state.user = None
            st.rerun()

    # --- PAGES ---
    if st.session_state.page == "Mur":
        st.title("🏠 Mur Mondial")
        msg_txt = st.text_input("Message...")
        if st.button("POSTER"):
            if msg_txt:
                requests.post(URL_MSG, json={"u": me, "m": msg_txt, "d": "mondial", "t": time.time()})
                st.rerun()
        
        if all_msgs:
            for v in reversed(list(all_msgs.values())):
                if v.get("d") == "mondial":
                    st.markdown(f"<div class='msg-card'><b>{v['u']}</b> : {v['m']}</div>", unsafe_allow_html=True)

    elif st.session_state.page == "Messages":
        st.title("💬 Messagerie")
        
        if notifs:
            st.write("📩 Nouveaux messages de :")
            for sender in notifs:
                if st.button(f"Répondre à {sender}", key=f"notif_{sender}"):
                    st.session_state.chat_target = sender
        
        search = st.text_input("Chercher un pseudo pour discuter...")
        if st.button("LANCER LE CHAT"):
            st.session_state.chat_target = search

        if st.session_state.chat_target:
            dest = st.session_state.chat_target
            st.divider()
            st.subheader(f"Chat avec {dest}")
            if all_msgs:
                for v in all_msgs.values():
                    if (v.get("u") == me and v.get("d") == dest) or (v.get("u") == dest and v.get("d") == me):
                        side = "right" if v['u'] == me else "left"
                        bg_c = s['accent'] if v['u'] == me else "#333"
                        st.markdown(f"<div style='text-align:{side};'><span style='background:{bg_c}; padding:10px; border-radius:10px; display:inline-block; margin:2px;'>{v['m']}</span></div>", unsafe_allow_html=True)
            
            m_in = st.text_input("Message...", key="m_in")
            if st.button("ENVOYER 🚀"):
                if m_in:
                    requests.post(URL_MSG, json={"u": me, "m": m_in, "d": dest, "t": time.time()})
                    st.rerun()

# Rafraîchissement auto
time.sleep(4)
st.rerun()
