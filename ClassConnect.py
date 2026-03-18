import streamlit as st
import requests
import time

# --- 1. CONFIGURATION ÉCRAN TOTAL ---
st.set_page_config(page_title="Connect Class Algeria", page_icon="😊", layout="wide")

# CSS BLINDÉ POUR CACHER REPLIT ET BOOSTER LE MOBILE
st.markdown("""
    <style>
    header {visibility: hidden;}
    [data-testid="stSidebar"] {visibility: hidden; width: 0;} /* Cacher sidebar au cas où */
    .stApp { background-color: #0e1117; color: white; }
    
    /* LOGO CC ORANGE */
    .logo-box {
        background: linear-gradient(135deg, #FF8C00, #FF4500);
        width: 65px; height: 65px; border-radius: 12px;
        display: flex; align-items: center; justify-content: center;
        margin: 0 auto; font-size: 38px; font-weight: bold; color: white;
    }
    
    /* BARRE DE NAVIGATION EN COLONNES (Style Mobile App) */
    .nav-btn {
        background: linear-gradient(90deg, #FF8C00, #FF4500) !important;
        color: white !important;
        border-radius: 10px;
        font-weight: bold;
        width: 100%; height: 45px;
        border: none;
    }

    /* CARTES DU MUR AVEC IMAGES */
    .msg-card { 
        background: #1c1f26; 
        padding: 15px; 
        border-radius: 12px; 
        border-left: 5px solid #FF8C00; 
        margin-bottom: 10px; 
    }
    </style>
    """, unsafe_allow_html=True)

URL_BASE = "https://classconect-f1767-default-rtdb.europe-west1.firebasedatabase.app/"
URL_MSG = f"{URL_BASE}messages.json"
URL_USERS = f"{URL_BASE}utilisateurs.json"

# --- 2. GESTION DE LA SESSION ---
if 'user' not in st.session_state: st.session_state.user = None
if 'page' not in st.session_state: st.session_state.page = "Mur"
if 'chat_target' not in st.session_state: st.session_state.chat_target = None

# FONCTION DE CHARGEMENT ULTRA-RAPIDE SANS CACHE
def get_data(url):
    try:
        r = requests.get(url, timeout=4)
        return r.json() if r.status_code == 200 else {}
    except: return {}

# --- 3. INTERFACE ---

if st.session_state.user is None:
    # --- PAGE D'ACCUEIL ---
    st.markdown("<div class='logo-box'>C</div><h3 style='text-align:center;'>Class Connect Algeria 😊</h3>", unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["🔑 CONNEXION", "📝 S'INSCRIRE"])
    
    data_u = get_data(URL_USERS)
    
    with tab1:
        u_in = st.text_input("Pseudo exact", key="login_u")
        p_in = st.text_input("Mot de passe", type="password", key="login_p")
        if st.button("SE CONNECTER", key="btn_login"):
            if u_in in data_u and str(data_u[u_in].get("mdp")) == str(p_in):
                st.session_state.user = u_in
                st.balloons()
                st.rerun()
            else: st.error("Pseudo ou Mdp incorrect.")
            
    with tab2:
        nu = st.text_input("Nouveau Pseudo", key="new_u")
        np = st.text_input("Nouveau Mdp", type="password", key="new_p")
        cl = st.selectbox("Club", ["Paris SG", "Juventus", "Arsenal"])
        if st.button("CRÉER COMPTE & ENTRER", key="btn_reg"):
            if nu and np:
                requests.patch(URL_USERS, json={nu: {"mdp": np, "club": cl, "amis": {}}})
                st.session_state.user = nu
                st.balloons()
                st.rerun()

