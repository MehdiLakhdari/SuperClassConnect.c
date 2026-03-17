import streamlit as st
import requests
import time

# --- 1. CONFIGURATION ---
URL_BASE = "https://classconect-f1767-default-rtdb.europe-west1.firebasedatabase.app/"
URL_MSG = f"{URL_BASE}messages.json"
URL_USERS = f"{URL_BASE}utilisateurs.json"

st.set_page_config(page_title="Connect Class Algeria", page_icon="🇩🇿", layout="wide")

# --- 2. ÉTAT DE LA SESSION ---
if 'user' not in st.session_state: st.session_state.user = None
if 'page' not in st.session_state: st.session_state.page = "🏠 Mur Mondial"
if 'chat_target' not in st.session_state: st.session_state.chat_target = None

# --- 3. DESIGN VIF & ÉLECTRIQUE ---
st.markdown("""
    <style>
    /* Fond Noir Pur pour faire ressortir le Rouge */
    .stApp { background-color: #000000; color: #FFFFFF; }
    
    /* Barre Latérale Rouge Éclatant */
    [data-testid="stSidebar"] { 
        background-color: #1a0000; 
        border-right: 3px solid #FF0000; 
    }
    
    /* Boutons Rouge Néon */
    .stButton>button { 
        background-color: #FF0000 !important; 
        color: white !important; 
        border-radius: 5px; 
        width: 100%; 
        border: none; 
        font-weight: bold; 
        height: 50px; 
        font-size: 18px;
        box-shadow: 0 0 10px #FF0000; /* Effet de lueur */
    }
    .stButton>button:hover {
        background-color: #FF4D4D !important;
        box-shadow: 0 0 20px #FF0000;
    }

    /* Cartes du Mur */
    .msg-card { 
        background: #111111; 
        padding: 20px; 
        border-radius: 12px; 
        border: 1px solid #FF0000; 
        margin-bottom: 15px; 
        box-shadow: 2px 2px 15px rgba(255, 0, 0, 0.2);
    }
    
    /* Titres Ultra Blancs */
    h1, h2, h3 { color: #FF0000 !important; font-weight: 800 !important; }
    
    /* Inputs (Champs de texte) */
    .stTextInput>div>div>input {
        background-color: #222 !important;
        color: white !important;
        border: 1px solid #FF0000 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 4. CHARGEMENT DONNÉES ---
def charger(url):
    try:
        r = requests.get(url)
        return r.json() if r.status_code == 200 and r.json() else {}
    except: return {}

data_u = charger(URL_USERS)

# --- 5. INTERFACE ---

if st.session_state.user is None:
    st.markdown("<h1 style='text-align:center; font-size:50px;'>CONNECT CLASS ALGERIA</h1>", unsafe_allow_html=True)
    t1, t2 = st.tabs(["CONNEXION", "INSCRIPTION"])
    with t1:
        u = st.text_input("Pseudo", key="login_u")
        p = st.text_input("Mot de passe", type="password", key="login_p")
        if st.button("LANCER LA SESSION"):
            if u in data_u and str(data_u[u].get("mdp")) == str(p):
                st.session_state.user = u
                st.rerun()
            else: st.error("Identifiants incorrects")
    with t2:
        nu = st.text_input("Nouveau Pseudo", key="new_u")
        np = st.text_input("Nouveau MDP", type="password", key="new_p")
        if st.button("CRÉER MON COMPTE STARTUP"):
            requests.patch(URL_USERS, json={nu: {"mdp": np, "pfp": ""}})
            st.success("Compte créé avec succès !")

else:
    me = st.session_state.user
    
    # SIDEBAR
    with st.sidebar:
        st.markdown("<h2 style='text-align:center;'>MENU</h2>", unsafe_allow_html=True)
        st.write(f"Utilisateur : **{me}**")
        st.divider()
        if st.button("🏠 MUR MONDIAL"): st.session_state.page = "🏠 Mur Mondial"
        if st.button("💬 MESSAGES PRIVÉS"): st.session_state.page = "💬 Messages Privés"
        if st.button("⚙️ PARAMÈTRES"): st.session_state.page = "⚙️ Paramètres"
        st.divider()
        if st.button("🚪 QUITTER"):
            st.session_state.user = None
            st.rerun()

    # --- PAGES ---
    if st.session_state.page == "🏠 Mur Mondial":
        st.title("🏠 FLUX MONDIAL")
        with st.expander("➕ PUBLIER UNE ACTUALITÉ"):
            m_txt = st.text_area("Votre message...")
            m_img = st.text_input("Lien Image URL (optionnel)")
            if st.button("PUBLIER MAINTENANT"):
                requests.post(URL_MSG, json={"u": me, "m": m_txt, "i": m_img, "d": "mondial", "t": time.time()})
                st.rerun()
        
        st.write("---")
        msgs = charger(URL_MSG)
        if msgs:
            for k in reversed(list(msgs.keys())):
                v = msgs[k]
                if v.get("d") == "mondial":
                    st.markdown(f"<div class='msg-card'><b>{v['u']}</b><br><br>{v.get('m','')}</div>", unsafe_allow_html=True)
                    if v.get("i"): st.image(v["i"])

    elif st.session_state.page == "💬 Messages Privés":
        st.title("💬 MESSAGES PRIVÉS")
        target = st.text_input("Entrez le pseudo exact pour discuter")
        if st.button("DÉMARRER CHAT"):
            if target in data_u: st.session_state.chat_target = target
            else: st.error("Utilisateur introuvable")

        if st.session_state.chat_target:
            dest = st.session_state.chat_target
            st.subheader(f"Discussion avec {dest}")
            
            msgs = charger(URL_MSG)
            if msgs:
                for k, v in msgs.items():
                    if (v.get("u") == me and v.get("d") == dest) or (v.get("u") == dest and v.get("d") == me):
                        align = "right" if v['u'] == me else "left"
                        bg = "#FF0000" if v['u'] == me else "#333"
                        st.markdown(f"<div style='text-align:{align};'><span style='background:{bg}; padding:10px 15px; border-radius:15px; display:inline-block; margin:5px; border: 1px solid white;'>{v['m']}</span></div>", unsafe_allow_html=True)
            
            msg_in = st.text_input("Votre message...", key="chat_in")
            if st.button("ENVOYER 🚀"):
                if msg_in:
                    requests.post(URL_MSG, json={"u": me, "m": msg_in, "d": dest, "t": time.time()})
                    st.rerun()

    elif st.session_state.page == "⚙️ Paramètres":
        st.title("⚙️ CONFIGURATION")
        pfp_url = st.text_input("URL de votre Photo de Profil")
        if st.button("METTRE À JOUR LE PROFIL"):
            requests.patch(f"{URL_BASE}utilisateurs/{me}.json", json={"pfp": pfp_url})
            st.success("C'est enregistré !")

time.sleep(10)
st.rerun()
