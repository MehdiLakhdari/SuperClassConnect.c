import streamlit as st
import requests
import time

# --- 1. CONFIGURATION ---
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

    /* NOTIF FLASH */
    @keyframes blink { 0% {box-shadow: 0 0 5px #FF0000;} 50% {box-shadow: 0 0 20px #FF0000;} 100% {box-shadow: 0 0 5px #FF0000;} }
    .notif-active button { animation: blink 1s infinite !important; border: 1px solid white !important; }

    /* CARTES */
    .msg-card { background: #111; padding: 15px; border-radius: 10px; border-left: 5px solid #D32F2F; margin-bottom: 10px; }
    .req-card { background: #1a1a1a; padding: 10px; border-radius: 8px; border: 1px dashed #FF8C00; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

URL_BASE = "https://classconect-f1767-default-rtdb.europe-west1.firebasedatabase.app/"
URL_MSG = f"{URL_BASE}messages.json"
URL_USERS = f"{URL_BASE}utilisateurs.json"

if 'user' not in st.session_state: st.session_state.user = None
if 'page' not in st.session_state: st.session_state.page = "Mur"
if 'chat_target' not in st.session_state: st.session_state.chat_target = None
if 'last_count' not in st.session_state: st.session_state.last_count = 0

def get_db(url):
    try:
        r = requests.get(url, timeout=5)
        return r.json() if r.status_code == 200 else {}
    except: return {}

# --- 2. LOGIQUE ---
data_u = get_db(URL_USERS)
all_m = get_db(URL_MSG)

# Notifs
curr_count = len(all_m) if all_m else 0
has_notif = False
if st.session_state.user and curr_count > st.session_state.last_count:
    keys = list(all_m.keys())
    if keys and all_m[keys[-1]].get("d") == st.session_state.user:
        has_notif = True

if st.session_state.user is None:
    st.markdown("<h2 style='text-align:center; color:#FF8C00;'>Connect Class 😊</h2>", unsafe_allow_html=True)
    u = st.text_input("Pseudo").strip()
    p = st.text_input("Mdp", type="password").strip()
    if st.button("SE CONNECTER"):
        if u in data_u and str(data_u[u].get("mdp")) == str(p):
            st.session_state.user = u
            st.rerun()
else:
    me = st.session_state.user
    st.markdown(f"<div class='nav-bar'>🟠 <b>@{me}</b> | Connecté</div>", unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("🏠 LE MUR"): st.session_state.page = "Mur" ; st.rerun()
    with c2:
        div_class = "notif-active" if has_notif else ""
        st.markdown(f"<div class='{div_class}'>", unsafe_allow_html=True)
        if st.button("💬 MESSAGES"):
            st.session_state.page = "Chat"
            st.session_state.last_count = curr_count
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    with c3:
        if st.button("🚪 QUITTER"): st.session_state.user = None ; st.rerun()

    # --- PAGES ---
    if st.session_state.page == "Mur":
        st.subheader("🌍 Fil d'actualité")
        with st.form("mur_post"):
            m_txt = st.text_area("Partage quelque chose...")
            m_img = st.text_input("Lien Image")
            if st.form_submit_button("PUBLIER 🚀"):
                requests.post(URL_MSG, json={"u": me, "m": m_txt, "i": m_img, "d": "mondial", "t": time.time()})
                st.rerun()
        if all_m:
            for k in reversed(list(all_m.keys())):
                v = all_m[k]
                if v.get("d") == "mondial":
                    st.markdown(f"<div class='msg-card'><b>@{v['u']}</b><br>{v.get('m','')}</div>", unsafe_allow_html=True)
                    if v.get("i"): st.image(v["i"], use_container_width=True)

    elif st.session_state.page == "Chat":
        tab_amis, tab_inc = st.tabs(["👥 MES AMIS", "📩 INCONNUS"])
        mes_amis = list(data_u.get(me, {}).get("amis", {}).keys())

        with tab_amis:
            col_l, col_r = st.columns([1, 2])
            with col_l:
                st.write("**Ma liste**")
                for a in mes_amis:
                    is_t = data_u.get(a, {}).get("typing_to") == me
                    label = f"🟢 {a}" if is_t else f"👤 {a}"
                    if st.button(label, key=f"f_{a}"):
                        st.session_state.chat_target = a
                        st.rerun()
                st.divider()
                new_f = st.text_input("Ajouter un pseudo").strip()
                if st.button("AJOUTER 👤+"):
                    if new_f in data_u and new_f != me:
                        requests.patch(f"{URL_BASE}utilisateurs/{me}/amis.json", json={new_f: True})
                        requests.patch(f"{URL_BASE}utilisateurs/{new_f}/amis.json", json={me: True}) # Ami des deux côtés
                        st.success(f"{new_f} ajouté !")
                        time.sleep(1)
                        st.rerun()

            with col_r:
                t = st.session_state.get("chat_target")
                if t and t in mes_amis:
                    st.subheader(f"Chat avec {t}")
                    room = "".join(sorted([me, t]))
                    st.markdown(f'<a href="https://meet.jit.si/CC_{room}" target="_blank"><button style="background:#28a745; color:white; border:none; padding:8px; border-radius:5px; width:100%; cursor:pointer; font-weight:bold;">📞 APPEL VOCAL</button></a>', unsafe_allow_html=True)
                    if all_m:
                        for k, v in all_m.items():
                            if (v.get("u") == me and v.get("d") == t) or (v.get("u") == t and v.get("d") == me):
                                side = "right" if v['u'] == me else "left"
                                bg = "#D32F2F" if side == "right" else "#222"
                                st.markdown(f"<div style='text-align:{side};'><span style='background:{bg}; padding:10px; border-radius:10px; display:inline-block; margin:5px;'>{v['m']}</span></div>", unsafe_allow_html=True)
                    m_in = st.text_input("Message...", key="chat_in")
                    if m_in: requests.patch(f"{URL_BASE}utilisateurs/{me}.json", json={"typing_to": t})
                    else: requests.patch(f"{URL_BASE}utilisateurs/{me}.json", json={"typing_to": ""})
                    if st.button("ENVOYER 📩"):
                        requests.post(URL_MSG, json={"u": me, "m": m_in, "d": t, "t": time.time()})
                        requests.patch(f"{URL_BASE}utilisateurs/{me}.json", json={"typing_to": ""})
                        st.rerun()

        with tab_inc:
            st.write("**Demandes de message**")
            inc_list = []
            if all_m:
                for k, v in all_m.items():
                    exp = v.get("u")
                    if v.get("d") == me and exp not in mes_amis:
                        if exp not in inc_list: inc_list.append(exp)
            if inc_list:
                for inc in inc_list:
                    st.markdown(f"<div class='req-card'><b>@{inc}</b> veut te parler.</div>", unsafe_allow_html=True)
                    if st.button(f"Accepter {inc}", key=f"acc_{inc}"):
                        requests.patch(f"{URL_BASE}utilisateurs/{me}/amis.json", json={inc: True})
                        requests.patch(f"{URL_BASE}utilisateurs/{inc}/amis.json", json={me: True})
                        st.session_state.chat_target = inc
                        st.rerun()
            else:
                st.info("Aucun message d'inconnus.")

# Sync
if st.session_state.user:
    requests.patch(f"{URL_BASE}utilisateurs/{me}.json", json={"last_seen": time.time()})
time.sleep(5)
st.rerun()
