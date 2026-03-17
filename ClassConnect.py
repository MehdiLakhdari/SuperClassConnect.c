import streamlit as st
import requests
import time

# --- 1. CONFIGURATION ---
URL_BASE = "https://classconect-f1767-default-rtdb.europe-west1.firebasedatabase.app/"
URL_MSG = f"{URL_BASE}messages.json"
URL_USERS = f"{URL_BASE}utilisateurs.json"

st.set_page_config(page_title="ClassConnect - Dark Mode", page_icon="🌙", layout="centered")

# --- 2. STYLE "EYE CARE" (SOMBRE & APAISANT) ---
st.markdown("""
    <style>
    /* Fond global : Gris Anthracite très sombre */
    .stApp { 
        background-color: #121212; 
        color: #E0E0E0; 
    }
    
    /* Barre latérale : Gris Ardoise */
    [data-testid="stSidebar"] { 
        background-color: #1E1E1E; 
        border-right: 1px solid #333333;
    }
    [data-testid="stSidebar"] * { color: #BB86FC !important; }

    /* Boutons : Violet Pastel (Moins agressif que le rouge) */
    .stButton>button { 
        background-color: #3700B3; 
        color: white; 
        border-radius: 10px; 
        border: none;
        padding: 12px;
        font-weight: bold;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #BB86FC;
        color: #121212;
    }

    /* Cartes de message : Gris Foncé avec bordure Bleue */
    .message-card { 
        background-color: #1E1E1E; 
        padding: 15px; 
        border-radius: 12px; 
        border-left: 5px solid #03DAC6; /* Vert d'eau apaisant */
        box-shadow: 0px 4px 10px rgba(0,0,0,0.3);
        margin-bottom: 15px; 
        color: #E0E0E0;
    }

    /* Titres et Textes */
    h1, h2, h3 { color: #BB86FC !important; }
    
    /* Logo stylé */
    .logo-container {
        text-align: center;
        padding: 20px;
        background: linear-gradient(45deg, #3700B3, #03DAC6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 60px;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. LOGO ---
def afficher_logo():
    st.markdown("<div class='logo-container'>CC</div>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#03DAC6; font-weight:bold; margin-top:-20px;'>ClassConnect Pro</p>", unsafe_allow_html=True)

# --- 4. INITIALISATION ---
if 'user' not in st.session_state:
    st.session_state.user = None

# --- 5. FONCTIONS ---
def recuperer_utilisateurs():
    r = requests.get(URL_USERS).json()
    return r if r else {}

def verifier_connexion(pseudo, mdp):
    users = recuperer_utilisateurs()
    return pseudo in users and users[pseudo]["mdp"] == mdp

def ajouter_like(msg_key):
    url_msg_specifique = f"{URL_BASE}messages/{msg_key}.json"
    msg_data = requests.get(url_msg_specifique).json()
    if msg_data:
        current_likes = msg_data.get("l", 0)
        requests.patch(url_msg_specifique, json={"l": current_likes + 1})

# --- 6. AUTHENTIFICATION ---
if st.session_state.user is None:
    afficher_logo()
    tab1, tab2 = st.tabs(["🔑 Connexion", "📝 Inscription"])
    
    with tab1:
        u_log = st.text_input("Pseudo", key="log_u")
        p_log = st.text_input("Mot de passe", type="password", key="log_p")
        if st.button("Se connecter"):
            if verifier_connexion(u_log, p_log):
                st.session_state.user = u_log
                st.rerun()
            else: st.error("Identifiants incorrects.")

    with tab2:
        u_reg = st.text_input("Nouveau Pseudo", key="reg_u")
        p_reg = st.text_input("Nouveau Mot de passe", type="password", key="reg_p")
        if st.button("Créer mon compte"):
            if u_reg and p_reg:
                requests.patch(URL_USERS, json={u_reg: {"mdp": p_reg}})
                st.success("Compte prêt !")

# --- 7. APP PRINCIPALE ---
else:
    afficher_logo()
    st.sidebar.markdown(f"### 👤 {st.session_state.user}")
    menu = st.sidebar.radio("Navigation", ["🌍 Chat Mondial", "💬 Privé", "🚪 Sortir"])

    if menu == "🌍 Chat Mondial":
        st.subheader("🌍 Discussion Mondiale")
        msg = st.text_input("Message...", key="g_input")
        if st.button("Publier 🚀"):
            if msg:
                requests.post(URL_MSG, json={"u": st.session_state.user, "m": msg, "d": "mondial", "t": time.time(), "l": 0})
                st.rerun()

        st.divider()
        data = requests.get(URL_MSG).json()
        if data:
            for k in reversed(list(data.keys())):
                v = data[k]
                if v.get("d") == "mondial":
                    st.markdown(f"<div class='message-card'><b>{v['u']}</b><br>{v['m']}</div>", unsafe_allow_html=True)
                    if st.button(f"❤️ {v.get('l', 0)}", key=f"l_{k}"):
                        ajouter_like(k)
                        st.rerun()

    elif menu == "💬 Privé":
        ami = st.text_input("Ami :")
        if ami:
            msg_p = st.text_input("Message privé...", key="p_input")
            if st.button("Envoyer 🔒"):
                requests.post(URL_MSG, json={"u": st.session_state.user, "m": msg_p, "d": ami, "t": time.time(), "l": 0})
                st.rerun()
            
            data = requests.get(URL_MSG).json()
            if data:
                for k in reversed(list(data.keys())):
                    v = data[k]
                    if (v.get("u") == st.session_state.user and v.get("d") == ami) or (v.get("u") == ami and v.get("d") == st.session_state.user):
                        st.markdown(f"<div class='message-card'><b>{v['u']}</b><br>{v['m']}</div>", unsafe_allow_html=True)
                        if st.button(f"❤️ {v.get('l', 0)}", key=f"lp_{k}"):
                            ajouter_like(k)
                            st.rerun()

    elif menu == "🚪 Sortir":
        st.session_state.user = None
        st.rerun()
