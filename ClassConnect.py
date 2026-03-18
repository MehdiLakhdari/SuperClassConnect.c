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
    .stButton>button { 
        background: linear-gradient(90deg, #D32F2F, #8B0000) !important; 
        color: white !important; border-radius: 8px; font-weight: bold; height: 45px; border: none;
    }
    .msg-card { background: #111; padding: 15px; border-radius: 10px; border-left: 5px solid #D32F2F; margin-bottom: 10px; }
    .request-card { background: #1a1a1a; padding: 10px; border-radius: 8px; border: 1px dashed #FF8C00; margin-bottom: 5px; }
    </style>
    """, unsafe_allow_html=True)

URL_BASE = "https://classconect-f1767-default-rtdb.europe-west1.firebasedatabase.app/"
URL_MSG = f"{URL_BASE}messages.json"
URL_USERS = f"{URL_BASE}utilisateurs.json"

if 'user' not in st.session_state: st.session_state.user = None
if 'page' not in st.session_state: st.session_state.page = "Mur"
if 'chat_target' not in st.session_state: st.session_state.chat_target = None

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
    u_input = st.text_input("Pseudo", key="main_u").strip()
    p_input = st.text_input("Mdp", type="password", key="main_p").strip()
    if st.button("SE CONNECTER"):
        if u_input in data_u and str(data_u[u_input].get("mdp")) == str(p_input):
            st.session_state.user = u_input
            st.rerun()
        else:
            st.error("Pseudo ou mot de passe incorrect")
else:
    me = st.session_state.user
    
    # NAVIGATION (Correction de la ligne 73)
    st.markdown(f"<div class='nav-bar'>🔥 @{me} | Actif 🟢</div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("🏠 MUR"):
            st.session_state.page = "Mur"
            st.rerun()
    with c2:
        if st.button("💬 CHAT"):
            st.session_state.page = "Chat"
            st.rerun()
    with c3:
        if st.button("🚪 SORTIR"):
            st.session_state.user = None
            st.rerun()

    if st.session_state.page == "Mur":
        with st.form("form_mur", clear_on_submit=True):
            txt = st.text_area("Message pour le mur")
            if st.form_submit_button("PUBLIER"):
                if txt:
                    requests.post(URL_MSG, json={"u": me, "m": txt, "d": "mondial", "t": time.time()})
                    st.rerun()
        
        if all_m:
            for k in reversed(list(all_m.keys())):
                v = all_m[k]
                if v.get("d") == "mondial":
                    st.markdown(f"<div class='msg-card'><b>@{v['u']}</b><br>{v.get('m','')}</div>", unsafe_allow_html=True)

    elif st.session_state.page == "Chat":
        tab_a, tab_i = st.tabs(["👥 Mes Amis", "📩 Inconnus"])
        mes_amis = list(data_u.get(me, {}).get("amis", {}).keys())

        with tab_a:
            col_l, col_c = st.columns([1, 2])
            with col_l:
                for a in mes_amis:
                    if st.button(f"👤 {a}", key=f"f_{a}"):
                        st.session_state.chat_target = a
                        st.rerun()
                st.divider()
                nf = st.text_input("Ajouter un pseudo").strip()
                if st.button("AJOUTER"):
                    if nf in data_u:
                        requests.patch(f"{URL_BASE}utilisateurs/{me}/amis.json", json={nf: True})
                        st.rerun()

            with col_c:
                target = st.session_state.chat_target
                if target and target in mes_amis:
                    st.subheader(f"Chat avec {target}")
                    # Lien appel vocal
                    room = "".join(sorted([me, target]))
                    st.markdown(f'<a href="https://meet.jit.si/CC_{room}" target="_blank"><button style="background:#28a745; color:white; border:none; padding:10px; border-radius:5px; width:100%; cursor:pointer; font-weight:bold;">📞 APPEL VOCAL</button></a>', unsafe_allow_html=True)
                    
                    if all_m:
                        for k, v in all_m.items():
                            if (v.get("u") == me and v.get("d") == target) or (v.get("u") == target and v.get("d") == me):
                                side = "right" if v['u'] == me else "left"
                                st.markdown(f"<div style='text-align:{side};'><span style='background:{'#D32F2F' if side=='right' else '#333'}; padding:8px; border-radius:10px; display:inline-block; margin:5px;'>{v['m']}</span></div>", unsafe_allow_html=True)
                    
                    with st.form("form_chat", clear_on_submit=True):
                        m_in = st.text_input("Écrire...")
                        if st.form_submit_button("ENVOYER"):
                            requests.post(URL_MSG, json={"u": me, "m": m_in, "d": target, "t": time.time()})
                            st.rerun()

        with tab_i:
            inconnus = []
            if all_m:
                for k, v in all_m.items():
                    exp = v.get("u")
                    if v.get("d") == me and exp not in mes_amis:
                        if exp not in inconnus: inconnus.append(exp)
            
            if inconnus:
                for inc in inconnus:
                    st.markdown(f"<div class='request-card'><b>@{inc}</b> veut te parler</div>", unsafe_allow_html=True)
                    if st.button(f"Accepter {inc}", key=f"acc_{inc}"):
                        requests.patch(f"{URL_BASE}utilisateurs/{me}/amis.json", json={inc: True})
                        st.session_state.chat_target = inc
                        st.rerun()
            else:
                st.info("Aucun nouveau message d'inconnus.")

# Mise à jour présence et refresh
if st.session_state.user:
    requests.patch(f"{URL_BASE}utilisateurs/{me}.json", json={"last_seen": time.time()})
time.sleep(10)
st.rerun()
