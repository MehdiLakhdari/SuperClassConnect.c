import streamlit as st
import requests
import time

# --- 1. CONFIGURATION ---
URL_BASE = "https://classconect-f1767-default-rtdb.europe-west1.firebasedatabase.app/"
URL_MSG = f"{URL_BASE}messages.json"
URL_USERS = f"{URL_BASE}utilisateurs.json"

st.set_page_config(page_title="ClassConnect ⚽", page_icon="⚽", layout="centered")

# --- 2. ÉTAT DE LA SESSION ---
if 'theme' not in st.session_state: st.session_state.theme = "sombre"
if 'user' not in st.session_state: st.session_state.user = None
if 'chat_with' not in st.session_state: st.session_state.chat_with = None

# --- 3. DESIGN DYNAMIQUE ---
if st.session_state.theme == "sombre":
    bg, txt, btn, card = "#000000", "#ffffff", "#bc2a8d", "#1e1e1e"
else:
    bg, txt, btn, card = "#ffffff", "#000000", "#e1306c", "#f0f2f5"

st.markdown(f"""
    <style>
    .stApp {{ background-color: {bg}; color: {txt}; }}
    .message-card {{ background-color: {card}; padding: 15px; border-radius: 12px; margin-bottom: 10px; border: 1px solid #333; }}
    .pfp-large {{ width: 100px; height: 100px; border-radius: 50%; object-fit: cover; border: 3px solid {btn}; display: block; margin: 0 auto; }}
    .pfp-mini {{ width: 35px; height: 35px; border-radius: 50%; object-fit: cover; margin-right: 10px; vertical-align: middle; }}
    .stButton>button {{ border-radius: 10px; font-weight: bold; background-color: {btn}; color: white; border: none; width: 100%; }}
    
    /* BOUTON ENVOYER (BLEU) */
    div.stButton > button:first-child[kind="secondary"] {{
        background-color: #007bff !important;
        color: white !important;
    }}
    .sidebar-logo {{ font-size: 26px; font-weight: bold; color: {btn}; text-align: center; margin-bottom: 20px; }}
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
    return u_info.get("pfp") if u_info.get("pfp") else "https://cdn-icons-png.flaticon.com/512/149/149071.png"

# --- 5. LOGIQUE DE NAVIGATION (INDÉPENDANCE TOTALE) ---

main_container = st.empty() # Création d'une zone vide qui sera vidée à chaque changement

with main_container.container():
    if st.session_state.user is None:
        st.markdown("<div class='sidebar-logo'>⚽ ClassConnect</div>", unsafe_allow_html=True)
        t1, t2 = st.tabs(["Connexion", "Inscription"])
        with t1:
            u = st.text_input("Pseudo", key="login_u")
            p = st.text_input("Mot de passe", type="password", key="login_p")
            if st.button("Se connecter", key="btn_l"):
                users_data = charger(URL_USERS)
                if u in users_data and str(users_data[u].get("mdp")) == str(p):
                    st.session_state.user = u
                    st.rerun()
                else: st.error("Erreur d'identifiants")
        with t2:
            nu = st.text_input("Pseudo", key="reg_u")
            np = st.text_input("Mot de passe", type="password", key="reg_p")
            if st.button("S'inscrire", key="btn_r"):
                requests.patch(URL_USERS, json={nu: {"mdp": np, "pfp": "", "amis": {}}})
                st.success("Compte prêt !")

    else:
        users_data = charger(URL_USERS)
        st.sidebar.markdown("<div class='sidebar-logo'>⚽ ClassConnect</div>", unsafe_allow_html=True)
        page = st.sidebar.selectbox("Navigation", ["🏠 Mur Mondial", "💬 Messages Privés", "⚙️ Paramètres"])

        # --- PAGE 1 : MUR ---
        if page == "🏠 Mur Mondial":
            st.header("🏠 Mur Mondial")
            with st.expander("📝 Nouvelle Publication"):
                t = st.text_area("Ton message")
                i = st.text_input("Lien Image (URL)")
                if st.button("Publier"):
                    requests.post(URL_MSG, json={"u": st.session_state.user, "m": t, "i": i, "d": "mondial", "t": time.time()})
                    st.rerun()
            
            msgs = charger(URL_MSG)
            for k in reversed(list(msgs.keys())):
                v = msgs[k]
                if v.get("d") == "mondial":
                    p = get_pfp(v['u'], users_data)
                    st.markdown(f"<div class='message-card'><img src='{p}' class='pfp-mini'><b>{v['u']}</b><br>{v.get('m','')}</div>", unsafe_allow_html=True)
                    if v.get("i"): st.image(v["i"])
                    if v.get("u") == st.session_state.user:
                        if st.button("🗑️", key=f"del_{k}"):
                            requests.delete(f"{URL_BASE}messages/{k}.json")
                            st.rerun()

        # --- PAGE 2 : MESSAGES PRIVÉS ---
        elif page == "💬 Messages Privés":
            me = st.session_state.user
            st.markdown(f"<img src='{get_pfp(me, users_data)}' class='pfp-large'>", unsafe_allow_html=True)
            st.markdown(f"<h2 style='text-align: center;'>{me}</h2>", unsafe_allow_html=True)
            
            st.divider()
            search = st.text_input("🔍 Rechercher un contact...")
            if st.button("Ajouter à mes contacts"):
                if search and search != me:
                    st.session_state.chat_with = search
                    requests.patch(f"{URL_BASE}utilisateurs/{me}/amis.json", json={search: True})
                    st.rerun()

            # RÉPERTOIRE DES CONTACTS
            mes_amis = users_data.get(me, {}).get("amis", {})
            if mes_amis:
                st.write("### 📇 Tes Contacts")
                for ami in mes_amis.keys():
                    col1, col2 = st.columns([1, 5])
                    col1.image(get_pfp(ami, users_data), width=40)
                    if col2.button(f"Chat avec {ami}", key=f"chat_{ami}"):
                        st.session_state.chat_with = ami
                        st.rerun()

            # ZONE DE CHAT
            if st.session_state.chat_with:
                target = st.session_state.chat_with
                st.divider()
                st.subheader(f"💬 Discussion : {target}")
                m_in = st.text_input("Ton message...", key="m_in")
                if st.button("Envoyer 🚀", type="secondary"):
                    if m_in:
                        requests.post(URL_MSG, json={"u": me, "m": m_in, "d": target, "t": time.time()})
                        st.rerun()
                
                msgs = charger(URL_MSG)
                for k in list(msgs.keys()):
                    v = msgs[k]
                    if (v.get("u") == me and v.get("d") == target) or (v.get("u") == target and v.get("d") == me):
                        color = "#28a745" if v['u'] == me else "#6f42c1"
                        st.markdown(f"<div style='margin-bottom:8px;'><span style='background-color:{color}; color:white; padding:10px; border-radius:15px; display:inline-block;'><b>{v['u']}:</b> {v['m']}</span></div>", unsafe_allow_html=True)

        # --- PAGE 3 : PARAMÈTRES ---
        elif page == "⚙️ Paramètres":
            st.header("⚙️ Paramètres")
            me = st.session_state.user
            new_pfp = st.text_input("URL Photo de profil", value=get_pfp(me, users_data))
            if st.button("Sauvegarder"):
                requests.patch(f"{URL_BASE}utilisateurs/{me}.json", json={"pfp": new_pfp})
                st.success("Profil mis à jour")
            st.divider()
            if st.button("🌙 Mode Sombre"): st.session_state.theme = "sombre"; st.rerun()
            if st.button("☀️ Mode Clair"): st.session_state.theme = "clair"; st.rerun()
            if st.button("🚪 Déconnexion"):
                st.session_state.user = None
                st.rerun()

# Rafraîchissement automatique pour les nouveaux messages
time.sleep(10)
st.rerun()
