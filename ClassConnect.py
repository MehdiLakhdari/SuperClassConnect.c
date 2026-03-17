import streamlit as st
import requests
import time
import random

# --- 1. CONFIGURATION ---
URL_BASE = "https://classconect-f1767-default-rtdb.europe-west1.firebasedatabase.app/"
URL_MSG = f"{URL_BASE}messages.json"
URL_USERS = f"{URL_BASE}utilisateurs.json"

st.set_page_config(page_title="ClassConnect Enterprise", page_icon="⚽", layout="wide")

# --- 2. ÉTAT DE LA SESSION ---
if 'user' not in st.session_state: st.session_state.user = None
if 'chat_with' not in st.session_state: st.session_state.chat_with = None
if 'temp_code' not in st.session_state: st.session_state.temp_code = None

# --- 3. DESIGN "RED DARK GLOW" ---
st.markdown("""
    <style>
    /* Cacher les menus Streamlit */
    #MainMenu, footer, header {visibility: hidden;}
    
    .stApp {
        background: linear-gradient(180deg, #4b0000 0%, #000000 100%);
        color: #ffffff;
    }
    
    /* Logo Startup Bournemouth Style */
    .logo-box {
        background: linear-gradient(135deg, #ff0000, #8b0000);
        width: 50px; height: 50px; border-radius: 12px;
        display: flex; align-items: center; justify-content: center;
        font-size: 30px; font-weight: bold; color: white;
        box-shadow: 0 0 15px rgba(255, 0, 0, 0.5);
        margin-bottom: 10px;
    }

    .pfp-nav { width: 45px; height: 45px; border-radius: 50%; object-fit: cover; border: 2px solid #ff4b4b; margin-top: 10px; }
    .pfp-main { width: 110px; height: 110px; border-radius: 50%; object-fit: cover; border: 3px solid #ff0000; display: block; margin: 0 auto; }

    /* Bulles de Chat */
    .bubble { padding: 12px 18px; border-radius: 20px; margin-bottom: 8px; max-width: 75%; display: inline-block; font-family: sans-serif; }
    .me { background-color: #28a745; color: white; float: right; clear: both; border-bottom-right-radius: 2px; }
    .them { background-color: #6f42c1; color: white; float: left; clear: both; border-bottom-left-radius: 2px; }

    /* Inputs & Buttons */
    .stButton>button { background: #ff0000; color: white; border-radius: 10px; font-weight: bold; border:none; transition: 0.3s; }
    .stButton>button:hover { background: #ff4b4b; transform: scale(1.02); }
    div.stButton > button:first-child[kind="secondary"] { background: #007bff !important; }
    
    .stTextInput>div>div>input { background-color: rgba(255,255,255,0.08) !important; color: white !important; border-radius: 10px !important; border: 1px solid #444 !important; }
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

# --- 5. LOGIQUE DE NAVIGATION ---
users_data = charger(URL_USERS)
display_area = st.empty() # Pour garantir l'indépendance des pages

with display_area.container():
    if st.session_state.user is None:
        # --- ECRAN D'ACCUEIL / AUTHENTIFICATION ---
        st.markdown("<center><div class='logo-box'>C</div><h1 style='color:white; letter-spacing:2px;'>CLASS CONNECT</h1></center>", unsafe_allow_html=True)
        tab_login, tab_sign = st.tabs(["Connexion", "Rejoindre Bournemouth Corp"])
        
        with tab_login:
            u_l = st.text_input("Pseudo", key="login_user")
            p_l = st.text_input("Mot de passe", type="password", key="login_pass")
            if st.button("DÉVERROUILLER L'ACCÈS"):
                if u_l in users_data and str(users_data[u_l].get("mdp")) == str(p_l):
                    st.session_state.user = u_l
                    st.rerun()
                else: st.error("Identifiants invalides.")

        with tab_sign:
            st.write("### 📝 Inscription Sécurisée")
            nu = st.text_input("Pseudo Choisi", key="reg_user")
            nm = st.text_input("Email (Google/Outlook)", key="reg_mail")
            np = st.text_input("Mot de passe", type="password", key="reg_pass")
            col_1, col_2 = st.columns(2)
            ns = col_1.selectbox("Genre", ["Homme", "Femme"])
            na = col_2.number_input("Âge", 13, 99)
            
            if st.button("GÉNÉRER CODE DE SÉCURITÉ"):
                if nu in users_data: st.error("Désolé, ce pseudo appartient déjà à un membre.")
                elif not nu or not nm: st.warning("Données incomplètes.")
                else:
                    st.session_state.temp_code = random.randint(1111, 9999)
                    st.info(f"🛡️ CODE GOOGLE AUTH : **{st.session_state.temp_code}**")
            
            if st.session_state.temp_code:
                c_in = st.text_input("Entrez le code de vérification")
                if st.button("CONFIRMER LA CRÉATION"):
                    if str(c_in) == str(st.session_state.temp_code):
                        requests.patch(URL_USERS, json={nu: {"mdp": np, "mail": nm, "sexe": ns, "age": na, "pfp": "", "amis": {}}})
                        st.success("Compte validé ! Connectez-vous.")
                        st.session_state.temp_code = None
                    else: st.error("Code erroné.")

    else:
        # --- INTERFACE UTILISATEUR CONNECTÉ ---
        me = st.session_state.user
        pfp_me = get_pfp(me, users_data)
        
        # LOGO EN HAUT À GAUCHE DANS LA SIDEBAR
        st.sidebar.markdown(f"""
            <div class='logo-box' style='width:40px; height:40px; font-size:22px; margin:0;'>C</div>
            <div style='margin-top:10px;'>
                <img src='{pfp_me}' class='pfp-nav'>
                <p style='margin-top:5px;'><b>Session : {me}</b></p>
            </div>
        """, unsafe_allow_html=True)
        
        choice = st.sidebar.radio("Navigation", ["🏠 Mur Mondial", "💬 Messages Privés", "⚙️ Paramètres"])

        # --- PAGE MUR ---
        if choice == "🏠 Mur Mondial":
            st.header("🏠 Flux Mondial")
            with st.expander("📝 Publier une actualité"):
                t_mur = st.text_area("Votre message...")
                i_mur = st.text_input("Lien image (URL)")
                if st.button("PUBLIER MAINTENANT"):
                    requests.post(URL_MSG, json={"u": me, "m": t_mur, "i": i_mur, "d": "mondial", "t": time.time()})
                    st.rerun()
            
            st.write("---")
            msgs = charger(URL_MSG)
            if msgs:
                for k in reversed(list(msgs.keys())):
                    v = msgs[k]
                    if v.get("d") == "mondial":
                        p_v = get_pfp(v['u'], users_data)
                        st.markdown(f"""
                            <div style='background:rgba(255,255,255,0.05); padding:15px; border-radius:15px; margin-bottom:15px; border-left:4px solid #ff0000;'>
                                <img src='{p_v}' class='pfp-nav' style='width:30px; height:30px;'> <b>{v['u']}</b>
                                <p style='margin-top:10px;'>{v.get('m','')}</p>
                            </div>
                        """, unsafe_allow_html=True)
                        if v.get("i"): st.image(v["i"], use_container_width=True)

        # --- PAGE MESSAGES ---
        elif choice == "💬 Messages Privés":
            st.markdown(f"<img src='{pfp_me}' class='pfp-main'>", unsafe_allow_html=True)
            st.markdown(f"<h2 style='text-align:center;'>{me}</h2>", unsafe_allow_html=True)
            
            st.write("### 🔍 Rechercher un collaborateur")
            search = st.text_input("Pseudo de l'utilisateur...")
            if st.button("DÉMARRER LE CHAT"):
                if search in users_data and search != me:
                    st.session_state.chat_with = search
                    requests.patch(f"{URL_BASE}utilisateurs/{me}/amis.json", json={search: True})
                    st.rerun()
                else: st.warning("Utilisateur introuvable dans la base Bournemouth.")

            amis = users_data.get(me, {}).get("amis", {})
            if amis:
                st.sidebar.write("---")
                st.sidebar.write("👤 **Contacts Récents**")
                for ami in amis.keys():
                    if st.sidebar.button(f"Chat : {ami}", key=f"chatbtn_{ami}"):
                        st.session_state.chat_with = ami
                        st.rerun()

            if st.session_state.chat_with:
                target = st.session_state.chat_with
                st.write(f"### 💬 Discussion avec **{target}**")
                
                msgs = charger(URL_MSG)
                if msgs:
                    for k in list(msgs.keys()):
                        v = msgs[k]
                        if (v.get("u") == me and v.get("d") == target) or (v.get("u") == target and v.get("d") == me):
                            cls = "me" if v['u'] == me else "them"
                            st.markdown(f"<div class='bubble {cls}'><b>{v['u']}:</b> {v['m']}</div>", unsafe_allow_html=True)
                
                st.write(" ")
                m_in = st.text_input("Écrire un message...", key="input_msg")
                if st.button("ENVOYER 🚀", type="secondary"):
                    if m_in:
                        requests.post(URL_MSG, json={"u": me, "m": m_in, "d": target, "t": time.time()})
                        st.rerun()

        # --- PAGE PARAMÈTRES ---
        elif choice == "⚙️ Paramètres":
            st.header("⚙️ Gestion du Compte")
            new_pfp = st.text_input("Lien vers votre photo de profil (URL)", value=pfp_me)
            if st.button("SAUVEGARDER LE PROFIL"):
                requests.patch(f"{URL_BASE}utilisateurs/{me}.json", json={"pfp": new_pfp})
                st.success("Profil mis à jour !")
            
            if st.button("🚪 QUITTER LA SESSION"):
                st.session_state.user = None
                st.session_state.chat_with = None
                st.rerun()

# Rafraîchissement automatique
time.sleep(10)
st.rerun()
