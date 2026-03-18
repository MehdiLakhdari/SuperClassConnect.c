import streamlit as st
import requests
import time

# --- 1. CONFIGURATION 😊 ---
st.set_page_config(page_title="Connect Class", page_icon="😊", layout="wide")

st.markdown("""
    <style>
    header {visibility: hidden;}
    .stApp { background-color: #0e1117; color: white; }
    .logo-box {
        background: linear-gradient(135deg, #FF8C00, #FF4500);
        width: 60px; height: 60px; border-radius: 12px;
        display: flex; align-items: center; justify-content: center;
        margin: 0 auto; font-size: 35px; font-weight: bold; color: white;
    }
    .notif-badge {
        background-color: #FF0000; color: white; padding: 2px 8px;
        border-radius: 10px; font-size: 14px; margin-left: 10px; font-weight: bold;
    }
    .stButton>button { 
        background: linear-gradient(90deg, #FF8C00, #FF4500) !important; 
        color: white !important; border-radius: 10px; font-weight: bold; width: 100%; height: 50px;
    }
    .msg-card { background: #1c1f26; padding: 15px; border-radius: 12px; border-left: 5px solid #FF8C00; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

URL_BASE = "https://classconect-f1767-default-rtdb.europe-west1.firebasedatabase.app/"
URL_MSG = f"{URL_BASE}messages.json"
URL_USERS = f"{URL_BASE}utilisateurs.json"

# --- 2. SESSION & NOTIFS ---
if 'user' not in st.session_state: st.session_state.user = None
if 'page' not in st.session_state: st.session_state.page = "Mur"
if 'chat_target' not in st.session_state: st.session_state.chat_target = None
if 'last_read' not in st.session_state: st.session_state.last_read = time.time()

def get_db(url):
    try:
        r = requests.get(url, timeout=5)
        return r.json() if r.status_code == 200 else {}
    except: return {}

# --- 3. INTERFACE ---

data_u = get_db(URL_USERS)
all_m = get_db(URL_MSG)

if st.session_state.user is None:
    st.markdown("<div class='logo-box'>C</div><h3 style='text-align:center;'>Class Connect Algeria 😊</h3>", unsafe_allow_html=True)
    t1, t2 = st.tabs(["Connexion", "Inscription"])
    with t1:
        u = st.text_input("Pseudo", key="l_u")
        p = st.text_input("Mdp", type="password", key="l_p")
        if st.button("SE CONNECTER"):
            if u in data_u and str(data_u[u].get("mdp")) == str(p):
                st.session_state.user = u
                st.session_state.last_read = time.time()
                st.rerun()
else:
    me = st.session_state.user
    
    # CALCUL DES NOTIFS (Messages pour MOI arrivés après ma dernière lecture)
    new_msg_count = 0
    if all_m:
        for k, v in all_m.items():
            if v.get("d") == me and v.get("t", 0) > st.session_state.last_read:
                new_msg_count += 1

    # BARRE DE NAVIGATION AVEC NOTIFS
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("🏠 MUR"): 
            st.session_state.page = "Mur"
            st.rerun()
    with c2:
        btn_label = f"💬 CHAT 🔴 ({new_msg_count})" if new_msg_count > 0 else "💬 CHAT"
        if st.button(btn_label): 
            st.session_state.page = "Chat"
            st.session_state.last_read = time.time() # On marque comme lu
            st.rerun()
    with c3:
        if st.button("🚪 QUITTER"):
            st.session_state.user = None
            st.rerun()

    st.divider()

    # --- PAGES ---
    if st.session_state.page == "Mur":
        st.subheader("🌍 Mur Mondial")
        with st.expander("📝 Nouveau Post"):
            txt = st.text_area("Légende")
            img = st.text_input("Lien Image (URL)")
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
        col_f, col_c = st.columns([1, 2])
        with col_f:
            st.subheader("👥 Amis")
            amis = data_u.get(me, {}).get("amis", {})
            for a in amis:
                if st.button(f"👤 {a}", key=f"a_{a}"):
                    st.session_state.chat_target = a
                    st.rerun()
            
            st.divider()
            nf = st.text_input("Ajouter pseudo").strip()
            if st.button("AJOUTER"):
                if nf in data_u and nf != me:
                    requests.patch(f"{URL_BASE}utilisateurs/{me}/amis.json", json={nf: True})
                    st.rerun()

        with col_c:
            target = st.session_state.chat_target
            if target:
                st.subheader(f"Chat avec {target}")
                if all_m:
                    for k, v in all_m.items():
                        if (v.get("u") == me and v.get("d") == target) or (v.get("u") == target and v.get("d") == me):
                            side = "right" if v['u'] == me else "left"
                            st.markdown(f"<div style='text-align:{side};'><span style='background:{'#FF8C00' if side=='right' else '#333'}; padding:8px; border-radius:10px; display:inline-block; margin:5px;'>{v['m']}</span></div>", unsafe_allow_html=True)
                
                m_i = st.text_input("Message...", key="chat_in")
                if st.button("ENVOYER"):
                    requests.post(URL_MSG, json={"u": me, "m": m_i, "d": target, "t": time.time()})
                    st.rerun()
