import streamlit as st
import requests
import time

# --- 1. CONFIGURATION ---
URL_BASE = "https://classconect-f1767-default-rtdb.europe-west1.firebasedatabase.app/"
URL_MSG = f"{URL_BASE}messages.json"
URL_USERS = f"{URL_BASE}utilisateurs.json"

st.set_page_config(page_title="ClassConnect Business", page_icon="⚽", layout="wide")

# --- 2. ÉTAT DE LA SESSION ---
if 'theme' not in st.session_state: st.session_state.theme = "sombre"
if 'user' not in st.session_state: st.session_state.user = None
if 'chat_with' not in st.session_state: st.session_state.chat_with = None

# --- 3. MODE PLEIN ÉCRAN & DESIGN PROFESSIONNEL ---
# Ce bloc CSS cache la barre Streamlit et crée le logo en dégradé
st.markdown("""
    <style>
    /* Cacher les menus Streamlit pour le mode Plein Écran */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .block-container {padding-top: 2rem; padding-bottom: 0rem;}
    
    /* Logo de l'entreprise avec dégradé personnel */
    .company-logo {
        background: linear-gradient(45deg, #ff0000, #000000);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 40px;
        font-weight: 900;
        text-align: center;
        letter-spacing: -1px;
        margin-bottom: 20px;
        font-family: 'Arial Black', sans-serif;
    }
    
    .stApp { background-color: #000000; color: #ffffff; }
    .message-card { background-color: #121212; padding: 15px; border-radius: 12px; border: 1px solid #333; margin-bottom: 10px; }
    .stButton>button { border-radius: 10px; font-weight: bold; background: linear-gradient(to right, #e1306c, #bc2a8d); color: white; border: none; }
    
    /* Style Spécial Bouton Envoyer Bleu */
    div.stButton > button:first-child[kind="secondary"] {
        background: #007bff !important;
        color: white !important;
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
    return u_info.get("pfp") if u_info.get("pfp") else "https://cdn-icons-png.flaticon.com/512/149/149071.png"

# --- 5. INTERFACE ---
main_view = st.empty()

with main_view.container():
    if st.session_state.user is None:
        st.markdown("<div class='company-logo'>CLASS CONNECT ⚽</div>", unsafe_allow_html=True)
        t1, t2 = st.tabs(["Connexion", "Créer un compte"])
        with t1:
            u = st.text_input("Identifiant", key="l_u")
            p = st.text_input("Mot de passe", type="password", key="l_p")
            if st.button("ACCÉDER AU RÉSEAU"):
                users_data = charger(URL_USERS)
                if u in users_data and str(users_data[u].get("mdp")) == str(p):
                    st.session_state.user = u
                    st.rerun()
        with t2:
            nu = st.text_input("Pseudo", key="r_u")
            np = st.text_input("Mot de passe", type="password", key="r_p")
            if st.button("S'INSCRIRE"):
                requests.patch(URL_USERS, json={nu: {"mdp": np, "pfp": "", "amis": {}}})
                st.success("Bienvenue dans l'entreprise !")

    else:
        users_data = charger(URL_USERS)
        # Logo dans la barre latérale
        st.sidebar.markdown("<div class='company-logo' style='font-size:25px;'>CLASS CONNECT</div>", unsafe_allow_html=True)
        page = st.sidebar.selectbox("Navigation", ["🏠 Mur Mondial", "💬 Messages Privés", "⚙️ Paramètres"])

        if page == "🏠 Mur Mondial":
            st.header("🏠 Flux Mondial")
            with st.expander("📝 Nouvelle Publication"):
                t = st.text_area("Que voulez-vous partager ?")
                i = st.text_input("Lien Image")
                if st.button("PUBLIER"):
                    requests.post(URL_MSG, json={"u": st.session_state.user, "m": t, "i": i, "d": "mondial", "t": time.time()})
                    st.rerun()
            
            msgs = charger(URL_MSG)
            for k in reversed(list(msgs.keys())):
                v = msgs[k]
                if v.get("d") == "mondial":
                    p = get_pfp(v['u'], users_data)
                    st.markdown(f"<div class='message-card'><img src='{p}' style='width:35px; border-radius:50%;'> <b>{v['u']}</b><br><br>{v.get('m','')}</div>", unsafe_allow_html=True)
                    if v.get("i"): st.image(v["i"])

        elif page == "💬 Messages Privés":
            me = st.session_state.user
            st.markdown(f"<h2 style='text-align: center;'>Espace de {me}</h2>", unsafe_allow_html=True)
            
            # Recherche & Ajout
            search = st.text_input("🔍 Rechercher un collaborateur...")
            if st.button("Ouvrir la discussion"):
                if search and search != me:
                    st.session_state.chat_with = search
                    requests.patch(f"{URL_BASE}utilisateurs/{me}/amis.json", json={search: True})
                    st.rerun()

            # Liste des contacts
            mes_amis = users_data.get(me, {}).get("amis", {})
            if mes_amis:
                st.write("### 📇 Répertoire")
                for ami in mes_amis.keys():
                    if st.button(f"👤 Chat avec {ami}", key=f"c_{ami}"):
                        st.session_state.chat_with = ami
                        st.rerun()

            # Zone de Chat
            if st.session_state.chat_with:
                target = st.session_state.chat_with
                st.divider()
                st.subheader(f"Conversation : {target}")
                m_in = st.text_input("Écrire...", key="m_in")
                if st.button("ENVOYER 🚀", type="secondary"):
                    if m_in:
                        requests.post(URL_MSG, json={"u": me, "m": m_in, "d": target, "t": time.time()})
                        st.rerun()
                
                msgs = charger(URL_MSG)
                for k in list(msgs.keys()):
                    v = msgs[k]
                    if (v.get("u") == me and v.get("d") == target) or (v.get("u") == target and v.get("d") == me):
                        color = "#28a745" if v['u'] == me else "#6f42c1"
                        st.markdown(f"<div style='margin-bottom:8px;'><span style='background-color:{color}; color:white; padding:10px; border-radius:15px; display:inline-block;'><b>{v['u']}:</b> {v['m']}</span></div>", unsafe_allow_html=True)

        elif page == "⚙️ Paramètres":
            st.header("⚙️ Configuration")
            if st.button("🚪 Déconnexion du système"):
                st.session_state.user = None
                st.rerun()

# Auto-Refresh
time.sleep(10)
st.rerun()
