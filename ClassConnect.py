import streamlit as st
import requests
import time

# --- 1. CONFIGURATION & STYLE NOIR/ROUGE ---
st.set_page_config(page_title="Connect Class Algeria", page_icon="😊", layout="wide")

st.markdown("""
    <style>
    header {visibility: hidden;}
    .stApp { background-color: #050505; color: #ffffff; }
    
    /* BARRE LATÉRALE NOIRE */
    [data-testid="stSidebar"] {
        background-color: #0e0e0e !important;
        border-right: 3px solid #FF0000;
    }

    /* LOGO ORANGE CC */
    .logo-box {
        background: linear-gradient(135deg, #FF8C00, #FF4500);
        width: 60px; height: 60px; border-radius: 12px;
        display: flex; align-items: center; justify-content: center;
        margin: 0 auto; font-size: 35px; font-weight: bold; color: white;
        box-shadow: 0 0 15px rgba(255, 140, 0, 0.4);
    }

    /* BOUTONS ROUGE ÉLITE */
    .stButton>button { 
        background: linear-gradient(90deg, #D32F2F, #B71C1C) !important; 
        color: white !important; border-radius: 5px; font-weight: bold; 
        width: 100%; border: none; height: 45px;
    }
    .stButton>button:hover { 
        box-shadow: 0 0 20px #FF0000;
        transform: translateY(-2px);
    }

    /* CARTES MESSAGES */
    .msg-card { 
        background: #141414; padding: 15px; border-radius: 10px; 
        border-left: 5px solid #D32F2F; margin-bottom: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    </style>
    """, unsafe_allow_html=True)

URL_BASE = "https://classconect-f1767-default-rtdb.europe-west1.firebasedatabase.app/"
URL_MSG = f"{URL_BASE}messages.json"
URL_USERS = f"{URL_BASE}utilisateurs.json"

# --- 2. ÉTAT DE LA SESSION ---
if 'user' not in st.session_state: st.session_state.user = None
if 'page' not in st.session_state: st.session_state.page = "Mur"
if 'last_read' not in st.session_state: st.session_state.last_read = time.time()

def get_db(url):
    try:
        r = requests.get(url, timeout=5)
        return r.json() if r.status_code == 200 else {}
    except: return {}

# --- 3. INTERFACE ---

data_u = get_db(URL_USERS)
all_m = get_db(URL_MSG)

# --- ÉCRAN DE CONNEXION ---
if st.session_state.user is None:
    st.markdown("<br><div class='logo-box'>C</div><h2 style='text-align:center; color:#FF8C00;'>Class Connect Algeria</h2>", unsafe_allow_html=True)
    
    t1, t2 = st.tabs(["🔴 CONNEXION", "⚪ INSCRIPTION"])
    
    with t1:
        u_log = st.text_input("Pseudo", key="login_user").strip()
        p_log = st.text_input("Mot de passe", type="password", key="login_pass").strip()
        
        if st.button("ACCÉDER AU RÉSEAU"):
            if not u_log or not p_log:
                st.error("Champs vides !")
            elif u_log in data_u and str(data_u[u_log].get("mdp")) == str(p_log):
                st.session_state.user = u_log
                st.success("Connexion...")
                time.sleep(1)
                st.rerun()
            else:
                st.error("Pseudo ou mot de passe incorrect.")

    with t2:
        nu = st.text_input("Nouveau Pseudo", key="reg_user").strip()
        np = st.text_input("Nouveau Mdp", type="password", key="reg_pass").strip()
        cl = st.selectbox("Ton Club", ["Paris SG", "Juventus", "Arsenal"])
        if st.button("CRÉER MON COMPTE"):
            if nu and np:
                requests.patch(URL_USERS, json={nu: {"mdp": np, "club": cl, "amis": {}}})
                st.session_state.user = nu
                st.rerun()

# --- ÉCRAN CONNECTÉ ---
else:
    me = st.session_state.user
    
    # BARRE LATÉRALE (SIDEBAR)
    with st.sidebar:
        st.markdown("<div class='logo-box'>C</div>", unsafe_allow_html=True)
        st.markdown(f"<h3 style='text-align:center;'>@{me}</h3>", unsafe_allow_html=True)
        st.divider()
        
        if st.button("🏠 MUR MONDIAL"): st.session_state.page = "Mur"
        
        # Système de notif visuelle Sofia/Amis
        new_msgs = 0
        if all_m:
            for k, v in all_m.items():
                if v.get("d") == me and v.get("t", 0) > st.session_state.last_read:
                    new_msgs += 1
        
        chat_btn_label = f"💬 MESSAGES ({new_msgs}) 🔴" if new_msgs > 0 else "💬 MESSAGES"
        if st.button(chat_btn_label): 
            st.session_state.page = "Chat"
            st.session_state.last_read = time.time()
        
        st.divider()
        if st.button("🚪 DÉCONNEXION"):
            st.session_state.user = None
            st.rerun()

    # --- PAGES ---
    if st.session_state.page == "Mur":
        st.title("🌍 Fil d'actualité")
        with st.expander("📝 Nouvelle publication"):
            txt = st.text_area("Ton message")
            img = st.text_input("Lien Image (Optionnel)")
            if st.button("PUBLIER SUR LE MUR"):
                requests.post(URL_MSG, json={"u": me, "m": txt, "i": img, "d": "mondial", "t": time.time()})
                st.rerun()
        
        if all_m:
            for k in reversed(list(all_m.keys())):
                v = all_m[k]
                if v.get("d") == "mondial":
                    st.markdown(f"<div class='msg-card'><b>@{v['u']}</b><br>{v.get('m','')}</div>", unsafe_allow_html=True)
                    if v.get("i"): st.image(v["i"], use_container_width=True)

    elif st.session_state.page == "Chat":
        col1, col2 = st.columns([1, 2])
        with col1:
            st.subheader("👥 Amis")
            amis = data_u.get(me, {}).get("amis", {})
            for a in amis:
                if st.button(f"👤 {a}", key=f"chat_{a}"):
                    st.session_state.chat_target = a
                    st.rerun()
            
            st.divider()
            nf = st.text_input("Ajouter un ami").strip()
            if st.button("AJOUTER 👤+"):
                if nf in data_u and nf != me:
                    requests.patch(f"{URL_BASE}utilisateurs/{me}/amis.json", json={nf: True})
                    st.rerun()

        with col2:
            target = st.session_state.get("chat_target")
            if target:
                st.subheader(f"Discussion avec {target}")
                if all_m:
                    for k, v in all_m.items():
                        if (v.get("u") == me and v.get("d") == target) or (v.get("u") == target and v.get("d") == me):
                            side = "right" if v['u'] == me else "left"
                            color = "#D32F2F" if side == "right" else "#222"
                            st.markdown(f"<div style='text-align:{side};'><span style='background:{color}; padding:10px; border-radius:10px; display:inline-block; margin:5px;'>{v['m']}</span></div>", unsafe_allow_html=True)
                
                m_in = st.text_input("Écrire...", key="chat_input")
                if st.button("ENVOYER 📩"):
                    requests.post(URL_MSG, json={"u": me, "m": m_in, "d": target, "t": time.time()})
                    st.rerun()

# --- ACTUALISATION ---
time.sleep(10)
st.rerun()