else:
    # --- INTERFACE CONNECTÉE ---
    me = st.session_state.user
    data_u = get_data(URL_USERS)
    my_club = data_u.get(me, {}).get("club", "Fan")

    # BARRE DE NAVIGATION STYLE APP MOBILE (3 Colonnes)
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("🏠 MUR", key="nav_mur"): 
            st.session_state.page = "Mur"
            st.rerun()
    with c2:
        if st.button("💬 CHAT", key="nav_chat"): 
            st.session_state.page = "Chat"
            st.rerun()
    with c3:
        if st.button("🚪 QUITTER", key="nav_quit"):
            st.session_state.user = None
            st.rerun()

    st.divider()

    # --- PAGES ---
    if st.session_state.page == "Mur":
        col_form, col_feed = st.columns([1, 2])
        
        with col_form:
            st.subheader("📝 Publier")
            txt = st.text_area("Légende", key="post_txt")
            img = st.text_input("URL de l'image (ImgBB, etc.)", key="post_img")
            if st.button("POSTER 🚀", key="btn_post"):
                if txt or img:
                    requests.post(URL_MSG, json={"u": me, "c": my_club, "m": txt, "i": img, "d": "mondial", "t": time.time()})
                    st.success("Posté ! Actualisation...")
                    time.sleep(0.5)
                    st.rerun() # FORCER L'ACTUALISATION

        with col_feed:
            st.subheader("🌍 Mur Mondial")
            msgs = get_data(URL_MSG)
            if msgs:
                for k in reversed(list(msgs.keys())):
                    v = msgs[k]
                    if v.get("d") == "mondial":
                        st.markdown(f"<div class='msg-card'><b>@{v['u']}</b> ({v.get('c','Fan')})<br>{v.get('m','')}</div>", unsafe_allow_html=True)
                        if v.get("i"):
                            st.image(v["i"], use_container_width=True)

    elif st.session_state.page == "Chat":
        col_list, col_conv = st.columns([1, 2])
        
        with col_list:
            st.subheader("👥 Mes Contacts")
            amis = data_u.get(me, {}).get("amis", {})
            if amis:
                for a in amis:
                    if st.button(f"👤 {a}", key=f"ami_{a}"):
                        st.session_state.chat_target = a
                        st.rerun()
            
            # --- AJOUTER UN AMI (LE VOILÀ RÉGLÉ !) ---
            st.divider()
            new_f = st.text_input("Pseudo exact de l'ami", key="input_add_friend").strip()
            if st.button("AJOUTER AMI 👤+", key="btn_add_friend"):
                if new_f in data_u and new_f != me:
                    # Sauvegarde l'ami dans Firebase
                    requests.patch(f"{URL_BASE}utilisateurs/{me}/amis.json", json={new_f: True})
                    st.success(f"{new_f} ajouté ! Actualisation...")
                    time.sleep(0.5)
                    st.rerun() # FORCER ACTUALISATION POUR VOIR L'AMI
                else:
                    st.error("Pseudo introuvable ou c'est toi.")

        with col_conv:
            target = st.session_state.chat_target
            if target:
                st.subheader(f"Discussion avec {target}")
                msgs = get_data(URL_MSG)
                if msgs:
                    for k, v in msgs.items():
                        if (v.get("u") == me and v.get("d") == target) or (v.get("u") == target and v.get("d") == me):
                            side = "right" if v['u'] == me else "left"
                            color = "#FF8C00" if v['u'] == me else "#333"
                            st.markdown(f"<div style='text-align:{side};'><span style='background:{color}; padding:8px; border-radius:10px; display:inline-block; margin:5px;'>{v['m']}</span></div>", unsafe_allow_html=True)
                
                # --- ENVOI DE MESSAGE ---
                m_in = st.text_input("Ton message...", key="input_chat_msg")
                if st.button("ENVOYER 📩", key="btn_send_chat"):
                    if m_in:
                        requests.post(URL_MSG, json={"u": me, "m": m_in, "d": target, "t": time.time()})
                        st.rerun() # FORCER ACTUALISATION POUR VOIR LE MESSAGE
            else:
                st.info("Choisis un contact à gauche pour discuter.")

# --- ACTUALISATION MANUELLE (LE SEUL MOYEN ANTI-LAG NOIR) ---
if st.session_state.user:
    st.divider()
    col_actu1, col_actu2, col_actu3 = st.columns([1,1,1])
    with col_actu2:
        if st.button("🔄 ACTUALISER TOUT", key="btn_actu_all"):
            st.rerun()
