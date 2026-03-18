import streamlit as st
import requests
import time

# --- 1. CONFIGURATION ---
URL_BASE = "https://classconect-f1767-default-rtdb.europe-west1.firebasedatabase.app/"
URL_MSG = f"{URL_BASE}messages.json"
URL_USERS = f"{URL_BASE}utilisateurs.json"

st.set_page_config(page_title="Connect Class Algeria", page_icon="⚽", layout="wide")

# --- 2. SESSION STATE ---
if 'user' not in st.session_state: st.session_state.user = None
if 'page' not in st.session_state: st.session_state.page = "🏠 Mur"
if 'chat_target' not in st.session_state: st.session_state.chat_target = None

# --- 3. FONCTIONS ---
def charger(url):
    try:
        r = requests.get(url)
        return r.json() if r.status_code == 200 and r.json() else {}
    except: return {}

def get_club_style(club):
    styles = {
        "PSG": {"bg": "#001C3F", "btn": "#E30613", "txt": "#FFFFFF", "accent": "#E30613"},
        "Barça": {"bg": "#004D98", "btn": "#A50044", "txt": "#FFFFFF", "accent": "#EDBB00"},
        "Juventus": {"bg": "#000000", "btn": "#FFFFFF", "txt": "#000000", "accent": "#FFFFFF"}
    }
    return styles.get(club, {"bg": "#1a0000", "btn": "#ff0000", "txt": "#FFFFFF", "accent": "#ff0000"})

data_u = charger(URL_USERS)
user_club = data_u.get(st.session_state.user, {}).get("club", "PSG") if st.session_state.user else "PSG"
s = get_club_style(user_club)

# --- 4. DESIGN DYNAMIQUE ---
st.markdown(f"""
    <style>
    .stApp {{ background-color: {s['bg']}; color: white; }}
    [data-testid="stSidebar"] {{ background-color: rgba(0,0,0,0.5); border-right: 3px solid {s['accent']}; }}
    .stButton>button {{ 
        background-color: {s['btn']} !important; color: {s['txt']} !important; 
        border-radius: 8px; font-weight: bold; border: none; width: 100%;
    }}
    .msg-card {{ background: rgba(255,255,255,0.1); padding: 15px; border-radius: 10px; border-left: 5px solid {s['accent']}; margin-bottom: 10px; }}
    .logo-cc {{ font-size: 50px; font-weight: bold; text-align: center; color: white; }}
    </style>
    """, unsafe_allow_html=True)

# --- 5. INTERFACE ---

if st.session_state.user is None:
    st.markdown("<div class='logo-cc'>CC</div>", unsafe_allow_html=True)
    t1, t2 = st.tabs(["CONNEXION", "INSCRIPTION"])
    with t1:
        u = st.text_input("Pseudo", key="l_u")
        p = st.text_input("Mdp", type="password", key="l_p")
        if st.button("LANCER"):
            if u in data_u and str(data_u[u].get("mdp")) == str(p):
                st.session_state.user = u
                st.rerun()
    with t2:
        nu = st.text_input("Nouveau Pseudo", key="n_u")
        np = st.text_input("Mot de passe", type="password", key="n_p")
        nclub = st.selectbox("Choisis ton Club", ["PSG", "Barça", "Juventus"])
        if st.button("CRÉER MON COMPTE"):
            requests.patch(URL_USERS, json={nu: {"mdp": np, "club": nclub, "pfp": ""}})
            st.success("Compte créé ! Connecte-toi.")

else:
    me = st.session_state.user
    
    # --- LOGIQUE NOTIFICATIONS / AMIS AUTO ---
    all_msgs = charger(URL_MSG)
    contacts_auto = set()
    new_msg_count = 0
    if all_msgs:
        for m in all_msgs.values():
            if m.get("d") == me:
                contacts_auto.add(m["u"]) # Ajoute celui qui t'a écrit
                new_msg_count += 1

    # --- SIDEBAR ---
    with st.sidebar:
        st.markdown(f"<div class='logo-cc'>{user_club[:2].upper()}</div>", unsafe_allow_html=True)
        st.write(f"Joueur : **{me}**")
        st.write(f"Club : **{user_club}**")
        st.divider()
        if st.button("🏠 MUR MONDIAL"): st.session_state.page = "Mur"
        label_msg = f"💬 MESSAGES ({new_msg_count})" if new_msg_count > 0 else "💬 MESSAGES"
        if st.button(label_msg): st.session_state.page = "Messages"
        if st.button("⚙️ RÉGLAGES"): st.session_state.page = "Settings"
        st.divider()
        if st.button("🚪 QUITTER"):
            st.session_state.user = None
            st.rerun()

    # --- PAGES ---
    if st.session_state.page == "Mur":
        st.title("🏠 Mur du Club")
        with st.expander("📝 Publier"):
            txt = st.text_area("Message")
            if st.button("POSTER"):
                requests.post(URL_MSG, json={"u": me, "m": txt, "d": "mondial", "t": time.time()})
                st.rerun()
        
        if all_msgs:
            for v in reversed(list(all_msgs.values())):
                if v.get("d") == "mondial":
                    st.markdown(f"<div class='msg-card'><b>{v['u']}</b> : {v['m']}</div>", unsafe_allow_html=True)

    elif st.session_state.page == "Messages":
        st.title("💬 Messagerie Directe")
        
        # Liste des gens qui t'ont écrit ou que tu cherches
        st.subheader("Tes discussions")
        for c in contacts_auto:
            if st.button(f"Discuter avec {c} (Nouveau message)", key=f"btn_{c}"):
                st.session_state.chat_target = c
        
        target = st.text_input("Chercher un autre pseudo...")
        if st.button("Lancer Chat"):
            if target in data_u: st.session_state.chat_target = target

        if st.session_state.chat_target:
            dest = st.session_state.chat_target
            st.divider()
            st.subheader(f"Chat : {dest}")
            if all_msgs:
                for v in all_msgs.values():
                    if (v.get("u") == me and v.get("d") == dest) or (v.get("u") == dest and v.get("d") == me):
                        align = "right" if v['u'] == me else "left"
                        bg = s['accent'] if v['u'] == me else "#444"
                        st.markdown(f"<div style='text-align:{align};'><span style='background:{bg}; color:white; padding:8px; border-radius:10px; display:inline-block; margin:2px;'>{v['m']}</span></div>", unsafe_allow_html=True)
            
            msg_in = st.text_input("Écrire...", key="chat_in")
            if st.button("ENVOYER 🚀"):
                if msg_in:
                    requests.post(URL_MSG, json={"u": me, "m": msg_in, "d": dest, "t": time.time()})
                    st.rerun()

    elif st.session_state.page == "Settings":
        st.title("⚙️ Paramètres")
        new_pfp = st.text_input("URL Photo de Profil")
        if st.button("Mettre à jour"):
            requests.patch(f"{URL_BASE}utilisateurs/{me}.json", json={"pfp": new_pfp})
            st.success("Ok !")

time.sleep(5)
st.rerun()
