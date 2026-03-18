import streamlit as st
import requests
import time
import webbrowser

# --- 1. CONFIGURATION 😊 ---
st.set_page_config(page_title="Connect Class Algeria", page_icon="😊", layout="wide")

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
    .nav-bar { background: #111; padding: 10px; border-radius: 10px; border-bottom: 3px solid #D32F2F; margin-bottom: 20px; text-align:center; }
    .stButton>button { 
        background: linear-gradient(90deg, #D32F2F, #8B0000) !important; 
        color: white !important; border-radius: 8px; font-weight: bold; height: 45px;
    }
    /* Bouton Appel Spécial */
    .btn-call>button {
        background: linear-gradient(90deg, #28a745, #1e7e34) !important;
        border: none !important;
    }
    .msg-card { background: #111; padding: 15px; border-radius: 10px; border-left: 5px solid #D32F2F; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

URL_BASE = "https://classconect-f1767-default-rtdb.europe-west1.firebasedatabase.app/"
URL_MSG = f"{URL_BASE}messages.json"
URL_USERS = f"{URL_BASE}utilisateurs.json"

if 'user' not in st.session_state: st.session_state.user = None
if 'page' not in st.session_state: st.session_state.page = "Mur"

def get_db(url):
    try:
        r = requests.get(url, timeout=5)
        return r.json() if r.status_code == 200 else {}
    except: return {}

# --- 2. PRÉSENCE & SON ---
def update_presence(user):
    if user: requests.patch(f"{URL_BASE}utilisateurs/{user}.json", json={"last_seen": time.time()})

def play_notif():
    st.markdown('<audio autoplay><source src="https://www.soundjay.com/buttons/beep-01a.mp3"></audio>', unsafe_allow_html=True)

# --- 3. INTERFACE ---
data_u = get_db(URL_USERS)
all_m = get_db(URL_MSG)

if st.session_state.user is None:
    st.markdown("<div class='logo-box'>C</div><h2 style='text-align:center;'>Connect Class 😊</h2>", unsafe_allow_html=True)
    t1, t2 = st.tabs(["🔴 CONNEXION", "⚪ REJOINDRE"])
    with t1:
        u = st.text_input("Pseudo").strip()
        p = st.text_input("Mdp", type="password").strip()
        if st.button("LANCER LA SESSION"):
            if u in data_u and str(data_u[u].get("mdp")) == str(p):
                st.session_state.user = u
                update_presence(u)
                st.rerun()
else:
    me = st.session_state.user
    update_presence(me)
    
    st.markdown(f"<div class='nav-bar'>🔥 <b>Connecté : @{me}</b></div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("🏠 LE MUR"): st.session_state.page = "Mur" ; st.rerun()
    with c2:
        if st.button("💬 MESSAGES"): st.session_state.page = "Chat" ; st.rerun()
    with c3:
        if st.button("🚪 QUITTER"): st.session_state.user = None ; st.rerun()

    if st.session_state.page == "Mur":
        st.subheader("🌍 Fil d'actualité")
        with st.form("p_form", clear_on_submit=True):
            txt = st.text_area("Quoi de neuf ?")
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
        col_f, col_c = st.columns([1, 2])
        with col_f:
            st.write("👥 **Amis**")
            amis = data_u.get(me, {}).get("amis", {})
            if amis:
                for a in amis:
                    last_seen = data_u.get(a, {}).get("last_seen", 0)
                    is_online = "🟢" if (time.time() - last_seen) < 120 else "⚪"
                    if st.button(f"{is_online} {a}", key=f"c_{a}"):
                        st.session_state.chat_target = a
                        st.rerun()
            
            nf = st.text_input("Nouveau pseudo").strip()
            if st.button("➕ AJOUTER"):
                if nf in data_u:
                    requests.patch(f"{URL_BASE}utilisateurs/{me}/amis.json", json={nf: True})
                    st.rerun()

        with col_c:
            target = st.session_state.get("chat_target")
            if target:
                # HEADER CHAT AVEC BOUTON APPEL
                head1, head2 = st.columns([2, 1])
                with head1: st.subheader(f"Chat avec {target}")
                with head2:
                    # LIEN D'APPEL UNIQUE ENTRE LES DEUX UTILISATEURS
                    room_id = "".join(sorted([me, target]))
                    call_url = f"https://meet.jit.si/ConnectClass_{room_id}"
                    st.markdown(f'<a href="{call_url}" target="_blank"><button style="background-color:#28a745; color:white; border:none; padding:10px; border-radius:5px; width:100%; cursor:pointer; font-weight:bold;">📞 APPEL VIDÉO</button></a>', unsafe_allow_html=True)
                
                if all_m:
                    for k, v in all_m.items():
                        if (v.get("u") == me and v.get("d") == target) or (v.get("u") == target and v.get("d") == me):
                            side = "right" if v['u'] == me else "left"
                            color = "#D32F2F" if side == "right" else "#222"
                            st.markdown(f"<div style='text-align:{side};'><span style='background:{color}; padding:8px; border-radius:10px; display:inline-block; margin:5px;'>{v['m']}</span></div>", unsafe_allow_html=True)
                
                with st.form("c_form", clear_on_submit=True):
                    m_i = st.text_input("Message...")
                    if st.form_submit_button("ENVOYER 📩"):
                        requests.post(URL_MSG, json={"u": me, "m": m_i, "d": target, "t": time.time()})
                        st.rerun()

# --- RECHARGEMENT ---
time.sleep(10)
st.rerun()
