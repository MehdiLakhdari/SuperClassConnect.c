import streamlit as st
import requests
import time

# --- 1. CONFIGURATION ---
URL_BASE = "https://classconect-f1767-default-rtdb.europe-west1.firebasedatabase.app/"
URL_MSG = f"{URL_BASE}messages.json"
URL_USERS = f"{URL_BASE}utilisateurs.json"

st.set_page_config(page_title="Connect Class Algeria", page_icon="⚽", layout="wide")

# --- 2. ÉTAT DE LA SESSION ---
if 'user' not in st.session_state: st.session_state.user = None
if 'page' not in st.session_state: st.session_state.page = "🏠 Mur"
if 'chat_target' not in st.session_state: st.session_state.chat_target = None

# --- 3. FONCTIONS ---
def charger(url):
    try:
        r = requests.get(url, timeout=5)
        return r.json() if r.status_code == 200 and r.json() else {}
    except: return {}

# --- 4. RÉCUPÉRATION DATA ---
data_u = charger(URL_USERS)
all_msgs = charger(URL_MSG)

# --- 5. SYSTÈME DE COULEURS ÉDITION CLUBS ---
user_info = data_u.get(st.session_state.user, {})
user_club = user_info.get("club", "PSG")

# Dictionnaire de styles précis
styles = {
    "PSG": {"bg": "#001C3F", "accent": "#E30613", "txt": "#FFFFFF", "card": "rgba(255,255,255,0.1)"},
    "Barça": {"bg": "#004D98", "accent": "#A50044", "txt": "#EDBB00", "card": "rgba(165,0,68,0.2)"},
    "Juventus": {"bg": "#000000", "accent": "#FFFFFF", "txt": "#000000", "card": "rgba(255,255,255,0.9)"}
}
s = styles.get(user_club)

# Injection CSS Forcée
st.markdown(f"""
    <style>
    .stApp {{ background-color: {s['bg']} !important; color: white !important; }}
    [data-testid="stSidebar"] {{ background-color: rgba(0,0,0,0.7) !important; border-right: 4px solid {s['accent']} !important; }}
    .stButton>button {{ 
        background-color: {s['accent']} !important; 
        color: {s['txt']} !important; 
        border: 2px solid white !important;
        font-weight: bold !important;
        border-radius: 10px !important;
    }}
    .msg-card {{ 
        background: {s['card']}; 
        padding: 15px; border-radius: 12px; 
        border-left: 6px solid {s['accent']}; 
        margin-bottom: 10px;
        color: {"black" if user_club=="Juventus" else "white"};
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 6. LOGIQUE ---

if st.session_state.user is None:
    st.markdown("<h1 style='text-align:center;'>CC - ALGERIA</h1>", unsafe_allow_html=True)
    t1, t2 = st.tabs(["CONNEXION", "REJOINDRE LE CLUB"])
    with t1:
        u = st.text_input("Pseudo", key="l_u")
        p = st.text_input("Mdp", type="password", key="l_p")
        if st.button("S'IDENTIFIER"):
            if u in data_u and str(data_u[u].get("mdp")) == str(p):
                st.session_state.user = u
                st.rerun()
    with t2:
        nu = st.text_input("Nouveau Pseudo", key="n_u")
        np = st.text_input("Mot de passe", type="password", key="n_p")
        nclub = st.selectbox("Ton Club de Coeur", ["PSG", "Barça", "Juventus"])
        if st.button("CRÉER MON COMPTE"):
            requests.patch(URL_USERS, json={nu: {"mdp": np, "club": nclub, "pfp": ""}})
            st.success("Compte validé ! Connecte-toi.")

else:
    me = st.session_state.user
    
    # Détection automatique de messages reçus (NOTIFS)
    contacts_actifs = []
    if all_msgs:
        for m in all_msgs.values():
            if m.get("d") == me:
                if m["u"] not in contacts_actifs: contacts_actifs.append(m["u"])

    # --- SIDEBAR ---
    with st.sidebar:
        st.markdown(f"<h1 style='color:{s['accent']};'>CC</h1>", unsafe_allow_html=True)
        st.write(f"Utilisateur : **{me}**")
        st.write(f"Club : **{user_club}**")
        st.divider()
        if st.button("🏠 LE MUR"): st.session_state.page = "Mur"
        label = f"💬 MESSAGES ({len(contacts_actifs)})" if contacts_actifs else "💬 MESSAGES"
        if st.button(label): st.session_state.page = "Messages"
        if st.button("⚙️ PROFIL"): st.session_state.page = "Settings"
        st.divider()
        if st.button("🚪 QUITTER"):
            st.session_state.user = None
            st.rerun()

    # --- PAGES ---
    if st.session_state.page == "Mur":
        st.title("🏠 Mur Mondial")
        txt = st.text_input("Écris quelque chose sur le mur...")
        if st.button("POSTER"):
            requests.post(URL_MSG, json={"u": me, "m": txt, "d": "mondial", "t": time.time()})
            st.rerun()
        
        if all_msgs:
            for v in reversed(list(all_msgs.values())):
                if v.get("d") == "mondial":
                    st.markdown(f"<div class='msg-card'><b>{v['u']}</b> : {v['m']}</div>", unsafe_allow_html=True)

    elif st.session_state.page == "Messages":
        st.title("💬 Messagerie")
        
        # Affichage des discussions en cours
        if contacts_actifs:
            st.write("📩 Tu as reçu des messages de :")
            for c in contacts_actifs:
                if st.button(f"Répondre à {c}"):
                    st.session_state.chat_target = c
        
        target = st.text_input("Chercher un pseudo pour discuter...")
        if st.button("LANCER LE CHAT"):
            if target in data_u: st.session_state.chat_target = target

        if st.session_state.chat_target:
            dest = st.session_state.chat_target
            st.divider()
            st.subheader(f"Chat avec {dest}")
            if all_msgs:
                for v in all_msgs.values():
                    if (v.get("u") == me and v.get("d") == dest) or (v.get("u") == dest and v.get("d") == me):
                        color = s['accent'] if v['u'] == me else "#444"
                        align = "right" if v['u'] == me else "left"
                        st.markdown(f"<div style='text-align:{align};'><span style='background:{color}; padding:10px; border-radius:10px; display:inline-block; margin:2px;'>{v['m']}</span></div>", unsafe_allow_html=True)
            
            m_in = st.text_input("Message...", key="m_in")
            if st.button("ENVOYER 🚀"):
                requests.post(URL_MSG, json={"u": me, "m": m_in, "d": dest, "t": time.time()})
                st.rerun()

    elif st.session_state.page == "Settings":
        st.title("⚙️ Paramètres")
        st.write("Plus d'options bientôt !")

# Refresh auto rapide pour le lancement
time.sleep(3)
st.rerun()
