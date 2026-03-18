import streamlit as st
import requests
import time

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Connect Class Algeria", page_icon="😊", layout="wide")

st.markdown("""
    <style>
    header {visibility: hidden;}
    .stApp { background-color: #050505; color: #ffffff; }
    
    /* LOGO ORANGE CC */
    .logo-box {
        background: linear-gradient(135deg, #FF8C00, #FF4500);
        width: 55px; height: 55px; border-radius: 10px;
        display: flex; align-items: center; justify-content: center;
        margin: 0 auto; font-size: 30px; font-weight: bold; color: white;
    }

    /* MENU DE NAVIGATION VISIBLE (Remplace la Sidebar) */
    .nav-bar {
        background-color: #111;
        padding: 10px;
        border-radius: 10px;
        border: 2px solid #D32F2F;
        margin-bottom: 20px;
        text-align: center;
    }

    /* BOUTONS ROUGE SANG */
    .stButton>button { 
        background: linear-gradient(90deg, #D32F2F, #8B0000) !important; 
        color: white !important; border-radius: 8px; font-weight: bold; 
        width: 100%; border: none; height: 45px;
    }
    .stButton>button:hover { box-shadow: 0 0 15px #FF0000; }

    /* CARTES MESSAGES */
    .msg-card { 
        background: #111; padding: 15px; border-radius: 10px; 
        border-left: 5px solid #D32F2F; margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

URL_BASE = "https://classconect-f1767-default-rtdb.europe-west1.firebasedatabase.app/"
URL_MSG = f"{URL_BASE}messages.json"
URL_USERS = f"{URL_BASE}utilisateurs.json"

if 'user' not in st.session_state: st.session_state.user = None
if 'page' not in st.session_state: st.session_state.page = "Mur"
if 'last_read' not in st.session_state: st.session_state.last_read = time.time()

def get_db(url):
    try:
        r = requests.get(url, timeout=5)
        return r.json() if r.status_code == 200 else {}
    except: return {}

# --- 2. INTERFACE ---

data_u = get_db(URL_USERS)
all_m = get_db(URL_MSG)

if st.session_state.user is None:
    st.markdown("<div class='logo-box'>C</div><h3 style='text-align:center; color:#FF8C00;'>Class Connect Algeria</h3>", unsafe_allow_html=True)
    t1, t2 = st.tabs(["🔴 CONNEXION", "⚪ INSCRIPTION"])
    with t1:
        u = st.text_input("Pseudo", key="l_u").strip()
        p = st.text_input("Mdp", type="password", key="l_p").strip()
        if st.button("ENTRER"):
            if u in data_u and str(data_u[u].get("mdp")) == str(p):
                st.session_state.user = u
                st.rerun()
    with t2:
        nu = st.text_input("Nouveau Pseudo").strip()
        np = st.text_input("Nouveau Mdp", type="password").strip()
        if st.button("CRÉER COMPTE"):
            if nu and np:
                requests.patch(URL_USERS, json={nu: {"mdp": np, "club": "Fan", "amis": {}}})
                st.session_state.user = nu
                st.rerun()

else:
    me = st.session_state.user
    
    # --- LA BARRE DE NAVIGATION (FIXE ET VISIBLE) ---
    st.markdown(f"<div class='nav-bar'><b>@{me}</b> | Connecté 😊</div>", unsafe_allow_html=True)
    
    col_nav1, col_nav2, col_nav3 = st.columns(3)
    
    # Calcul notifs Sofia/Amis
    new_count = 0
    if all_m:
        for k, v in all_m.items():
            if v.get("d") == me and v.get("t", 0) > st.session_state.last_read:
                new_count += 1

    with col_nav1:
        if st.button("🏠 MUR"): st.session_state.page = "Mur" ; st.rerun()
    with col_nav2:
        notif_label = f"💬 MESSAGES ({new_count}) 🔴" if new_count > 0 else "💬 MESSAGES"
        if st.button(notif_label): 
            st.session_state.page = "Chat"
            st.session_state.last_read = time.time()
            st.rerun()
    with col_nav3:
        if st.button("🚪 QUITTER"): st.session_state.user = None ; st.rerun()

    st.divider()

    # --- PAGES ---
    if st.session_state.page == "Mur":
        st.subheader("🌍 Mur Mondial")
        with st.expander("📝 Poster un message"):
            txt = st.text_area("Ton texte...")
            img = st.text_input("URL de l'image")
            if st.button("PUBLIER 🚀"):
                requests.post(URL_MSG, json={"u": me, "m": txt, "i": img, "d": "mondial", "t": time.time()})
                st.rerun()
        
        if all_m:
            for k in reversed(list(all_m.keys())):
                v = all_m[k]
                if v.get("d") == "mondial":
                    st.markdown(f"<div class='msg-card'><b>@{v['u']}</b><br>{v.get('m','')}</div>", unsafe_allow_html=True)
                    if v.get("i"): st.image(v["i"], use_container_width=True)

    elif st.session_state.page == "Chat":
        col_list, col_conv = st.columns([1, 2])
        with col_list:
            st.subheader("👥 Amis")
            amis = data_u.get(me, {}).get("amis", {})
            for a in amis:
                if st.button(f"👤 {a}", key=f"f_{a}"):
                    st.session_state.chat_target = a
                    st.rerun()
            
            st.divider()
            nf = st.text_input("Ajouter pseudo").strip()
            if st.button("AJOUTER 👤+"):
                if nf in data_u and nf != me:
                    requests.patch(f"{URL_BASE}utilisateurs/{me}/amis.json", json={nf: True})
                    st.rerun()

        with col_conv:
            target = st.session_state.get("chat_target")
            if target:
                st.subheader(f"Chat avec {target}")
                if all_m:
                    for k, v in all_m.items():
                        if (v.get("u") == me and v.get("d") == target) or (v.get("u") == target and v.get("d") == me):
                            side = "right" if v['u'] == me else "left"
                            color = "#D32F2F" if side == "right" else "#222"
                            st.markdown(f"<div style='text-align:{side};'><span style='background:{color}; padding:8px; border-radius:10px; display:inline-block; margin:5px;'>{v['m']}</span></div>", unsafe_allow_html=True)
                
                m_in = st.text_input("Message...", key="in_chat")
                if st.button("ENVOYER 📩"):
                    requests.post(URL_MSG, json={"u": me, "m": m_in, "d": target, "t": time.time()})
                    st.rerun()

# --- ACTUALISATION ---
time.sleep(10)
st.rerun()
