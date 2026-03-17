import streamlit as st
import requests
import time

# --- 1. CONFIGURATION ---
URL_BASE = "https://classconect-f1767-default-rtdb.europe-west1.firebasedatabase.app/"
URL_MSG = f"{URL_BASE}messages.json"
URL_USERS = f"{URL_BASE}utilisateurs.json"

st.set_page_config(page_title="ClassConnect - Red & White Edition", page_icon="❤️", layout="centered")

# --- 2. STYLE PERSONNALISÉ (ROUGE, BLANC & VIOLET) ---
st.markdown("""
    <style>
    /* Fond global blanc propre */
    .stApp { background-color: #ffffff; color: #333333; }
    
    /* Barre latérale en rouge */
    [data-testid="stSidebar"] { background-color: #d32f2f; color: white; }
    [data-testid="stSidebar"] * { color: white !important; }

    /* Boutons personnalisés (Rouge avec texte Blanc) */
    .stButton>button { 
        background-color: #d32f2f; 
        color: white; 
        border-radius: 8px; 
        border: none;
        padding: 10px 20px;
        font-weight: bold;
        width: 100%;
    }
    .stButton>button:hover {
        background-color: #b71c1c;
        border: none;
        color: white;
    }

    /* Cartes de message (Fond Blanc, Bordure Rouge) */
    .message-card { 
        background-color: #f8f9fa; 
        padding: 15px; 
        border-radius: 12px; 
        border-left: 6px solid #d32f2f; 
        box-shadow: 2px 2px 10px rgba(0,0,0,0.05);
        margin-bottom: 15px; 
        color: #333333;
    }

    /* Logo Violet Sombre */
    .logo-text {
        font-family: 'Trebuchet MS', sans-serif;
        font-size: 45px;
        font-weight: bold;
        color: #4B0082; /* Violet Sombre (Indigo) */
        text-align: center;
        margin-bottom: 5px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. LOGO DE L'APPLICATION ---
def afficher_logo():
    st.markdown("<div class='logo-text'>CC</div>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#4B0082; font-weight:bold; margin-top:-15px;'>ClassConnect</p>", unsafe_allow_html=True)

# --- 4. INITIALISATION DE LA SESSION ---
if 'user' not in st.session_state:
    st.session_state.user = None

# --- 5. FONCTIONS TECHNIQUES ---
def recuperer_utilisateurs():
    r = requests.get(URL_USERS).json()
    return r if r else {}

def creer_compte(pseudo, mdp):
    users = recuperer_utilisateurs()
    if pseudo in users: return False
    requests.patch(URL_USERS, json={pseudo: {"mdp": mdp}})
    return True

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
    tab1, tab2 = st.tabs(["🔒 Connexion", "📝 Inscription"])
    
    with tab1:
        u_log = st.text_input("Pseudo", key="log_u")
        p_log = st.text_input("Mot de passe", type="password", key="log_p")
        if st.button("Se connecter"):
            if verifier_connexion(u_log, p_log):
                st.session_state.user = u_log
                st.rerun()
            else: st.error("Erreur de pseudo/mot de passe")

    with tab2:
        u_reg = st.text_input("Pseudo souhaité", key="reg_u")
        p_reg = st.text_input("Mot de passe souhaité", type="password", key="reg_p")
        if st.button("Créer mon compte"):
            if u_reg and p_reg:
                if creer_compte(u_reg, p_reg): st.success("Compte créé ! Connecte-toi.")
                else: st.error("Pseudo déjà utilisé.")

# --- 7. APPLICATION PRINCIPALE ---
else:
    afficher_logo()
    
    st.sidebar.markdown(f"### 👤 {st.session_state.user}")
    menu = st.sidebar.radio("Menu", ["🌍 Chat Mondial", "💬 Messages Privés", "🚪 Déconnexion"])

    if menu == "🌍 Chat Mondial":
        st.subheader("🌍 Mur de la classe")
        msg = st.text_input("Ton message...", key="global_input")
        if st.button("Publier ❤️"):
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

    elif menu == "💬 Messages Privés":
        st.subheader("💬 Conversations Privées")
        ami = st.text_input("Discuter avec :")
        if ami:
            msg_p = st.text_input(f"Message pour {ami}...", key="priv_input")
            if st.button("Envoyer 🔒"):
                requests.post(URL_MSG, json={"u": st.session_state.user, "m": msg_p, "d": ami, "t": time.time(), "l": 0})
                st.rerun()

            st.divider()
            data = requests.get(URL_MSG).json()
            if data:
                for k in reversed(list(data.keys())):
                    v = data[k]
                    if (v.get("u") == st.session_state.user and v.get("d") == ami) or (v.get("u") == ami and v.get("d") == st.session_state.user):
                        st.markdown(f"<div class='message-card'><b>{v['u']}</b><br>{v['m']}</div>", unsafe_allow_html=True)
                        if st.button(f"❤️ {v.get('l', 0)}", key=f"lp_{k}"):
                            ajouter_like(k)
                            st.rerun()

    elif menu == "🚪 Déconnexion":
        st.session_state.user = None
        st.rerun()
