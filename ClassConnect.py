import streamlit as st
import requests
import time

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Connect Class", page_icon="😊", layout="wide")

st.markdown("""
    <style>
    header {visibility: hidden;}
    .stApp { background-color: #050505; color: white; }
    
    /* NAVIGATION HAUT - BORDURE ROUGE */
    .nav-bar { 
        background: #111; 
        padding: 10px; 
        border-radius: 10px; 
        border-bottom: 3px solid #D32F2F; 
        margin-bottom: 20px; 
        text-align:center; 
    }
    
    /* BOUTONS NAVIGATION - ORANGE */
    div[data-testid="stColumn"] .stButton>button { 
        background: linear-gradient(90deg, #FF8C00, #FF4500) !important; 
        color: white !important; 
        border-radius: 8px; 
        font-weight: bold; 
        height: 50px; 
        border: none;
        font-size: 18px;
    }

    /* BOUTONS D'ACTION (Envoyer/Poster) - ROUGE */
    .stFormSubmitButton>button, .btn-red button {
        background: linear-gradient(90deg, #D32F2F, #8B0000) !important;
        color: white !important;
        border: none !important;
    }

    /* ANIMATION FLASH ROUGE POUR NOTIFS */
    @keyframes blink { 0% {box-shadow: 0 0 5px #FF0000;} 50% {box-shadow: 0 0 25px #FF0000;} 100% {box-shadow: 0 0 5px #FF0000;} }
    .notif-active button { animation: blink 1s infinite !important; border: 2px solid white !important; }

    /* CARTES MESSAGES */
    .msg-card { 
        background: #111; 
        padding: 15px; 
        border-radius: 10px; 
        border-left: 5px solid #D32F2F; 
        margin-bottom: 10px; 
    }
    </style>
    """, unsafe_allow_html=True)

URL_BASE = "https://classconect-f1767-default-rtdb.europe-west1.firebasedatabase.app/"
URL_MSG = f"{URL_BASE}messages.json"
URL_USERS = f"{URL_BASE}utilisateurs.json"

if 'user' not in st.session_state: st.session_state.user = None
if 'page' not in st.session_state: st.session_state.page = "Mur"
if 'last_count' not in st.session_state: st.session_state.last_count = 0

def get_db(url):
    try:
        r = requests.get(url, timeout=5)
        return r.json() if r.status_code == 200 else {}
    except: return {}

# --- 2. LOGIQUE ---
data_u = get_db(URL_USERS)
all_m = get_db(URL_MSG)

# Notifs
curr_count = len(all_m) if all_m else 0
has_notif = False
if st.session_state.user and curr_count > st.session_state.last_count:
    keys = list(all_m.keys())
    if keys and all_m[keys[-1]].get("d") == st.session_state.user:
        has_notif = True
        st.markdown('<audio autoplay><source src="https://www.soundjay.com/buttons/beep-01a.mp3"></audio>', unsafe_allow_html=True)

if st.session_state.user is None:
    st.markdown("<h2 style='text-align:center; color:#FF8C00;'>Connect Class 😊</h2>", unsafe_allow_html=True)
    u = st.text_input("Pseudo").strip()
    p = st.text_input("Mdp", type="password").strip()
    if st.button("SE CONNECTER"):
        if u in data_u and str(data_u[u].get("mdp")) == str(p):
            st.session_state.user = u
            st.rerun()
else:
    me = st.session_state.user
    st.markdown(f"<div class='nav-bar'>🟠 <b>@{me}</b> | Connecté</div>", unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("🏠 LE MUR"): 
            st.session_state.page = "Mur"
            st.rerun()
    with c2:
        div_class = "notif-active" if has_notif else ""
        st.markdown(f"<div class='{div_class}'>", unsafe_allow_html=True)
        if st.button("💬 MESSAGES"):
            st.session_state.page = "Chat"
            st.session_state.last_count = curr_count
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    with c3:
        # Bouton Quitter en rouge pour bien le voir
        st.markdown("<div class='btn-red'>", unsafe_allow_html=True)
        if st.button("🚪 QUITTER"): 
            st.session_state.user = None
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    # --- PAGES ---
    if st.session_state.page == "Mur":
        st.subheader("🌍 Mur Mondial")
        with st.form("mur_post"):
            m_txt = st.text_area("Partage quelque chose...")
            m_img = st.text_input("URL Image")
            if st.form_submit_button("PUBLIER SUR LE MUR 🚀"):
                requests.post(URL_MSG, json={"u": me, "m": m_txt, "i": m_img, "d": "mondial", "t": time.time()})
                st.rerun()
        
        if all_m:
            for k in reversed(list(all_m.keys())):
                v = all_m[k]
                if v.get("d") == "mondial":
                    st.markdown(f"<div class='msg-card'><b>@{v['u']}</b><br>{v.get('m','')}</div>", unsafe_allow_html=True)
                    if v.get("i"): st.image(v["i"], use_container_width=True)

    elif st.session_state.page == "Chat":
        col_l, col_r = st.columns([1, 2])
        with col_l:
            st.write("👥 Amis")
            amis = data_u.get(me, {}).get("amis", {})
            for a in amis:
                is_typing = data_u.get(a, {}).get("typing_to") == me
                label = f"🟢 {a}" if is_typing else f"👤 {a}"
                if st.button(label, key=f"chat_{a}"):
                    st.session_state.chat_target = a
                    st.rerun()
        
        with col_r:
            target = st.session_state.get("chat_target")
            if target:
                st.subheader(f"Chat avec {target}")
                if data_u.get(target, {}).get("typing_to") == me:
                    st.caption(f"💬 {target} est en train d'écrire...")
                
                # Messages
                if all_m:
                    for k, v in all_m.items():
                        if (v.get("u") == me and v.get("d") == target) or (v.get("u") == target and v.get("d") == me):
                            side = "right" if v['u'] == me else "left"
                            bg = "#D32F2F" if side == "right" else "#222"
                            st.markdown(f"<div style='text-align:{side};'><span style='background:{bg}; padding:10px; border-radius:10px; display:inline-block; margin:5px;'>{v['m']}</span></div>", unsafe_allow_html=True)
                
                # Input
                m_in = st.text_input("Message...", key="chat_in")
                # Typing status update
                if m_in: requests.patch(f"{URL_BASE}utilisateurs/{me}.json", json={"typing_to": target})
                else: requests.patch(f"{URL_BASE}utilisateurs/{me}.json", json={"typing_to": ""})
                
                if st.button("ENVOYER 📩"):
                    if m_in:
                        requests.post(URL_MSG, json={"u": me, "m": m_in, "d": target, "t": time.time()})
                        requests.patch(f"{URL_BASE}utilisateurs/{me}.json", json={"typing_to": ""})
                        st.rerun()

# Sync
if st.session_state.user:
    requests.patch(f"{URL_BASE}utilisateurs/{me}.json", json={"last_seen": time.time()})
time.sleep(5)
st.rerun()
