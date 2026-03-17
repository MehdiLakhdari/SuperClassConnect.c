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
    /* Cacher les barres de recherche navigateur & menus Streamlit */
    #MainMenu, footer, header {visibility: hidden;}
    
    .stApp {
        background: linear-gradient(180deg, #4b0000 0%, #000000 100%);
        color: #ffffff;
    }
    
    /* Logo Startup Bournemouth Style */
    .logo-box {
        background: linear-gradient(135deg, #ff0000, #8b0000);
        width: 60px; height: 60px; border-radius: 15px;
        display: flex; align-items: center; justify-content: center;
        margin: 0 auto 10px auto; font-size: 35px; font-weight: bold;
        box-shadow: 0 0 20px rgba(255, 0, 0, 0.4);
    }

    /* Photos de profil */
    .pfp-nav { width: 45px; height: 45px; border-radius: 50%; object-fit: cover; border: 2px solid #ff0000; }
    .pfp-main { width: 120px; height: 120px; border-radius: 50%; object-fit: cover; border: 4px solid #ff0000; display: block; margin: 0 auto; }

    /* Bulles de Chat */
    .bubble { padding: 12px 18px; border-radius: 20px; margin-bottom: 8px; max-width: 70%; display: inline-block; }
    .me { background-color: #28a745; color: white; float: right; clear: both; }
    .them { background-color: #6f42c1; color: white; float: left; clear: both; }

    /* Boutons et Inputs */
    .stButton>button { background: #ff0000; color: white; border-radius: 12px; font-weight: bold; border:none; width: 100%; }
    div.stButton > button:first-child[kind="secondary"] { background: #007bff !important; }
    .stTextInput>div>div>input { background-color: rgba(255,255,255,0.1) !important; color: white !important; border-radius: 10px !important; }
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
    return u_info.get("pfp") if u_info.get("pfp") and u_info.get("pfp") != "" else "https://cdn-icons-png.flaticon.com/512/149/149071.png"

# --- 5. SYSTÈME DE NAVIGATION ---
users_data = charger(URL_USERS)
page_holder = st.empty() # Zone dynamique pour l'indépendance des pages

with page_holder.container():
    if st.session_state.user is None:
        # --- LOGIN / SIGNUP ---
        st.markdown("<div class='logo-box'>C</div><h1 style='text-align:center;'>CLASS CONNECT</h1>", unsafe_allow_html=True)
        t1, t2 = st.tabs(["Connexion", "Créer un Compte Startup"])
        
        with t1:
            u = st.text_input("Pseudo", key="l_u")
            p = st.text_input("Pass", type="password", key="l_p")
            if st.button("ACCÉDER AU SYSTÈME"):
                if u in users_data and str(users_data[u].get("mdp")) == str(p):
                    st.session_state.user = u
                    st.rerun()
                else: st.error("Identifiants incorrects.")

        with t2:
            st.write("### 🛡️ Formulaire de Sécurité")
            nu = st.text_input("Pseudo Unique", key="r_u")
            nm = st.text_input("Email Professionnel", key="r_m")
            np = st.text_input("Mot de passe", type="password", key="r_p")
            col_s, col_a = st.columns(2)
            ns = col_s.selectbox("Sexe", ["Homme", "Femme"])
            na = col_a.number_input("Âge", 13, 99)
            
            if st.button("ENVOYER CODE DE VÉRIFICATION"):
                if nu in users_data: st.error("Ce pseudo est déjà réservé !")
                elif not nu or not nm: st.warning("Remplis tous les champs !")
                else:
                    st.session_state.temp_code = random.randint(1000, 9999)
                    st.info(f"Vérification Google/Mail : Ton code est **{st.session_state.temp_code}**")
            
            if st.session_state.temp_code:
                code_in = st.text_input("Entrez le code à 4 chiffres")
                if st.button("VALIDER L'INSCRIPTION"):
                    if str(code_in) == str(st.session_state.temp_code):
                        requests.patch(URL_USERS, json={nu: {"mdp": np, "mail": nm, "sexe": ns, "age": na, "pfp": "", "amis": {}}})
                        st.success("Compte validé ! Connecte-toi.")
                        st.session_state.temp_code = None
                    else: st.error("Code invalide.")

    else:
        # --- INTERFACE CONNECTÉE ---
        me = st.session_state.user
        pfp_me = get_pfp(me, users_data)
        
        st.sidebar.markdown(f"<center><img src='{pfp_me}' class='pfp-nav'><br><b>Collaborateur : {me}</b></center>", unsafe_allow_html=True)
        menu = st.sidebar.radio("Navigation", ["🏠 Mur Mondial", "💬 Direct Messages", "⚙️ Paramètres"])

        # PAGE 1 : MUR
        if menu == "🏠 Mur Mondial":
            st.header("🏠 Flux de l'Entreprise")
            with st.expander("📸 Partager une image ou un texte"):
                txt = st.text_area("Légende")
                img = st.text_input("URL Image")
                if st.button("DIFFUSER"):
                    requests.post(URL_MSG, json={"u": me, "m": txt, "i": img, "d": "mondial", "t": time.time()})
                    st.rerun()
            
            msgs = charger(URL_MSG)
            for k in reversed(list(msgs.keys())):
                v = msgs[k]
                if v.get("d") == "mondial":
                    p_v = get_pfp(v['u'], users_data)
                    st.markdown(f"<div style='background:rgba(255,255,255,0.05); padding:15px; border-radius:12px; margin-bottom:10px;'><img src='{p_v}' class='pfp-nav'> <b>{v['u']}</b><br>{v.get('m','') if v.get('m') else ''}</div>", unsafe_allow_html=True)
                    if v.get("i"): st.image(v["i"])

        # PAGE 2 : MESSAGES
        elif menu == "💬 Direct Messages":
            st.markdown(f"<img src='{pfp_me}' class='pfp-main'>", unsafe_allow_html=True)
            st.markdown(f"<h2 style='text-align:center;'>{me}</h2>", unsafe_allow_html=True)
            
            # BARRE DE RECHERCHE CONTACTS
            st.write("### 🔍 Ajouter un contact")
            search = st.text_input("Entrez le pseudo exact d'un collègue...")
            if st.button("Lancer la discussion"):
                if search in users_data and search != me:
                    st.session_state.chat_with = search
                    requests.patch(f"{URL_BASE}utilisateurs/{me}/amis.json", json={search: True})
                    st.rerun()
                else: st.error("Utilisateur non trouvé.")

            # RÉPERTOIRE
            mes_amis = users_data.get(me, {}).get("amis", {})
            if mes_amis:
                st.write("---")
                st.write("### 📇 Tes discussions")
                for ami in mes_amis.keys():
                    if st.sidebar.button(f"👤 {ami}", key=f"s_{ami}"):
                        st.session_state.chat_with = ami
                        st.rerun()

            if st.session_state.chat_with:
                target = st.session_state.chat_with
                st.divider()
                st.subheader(f"💬 Chat avec {target}")
                
                # Zone de messages
                msgs = charger(URL_MSG)
                for k in list(msgs.keys()):
                    v = msgs[k]
                    if (v.get("u") == me and v.get("d") == target) or (v.get("u") == target and v.get("d") == me):
                        side = "me" if v['u'] == me else "them"
                        st.markdown(f"<div class='bubble {side}'><b>{v['u']}:</b> {v['m']}</div>", unsafe_allow_html=True)
                
                # Envoyer
                st.write("")
                msg_in = st.text_input("Écrire...", key="msg_in")
                if st.button("ENVOYER 🚀", type="secondary"):
                    if msg_in:
                        requests.post(URL_MSG, json={"u": me, "m": msg_in, "d": target, "t": time.time()})
                        st.rerun()

        # PAGE 3 : SETTINGS
        elif menu == "⚙️ Paramètres":
            st.header("⚙️ Paramètres")
            new_pfp = st.text_input("Lien vers ta photo de profil (URL)", value=pfp_me)
            if st.button("Mettre à jour la photo"):
                requests.patch(f"{URL_BASE}utilisateurs/{me}.json", json={"pfp": new_pfp})
                st.success("C'est fait !")
            if st.button("🚪 Déconnexion"):
                st.session_state.user = None
                st.rerun()

# Auto-refresh
time.sleep(10)
st.rerun()
