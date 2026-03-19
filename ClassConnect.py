import streamlit as st
import requests
import time

# --- 1. TA CONFIGURATION PERSONNELLE ---
# REMPLACE LE LIEN CI-DESSOUS PAR TON LIEN MP3
LIEN_DU_SON = "https://www.youtube.com/watch?v=p2rBHjShJjw.mp3" 

st.set_page_config(page_title="Connect Class", page_icon="😊", layout="wide")

st.markdown("""
    <style>
    header {visibility: hidden;}
    .stApp { background-color: #050505; color: white; }
    .nav-bar { background: #111; padding: 10px; border-radius: 10px; border-bottom: 3px solid #D32F2F; margin-bottom: 20px; text-align:center; }
    
    /* BOUTONS NAVIGATION - ORANGE CC */
    div[data-testid="stColumn"] .stButton>button { 
        background: linear-gradient(90deg, #FF8C00, #FF4500) !important; 
        color: white !important; border-radius: 8px; font-weight: bold; height: 50px; border: none;
    }

    /* ANIMATION SI NOTIFICATION ACTIVE */
    @keyframes pulse { 0% {box-shadow: 0 0 0px #FF0000;} 50% {box-shadow: 0 0 20px #FF0000;} 100% {box-shadow: 0 0 0px #FF0000;} }
    .notif-active button { animation: pulse 1s infinite !important; border: 2px solid #FF0000 !important; }

    /* CARTES MESSAGES */
    .msg-card { background: #111; padding: 15px; border-radius: 10px; border-left: 5px solid #D32F2F; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

URL_BASE = "https://classconect-f1767-default-rtdb.europe-west1.firebasedatabase.app/"
URL_MSG = f"{URL_BASE}messages.json"
URL_USERS = f"{URL_BASE}utilisateurs.json"

# --- INITIALISATION DES VARIABLES DE SESSION ---
if 'user' not in st.session_state: st.session_state.user = None
if 'page' not in st.session_state: st.session_state.page = "Mur"
if 'last_msg_count' not in st.session_state: st.session_state.last_msg_count = 0

def get_db(url):
    try:
        r = requests.get(url, timeout=5)
        return r.json() if r.status_code == 200 else {}
    except: return {}

# --- 2. LOGIQUE DE DÉTECTION ---
data_u = get_db(URL_USERS)
all_m = get_db(URL_MSG)

# Calcul du nombre actuel de messages
total_messages = len(all_m) if all_m else 0
nouveau_message_pour_moi = False

if st.session_state.user:
    # Si le nombre de messages a augmenté depuis la dernière actualisation
    if total_messages > st.session_state.last_msg_count:
        derniere_cle = list(all_m.keys())[-1]
        dernier_msg = all_m[derniere_cle]
        
        # Est-ce que ce message m'est destiné ?
        if dernier_msg.get("d") == st.session_state.user:
            nouveau_message_pour_moi = True
            # JOUER LE SON
            st.markdown(f'<audio autoplay><source src="{LIEN_DU_SON}" type="audio/mp3"></audio>', unsafe_allow_html=True)
    
    # On met à jour le compteur pour la prochaine fois
    st.session_state.last_msg_count = total_messages

# --- 3. INTERFACE ---
if st.session_state.user is None:
    st.markdown("<h2 style='text-align:center; color:#FF8C00;'>Connect Class Algeria 😊</h2>", unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["🔴 CONNEXION", "🟠 INSCRIPTION"])
    with tab1:
        u = st.text_input("Pseudo").strip()
        p = st.text_input("Mdp", type="password").strip()
        if st.button("LANCER"):
            if u in data_u and str(data_u[u].get("mdp")) == str(p):
                st.session_state.user = u
                st.rerun()
    with tab2:
        nu = st.text_input("Nouveau Pseudo").strip()
        np = st.text_input("Nouveau Mdp", type="password").strip()
        if st.button("CRÉER COMPTE"):
            if nu and np and nu not in data_u:
                requests.patch(URL_USERS, json={nu: {"mdp": np, "amis": {"Admin": True}}})
                st.success("Compte créé !") ; time.sleep(1) ; st.rerun()
else:
    me = st.session_state.user
    mes_amis = list(data_u.get(me, {}).get("amis", {}).keys())
    
    # Calcul des inconnus pour le badge
    inc_list = [v.get("u") for k, v in (all_m.items() if all_m else []) if v.get("d") == me and v.get("u") not in mes_amis]
    nb_inc = len(set(inc_list))

    # BARRE DE NAVIGATION
    st.markdown(f"<div class='nav-bar'>🟠 <b>@{me}</b></div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    
    with c1:
        if st.button("🏠 LE MUR"): st.session_state.page = "Mur" ; st.rerun()
    
    with c2:
        # Appliquer l'animation ROUGE si un nouveau message arrive
        div_class = "notif-active" if nouveau_message_pour_moi else ""
        label_chat = "💬 CHAT"
        if nb_inc > 0: label_chat += f" ({nb_inc})"
        
        st.markdown(f"<div class='{div_class}'>", unsafe_allow_html=True)
        if st.button(label_chat):
            st.session_state.page = "Chat"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
        
    with c3:
        if st.button("🚪 QUITTER"): st.session_state.user = None ; st.rerun()

    # --- PAGES ---
    if st.session_state.page == "Mur":
        with st.form("post_mur"):
            txt = st.text_area("Ton message...")
            img = st.text_input("Lien Image (Optionnel)")
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
        t_a, t_i = st.tabs(["👥 AMIS", f"📩 INCONNUS ({nb_inc})"])
        
        with t_a:
            col_l, col_r = st.columns([1, 2])
            with col_l:
                for a in mes_amis:
                    status = "🟢" if (time.time() - data_u.get(a, {}).get("last_seen", 0)) < 60 else "👤"
                    if st.button(f"{status} {a}", key=f"f_{a}"):
                        st.session_state.chat_target = a
                        st.rerun()
                st.divider()
                nf = st.text_input("Ajouter quelqu'un").strip()
                if st.button("AJOUTER"):
                    if nf in data_u:
                        requests.patch(f"{URL_BASE}utilisateurs/{me}/amis.json", json={nf: True})
                        requests.patch(f"{URL_BASE}utilisateurs/{nf}/amis.json", json={me: True})
                        st.rerun()

            with col_r:
                target = st.session_state.get("chat_target")
                if target:
                    st.subheader(f"Discussion : {target}")
                    if all_m:
                        for k, v in all_m.items():
                            if (v.get("u")==me and v.get("d")==target) or (v.get("u")==target and v.get("d")==me):
                                side = "right" if v['u']==me else "left"
                                bg = "#D32F2F" if side=="right" else "#222"
                                st.markdown(f"<div style='text-align:{side};'><span style='background:{bg}; padding:10px; border-radius:10px; display:inline-block; margin:5px;'>{v['m']}</span></div>", unsafe_allow_html=True)
                    m_val = st.text_input("Message...", key="chat_input")
                    if st.button("ENVOYER"):
                        requests.post(URL_MSG, json={"u": me, "m": m_val, "d": target, "t": time.time()})
                        st.rerun()

        with t_i:
            if nb_inc > 0:
                for inc in set(inc_list):
                    st.markdown(f"<div class='msg-card'><b>@{inc}</b> veut te parler.</div>", unsafe_allow_html=True)
                    if st.button(f"Accepter {inc}", key=f"acc_{inc}"):
                        requests.patch(f"{URL_BASE}utilisateurs/{me}/amis.json", json={inc: True})
                        requests.patch(f"{URL_BASE}utilisateurs/{inc}/amis.json", json={me: True})
                        st.rerun()
            else:
                st.info("Aucun nouveau message d'inconnu.")

# --- ACTUALISATION ---
if st.session_state.user:
    requests.patch(f"{URL_BASE}utilisateurs/{me}.json", json={"last_seen": time.time()})
time.sleep(4)
st.rerun()
