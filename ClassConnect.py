import streamlit as st
import requests
import time

# --- 1. CONFIGURATION PLEIN ÉCRAN ---
st.set_page_config(page_title="Connect Class Algeria", page_icon="⚽", layout="wide")

# --- 2. CACHER TOUT LE SUPERFLU (REPLIT/STREAMLIT) ---
st.markdown("""
    <style>
    header {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stApp { background-color: #0e1117; color: white; }
    
    /* LOGO ORANGE DÉGRADÉ PRO */
    .logo-box {
        background: linear-gradient(135deg, #FF8C00 0%, #FF4500 100%);
        width: 80px; height: 80px; border-radius: 18px;
        display: flex; align-items: center; justify-content: center;
        margin: 0 auto; font-size: 50px; font-weight: bold; color: white;
        box-shadow: 0 10px 20px rgba(255, 69, 0, 0.3);
    }
    .logo-text { 
        font-family: 'Trebuchet MS', sans-serif;
        font-size: 26px; font-weight: bold; color: #FF8C00; 
        text-align: center; margin-top: 10px; text-transform: uppercase;
    }

    /* BOUTONS FIXES */
    .stButton>button { 
        background: linear-gradient(90deg, #FF8C00, #FF4500) !important; 
        color: white !important; border-radius: 12px; border: none; 
        font-weight: bold; width: 100%; height: 45px; transition: 0.3s;
    }
    .stButton>button:hover { transform: scale(1.02); box-shadow: 0 5px 15px rgba(255, 69, 0, 0.4); }
    
    /* CARTES DU MUR */
    .msg-card { 
        background: #1c1f26; padding: 20px; border-radius: 15px; 
        margin-bottom: 15px; border-left: 6px solid #FF8C00;
        box-shadow: 0 4px 10px rgba(0,0,0,0.2);
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. INITIALISATION (SÉCURITÉ) ---
URL_BASE = "https://classconect-f1767-default-rtdb.europe-west1.firebasedatabase.app/"
URL_MSG = f"{URL_BASE}messages.json"
URL_USERS = f"{URL_BASE}utilisateurs.json"

if 'user' not in st.session_state: st.session_state.user = None
if 'page' not in st.session_state: st.session_state.page = "Mur"

def charger(url):
    try:
        r = requests.get(url, timeout=5)
        return r.json() if r.status_code == 200 and r.json() else {}
    except: return {}

# --- 4. INTERFACE DE CONNEXION ---
data_u = charger(URL_USERS)

if st.session_state.user is None:
    st.markdown("<div class='logo-box'>C</div><div class='logo-text'>Class Connect Algeria</div>", unsafe_allow_html=True)
    tab_log, tab_reg = st.tabs(["Connexion", "Créer un compte"])
    
    with tab_log:
        u = st.text_input("Pseudo", key="l_u")
        p = st.text_input("Mot de passe", type="password", key="l_p")
        if st.button("ACCÉDER AU CLUB"):
            if u in data_u and str(data_u[u].get("mdp")) == str(p):
                st.session_state.user = u
                st.rerun()
            else: st.error("Identifiants incorrects")

    with tab_reg:
        nu = st.text_input("Nouveau Pseudo", key="n_u")
        np = st.text_input("Mot de passe", type="password", key="n_p")
        club = st.selectbox("Ton Club", ["Paris SG", "Juventus", "Arsenal"])
        if st.button("S'INSCRIRE ET ENTRER"):
            if nu and np:
                requests.patch(URL_USERS, json={nu: {"mdp": np, "club": club}})
                st.session_state.user = nu
                st.rerun()

# --- 5. INTERFACE PRINCIPALE (FIXE) ---
else:
    me = st.session_state.user
    my_club = data_u.get(me, {}).get("club", "Fan")

    # Barre de navigation fixe à gauche
    with st.sidebar:
        st.markdown("<div class='logo-box' style='width:60px; height:60px; font-size:35px;'>C</div>", unsafe_allow_html=True)
        st.markdown(f"<h3 style='text-align:center;'>{me}</h3>", unsafe_allow_html=True)
        st.write(f"⚽ Club : **{my_club}**")
        st.divider()
        
        # Navigation par boutons (plus stable que radio)
        if st.button("🏠 MUR MONDIAL"): 
            st.session_state.page = "Mur"
            st.rerun()
        if st.button("💬 MESSAGES PRIVÉS"): 
            st.session_state.page = "Chat"
            st.rerun()
        
        st.divider()
        if st.button("🚪 DÉCONNEXION"):
            st.session_state.user = None
            st.rerun()

    # --- LOGIQUE DES PAGES (INDÉPENDANCE TOTALE) ---
    if st.session_state.page == "Mur":
        st.title("🏠 Mur Mondial")
        with st.expander("📝 Publier un message"):
            txt = st.text_area("Écris quelque chose...")
            if st.button("DIFFUSER 🚀"):
                if txt:
                    requests.post(URL_MSG, json={"u": me, "c": my_club, "m": txt, "d": "mondial", "t": time.time()})
                    st.rerun()
        
        msgs = charger(URL_MSG)
        if msgs:
            for k in reversed(list(msgs.keys())):
                v = msgs[k]
                if v.get("d") == "mondial":
                    st.markdown(f"""
                        <div class='msg-card'>
                            <b style='color:#FF8C00;'>@{v['u']}</b> <small>({v.get('c','Fan')})</small><br>
                            <p style='margin-top:10px; font-size:18px;'>{v['m']}</p>
                        </div>
                    """, unsafe_allow_html=True)

    elif st.session_state.page == "Chat":
        st.title("💬 Messages Privés")
        target = st.text_input("Pseudo du destinataire")
        
        if target:
            if target in data_u:
                st.write(f"Conversation avec **{target}**")
                msgs = charger(URL_MSG)
                for k, v in msgs.items():
                    if (v.get("u") == me and v.get("d") == target) or (v.get("u") == target and v.get("d") == me):
                        side = "right" if v['u'] == me else "left"
                        bg = "#FF8C00" if v['u'] == me else "#333"
                        st.markdown(f"<div style='text-align:{side};'><span style='background:{bg}; padding:10px; border-radius:12px; display:inline-block; margin:5px;'>{v['m']}</span></div>", unsafe_allow_html=True)
                
                msg_in = st.text_input("Ton message...", key="chat_in")
                if st.button("ENVOYER 📩"):
                    if msg_in:
                        requests.post(URL_MSG, json={"u": me, "m": msg_in, "d": target, "t": time.time()})
                        st.rerun()
            else:
                st.warning("Utilisateur introuvable.")

# Suppression du rafraîchissement auto sauvage qui fait bugger le tout
# Si tu veux voir les nouveaux messages, clique sur le bouton de la page ou rafraîchis manuellement.
