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

    /* COMPTEUR ORANGE FLASH */
    .notif-badge {
        background-color: #FF4500;
        color: white;
        padding: 2px 8px;
        border-radius: 50%;
        font-size: 14px;
        margin-left: 5px;
        font-weight: bold;
        box-shadow: 0 0 10px #FF4500;
    }

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

def get_db(url):
    try:
        r = requests.get(url, timeout=5)
        return r.json() if r.status_code == 200 else {}
    except: return {}

# --- 2. LOGIQUE ---
data_u = get_db(URL_USERS)
all_m = get_db(URL_MSG)

if st.session_state.user is None:
    st.markdown("<h2 style='text-align:center; color:#FF8C00;'>Connect Class 😊</h2>", unsafe_allow_html=True)
    tab_login, tab_signup = st.tabs(["🔴 SE CONNECTER", "🟠 CRÉER UN COMPTE"])
    
    with tab_login:
        u = st.text_input("Pseudo").strip()
        p = st.text_input("Mdp", type="password").strip()
        if st.button("ENTRER"):
            if u in data_u and str(data_u[u].get("mdp")) == str(p):
                st.session_state.user = u
                st.rerun()
    with tab_signup:
        new_u = st.text_input("Nouveau Pseudo").strip()
        new_p = st.text_input("Nouveau Mdp", type="password").strip()
        if st.button("CRÉER MON COMPTE"):
            if new_u and new_p and new_u not in data_u:
                requests.patch(URL_USERS, json={new_u: {"mdp": new_p, "amis": {"Admin": True}}})
                st.success("Compte prêt !")
                time.sleep(1)
                st.rerun()
else:
    me = st.session_state.user
    mes_amis = list(data_u.get(me, {}).get("amis", {}).keys())

    # --- CALCUL DU COMPTEUR D'INCONNUS ---
    inc_list = []
    if all_m:
        for k, v in all_m.items():
            exp = v.get("u")
            if v.get("d") == me and exp not in mes_amis:
                if exp not in inc_list: inc_list.append(exp)
    nb_inconnus = len(inc_list)

    # --- NAVIGATION ---
    st.markdown(f"<div class='nav-bar'>🟠 <b>@{me}</b></div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("🏠 MUR"): st.session_state.page = "Mur" ; st.rerun()
    with c2:
        btn_label = "💬 CHAT"
        if nb_inconnus > 0: btn_label += f" ({nb_inconnus})"
        if st.button(btn_label): st.session_state.page = "Chat" ; st.rerun()
    with c3:
        if st.button("🚪 QUITTER"): st.session_state.user = None ; st.rerun()

    if st.session_state.page == "Mur":
        with st.form("p_mur"):
            t = st.text_area("Ton post...")
            im = st.text_input("Lien Image")
            if st.form_submit_button("PUBLIER"):
                requests.post(URL_MSG, json={"u": me, "m": t, "i": im, "d": "mondial", "t": time.time()})
                st.rerun()
        if all_m:
            for k in reversed(list(all_m.keys())):
                v = all_m[k]
                if v.get("d") == "mondial":
                    st.markdown(f"<div class='msg-card'><b>@{v['u']}</b><br>{v.get('m','')}</div>", unsafe_allow_html=True)
                    if v.get("i"): st.image(v["i"], use_container_width=True)

    elif st.session_state.page == "Chat":
        # ICI LE COMPTEUR SUR L'ONGLET
        label_inc = f"📩 INCONNUS ({nb_inconnus})" if nb_inconnus > 0 else "📩 INCONNUS"
        tab_a, tab_i = st.tabs(["👥 MES AMIS", label_inc])

        with tab_a:
            col_l, col_r = st.columns([1, 2])
            with col_l:
                for a in mes_amis:
                    it = data_u.get(a, {}).get("typing_to") == me
                    label = f"🟢 {a}" if it else f"👤 {a}"
                    if st.button(label, key=f"f_{a}"):
                        st.session_state.chat_target = a
                        st.rerun()
                st.divider()
                nf = st.text_input("Pseudo à ajouter").strip()
                if st.button("AJOUTER"):
                    if nf in data_u:
                        requests.patch(f"{URL_BASE}utilisateurs/{me}/amis.json", json={nf: True})
                        requests.patch(f"{URL_BASE}utilisateurs/{nf}/amis.json", json={me: True})
                        st.rerun()

            with col_r:
                t = st.session_state.get("chat_target")
                if t and t in mes_amis:
                    st.subheader(f"Chat avec {t}")
                    if all_m:
                        for k, v in all_m.items():
                            if (v.get("u")==me and v.get("d")==t) or (v.get("u")==t and v.get("d")==me):
                                side = "right" if v['u']==me else "left"
                                bg = "#D32F2F" if side=="right" else "#222"
                                st.markdown(f"<div style='text-align:{side};'><span style='background:{bg}; padding:10px; border-radius:10px; display:inline-block; margin:5px;'>{v['m']}</span></div>", unsafe_allow_html=True)
                    m_i = st.text_input("Message...")
                    if m_i: requests.patch(f"{URL_BASE}utilisateurs/{me}.json", json={"typing_to": t})
                    else: requests.patch(f"{URL_BASE}utilisateurs/{me}.json", json={"typing_to": ""})
                    if st.button("ENVOYER"):
                        requests.post(URL_MSG, json={"u": me, "m": m_i, "d": t, "t": time.time()})
                        st.rerun()

        with tab_i:
            if inc_list:
                for inc in inc_list:
                    st.markdown(f"<div class='req-card'><b>@{inc}</b> t'a envoyé un message !</div>", unsafe_allow_html=True)
                    if st.button(f"Accepter {inc}", key=f"acc_{inc}"):
                        requests.patch(f"{URL_BASE}utilisateurs/{me}/amis.json", json={inc: True})
                        requests.patch(f"{URL_BASE}utilisateurs/{inc}/amis.json", json={me: True})
                        st.session_state.chat_target = inc
                        st.rerun()
            else:
                st.info("Aucun message d'inconnu.")

# Sync
if st.session_state.user:
    requests.patch(f"{URL_BASE}utilisateurs/{me}.json", json={"last_seen": time.time()})
time.sleep(5)
st.rerun()
