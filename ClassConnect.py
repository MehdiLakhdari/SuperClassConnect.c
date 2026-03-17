import streamlit as st
import requests
import time

# --- 1. CONFIGURATION ---
URL_BASE = "https://classconect-f1767-default-rtdb.europe-west1.firebasedatabase.app/"
URL_MSG = f"{URL_BASE}messages.json"
URL_USERS = f"{URL_BASE}utilisateurs.json"

st.set_page_config(page_title="Connect Class Algeria", page_icon="🇩🇿", layout="wide")

# --- 2. SESSION STATE (Mémoire de l'appli) ---
if 'user' not in st.session_state: st.session_state.user = None
if 'page' not in st.session_state: st.session_state.page = "🏠 Mur Mondial"
if 'chat_target' not in st.session_state: st.session_state.chat_target = None

# --- 3. STYLE ROUGE SOMBRE ---
st.markdown("""
    <style>
    #MainMenu, footer, header {visibility: hidden;}
    .stApp { background-color: #1a0000; color: white; }
    .stButton>button { background-color: #ff0000; color: white; border-radius: 10px; width: 100%; border: none; font-weight: bold; }
    .sidebar-logo { background: linear-gradient(135deg, #ff0000, #800000); padding: 15px; border-radius: 10px; text-align: center; font-size: 24px; font-weight: bold; margin-bottom: 20px; }
    .msg-box { background: rgba(255,255,255,0.1); padding: 10px; border-radius: 10px; margin-bottom: 5px; border-left: 5px solid #ff0000; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. FONCTION CHARGEMENT ---
def charger(url):
    try:
        r = requests.get(url)
        return r.json() if r.status_code == 200 and r.json() else {}
    except: return {}

data_u = charger(URL_USERS)

# --- 5. LOGIQUE DE CONNEXION ---
if st.session_state.user is None:
    st.markdown("<div class='sidebar-logo'>CONNECT CLASS</div>", unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["Connexion", "Inscription"])
    with tab1:
        u = st.text_input("Pseudo", key="log_u")
        p = st.text_input("Pass", type="password", key="log_p")
        if st.button("ENTRER"):
            if u in data_u and str(data_u[u].get("mdp")) == str(p):
                st.session_state.user = u
                st.rerun()
            else: st.error("Erreur d'identifiants")
    with tab2:
        nu = st.text_input("Nouveau Pseudo", key="reg_u")
        np = st.text_input("Nouveau Pass", type="password", key="reg_p")
        if st.button("CRÉER MON COMPTE"):
            requests.patch(URL_USERS, json={nu: {"mdp": np, "pfp": ""}})
            st.success("Compte créé ! Connecte-toi.")

else:
    # --- 6. INTERFACE PRINCIPALE ---
    me = st.session_state.user
    
    # SIDEBAR FIXE
    with st.sidebar:
        st.markdown(f"<div class='sidebar-logo'>C</div>", unsafe_allow_html=True)
        st.write(f"Connecté : **{me}**")
        st.divider()
        if st.button("🏠 Mur Mondial"): st.session_state.page = "🏠 Mur Mondial"
        if st.button("💬 Messages Privés"): st.session_state.page = "💬 Messages Privés"
        if st.button("⚙️ Paramètres"): st.session_state.page = "⚙️ Paramètres"
        st.divider()
        if st.button("🚪 Déconnexion"):
            st.session_state.user = None
            st.rerun()

    # --- AFFICHAGE DES SECTIONS ---
    
    # SECTION 1 : MUR
    if st.session_state.page == "🏠 Mur Mondial":
        st.header("🏠 Mur Mondial")
        with st.expander("➕ Publier quelque chose"):
            txt = st.text_area("Ton message")
            img = st.text_input("URL d'une image (optionnel)")
            if st.button("POSTER"):
                requests.post(URL_MSG, json={"u": me, "m": txt, "i": img, "d": "mondial", "t": time.time()})
                st.rerun()
        
        st.write("---")
        tous_msgs = charger(URL_MSG)
        if tous_msgs:
            for k in reversed(list(tous_msgs.keys())):
                v = tous_msgs[k]
                if v.get("d") == "mondial":
                    st.markdown(f"<div class='msg-box'><b>{v['u']}</b> : {v.get('m','')}</div>", unsafe_allow_html=True)
                    if v.get("i"): st.image(v["i"])

    # SECTION 2 : MESSAGES PRIVÉS
    elif st.session_state.page == "💬 Messages Privés":
        st.header("💬 Messages Privés")
        target = st.text_input("Chercher un pseudo exact (ex: Norman)")
        if st.button("Ouvrir la discussion"):
            if target in data_u and target != me:
                st.session_state.chat_target = target
            else: st.error("Utilisateur non trouvé")

        if st.session_state.chat_target:
            dest = st.session_state.chat_target
            st.subheader(f"Discussion avec {dest}")
            
            # Voir les messages
            tous_msgs = charger(URL_MSG)
            if tous_msgs:
                for k, v in tous_msgs.items():
                    if (v.get("u") == me and v.get("d") == dest) or (v.get("u") == dest and v.get("d") == me):
                        color = "#28a745" if v['u'] == me else "#6f42c1"
                        st.markdown(f"<div style='background:{color}; padding:8px; border-radius:10px; margin:5px; width:fit-content; color:white;'><b>{v['u']}:</b> {v['m']}</div>", unsafe_allow_html=True)
            
            # Envoyer
            msg_in = st.text_input("Écrire...", key="input_prive")
            if st.button("ENVOYER 🚀"):
                if msg_in:
                    requests.post(URL_MSG, json={"u": me, "m": msg_in, "d": dest, "t": time.time()})
                    st.rerun()

    # SECTION 3 : PARAMÈTRES
    elif st.session_state.page == "⚙️ Paramètres":
        st.header("⚙️ Paramètres")
        st.write("Ici tu peux gérer ton compte.")
        pfp = st.text_input("Lien URL de ta photo de profil")
        if st.button("Enregistrer"):
            requests.patch(f"{URL_BASE}utilisateurs/{me}.json", json={"pfp": pfp})
            st.success("C'est fait !")

# Rafraîchissement auto toutes les 10 secondes
time.sleep(10)
st.rerun()
