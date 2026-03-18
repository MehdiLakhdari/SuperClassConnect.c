import streamlit as st
import requests
import time

# --- 1. CONFIGURATION & SON ---
st.set_page_config(page_title="Connect Class Algeria", page_icon="😊", layout="wide")

# Fonction pour jouer un son de notification
def play_notif_sound():
    sound_html = """
    <audio autoplay>
        <source src="https://www.soundjay.com/buttons/beep-01a.mp3" type="audio/mpeg">
    </audio>
    """
    st.markdown(sound_html, unsafe_allow_html=True)

# --- 2. DESIGN NOIR & ROUGE ---
st.markdown("""
    <style>
    header {visibility: hidden;}
    .stApp { background-color: #050505; color: #ffffff; }
    
    /* Barre latérale personnalisée */
    [data-testid="stSidebar"] {
        background-color: #121212 !important;
        border-right: 2px solid #FF0000;
    }

    /* LOGO CC ORANGE (On le garde comme demandé) */
    .logo-box {
        background: linear-gradient(135deg, #FF8C00, #FF4500);
        width: 60px; height: 60px; border-radius: 12px;
        display: flex; align-items: center; justify-content: center;
        margin: 0 auto; font-size: 35px; font-weight: bold; color: white;
    }

    /* BOUTONS ROUGES */
    .stButton>button { 
        background: linear-gradient(90deg, #CC0000, #8B0000) !important; 
        color: white !important; border-radius: 5px; font-weight: bold; width: 100%;
        border: none; transition: 0.3s;
    }
    .stButton>button:hover { transform: scale(1.02); box-shadow: 0 0 10px #FF0000; }

    /* CARTES MESSAGES */
    .msg-card { 
        background: #1a1a1a; padding: 15px; border-radius: 8px; 
        border-left: 5px solid #FF0000; margin-bottom: 10px; 
    }
    </style>
    """, unsafe_allow_html=True)

URL_BASE = "https://classconect-f1767-default-rtdb.europe-west1.firebasedatabase.app/"
URL_MSG = f"{URL_BASE}messages.json"
URL_USERS = f"{URL_BASE}utilisateurs.json"

# --- 3. LOGIQUE SESSION ---
if 'user' not in st.session_state: st.session_state.user = None
if 'page' not in st.session_state: st.session_state.page = "Mur"
if 'last_msg_count' not in st.session_state: st.session_state.last_msg_count = 0
if 'sound_enabled' not in st.session_state: st.session_state.sound_enabled = False

def get_db(url):
    try:
        r = requests.get(url, timeout=5)
        return r.json() if r.status_code == 200 else {}
    except: return {}

# --- 4. INTERFACE ---

data_u = get_db(URL_USERS)
all_m = get_db(URL_MSG)

# Vérification auto des nouveaux messages pour le son
current_count = len(all_m) if all_m else 0
if st.session_state.sound_enabled and current_count > st.session_state.last_msg_count:
    play_notif_sound()
st.session_state.last_msg_count = current_count

if st.session_state.user is None:
    st.markdown("<div class='logo-box'>C</div><h3 style='text-align:center;'>Class Connect Algeria 😊</h3>", unsafe_allow_html=True)
    t1, t2 = st.tabs(["Connexion", "Inscription"])
    with t1:
        u = st.text_input("Pseudo", key="l_u")
        p = st.text_input("Mdp", type="password", key="l_p")
        if st.button("SE CONNECTER"):
            if u in data_u and str(data_u[u].get("mdp")) == str(p):
                st.session_state.user = u
                st.rerun()

else:
    me = st.session_state.user
    
    # --- RETOUR DE LA BARRE LATÉRALE ---
    with st.sidebar:
        st.markdown("<div class='logo-box'>C</div>", unsafe_allow_html=True)
        st.markdown(f"<h3 style='text-align:center;'>@{me}</h3>", unsafe_allow_html=True)
        st.divider()
        
        if st.button("🏠 MUR MONDIAL"): st.session_state.page = "Mur"
        if st.button("💬 MESSAGES PRIVÉS"): st.session_state.page = "Chat"
        
        st.divider()
        st.write("🔔 **Paramètres**")
        st.session_state.sound_enabled = st.checkbox("Activer les sons 🔊", value=st.session_state.sound_enabled)
        st.caption("Activez ceci pour entendre un 'bip' lors des nouveaux messages.")
        
        st.divider()
        if st.button("🚪 QUITTER"):
            st.session_state.user = None
            st.rerun()

    # --- PAGES ---
    if st.session_state.page == "Mur":
        st.title("🌍 Mur Mondial")
        with st.expander("📝 Publier"):
            txt = st.text_area("Message")
            img = st.text_input("Lien Image URL")
            if st.button("POSTER"):
                requests.post(URL_MSG, json={"u": me, "m": txt, "i": img, "d": "mondial", "t": time.time()})
                st.rerun()
        
        if all_m:
            for k in reversed(list(all_m.keys())):
                v = all_m[k]
                if v.get("d") == "mondial":
                    st.markdown(f"<div class='msg-card'><b>@{v['u']}</b><br>{v.get('m','')}</div>", unsafe_allow_html=True)
                    if v.get("i"): st.image(v["i"], use_container_width=True)

    elif st.session_state.page == "Chat":
        st.title("💬 Messagerie")
        col_f, col_c = st.columns([1, 2])
        with col_f:
            st.write("👥 **Amis**")
            amis = data_u.get(me, {}).get("amis", {})
            for a in amis:
                if st.button(f"👤 {a}", key=f"chat_{a}"):
                    st.session_state.chat_target = a
                    st.rerun()
            
            st.divider()
            nf = st.text_input("Ajouter un pseudo").strip()
            if st.button("AJOUTER"):
                if nf in data_u and nf != me:
                    requests.patch(f"{URL_BASE}utilisateurs/{me}/amis.json", json={nf: True})
                    st.rerun()

        with col_c:
            target = st.session_state.get("chat_target")
            if target:
                st.write(f"Discussion avec **{target}**")
                if all_m:
                    for k, v in all_m.items():
                        if (v.get("u") == me and v.get("d") == target) or (v.get("u") == target and v.get("d") == me):
                            side = "right" if v['u'] == me else "left"
                            color = "#CC0000" if side == "right" else "#333"
                            st.markdown(f"<div style='text-align:{side};'><span style='background:{color}; padding:8px; border-radius:10px; display:inline-block; margin:5px;'>{v['m']}</span></div>", unsafe_allow_html=True)
                
                m_in = st.text_input("Écrire...", key="chat_input")
                if st.button("ENVOYER"):
                    requests.post(URL_MSG, json={"u": me, "m": m_in, "d": target, "t": time.time()})
                    st.rerun()

# --- ACTUALISATION ---
time.sleep(10)
st.rerun()
