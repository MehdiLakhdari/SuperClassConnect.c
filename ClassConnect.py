import streamlit as st
import requests
import time

# --- 1. CONFIGURATION ---
URL_BASE = "https://classconect-f1767-default-rtdb.europe-west1.firebasedatabase.app/"
URL_MSG = f"{URL_BASE}messages.json"
URL_USERS = f"{URL_BASE}utilisateurs.json"

st.set_page_config(page_title="ClassConnect Master", page_icon="💎", layout="centered")

# --- 2. ÉTAT DE LA SESSION ---
if 'theme' not in st.session_state: st.session_state.theme = "sombre"
if 'user' not in st.session_state: st.session_state.user = None
if 'chat_with' not in st.session_state: st.session_state.chat_with = None

# --- 3. DESIGN DYNAMIQUE & BOUTON BLEU ---
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
    
    /* Bouton Standard (Violet/Rose) */
    .stButton>button {{ border-radius: 8px; font-weight: bold; background-color: {btn}; color: white; border: none; width: 100%; }}
    
    /* STYLE SPÉCIAL POUR LE BOUTON ENVOYER (BLEU) */
    div.stButton > button:first-child[kind="secondary"] {{
        background-color: #007bff !important;
        color: white !important;
        border: none !important;
    }}
    
    /* Style du titre Sidebar */
    .sidebar-logo {{ font-size: 24px; font-weight: bold; color: {btn}; text-align: center; margin-bottom: 20px; }}
    </style>
    """, unsafe_allow_html=True)

# --- 4. FONCTIONS OUTILS ---
def charger(url):
    try:
        r = requests.get(url)
        return r.json() if r.status_code == 200 and r.json() else {}
    except: return {}

def get_pfp(pseudo, users_data):
    u_info = users_data.get(pseudo, {})
    return u_info.get("pfp") if u_info.get("pfp") else "https://cdn-icons-png.flaticon.com/512/149/149071.png"

# --- 5. PAGES INDÉPENDANTES ---

def page_mur(me, users_data):
    st.header("🏠 Mur Mondial")
    with st.expander("📝 Publier"):
        t = st.text_area("Texte")
        i = st.text_input("Lien Image (URL)")
        if st.button("Partager", type="primary"):
            requests.post(URL_MSG, json={"u": me, "m": t, "i": i, "d": "mondial", "t": time.time()})
            st.rerun()
    
    msgs = charger(URL_MSG)
    if msgs:
        for k in reversed(list(msgs.keys())):
            v = msgs[k]
            if v.get("d") == "mondial":
                p = get_pfp(v['u'], users_data)
                st.markdown(f"<div class='message-card'><img src='{p}' class='pfp-mini'><b>{v['u']}</b></div>", unsafe_allow_html=True)
                if v.get("m"): st.write(v["m"])
                if v.get("i"): st.image(v["i"])
                if v.get("u") == me:
                    if st.button("🗑️ Supprimer", key=f"del_{k}"):
                        requests.delete(f"{URL_BASE}messages/{k}.json")
                        st.rerun()

def page_messages(me, users_data):
    st.markdown(f"<img src='{get_pfp(me, users_data)}' class='pfp-large'>", unsafe_allow_html=True)
    st.markdown(f"<h2 style='text-align: center;'>{me}</h2>", unsafe_allow_html=True)
    
    st.divider()
    search = st.text_input("🔍 Rechercher un ami...")
    if search and st.button("Lancer la discussion", type="primary"):
        st.session_state.chat_with = search
        requests.patch(f"{URL_BASE}utilisateurs/{me}/amis.json", json={search: True})
        st.rerun()

    amis = users_data.get(me, {}).get("amis", {})
    if amis:
        st.write("### Discussions")
        for a in amis.keys():
            col1, col2 = st.columns([1, 5])
            col1.image(get_pfp(a, users_data), width=40)
            if col2.button(f"Chat avec {a}", key=f"c_{a}", type="primary"):
                st.session_state.chat_with = a
                st.rerun()

    if st.session_state.chat_with:
        target = st.session_state.chat_with
        st.divider()
        st.subheader(f"💬 Discussion avec {target}")
        
        m_in = st.text_input("Ecris ton message ici...", key="m_in")
        # BOUTON ENVOYER : type="secondary" pour qu'il devienne BLEU via le CSS
        if st.button("Envoyer 🚀", key="btn_send", type="secondary"):
            if m_in:
                requests.post(URL_MSG, json={"u": me, "m": m_in, "d": target, "t": time.time()})
                st.rerun()
        
        msgs = charger(URL_MSG)
        if msgs:
            for k in list(msgs.keys()):
                v = msgs[k]
                if (v.get("u") == me and v.get("d") == target) or (v.get("u") == target and v.get("d") == me):
                    c = "#007bff" if v['u'] == me else "#444"
                    st.markdown(f"<div style='margin-bottom:5px;'><span style='background-color:{c}; color:white; padding:8px 12px; border-radius:12px; display:inline-block;'><b>{v['u']}:</b> {v['m']}</span></div>", unsafe_allow_html=True)

def page_settings(me, users_data):
    st.header("⚙️ Paramètres")
    new_pfp = st.text_input("Lien de ta photo de profil", value=get_pfp(me, users_data))
    if st.button("Enregistrer", type="primary"):
        requests.patch(f"{URL_BASE}utilisateurs/{me}.json", json={"pfp": new_pfp})
        st.success("Profil mis à jour !")
    
    st.divider()
    if st.button("🌙 Sombre", key="thm_s"): st.session_state.theme = "sombre"; st.rerun()
    if st.button("☀️ Clair", key="thm_c"): st.session_state.theme = "clair"; st.rerun()
    if st.button("🚪 Se déconnecter", key="logout"): st.session_state.user = None; st.rerun()

# --- 6. ROUTAGE ---
users_data = charger(URL_USERS)

if st.session_state.user is None:
    st.markdown("<div class='sidebar-logo'>🛡️ ClassConnect</div>", unsafe_allow_html=True)
    t1, t2 = st.tabs(["Connexion", "Inscription"])
    with t1:
        u = st.text_input("Pseudo", key="l_u")
        p = st.text_input("Mot de passe", type="password", key="l_p")
        if st.button("Entrer", type="primary"):
            if u in users_data and str(users_data[u].get("mdp")) == str(p):
                st.session_state.user = u
                st.rerun()
    with t2:
        nu = st.text_input("Pseudo", key="r_u")
        np = st.text_input("Mot de passe", type="password", key="r_p")
        if st.button("S'inscrire", type="primary"):
            requests.patch(URL_USERS, json={nu: {"mdp": np, "pfp": "", "amis": {}}})
            st.success("Compte créé !")
else:
    # Logo ClassConnect placé en haut de la Sidebar
    st.sidebar.markdown("<div class='sidebar-logo'>🛡️ ClassConnect</div>", unsafe_allow_html=True)
    page = st.sidebar.selectbox("Navigation", ["🏠 Mur Mondial", "💬 Direct Messages", "⚙️ Paramètres"])
    
    if page == "🏠 Mur Mondial": page_mur(st.session_state.user, users_data)
    elif page == "💬 Direct Messages": page_messages(st.session_state.user, users_data)
    else: page_settings(st.session_state.user, users_data)

time.sleep(10)
st.rerun()
