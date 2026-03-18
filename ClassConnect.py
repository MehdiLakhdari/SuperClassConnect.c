import streamlit as st
import requests
import time

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Connect Class Algeria", page_icon="😊", layout="wide")

st.markdown("""
    <style>
    header {visibility: hidden;}
    .stApp { background-color: #0e1117; color: white; }
    
    /* LOGO ORANGE CARRÉ */
    .logo-box {
        background: linear-gradient(135deg, #FF8C00, #FF4500);
        width: 70px; height: 70px; border-radius: 15px;
        display: flex; align-items: center; justify-content: center;
        margin: 0 auto; font-size: 45px; font-weight: bold; color: white;
    }
    .logo-text { font-size: 22px; font-weight: bold; color: #FF8C00; text-align: center; margin: 10px 0; }

    /* BOUTONS NAVIGATION HAUT */
    .nav-bar { background-color: #1c1f26; padding: 10px; border-radius: 10px; margin-bottom: 20px; border-bottom: 3px solid #FF8C00; }

    .stButton>button { 
        background: linear-gradient(90deg, #FF8C00, #FF4500) !important; 
        color: white !important; border-radius: 8px; font-weight: bold; width: 100%; height: 45px;
    }
    .msg-card { background: #1c1f26; padding: 15px; border-radius: 12px; border-left: 5px solid #FF8C00; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

URL_BASE = "https://classconect-f1767-default-rtdb.europe-west1.firebasedatabase.app/"
URL_MSG = f"{URL_BASE}messages.json"
URL_USERS = f"{URL_BASE}utilisateurs.json"

# --- 2. GESTION SESSION ---
if 'user' not in st.session_state: st.session_state.user = None
if 'page' not in st.session_state: st.session_state.page = "Mur"
if 'chat_target' not in st.session_state: st.session_state.chat_target = None

# FONCTION DE CHARGEMENT SANS CACHE POUR ÉVITER LES BUGS
def get_data(url):
    try:
        r = requests.get(url, timeout=5)
        return r.json() if r.status_code == 200 else {}
    except: return {}

# --- 3. INTERFACE ---

if st.session_state.user is None:
    st.markdown("<div class='logo-box'>C</div><div class='logo-text'>Class Connect Algeria 😊</div>", unsafe_allow_html=True)
    t1, t2 = st.tabs(["🔑 CONNEXION", "📝 INSCRIPTION"])
    
    data_u = get_data(URL_USERS)
    
    with t1:
        u = st.text_input("Pseudo", key="l_u")
        p = st.text_input("Mdp", type="password", key="l_p")
        if st.button("SE CONNECTER"):
            if u in data_u and str(data_u[u].get("mdp")) == str(p):
                st.session_state.user = u
                st.rerun()
            else: st.error("Pseudo ou mot de passe incorrect.")
            
    with t2:
        nu = st.text_input("Nouveau Pseudo", key="n_u")
        np = st.text_input("Nouveau Mdp", type="password", key="n_p")
        cl = st.selectbox("Club", ["Paris SG", "Juventus", "Arsenal"])
        if st.button("CRÉER MON COMPTE"):
            if nu and np:
                requests.patch(URL_USERS, json={nu: {"mdp": np, "club": cl, "amis": {}}})
                st.session_state.user = nu
                st.rerun()

else:
    me = st.session_state.user
    # On recharge les données utilisateurs pour avoir les clubs et amis à jour
    data_u = get_data(URL_USERS)
    my_club = data_u.get(me, {}).get("club", "Fan")

    # --- MENU DE NAVIGATION ---
    st.markdown(f"<div class='nav-bar'><h3 style='text-align:center;'>😊 Salut {me} ({my_club})</h3></div>", unsafe_allow_html=True)
    
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        if st.button("🏠 MUR"): st.session_state.page = "Mur"
    with c2:
        if st.button("💬 CHAT"): st.session_state.page = "Chat"
    with c3:
        if st.button("🔄 ACTUALISER"): st.rerun()
    with c4:
        if st.button("🚪 QUITTER"):
            st.session_state.user = None
            st.rerun()

    st.divider()

    # --- PAGES ---
    if st.session_state.page == "Mur":
        col_write, col_view = st.columns([1, 2])
        
        with col_write:
            st.subheader("📝 Publier")
            txt = st.text_area("Ton message...", key="post_txt")
            img = st.text_input("Lien Image (URL)", key="post_img")
            if st.button("POSTER 🚀"):
                if txt or img:
                    requests.post(URL_MSG, json={"u": me, "c": my_club, "m": txt, "i": img, "d": "mondial", "t": time.time()})
                    st.rerun()

        with col_view:
            st.subheader("🌍 Fil d'actualité")
            msgs = get_data(URL_MSG)
            if msgs:
                for k in reversed(list(msgs.keys())):
                    v = msgs[k]
                    if v.get("d") == "mondial":
                        st.markdown(f"<div class='msg-card'><b>{v['u']}</b> ({v.get('c','Fan')})<br>{v.get('m','')}</div>", unsafe_allow_html=True)
                        if v.get("i"): st.image(v["i"], use_container_width=True)

    elif st.session_state.page == "Chat":
        col_list, col_chat = st.columns([1, 2])
        
        with col_list:
            st.subheader("👥 Contacts")
            amis = data_u.get(me, {}).get("amis", {})
            if amis:
                for a in amis:
                    if st.button(f"👤 {a}", key=f"btn_{a}"):
                        st.session_state.chat_target = a
                        st.rerun()
            
            new_f = st.text_input("Ajouter un pseudo")
            if st.button("Ajouter"):
                if new_f in data_u and new_f != me:
                    requests.patch(f"{URL_BASE}utilisateurs/{me}/amis.json", json={new_f: True})
                    st.rerun()

        with col_chat:
            target = st.session_state.chat_target
            if target:
                st.subheader(f"Chat avec {target}")
                msgs = get_data(URL_MSG)
                if msgs:
                    for k, v in msgs.items():
                        if (v.get("u") == me and v.get("d") == target) or (v.get("u") == target and v.get("d") == me):
                            side = "right" if v['u'] == me else "left"
                            color = "#FF8C00" if v['u'] == me else "#333"
                            st.markdown(f"<div style='text-align:{side};'><span style='background:{color}; padding:10px; border-radius:10px; display:inline-block; margin:5px;'>{v['m']}</span></div>", unsafe_allow_html=True)
                
                m_in = st.text_input("Écrire...", key="chat_msg")
                if st.button("ENVOYER"):
                    if m_in:
                        requests.post(URL_MSG, json={"u": me, "m": m_in, "d": target, "t": time.time()})
                        st.rerun()
            else:
                st.info("Choisis un ami à gauche pour discuter.")

# SUPPRESSION DU AUTO-REFRESH QUI CRÉE LE LAG ET LE NOIR
# L'utilisateur doit cliquer sur "ACTUALISER" pour voir les nouveaux messages.
