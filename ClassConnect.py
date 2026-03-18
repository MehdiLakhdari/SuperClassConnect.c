import streamlit as st
import requests
import time

# --- 1. CONFIGURATION ---
URL_BASE = "https://classconect-f1767-default-rtdb.europe-west1.firebasedatabase.app/"
URL_MSG = f"{URL_BASE}messages.json"
URL_USERS = f"{URL_BASE}utilisateurs.json"

st.set_page_config(page_title="Connect Class Algeria", page_icon="⚽", layout="wide")

# --- 2. INITIALISATION ---
if 'user' not in st.session_state: st.session_state.user = None
if 'page' not in st.session_state: st.session_state.page = "🏠 Mur"
if 'chat_target' not in st.session_state: st.session_state.chat_target = None

# --- 3. CHARGEMENT DATA ---
def charger(url):
    try:
        r = requests.get(url, timeout=5)
        return r.json() if r.status_code == 200 and r.json() else {}
    except: return {}

data_u = charger(URL_USERS)
all_msgs = charger(URL_MSG)

# --- 4. STYLE PAR CLUB ---
user_club = "PSG"
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
    [data-testid="stSidebar"] {{ 
        background-color: rgba(0,0,0,0.9) !important; 
        border-right: 3px solid {s['accent']} !important;
        min-width: 250px !important;
    }}
    .stButton>button {{ 
        background-color: {s['accent']} !important; color: {s['txt']} !important; 
        border-radius: 8px; font-weight: bold; border: 1px solid white; width: 100%;
    }}
    .msg-card {{ background: rgba(255,255,255,0.1); padding: 12px; border-radius: 10px; border-left: 5px solid {s['accent']}; margin-bottom: 8px; }}
    </style>
    """, unsafe_allow_html=True)

# --- 5. BARRE LATÉRALE (SORTIE DE TOUTE CONDITION) ---
with st.sidebar:
    st.markdown(f"<h1 style='color:{s['accent']}; text-align:center;'>CC</h1>", unsafe_allow_html=True)
    if st.session_state.user:
        st.write(f"⚽ Joueur : **{st.session_state.user}**")
        st.write(f"🏟️ Club : **{user_club}**")
        st.divider()
        if st.button("🏠 LE MUR"): st.session_state.page = "Mur"
        
        # Décompte Notifs
        notifs = []
        if all_msgs:
            for m in all_msgs.values():
                if m.get("d") == st.session_state.user and m["u"] not in notifs:
                    notifs.append(m["u"])
        
        label_msg = f"💬 MESSAGES ({len(notifs)})" if notifs else "💬 MESSAGES"
        if st.button(label_msg): st.session_state.page = "Messages"
        
        st.divider()
        if st.button("🚪 DÉCONNEXION"):
            st.session_state.user = None
            st.rerun()
    else:
        st.info("Connectez-vous pour voir le menu")

# --- 6. CONTENU PRINCIPAL ---
if st.session_state.user is None:
    st.markdown("<h1 style='text-align:center;'>CONNECT CLASS ALGERIA</h1>", unsafe_allow_html=True)
    t1, t2 = st.tabs(["CONNEXION", "REJOINDRE LE CLUB"])
    
    with t1:
        u_in = st.text_input("Pseudo", key="login_u")
        p_in = st.text_input("Mdp", type="password", key="login_p")
        if st.button("S'IDENTIFIER"):
            if u_in in data_u and str(data_u[u_in].get("mdp")) == str(p_in):
                st.session_state.user = u_in
                st.rerun()
            else:
                st.error("❌ Identifiants incorrects")

    with t2:
        nu = st.text_input("Nouveau Pseudo", key="reg_u")
        np = st.text_input("Nouveau Mdp", type="password", key="reg_p")
        nclub = st.selectbox("Ton Club", ["PSG", "Barça", "Juventus"])
        if st.button("CRÉER MON COMPTE"):
            if nu and np:
                requests.patch(URL_USERS, json={nu: {"mdp": np, "club": nclub, "pfp": ""}})
                st.success("Compte validé ! Connecte-toi.")

else:
    # PAGES UNE FOIS CONNECTÉ
    if st.session_state.page == "Mur":
        st.title(f"🏠 Mur {user_club}")
        msg_txt = st.text_input("Quoi de neuf ?")
        if st.button("POSTER"):
            if msg_txt:
                requests.post(URL_MSG, json={"u": st.session_state.user, "m": msg_txt, "d": "mondial", "t": time.time()})
                st.rerun()
        
        if all_msgs:
            for v in reversed(list(all_msgs.values())):
                if v.get("d") == "mondial":
                    st.markdown(f"<div class='msg-card'><b>{v['u']}</b> : {v['m']}</div>", unsafe_allow_html=True)

    elif st.session_state.page == "Messages":
        st.title("💬 Messagerie Directe")
        
        # Liste notifs
        if 'notifs' in locals() and notifs:
            st.write("📩 Nouveaux messages de :")
            for sender in notifs:
                if st.button(f"Répondre à {sender}", key=f"notif_{sender}"):
                    st.session_state.chat_target = sender
        
        target = st.text_input("Pseudo de l'ami...")
        if st.button("LANCER LE CHAT"):
            if target in data_u: st.session_state.chat_target = target

        if st.session_state.chat_target:
            dest = st.session_state.chat_target
            st.subheader(f"Discussion avec {dest}")
            if all_msgs:
                for v in all_msgs.values():
                    if (v.get("u") == st.session_state.user and v.get("d") == dest) or (v.get("u") == dest and v.get("d") == st.session_state.user):
                        side = "right" if v['u'] == st.session_state.user else "left"
                        bg_c = s['accent'] if v['u'] == st.session_state.user else "#333"
                        st.markdown(f"<div style='text-align:{side};'><span style='background:{bg_c}; padding:10px; border-radius:10px; display:inline-block; margin:2px;'>{v['m']}</span></div>", unsafe_allow_html=True)
            
            m_in = st.text_input("Message...", key="m_in")
            if st.button("ENVOYER"):
                if m_in:
                    requests.post(URL_MSG, json={"u": st.session_state.user, "m": m_in, "d": dest, "t": time.time()})
                    st.rerun()

# Auto-refresh
time.sleep(4)
st.rerun()
