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
if 'user_club' not in st.session_state: st.session_state.user_club = None

# --- 3. DESIGN ORANGE DÉGRADÉ & CLUBS ---
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: white; }
    
    /* Nouveau Logo CC Carré Orange Dégradé */
    .logo-container { text-align: center; margin-bottom: 20px; }
    .logo-box {
        background: linear-gradient(135deg, #FF8C00, #FF4500);
        width: 80px; height: 80px; border-radius: 15px;
        display: flex; align-items: center; justify-content: center;
        margin: 0 auto; font-size: 50px; font-weight: bold; color: white;
        box-shadow: 0 4px 15px rgba(255, 69, 0, 0.4);
    }
    .logo-text { font-size: 24px; font-weight: bold; color: white; margin-top: 10px; }

    /* Boutons et Inputs */
    .stButton>button { 
        background: linear-gradient(90deg, #FF8C00, #FF4500) !important; 
        color: white !important; border-radius: 10px; border: none; font-weight: bold; height: 50px; 
    }
    
    /* Styles des Clubs */
    .club-tag { padding: 5px 10px; border-radius: 5px; font-weight: bold; font-size: 12px; }
    .psg { background-color: #001C3F; color: white; border: 1px solid #E30613; }
    .juve { background-color: white; color: black; border: 1px solid black; }
    .arsenal { background-color: #EF0107; color: white; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. FONCTIONS ---
@st.cache_data(ttl=5) # Cache de 5 secondes pour réduire le lag
def charger(url):
    try:
        r = requests.get(url)
        return r.json() if r.status_code == 200 and r.json() else {}
    except: return {}

data_u = charger(URL_USERS)

# --- 5. INTERFACE ---

if st.session_state.user is None:
    # --- LOGO ---
    st.markdown("""
        <div class='logo-container'>
            <div class='logo-box'>C</div>
            <div class='logo-text'>Class Connect Algeria</div>
        </div>
    """, unsafe_allow_html=True)

    t1, t2 = st.tabs(["Connexion", "Créer un Compte"])
    
    with t1:
        u = st.text_input("Pseudo", key="l_u")
        p = st.text_input("Mdp", type="password", key="l_p")
        if st.button("SE CONNECTER"):
            if u in data_u and str(data_u[u].get("mdp")) == str(p):
                st.session_state.user = u
                st.session_state.user_club = data_u[u].get("club", "Aucun")
                st.rerun()
            else: st.error("Pseudo ou mot de passe faux")

    with t2:
        nu = st.text_input("Ton Pseudo Unique", key="n_u")
        np = st.text_input("Ton Mot de Passe", type="password", key="n_p")
        
        st.write("⚽ **Choisis ton Club :**")
        club_choice = st.radio("Sélectionne une équipe", ["Paris Saint-Germain", "Juventus Turin", "Arsenal FC"], horizontal=True)
        
        if st.button("CRÉER MON COMPTE"):
            if nu in data_u:
                st.error("Ce pseudo existe déjà !")
            elif len(nu) < 3 or len(np) < 4:
                st.warning("Pseudo ou MDP trop court !")
            else:
                # Sauvegarde avec le club
                requests.patch(URL_USERS, json={nu: {"mdp": np, "club": club_choice, "pfp": ""}})
                st.success(f"Compte créé pour {nu} !")
                # AUTO-LOGIN DIRECT
                st.session_state.user = nu
                st.session_state.user_club = club_choice
                st.balloons()
                time.sleep(1)
                st.rerun()

else:
    # --- INTERFACE CONNECTÉE ---
    me = st.session_state.user
    mon_club = st.session_state.user_club
    
    with st.sidebar:
        st.markdown("<div class='logo-box' style='width:60px; height:60px; font-size:35px;'>C</div>", unsafe_allow_html=True)
        st.write(f"💼 **{me}**")
        
        # Affichage du Club dans la sidebar
        c_class = "psg" if "Paris" in mon_club else "juve" if "Juventus" in mon_club else "arsenal"
        st.markdown(f"<span class='club-tag {c_class}'>{mon_club}</span>", unsafe_allow_html=True)
        
        st.divider()
        if st.button("🏠 Mur Mondial"): st.session_state.page = "🏠 Mur Mondial"
        if st.button("💬 Messages Privés"): st.session_state.page = "💬 Messages Privés"
        st.divider()
        if st.button("🚪 Déconnexion"):
            st.session_state.user = None
            st.rerun()

    # --- PAGES ---
    if st.session_state.page == "🏠 Mur Mondial":
        st.title("🏠 Mur Mondial")
        with st.expander("📝 Publier"):
            txt = st.text_area("Ton message")
            if st.button("POSTER"):
                requests.post(URL_MSG, json={"u": me, "c": mon_club, "m": txt, "d": "mondial", "t": time.time()})
                st.rerun()
        
        msgs = charger(URL_MSG)
        if msgs:
            for k in reversed(list(msgs.keys())):
                v = msgs[k]
                if v.get("d") == "mondial":
                    c_v = "psg" if "Paris" in v.get('c','') else "juve" if "Juventus" in v.get('c','') else "arsenal"
                    st.markdown(f"""
                        <div style='background:#1e1e1e; padding:15px; border-radius:10px; margin-bottom:10px;'>
                            <span class='club-tag {c_v}'>{v.get('c','Fans')}</span> <b>{v['u']}</b><br>
                            <p style='margin-top:5px;'>{v['m']}</p>
                        </div>
                    """, unsafe_allow_html=True)

    elif st.session_state.page == "💬 Messages Privés":
        st.title("💬 Messages")
        target = st.text_input("Chercher un pseudo")
        if target:
            st.write(f"Discussion avec **{target}**")
            # Système de chat simplifié ici
            msg_in = st.text_input("Écrire...", key="chat_in")
            if st.button("ENVOYER"):
                requests.post(URL_MSG, json={"u": me, "m": msg_in, "d": target, "t": time.time()})
                st.rerun()

# Réduction du temps de rafraîchissement pour éviter le lag
time.sleep(5)
st.rerun()
