import streamlit as st
import requests
import time

# --- 1. CONFIGURATION ---
URL_BASE = "https://classconect-f1767-default-rtdb.europe-west1.firebasedatabase.app/"
URL_MSG = f"{URL_BASE}messages.json"
URL_USERS = f"{URL_BASE}utilisateurs.json"

st.set_page_config(page_title="ClassConnect Total", page_icon="⚽", layout="centered")

# --- 2. ÉTAT DE LA SESSION ---
if 'theme' not in st.session_state: st.session_state.theme = "sombre"
if 'user' not in st.session_state: st.session_state.user = None
if 'chat_with' not in st.session_state: st.session_state.chat_with = None

# --- 3. DESIGN DYNAMIQUE ---
if st.session_state.theme == "sombre":
    bg, txt, btn, card = "#000000", "#ffffff", "#bc2a8d", "#121212"
else:
    bg, txt, btn, card = "#ffffff", "#000000", "#e1306c", "#f0f2f5"

st.markdown(f"""
    <style>
    .stApp {{ background-color: {bg}; color: {txt}; }}
    .message-card {{ background-color: {card}; padding: 12px; border-radius: 10px; margin-bottom: 8px; border: 0.5px solid #333; }}
    .pfp-large {{ width: 100px; height: 100px; border-radius: 50%; object-fit: cover; border: 3px solid {btn}; display: block; margin: 0 auto; }}
    .pfp-mini {{ width: 30px; height: 30px; border-radius: 50%; object-fit: cover; margin-right: 8px; vertical-align: middle; }}
    
    /* Bouton Standard */
    .stButton>button {{ border-radius: 8px; font-weight: bold; background-color: {btn}; color: white; border: none; width: 100%; }}
    
    /* STYLE UNIQUE : BOUTON ENVOYER (BLEU) */
    div.stButton > button:first-child[kind="secondary"] {{
        background-color: #007bff !important;
        color: white !important;
        border: none !important;
    }}
    
    .sidebar-logo {{ font-size: 24px; font-weight: bold; color: {btn}; text-align: center; margin-bottom: 20px; }}
    </style>
    """, unsafe_allow_html=True)

# --- 4. FONCTIONS Outils ---
def charger(url):
    try:
        r = requests.get(url)
        return r.json() if r.status_code == 200 and r.json() else {}
    except: return {}

def get_pfp(pseudo, users_data):
    u_info = users_data.get(pseudo, {})
    return u_info.get("pfp") if u_info.get("pfp") else "https://cdn-icons-png.flaticon.com/512/149/149071.png"

# --- 5. PAGES INDÉPENDANTES (Structure Logique) ---

def page_connexion_inscription():
    st.markdown("<div class='sidebar-logo'>⚽ ClassConnect</div>", unsafe_allow_html=True)
    t1, t2 = st.tabs(["Connexion", "Inscription"])
    with t1:
        u = st.text_input("Pseudo", key="l_u")
        p = st.text_input("Mot de passe", type="password", key="l_p")
        if st.button("Entrer", type="primary", key="btn_login"):
            users_data = charger(URL_USERS)
            if u in users_data and str(users_data[u].get("mdp")) == str(p):
                st.session_state.user = u
                st.rerun()
            else:
                st.error("Identifiants incorrects.")
    with t2:
        nu = st.text_input("Pseudo", key="r_u")
        np = st.text_input("Mot de passe", type="password", key="r_p")
        if st.button("S'inscrire", type="primary", key="btn_reg"):
            if nu and np:
                requests.patch(URL_USERS, json={nu: {"mdp": np, "pfp": "", "amis": {}}})
                st.success("Compte créé ! Connecte-toi.")
            else:
                st.warning("Remplis tous les champs.")

