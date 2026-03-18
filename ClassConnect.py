import streamlit as st
import requests
import time

# --- 1. CONFIGURATION MOBILE & ÉMOJI ---
st.set_page_config(page_title="Connect Class Algeria", page_icon="😊", layout="wide")

# DESIGN SPÉCIAL TÉLÉPHONE (Barre de navigation fixe en haut)
st.markdown("""
    <style>
    header {visibility: hidden;}
    .stApp { background-color: #0e1117; color: white; }
    
    /* LOGO ORANGE CARRÉ */
    .logo-box {
        background: linear-gradient(135deg, #FF8C00, #FF4500);
        width: 60px; height: 60px; border-radius: 12px;
        display: flex; align-items: center; justify-content: center;
        margin: 0 auto; font-size: 35px; font-weight: bold; color: white;
    }

    /* BARRE DE NAVIGATION FLOTTANTE (Très visible sur mobile) */
    .mobile-nav {
        background: #1c1f26;
        padding: 10px;
        border-radius: 15px;
        border: 2px solid #FF8C00;
        margin-bottom: 20px;
        display: flex;
        justify-content: space-around;
    }

    /* BADGE DE NOTIFICATION ROUGE */
    .notif-badge {
        background-color: #FF0000;
        color: white;
        border-radius: 50%;
        padding: 2px 6px;
        font-size: 12px;
        margin-left: 5px;
        font-weight: bold;
    }

    .stButton>button { 
        background: linear-gradient(90deg, #FF8C00, #FF4500) !important; 
        color: white !important; border-radius: 10px; font-weight: bold; width: 100%;
    }
    .msg-card { background: #1c1f26; padding: 15px; border-radius: 12px; border-left: 5px solid #FF8C00; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

URL_BASE = "https://classconect-f1767-default-rtdb.europe-west1.firebasedatabase.app/"
URL_MSG = f"{URL_BASE}messages.json"
URL_USERS = f"{URL_BASE}utilisateurs.json"

if 'user' not in st.session_state: st.session_state.user = None
if 'page' not in st.session_state: st.session_state.page = "Mur"
if 'last_check' not in st.session_state: st.session_state.last_check = time.time()

def get_data(url):
    try:
        r = requests.get(url, timeout=5)
        return r.json() if r.status_code == 200 else {}
    except: return {}

# --- 2. LOGIQUE DES NOTIFICATIONS ---
def verifier_notifs(pseudo, messages):
    count = 0
    if messages:
        for k, v in messages.items():
            # Si le message est pour moi et qu'il est nouveau
            if v.get("d") == pseudo and v.get("t", 0) > st.session_state.last_check:
                count += 1
    return count

# --- 3. INTERFACE ---

data_u = get_data(URL_USERS)
all_msgs = get_data(URL_MSG)

if st.session_state.user is None:
    st.markdown("<div class='logo-box'>C</div><h3 style='text-align:center;'>Class Connect Algeria 😊</h3>", unsafe_allow_html=True)
    t1, t2 = st.tabs(["Connexion", "Inscription"])
    with t1:
        u = st.text_input("Pseudo", key="l_u")
        p = st.text_input("Mdp", type="password", key="l_p")
        if st.button("SE CONNECTER"):
            if u in data_u and str(data_u[u].get("mdp")) == str(p):
                st.session_state.user = u
                st.rerun()
    with t2:
        nu = st.text_input("Nouveau Pseudo", key="n_u")
        np = st.text_input("Nouveau Mdp", type="password", key="n_p")
        cl = st.selectbox("Club", ["Paris SG", "Juventus", "Arsenal"])
        if st.button("CRÉER COMPTE"):
            if nu and np:
                requests.patch(URL_USERS, json={nu: {"mdp": np, "club": cl, "amis": {}}})
                st.session_state.user = nu
                st.rerun()

else:
    me = st.session_state.user
    my_club = data_u.get(me, {}).get("club", "Fan")
    nb_notifs = verifier_notifs(me, all_msgs)

    # --- NOUVELLE NAVIGATION STYLE "APP MOBILE" ---
    st.markdown(f"<div style='text-align:center; margin-bottom:10px;'>😊 <b>{me}</b> ({my_club})</div>", unsafe_allow_html=True)
    
    # Menu horizontal qui remplace la sidebar pour le mobile
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("🏠 MUR"): 
            st.session_state.page = "Mur"
            st.rerun()
    with c2:
        notif_text = f"💬 CHAT ({nb_notifs})" if nb_notifs > 0 else "💬 CHAT"
        if st.button(notif_text): 
            st.session_state.page = "Chat"
            st.session_state.last_check = time.time() # On reset les notifs quand on ouvre
            st.rerun()
    with c3:
        if st.button("🚪 LOGOUT"):
            st.session_state.user = None
            st.rerun()

    st.divider()

    # --- PAGES ---
    if st.session_state.page == "Mur":
        st.subheader("🌍 Mur Mondial")
        with st.expander("📝 Publier un message"):
            txt = st.text_area("Message...")
            img = st.text_input("Lien Image (URL)")
            if st.button("PUBLIER 🚀"):
                if txt or img:
                    requests.post(URL_MSG, json={"u": me, "c": my_club, "m": txt, "i": img, "d": "mondial", "t": time.time()})
                    st.success("Posté ! L'application va s'actualiser...")
                    time.sleep(1)
                    st.rerun() # ACTUALISATION AUTOMATIQUE APRÈS POST

        # Liste des messages
        if all_msgs:
            for k in reversed(list(all_msgs.keys())):
                v = all_msgs[k]
                if v.get("d") == "mondial":
                    st.markdown(f"<div class='msg-card'><b>{v['u']}</b><br>{v.get('m','')}</div>", unsafe_allow_html=True)
                    if v.get("i"): st.image(v["i"], use_container_width=True)

    elif st.session_state.page == "Chat":
        st.subheader("💬 Messagerie")
        
        col_amis, col_conv = st.columns([1, 2])
        
        with col_amis:
            st.write("👥 **Amis**")
            amis = data_u.get(me, {}).get("amis", {})
            for a in amis:
                # Si Sofia t'a envoyé un message, on peut mettre un point rouge ici aussi
                if st.button(f"👤 {a}", key=f"btn_{a}"):
                    st.session_state.chat_target = a
                    st.rerun()
            
            st.divider()
            new_f = st.text_input("Ajouter pseudo")
            if st.button("Ajouter"):
                if new_f in data_u and new_f != me:
                    requests.patch(f"{URL_BASE}utilisateurs/{me}/amis.json", json={new_f: True})
                    st.rerun()

        with col_conv:
            target = st.session_state.get("chat_target")
            if target:
                st.write(f"Discussion avec **{target}**")
                if all_msgs:
                    for k, v in all_msgs.items():
                        if (v.get("u") == me and v.get("d") == target) or (v.get("u") == target and v.get("d") == me):
                            side = "right" if v['u'] == me else "left"
                            color = "#FF8C00" if v['u'] == me else "#333"
                            st.markdown(f"<div style='text-align:{side};'><span style='background:{color}; padding:8px; border-radius:10px; display:inline-block; margin:5px;'>{v['m']}</span></div>", unsafe_allow_html=True)
                
                m_in = st.text_input("Écrire...", key="chat_in")
                if st.button("ENVOYER"):
                    if m_in:
                        requests.post(URL_MSG, json={"u": me, "m": m_in, "d": target, "t": time.time()})
                        st.rerun() # ACTUALISATION AUTO APRÈS ENVOI DU MESSAGE
            else:
                st.info("Sélectionne un ami pour voir les messages de Sofia ou des autres.")

# BOUTON D'ACTUALISATION MANUELLE TOUT EN BAS POUR LES AUTRES MESSAGES
if st.session_state.user:
    st.divider()
    if st.button("🔄 ACTUALISER TOUT"):
        st.rerun()
