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
if 'page' not in st.session_state: st.session_state.page = "🏠 Mur Mondial"
if 'chat_target' not in st.session_state: st.session_state.chat_target = None

# --- 3. DESIGN STYLE PSG (Bleu Nuit, Rouge, Blanc) ---
st.markdown("""
    <style>
    /* Fond Bleu Nuit PSG */
    .stApp { 
        background-color: #001C3F; 
        color: #FFFFFF; 
    }
    
    /* Barre Latérale avec bordure Rouge */
    [data-testid="stSidebar"] { 
        background-color: #001025; 
        border-right: 3px solid #E30613; 
    }
    
    /* Logo CC Blanc Stylisé */
    .logo-cc {
        font-family: 'Arial Black', sans-serif;
        font-size: 60px;
        color: #FFFFFF;
        text-align: center;
        letter-spacing: -5px;
        margin-bottom: 10px;
        text-shadow: 0 0 15px rgba(255, 255, 255, 0.4);
    }

    /* Boutons Rouges PSG */
    .stButton>button { 
        background-color: #E30613 !important; 
        color: white !important; 
        border-radius: 4px; 
        border: none; 
        font-weight: bold; 
        text-transform: uppercase;
        transition: 0.3s;
        height: 45px;
    }
    .stButton>button:hover {
        background-color: #FF1E26 !important;
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(227, 6, 19, 0.4);
    }

    /* Cartes des messages Blanches (Style Maillot Extérieur) */
    .msg-card { 
        background: #FFFFFF; 
        color: #001C3F;
        padding: 15px; 
        border-radius: 8px; 
        margin-bottom: 15px;
        border-left: 8px solid #E30613;
    }
    
    /* Photos de profil */
    .pfp-circle { width: 55px; height: 55px; border-radius: 50%; border: 2px solid #E30613; object-fit: cover; }
    .pfp-small { width: 35px; height: 35px; border-radius: 50%; border: 1px solid #001C3F; vertical-align: middle; }
    
    h1, h2, h3 { color: #FFFFFF !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. FONCTIONS ---
def charger(url):
    try:
        r = requests.get(url)
        return r.json() if r.status_code == 200 and r.json() else {}
    except: return {}

def get_pfp(pseudo, data):
    url = data.get(pseudo, {}).get("pfp")
    return url if url and url.startswith("http") else "https://cdn-icons-png.flaticon.com/512/149/149071.png"

data_u = charger(URL_USERS)

# --- 5. LOGIQUE ---

if st.session_state.user is None:
    st.markdown("<div class='logo-cc'>CC</div>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align:center;'>CONNECT CLASS ALGERIA</h2>", unsafe_allow_html=True)
    t1, t2 = st.tabs(["SE CONNECTER", "S'INSCRIRE"])
    with t1:
        u = st.text_input("Identifiant", key="l_u")
        p = st.text_input("Code Secret", type="password", key="l_p")
        if st.button("REJOINDRE LE TERRAIN"):
            if u in data_u and str(data_u[u].get("mdp")) == str(p):
                st.session_state.user = u
                st.rerun()
    with t2:
        nu = st.text_input("Nouveau Pseudo", key="n_u")
        np = st.text_input("Mot de passe", type="password", key="n_p")
        if st.button("CRÉER MON COMPTE"):
            requests.patch(URL_USERS, json={nu: {"mdp": np, "pfp": ""}})
            st.success("Compte créé ! Bienvenue au club.")

else:
    me = st.session_state.user
    my_pfp = get_pfp(me, data_u)
    
    # SIDEBAR
    with st.sidebar:
        st.markdown("<div class='logo-cc' style='font-size:40px;'>CC</div>", unsafe_allow_html=True)
        st.markdown(f"<center><img src='{my_pfp}' class='pfp-circle'><br><br><b>PROFIL : {me}</b></center>", unsafe_allow_html=True)
        st.divider()
        if st.button("🏠 MUR MONDIAL"): st.session_state.page = "🏠 Mur Mondial"
        if st.button("💬 MESSAGES PRIVÉS"): st.session_state.page = "💬 Messages Privés"
        if st.button("⚙️ RÉGLAGES"): st.session_state.page = "⚙️ Paramètres"
        st.divider()
        if st.button("🚪 QUITTER"):
            st.session_state.user = None
            st.rerun()

    # --- PAGES ---
    if st.session_state.page == "🏠 Mur Mondial":
        st.title("🏠 Actualités du Club")
        with st.expander("📝 Publier un message"):
            m_txt = st.text_area("Quoi de neuf ?")
            m_img = st.text_input("Lien image (URL)")
            if st.button("DIFFUSER"):
                requests.post(URL_MSG, json={"u": me, "m": m_txt, "i": m_img, "d": "mondial", "t": time.time()})
                st.rerun()
        
        msgs = charger(URL_MSG)
        if msgs:
            for k in reversed(list(msgs.keys())):
                v = msgs[k]
                if v.get("d") == "mondial":
                    u_pfp = get_pfp(v['u'], data_u)
                    st.markdown(f"""
                        <div class='msg-card'>
                            <img src='{u_pfp}' class='pfp-small'> <b>{v['u']}</b>
                            <p style='margin-top:10px;'>{v.get('m','')}</p>
                        </div>
                    """, unsafe_allow_html=True)
                    if v.get("i"): st.image(v["i"], use_container_width=True)

    elif st.session_state.page == "💬 Messages Privés":
        st.title("💬 Messagerie Directe")
        target = st.text_input("Chercher un membre...")
        if st.button("DÉMARRER CHAT"):
            if target in data_u: st.session_state.chat_target = target
            else: st.error("Membre introuvable")

        if st.session_state.chat_target:
            dest = st.session_state.chat_target
            dest_p = get_pfp(dest, data_u)
            st.markdown(f"<h3><img src='{dest_p}' class='pfp-small'> Discussion avec {dest}</h3>", unsafe_allow_html=True)
            
            msgs = charger(URL_MSG)
            if msgs:
                for k, v in msgs.items():
                    if (v.get("u") == me and v.get("d") == dest) or (v.get("u") == dest and v.get("d") == me):
                        align = "right" if v['u'] == me else "left"
                        bg = "#E30613" if v['u'] == me else "#FFFFFF"
                        txt_c = "white" if v['u'] == me else "#001C3F"
                        st.markdown(f"<div style='text-align:{align};'><span style='background:{bg}; color:{txt_c}; padding:10px; border-radius:10px; display:inline-block; margin:5px; font-weight:500;'>{v['m']}</span></div>", unsafe_allow_html=True)
            
            msg_in = st.text_input("Écrire...", key="msg_in")
            if st.button("ENVOYER"):
                if msg_in:
                    requests.post(URL_MSG, json={"u": me, "m": msg_in, "d": dest, "t": time.time()})
                    st.rerun()

    elif st.session_state.page == "⚙️ Paramètres":
        st.title("⚙️ Paramètres")
        new_pfp = st.text_input("URL de ta photo de profil", value=my_pfp)
        if st.button("SAUVEGARDER"):
            requests.patch(f"{URL_BASE}utilisateurs/{me}.json", json={"pfp": new_pfp})
            st.success("Profil mis à jour !")

time.sleep(10)
st.rerun()
