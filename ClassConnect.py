import streamlit as st
import requests
import time

# --- 1. CONFIGURATION ---
URL_BASE = "https://classconect-f1767-default-rtdb.europe-west1.firebasedatabase.app/"
URL_MSG = f"{URL_BASE}messages.json"
URL_USERS = f"{URL_BASE}utilisateurs.json"
LOGO_URL = "https://i.ibb.co/v4mYmZ8/logo-argent-algerie.png" # Remplace par l'URL de ton image si besoin

st.set_page_config(page_title="Connect Class Algeria", page_icon="📸", layout="wide")

# --- 2. ÉTAT DE LA SESSION ---
if 'user' not in st.session_state: st.session_state.user = None
if 'page' not in st.session_state: st.session_state.page = "🏠 Mur Mondial"
if 'chat_target' not in st.session_state: st.session_state.chat_target = None

# --- 3. DESIGN STYLE INSTAGRAM ---
st.markdown(f"""
    <style>
    /* Fond dégradé Instagram */
    .stApp {{ 
        background: radial-gradient(circle at 30% 107%, #fdf497 0%, #fdf497 5%, #fd5949 45%,#d6249f 60%,#285AEB 90%);
        color: white; 
    }}
    
    /* Barre Latérale Transparente */
    [data-testid="stSidebar"] {{ 
        background: rgba(0, 0, 0, 0.6); 
        backdrop-filter: blur(10px);
        border-right: 1px solid rgba(255,255,255,0.2);
    }}
    
    /* Boutons Style Insta */
    .stButton>button {{ 
        background: linear-gradient(45deg, #f09433 0%,#e6683c 25%,#dc2743 50%,#cc2366 75%,#bc1888 100%) !important; 
        color: white !important; 
        border-radius: 20px; 
        border: none; 
        font-weight: bold; 
        transition: 0.3s;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }}
    .stButton>button:hover {{ transform: scale(1.05); }}

    /* Cartes des messages */
    .insta-card {{ 
        background: rgba(255, 255, 255, 0.95); 
        color: black;
        padding: 15px; 
        border-radius: 15px; 
        margin-bottom: 20px;
        box-shadow: 0 10px 20px rgba(0,0,0,0.2);
    }}
    
    /* Photos de profil circulaires */
    .pfp {{ width: 50px; height: 50px; border-radius: 50%; object-fit: cover; border: 2px solid #d6249f; margin-right: 10px; }}
    .pfp-mini {{ width: 35px; height: 35px; border-radius: 50%; object-fit: cover; vertical-align: middle; }}
    
    h1, h2, h3 {{ color: white !important; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); }}
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
    st.image(LOGO_URL, width=150) # Ton logo sur la page de co
    st.markdown("<h1>BIENVENUE SUR CONNECT CLASS</h1>", unsafe_allow_html=True)
    t1, t2 = st.tabs(["SE CONNECTER", "NOUVEAU COMPTE"])
    with t1:
        u = st.text_input("Pseudo", key="l_u")
        p = st.text_input("Pass", type="password", key="l_p")
        if st.button("LOG IN"):
            if u in data_u and str(data_u[u].get("mdp")) == str(p):
                st.session_state.user = u
                st.rerun()
    with t2:
        nu = st.text_input("Pseudo", key="n_u")
        np = st.text_input("Pass", type="password", key="n_p")
        if st.button("S'INSCRIRE"):
            requests.patch(URL_USERS, json={nu: {"mdp": np, "pfp": ""}})
            st.success("Compte créé !")

else:
    me = st.session_state.user
    my_pfp = get_pfp(me, data_u)
    
    # SIDEBAR
    with st.sidebar:
        st.image(LOGO_URL, width=100) # Logo en haut de la sidebar
        st.markdown(f"<img src='{my_pfp}' class='pfp'><br><b>@{me}</b>", unsafe_allow_html=True)
        st.divider()
        if st.button("🏠 FEED MONDIAL"): st.session_state.page = "🏠 Mur Mondial"
        if st.button("💬 DIRECT MESSAGES"): st.session_state.page = "💬 Messages Privés"
        if st.button("⚙️ SETTINGS"): st.session_state.page = "⚙️ Paramètres"
        st.divider()
        if st.button("🚪 LOG OUT"):
            st.session_state.user = None
            st.rerun()

    # --- PAGES ---
    if st.session_state.page == "🏠 Mur Mondial":
        st.title("🏠 Feed")
        with st.expander("📸 Partager un moment"):
            m_txt = st.text_area("Légende...")
            m_img = st.text_input("URL de l'image")
            if st.button("PARTAGER"):
                requests.post(URL_MSG, json={"u": me, "m": m_txt, "i": m_img, "d": "mondial", "t": time.time()})
                st.rerun()
        
        msgs = charger(URL_MSG)
        if msgs:
            for k in reversed(list(msgs.keys())):
                v = msgs[k]
                if v.get("d") == "mondial":
                    user_pfp = get_pfp(v['u'], data_u)
                    st.markdown(f"""
                        <div class='insta-card'>
                            <img src='{user_pfp}' class='pfp-mini'> <b>{v['u']}</b>
                            <p style='margin-top:10px;'>{v.get('m','')}</p>
                        </div>
                    """, unsafe_allow_html=True)
                    if v.get("i"): st.image(v["i"], use_container_width=True)

    elif st.session_state.page == "💬 Messages Privés":
        st.title("💬 Direct")
        target = st.text_input("Rechercher un utilisateur...")
        if st.button("CHAT"):
            if target in data_u: st.session_state.chat_target = target
            else: st.error("Inconnu")

        if st.session_state.chat_target:
            dest = st.session_state.chat_target
            dest_pfp = get_pfp(dest, data_u)
            st.markdown(f"<h3><img src='{dest_pfp}' class='pfp-mini'> Chat avec {dest}</h3>", unsafe_allow_html=True)
            
            msgs = charger(URL_MSG)
            if msgs:
                for k, v in msgs.items():
                    if (v.get("u") == me and v.get("d") == dest) or (v.get("u") == dest and v.get("d") == me):
                        align = "right" if v['u'] == me else "left"
                        color = "#efefef" if v['u'] == me else "#d6249f"
                        txt_c = "black" if v['u'] == me else "white"
                        st.markdown(f"<div style='text-align:{align};'><span style='background:{color}; color:{txt_c}; padding:10px; border-radius:15px; display:inline-block; margin:5px;'>{v['m']}</span></div>", unsafe_allow_html=True)
            
            msg_in = st.text_input("Écrire un message...", key="c_in")
            if st.button("ENVOYER"):
                if msg_in:
                    requests.post(URL_MSG, json={"u": me, "m": msg_in, "d": dest, "t": time.time()})
                    st.rerun()

    elif st.session_state.page == "⚙️ Paramètres":
        st.title("⚙️ Profil")
        new_pfp = st.text_input("URL de ta nouvelle photo de profil", value=my_pfp)
        if st.button("MODIFIER"):
            requests.patch(f"{URL_BASE}utilisateurs/{me}.json", json={"pfp": new_pfp})
            st.success("Photo mise à jour !")

time.sleep(10)
st.rerun()
