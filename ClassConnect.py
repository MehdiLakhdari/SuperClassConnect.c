import streamlit as st
import requests
import time
import random

# --- 1. CONFIGURATION ---
URL_BASE = "https://classconect-f1767-default-rtdb.europe-west1.firebasedatabase.app/"
URL_MSG = f"{URL_BASE}messages.json"
URL_USERS = f"{URL_BASE}utilisateurs.json"

st.set_page_config(page_title="Connect Class Algeria", page_icon="🇩🇿", layout="wide")

# --- 2. ÉTAT DE LA SESSION ---
if 'user' not in st.session_state: st.session_state.user = None
if 'chat_with' not in st.session_state: st.session_state.chat_with = None
if 'temp_code' not in st.session_state: st.session_state.temp_code = None

# --- 3. DESIGN "RED DARK" ---
st.markdown("""
    <style>
    #MainMenu, footer, header {visibility: hidden;}
    .stApp { background: linear-gradient(180deg, #300000 0%, #000000 100%); color: #ffffff; }
    
    /* Logo Sidebar */
    .logo-sidebar {
        background: linear-gradient(135deg, #ff0000, #8b0000);
        width: 50px; height: 50px; border-radius: 12px;
        display: flex; align-items: center; justify-content: center;
        font-size: 30px; font-weight: bold; color: white;
        box-shadow: 0 0 15px rgba(255, 0, 0, 0.5);
        margin-bottom: 20px;
    }

    .pfp-nav { width: 60px; height: 60px; border-radius: 50%; object-fit: cover; border: 2px solid #ff4b4b; }
    
    /* Bulles de Chat */
    .bubble { padding: 12px 18px; border-radius: 18px; margin-bottom: 10px; max-width: 75%; display: inline-block; font-family: sans-serif; }
    .me { background-color: #28a745; color: white; float: right; clear: both; border-bottom-right-radius: 2px; }
    .them { background-color: #6f42c1; color: white; float: left; clear: both; border-bottom-left-radius: 2px; }

    /* Boutons */
    .stButton>button { background: #ff0000; color: white; border-radius: 10px; font-weight: bold; border:none; transition: 0.3s; }
    .stButton>button:hover { background: #ff4b4b; transform: scale(1.02); }
    div.stButton > button:first-child[kind="secondary"] { background: #007bff !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. FONCTIONS ---
def charger(url):
    try:
        r = requests.get(url)
        return r.json() if r.status_code == 200 and r.json() else {}
    except: return {}

def get_pfp(pseudo, users_data):
    u_info = users_data.get(pseudo, {})
    url = u_info.get("pfp")
    return url if url and url.startswith("http") else "https://cdn-icons-png.flaticon.com/512/149/149071.png"

# --- 5. LOGIQUE PRINCIPALE ---
users_data = charger(URL_USERS)

if st.session_state.user is None:
    # --- ECRAN DE CONNEXION ---
    st.markdown("<center><div class='logo-sidebar' style='margin:auto;'>C</div><h1>CONNECT CLASS ALGERIA</h1></center>", unsafe_allow_html=True)
    t1, t2 = st.tabs(["Connexion", "Inscription"])
    
    with t1:
        u_l = st.text_input("Pseudo", key="login_user")
        p_l = st.text_input("Mot de passe", type="password", key="login_pass")
        if st.button("ACCÉDER AU SYSTÈME"):
            if u_l in users_data and str(users_data[u_l].get("mdp")) == str(p_l):
                st.session_state.user = u_l
                st.rerun()
            else: st.error("Pseudo ou mot de passe incorrect.")

    with t2:
        nu = st.text_input("Nouveau Pseudo", key="reg_user")
        nm = st.text_input("Email", key="reg_mail")
        np = st.text_input("Mot de passe", type="password", key="reg_pass")
        if st.button("DEMANDER CODE DE SÉCURITÉ"):
            if nu in users_data: st.error("Ce pseudo existe déjà.")
            else:
                st.session_state.temp_code = random.randint(1111, 9999)
                st.info(f"🛡️ CODE DE VÉRIFICATION : **{st.session_state.temp_code}**")
        
        if st.session_state.temp_code:
            c_in = st.text_input("Entrez le code")
            if st.button("VALIDER L'INSCRIPTION"):
                if str(c_in) == str(st.session_state.temp_code):
                    requests.patch(URL_USERS, json={nu: {"mdp": np, "mail": nm, "pfp": "", "amis": {}}})
                    st.success("Compte créé ! Connecte-toi.")
                    st.session_state.temp_code = None
                else: st.error("Code incorrect.")

else:
    # --- INTERFACE CONNECTÉE ---
    me = st.session_state.user
    pfp_me = get_pfp(me, users_data)
    
    # Sidebar Fixe
    st.sidebar.markdown("<div class='logo-sidebar'>C</div>", unsafe_allow_html=True)
    st.sidebar.image(pfp_me, width=80)
    st.sidebar.write(f"💼 **{me}**")
    
    menu = st.sidebar.radio("Navigation", ["🏠 Mur Mondial", "💬 Direct Messages", "⚙️ Paramètres"])

    # 1. PAGE MUR
    if menu == "🏠 Mur Mondial":
        st.header("🏠 Flux de l'Entreprise")
        with st.expander("📝 Publier un message ou une image"):
            m_txt = st.text_area("Votre message...")
            m_img = st.text_input("Lien de l'image (URL)")
            if st.button("DIFFUSER SUR LE MUR"):
                requests.post(URL_MSG, json={"u": me, "m": m_txt, "i": m_img, "d": "mondial", "t": time.time()})
                st.rerun()
        
        st.write("---")
        msgs = charger(URL_MSG)
        if msgs:
            for k in reversed(list(msgs.keys())):
                v = msgs[k]
                if v.get("d") == "mondial":
                    p_v = get_pfp(v['u'], users_data)
                    st.markdown(f"**{v['u']}**")
                    if v.get('m'): st.write(v['m'])
                    if v.get('i'): st.image(v['i'], use_container_width=True)
                    st.divider()

    # 2. PAGE MESSAGES + VIDÉO
    elif menu == "💬 Direct Messages":
        st.header("💬 Messagerie Privée")
        search = st.text_input("🔍 Rechercher un collègue (Pseudo)")
        if st.button("Ouvrir la discussion"):
            if search in users_data and search != me:
                st.session_state.chat_with = search
                requests.patch(f"{URL_BASE}utilisateurs/{me}/amis.json", json={search: True})
                st.rerun()

        # Liste des contacts à gauche
        amis = users_data.get(me, {}).get("amis", {})
        if amis:
            st.sidebar.write("---")
            st.sidebar.write("👤 **Vos Contacts**")
            for ami in amis.keys():
                if st.sidebar.button(f"Chat : {ami}", key=f"s_{ami}"):
                    st.session_state.chat_with = ami
                    st.rerun()

        if st.session_state.chat_with:
            target = st.session_state.chat_with
            st.subheader(f"Conversation avec {target}")
            
            # APPEL VIDÉO
            if st.button("📞 LANCER UN APPEL VIDÉO", key="v_call"):
                room = f"CC-Algeria-{min(me, target)}-{max(me, target)}"
                st.markdown(f'<iframe src="https://meet.jit.si/{room}" allow="camera; microphone; fullscreen" style="height: 500px; width: 100%; border-radius:15px; border: 2px solid #ff0000;"></iframe>', unsafe_allow_html=True)

            # AFFICHAGE DES MESSAGES
            msgs = charger(URL_MSG)
            if msgs:
                for k in list(msgs.keys()):
                    v = msgs[k]
                    if (v.get("u") == me and v.get("d") == target) or (v.get("u") == target and v.get("d") == me):
                        cls = "me" if v['u'] == me else "them"
                        st.markdown(f"<div class='bubble {cls}'><b>{v['u']}:</b> {v['m']}</div>", unsafe_allow_html=True)
            
            # Envoi
            m_input = st.text_input("Tapez votre message...", key="m_in")
            if st.button("ENVOYER 🚀", type="secondary"):
                if m_input:
                    requests.post(URL_MSG, json={"u": me, "m": m_input, "d": target, "t": time.time()})
                    st.rerun()

    # 3. PAGE PARAMÈTRES
    elif menu == "⚙️ Paramètres":
        st.header("⚙️ Votre Profil")
        new_pfp = st.text_input("URL de votre Photo de Profil", value=pfp_me)
        if st.button("Mettre à jour le profil"):
            requests.patch(f"{URL_BASE}utilisateurs/{me}.json", json={"pfp": new_pfp})
            st.success("Photo mise à jour !")
        
        if st.button("🚪 Se déconnecter"):
            st.session_state.user = None
            st.session_state.chat_with = None
            st.rerun()

# Auto-refresh
time.sleep(10)
st.rerun()
