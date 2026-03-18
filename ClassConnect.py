import streamlit as st
import requests
import time

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Connect Class", page_icon="😊", layout="wide")

st.markdown("""
    <style>
    header {visibility: hidden;}
    .stApp { background-color: #050505; color: white; }
    .logo-box {
        background: linear-gradient(135deg, #FF8C00, #FF4500);
        width: 60px; height: 60px; border-radius: 12px;
        display: flex; align-items: center; justify-content: center;
        margin: 0 auto; font-size: 35px; font-weight: bold; color: white;
    }
    .status-online { color: #00FF00; font-size: 20px; }
    .status-offline { color: #555; font-size: 20px; }
    .nav-bar { background: #111; padding: 10px; border-radius: 10px; border-bottom: 3px solid #D32F2F; margin-bottom: 20px; }
    .stButton>button { 
        background: linear-gradient(90deg, #D32F2F, #8B0000) !important; 
        color: white !important; border-radius: 8px; font-weight: bold; height: 45px;
    }
    .msg-card { background: #111; padding: 15px; border-radius: 10px; border-left: 5px solid #D32F2F; margin-bottom: 10px; }
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

# --- 2. SYSTÈME DE PRÉSENCE (Point Vert) ---
def update_presence(user):
    if user:
        requests.patch(f"{URL_BASE}utilisateurs/{user}.json", json={"last_seen": time.time()})

# --- 3. NOTIFICATION SONORE ---
def play_notif():
    st.markdown('<audio autoplay><source src="https://www.soundjay.com/buttons/beep-01a.mp3"></audio>', unsafe_allow_html=True)

# --- 4. INTERFACE ---
data_u = get_db(URL_USERS)
all_m = get_db(URL_MSG)

# Vérif nouveaux messages pour le SON
curr_m = len(all_m) if all_m else 0
if st.session_state.user and curr_m > st.session_state.last_count:
    # On vérifie si le dernier message est pour l'utilisateur
    last_key = list(all_m.keys())[-1]
    if all_m[last_key].get("d") == st.session_state.user:
        play_notif()
st.session_state.last_count = curr_m

if st.session_state.user is None:
    st.markdown("<div class='logo-box'>C</div><h2 style='text-align:center;'>Class Connect 😊</h2>", unsafe_allow_html=True)
    t1, t2 = st.tabs(["🔴 CONNEXION", "⚪ REJOINDRE"])
    with t1:
        u = st.text_input("Pseudo").strip()
        p = st.text_input("Mdp", type="password").strip()
        if st.button("ENTRER"):
            if u in data_u and str(data_u[u].get("mdp")) == str(p):
                st.session_state.user = u
                update_presence(u)
                st.rerun()
else:
    me = st.session_state.user
    update_presence(me) # On dit au serveur qu'on est en ligne
    
    # NAVIGATION HAUT
    st.markdown(f"<div class='nav-bar'><b>@{me}</b> | Connecté 😊</div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("🏠 MUR"): st.session_state.page = "Mur" ; st.rerun()
    with c2:
        if st.button("💬 MESSAGES"): st.session_state.page = "Chat" ; st.rerun()
    with c3:
        if st.button("🚪 QUITTER"): st.session_state.user = None ; st.rerun()

    # PAGES
    if st.session_state.page == "Mur":
        st.subheader("🌍 Fil d'actualité")
        with st.form("post_form", clear_on_submit=True):
            txt = st.text_area("Exprime-toi...")
            img = st.text_input("Lien Image (URL)")
            if st.form_submit_button("PUBLIER 🚀"):
                requests.post(URL_MSG, json={"u": me, "m": txt, "i": img, "d": "mondial", "t": time.time()})
                st.rerun()
        
        if all_m:
            for k in reversed(list(all_m.keys())):
                v = all_m[k]
                if v.get("d") == "mondial":
                    st.markdown(f"<div class='msg-card'><b>@{v['u']}</b><br>{v.get('m','')}</div>", unsafe_allow_html=True)
                    if v.get("i"): st.image(v["i"], use_container_width=True)

    elif st.session_state.page == "Chat":
        col_friends, col_conv = st.columns([1, 2])
        with col_friends:
            st.write("👥 **Amis**")
            amis = data_u.get(me, {}).get("amis", {})
            if amis:
                for a in amis:
                    # VERIFICATION POINT VERT (Actif il y a moins de 2 min)
                    last_seen = data_u.get(a, {}).get("last_seen", 0)
                    is_online = "🟢" if (time.time() - last_seen) < 120 else "⚪"
                    if st.button(f"{is_online} {a}", key=f"chat_{a}"):
                        st.session_state.chat_target = a
                        st.rerun()
            
            nf = st.text_input("Pseudo de l'ami").strip()
            if st.button("AJOUTER"):
                if nf in data_u:
                    requests.patch(f"{URL_BASE}utilisateurs/{me}/amis.json", json={nf: True})
                    st.rerun()

        with col_conv:
            target = st.session_state.get("chat_target")
            if target:
                st.subheader(f"Chat avec {target}")
                # Affichage messages
                if all_m:
                    for k, v in all_m.items():
                        if (v.get("u") == me and v.get("d") == target) or (v.get("u") == target and v.get("d") == me):
                            side = "right" if v['u'] == me else "left"
                            color = "#D32F2F" if side == "right" else "#222"
                            st.markdown(f"<div style='text-align:{side};'><span style='background:{color}; padding:8px; border-radius:10px; display:inline-block; margin:5px;'>{v['m']}</span></div>", unsafe_allow_html=True)
                
                with st.form("chat_form", clear_on_submit=True):
                    m_in = st.text_input("Message...")
                    if st.form_submit_button("ENVOYER 📩"):
                        requests.post(URL_MSG, json={"u": me, "m": m_in, "d": target, "t": time.time()})
                        st.rerun()

# ACTUALISATION AUTO (Plus lent pour éviter le lag noir)
time.sleep(5)
st.rerun()
