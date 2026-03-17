import streamlit as st
import requests
import time
import random

# --- 1. CONFIGURATION ---
URL_BASE = "https://classconect-f1767-default-rtdb.europe-west1.firebasedatabase.app/"
URL_MSG = f"{URL_BASE}messages.json"
URL_USERS = f"{URL_BASE}utilisateurs.json"

st.set_page_config(page_title="ClassConnect Startup", page_icon="⚽", layout="wide")

# --- 2. ÉTAT DE LA SESSION ---
if 'user' not in st.session_state: st.session_state.user = None
if 'chat_with' not in st.session_state: st.session_state.chat_with = None
if 'temp_code' not in st.session_state: st.session_state.temp_code = None

# --- 3. DESIGN "RED GLOW" IMMERSIF ---
st.markdown("""
    <style>
    #MainMenu, footer, header {visibility: hidden;}
    
    .stApp {
        background: linear-gradient(180deg, #4b0000 0%, #000000 100%);
        color: #ffffff;
    }
    
    /* Logo Startup */
    .logo-container { text-align: center; margin-bottom: 30px; }
    .logo-circle {
        background: #ff0000; width: 60px; height: 60px; border-radius: 15px;
        display: inline-flex; align-items: center; justify-content: center;
        color: white; font-size: 35px; font-weight: bold; box-shadow: 0 0 20px #ff0000;
    }

    /* Style Formulaire */
    .stTextInput>div>div>input, .stSelectbox>div>div>div {
        background-color: rgba(255, 255, 255, 0.1) !important;
        color: white !important;
        border-radius: 10px !important;
        border: 1px solid #ff4b4b !important;
    }
    
    /* Bulles de Chat */
    .bubble-me { background-color: #28a745; color: white; padding: 12px; border-radius: 15px; margin: 5px; display: inline-block; }
    .bubble-them { background-color: #6f42c1; color: white; padding: 12px; border-radius: 15px; margin: 5px; display: inline-block; }
    
    /* Boutons */
    .stButton>button {
        background: linear-gradient(to right, #ff0000, #8b0000);
        color: white; border: none; border-radius: 12px; font-weight: bold; padding: 10px;
    }
    div.stButton > button:first-child[kind="secondary"] { background: #007bff !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. FONCTIONS ---
def charger(url):
    try:
        r = requests.get(url)
        return r.json() if r.status_code == 200 and r.json() else {}
    except: return {}

# --- 5. LOGIQUE D'INSCRIPTION & AUTHENTIFICATION ---
users_data = charger(URL_USERS)

if st.session_state.user is None:
    st.markdown("<div class='logo-container'><div class='logo-circle'>C</div><h1 style='color:white;'>CLASS CONNECT</h1></div>", unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["Connexion", "Créer un Compte Startup"])
    
    with tab1:
        u_log = st.text_input("Pseudo", key="log_u")
        p_log = st.text_input("Mot de passe", type="password", key="log_p")
        if st.button("SE CONNECTER"):
            if u_log in users_data and str(users_data[u_log].get("mdp")) == str(p_log):
                st.session_state.user = u_log
                st.rerun()
            else: st.error("Accès refusé.")

    with tab2:
        st.write("### 📝 Formulaire d'adhésion")
        new_u = st.text_input("Pseudo (Unique)")
        new_m = st.text_input("Email")
        new_p = st.text_input("Mot de passe", type="password")
        col_a, col_b = st.columns(2)
        new_s = col_a.selectbox("Sexe", ["Homme", "Femme", "Autre"])
        new_age = col_b.number_input("Âge", min_value=13, max_value=100)
        
        if st.button("VÉRIFIER MON COMPTE"):
            if new_u in users_data:
                st.error("Ce pseudo est déjà utilisé par un autre collaborateur.")
            elif not new_u or not new_m or not new_p:
                st.warning("Veuillez remplir tout le formulaire.")
            else:
                # Simulation d'envoi de code Google/Mail
                st.session_state.temp_code = random.randint(1000, 9999)
                st.info(f"🛡️ CODE DE SÉCURITÉ ENVOYÉ : {st.session_state.temp_code}")
        
        if st.session_state.temp_code:
            code_in = st.text_input("Entrez le code reçu par mail")
            if st.button("VALIDER L'INSCRIPTION"):
                if str(code_in) == str(st.session_state.temp_code):
                    # Enregistrement final
                    requests.patch(URL_USERS, json={new_u: {
                        "mdp": new_p, "mail": new_m, "sexe": new_s, 
                        "age": new_age, "pfp": "", "amis": {}
                    }})
                    st.success("Compte validé ! Vous pouvez vous connecter.")
                    st.session_state.temp_code = None
                else:
                    st.error("Code incorrect.")

# --- 6. INTERFACE CONNECTÉE ---
else:
    me = st.session_state.user
    st.sidebar.markdown(f"<div class='logo-circle' style='width:40px; height:40px; font-size:20px;'>C</div><br><b>Propriété de {me}</b>", unsafe_allow_html=True)
    
    menu = st.sidebar.selectbox("Menu", ["🏠 Mur Mondial", "💬 Direct Messages", "⚙️ Paramètres"])

    if menu == "🏠 Mur Mondial":
        st.header("🏠 Flux de l'Entreprise")
        with st.expander("📢 Publier une annonce"):
            txt = st.text_area("Votre message...")
            if st.button("Diffuser"):
                requests.post(URL_MSG, json={"u": me, "m": txt, "d": "mondial", "t": time.time()})
                st.rerun()
        
        msgs = charger(URL_MSG)
        for k in reversed(list(msgs.keys())):
            v = msgs[k]
            if v.get("d") == "mondial":
                st.markdown(f"<div class='message-card'><b>{v['u']}</b>: {v['m']}</div>", unsafe_allow_html=True)

    elif menu == "💬 Direct Messages":
        st.header("💬 Centre de Communication")
        
        # BARRE DE RECHERCHE CORRIGÉE
        search = st.text_input("🔍 Rechercher un utilisateur pour discuter...")
        if st.button("Lancer la discussion"):
            if search in users_data and search != me:
                st.session_state.chat_with = search
                requests.patch(f"{URL_BASE}utilisateurs/{me}/amis.json", json={search: True})
                st.rerun()
            else: st.warning("Utilisateur introuvable.")

        # Répertoire
        mes_amis = users_data.get(me, {}).get("amis", {})
        if mes_amis:
            st.write("---")
            for ami in mes_amis.keys():
                if st.sidebar.button(f"👤 {ami}", key=f"chat_{ami}"):
                    st.session_state.chat_with = ami
                    st.rerun()

        if st.session_state.chat_with:
            target = st.session_state.chat_with
            st.subheader(f"Discussion sécurisée avec {target}")
            
            # Chat
            msgs = charger(URL_MSG)
            for k in list(msgs.keys()):
                v = msgs[k]
                if (v.get("u") == me and v.get("d") == target) or (v.get("u") == target and v.get("d") == me):
                    cls = "bubble-me" if v['u'] == me else "bubble-them"
                    st.markdown(f"<div class='{cls}'><b>{v['u']}:</b> {v['m']}</div>", unsafe_allow_html=True)
            
            msg_in = st.text_input("Message...", key="msg_in")
            if st.button("ENVOYER 🚀", type="secondary"):
                if msg_in:
                    requests.post(URL_MSG, json={"u": me, "m": msg_in, "d": target, "t": time.time()})
                    st.rerun()

    elif menu == "⚙️ Paramètres":
        if st.button("🚪 Se déconnecter"):
            st.session_state.user = None
            st.rerun()

time.sleep(10)
st.rerun()