def page_mur(me, users_data):
    st.header("🏠 Mur Mondial")
    with st.expander("📝 Publier"):
        t = st.text_area("Texte")
        i = st.text_input("Lien Image (URL)")
        if st.button("Partager", type="primary"):
            if t or i:
                requests.post(URL_MSG, json={"u": me, "m": t, "i": i, "d": "mondial", "t": time.time()})
                st.rerun()
    
    msgs = charger(URL_MSG)
    if msgs:
        for k in reversed(list(msgs.keys())):
            v = msgs[k]
            if v.get("d") == "mondial":
                p = get_pfp(v['u'], users_data)
                # MUR = GRIS
                st.markdown(f"<div style='background-color:#333; color:white; padding:10px; border-radius:10px; margin-bottom:10px;'><img src='{p}' class='pfp-mini'><b>{v['u']}</b>: {v.get('m','')}</div>", unsafe_allow_html=True)
                if v.get("i"): st.image(v["i"])
                if v.get("u") == me:
                    if st.button("🗑️", key=f"del_{k}"):
                        requests.delete(f"{URL_BASE}messages/{k}.json")
                        st.rerun()

def page_messages(me, users_data):
    st.markdown(f"<img src='{get_pfp(me, users_data)}' class='pfp-large'>", unsafe_allow_html=True)
    st.markdown(f"<h2 style='text-align: center;'>{me}</h2>", unsafe_allow_html=True)
    
    st.divider()
    col1, col2 = st.columns([3, 1])
    search = col1.text_input("🔍 Chercher un ami...", placeholder="Pseudo")
    if col2.button("Ajouter", type="primary"):
        if search and search != me:
            st.session_state.chat_with = search
            requests.patch(f"{URL_BASE}utilisateurs/{me}/amis.json", json={search: True})
            st.rerun()

    amis = users_data.get(me, {}).get("amis", {})
    if amis:
        st.write("### Discussions")
        for a in amis.keys():
            if st.sidebar.button(f"👤 {a}", key=f"side_{a}"):
                st.session_state.chat_with = a
                st.rerun()

    if st.session_state.chat_with:
        target = st.session_state.chat_with
        st.subheader(f"💬 Chat : {target}")
        
        m_in = st.text_input("Message...", key="m_in")
        if st.button("Envoyer 🚀", key="btn_send", type="secondary"):
            if m_in:
                requests.post(URL_MSG, json={"u": me, "m": m_in, "d": target, "t": time.time()})
                st.rerun()
        
        msgs = charger(URL_MSG)
        if msgs:
            for k in list(msgs.keys()):
                v = msgs[k]
                if (v.get("u") == me and v.get("d") == target) or (v.get("u") == target and v.get("d") == me):
                    if v['u'] == me:
                        c, label = "#28a745", "Moi"  # VERT POUR TES MESSAGES
                    else:
                        c, label = "#6f42c1", v['u'] # VIOLET POUR L'AMI
                        
                    st.markdown(f"""
                        <div style='margin-bottom:8px; text-align:left;'>
                            <span style='background-color:{c}; color:white; padding:10px 15px; border-radius:15px; display:inline-block;'>
                                <b>{label}:</b> {v['m']}
                            </span>
                        </div>
                    """, unsafe_allow_html=True)

def page_settings(me, users_data):
    st.header("⚙️ Paramètres")
    new_pfp = st.text_input("Lien photo de profil (URL)", value=get_pfp(me, users_data))
    if st.button("Valider", type="primary"):
        requests.patch(f"{URL_BASE}utilisateurs/{me}.json", json={"pfp": new_pfp})
        st.rerun()
    st.divider()
    if st.button("🌙 Mode Sombre"): st.session_state.theme = "sombre"; st.rerun()
    if st.button("☀️ Mode Clair"): st.session_state.theme = "clair"; st.rerun()
    if st.button("🚪 Déconnexion"): st.session_state.user = None; st.rerun()

# --- 6. ROUTAGE (Logique d'affichage des pages) ---
if st.session_state.user is None:
    page_connexion_inscription()
else:
    users_data = charger(URL_USERS)
    st.sidebar.markdown("<div class='sidebar-logo'>⚽ ClassConnect</div>", unsafe_allow_html=True)
    page = st.sidebar.selectbox("Aller vers", ["🏠 Mur Mondial", "💬 Direct Messages", "⚙️ Paramètres"])
    
    # Affichage de la page sélectionnée UNIQUEMENT
    if page == "🏠 Mur Mondial": page_mur(st.session_state.user, users_data)
    elif page == "💬 Direct Messages": page_messages(st.session_state.user, users_data)
    else: page_settings(st.session_state.user, users_data)

time.sleep(10)
st.rerun()
