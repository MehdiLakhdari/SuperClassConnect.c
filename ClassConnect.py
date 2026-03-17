import streamlit as st
import requests
import time
from datetime import datetime

# --- 1. CONFIGURATION ---
URL_BASE = "https://classconect-f1767-default-rtdb.europe-west1.firebasedatabase.app/"
URL_MSG = f"{URL_BASE}messages.json"
URL_USERS = f"{URL_BASE}utilisateurs.json"

st.set_page_config(page_title="ClassConnect Insta Pro", page_icon="📸", layout="centered")

# --- 2. GESTION DU THÈME ---
if 'theme' not in st.session_state: st.session_state.theme = "sombre"
if 'user' not in st.session_state: st.session_state.user = None
if 'chat_with' not in st.session_state: st.session_state.chat_with = None

if st.session_state.theme == "sombre":
    bg, txt, btn, card, input_bg = "#000000", "#ffffff", "#bc2a8d", "#121212", "#262626"
else:
    bg, txt, btn, card, input_bg = "#ffffff", "#000000", "#e1306c", "#fafafa", "#efefef"

st.markdown(f"""
    <style>
    .stApp {{ background-color: {bg}; color: {txt}; }}
    .message-card {{ 
        background-color: {card}; padding: 12px; border-radius: 10px; 
        margin-bottom: 8px; border: 0.5px solid #333; color: {txt};
    }}
    .pfp-large {{
        width: 100px; height: 100px; border-radius: 50%; 
        object-fit: cover; border: 3px solid {btn}; display: block; margin: 0 auto;
    }}
    .pfp-mini {{
        width: 35px; height: 35px; border-radius: 50%; 
        object-fit: cover; margin-right: 10px;
    }}
    .stButton>button {{ border-radius: 8px; font-weight: bold; border: none; }}
    .del-btn>button {{ background-color: #ff4b4b !important; color: white !important; font-size: 10px !important; }}
    </style>
    """, unsafe_allow_html=True)

# --- 3. FONCTIONS ---
def charger(url):
    try:
        r = requests.get(url)
        return r.json() if r.status_code == 200 and r.json() else {}
    except: return {}

def get_pfp(pseudo, users_data):
    user_info = users_data.get(pseudo, {})
    return user_info.get("pfp") if user_info.get("pfp") else "https://cdn-icons-png.flaticon.com/512/149/149071.png"

def supprimer_post(msg_id):
    requests.delete(f"{URL_BASE}messages/{msg_id}.json")

# --- 4. AUTHENTIFICATION ---
users_data = charger(URL_USERS)

if st.session_state.user is None:
    st.title("📸 ClassConnect")
    tab1, tab2 = st.tabs(["Connexion", "Inscription"])
    with tab1:
        u = st.text_input("Pseudo")
        p = st.text_input("Mot de passe", type="password")
        if st.button("Se connecter"):
            if u in users_data and str(users_data[u].get("mdp")) == str(p):
                st.session_state.user = u
                st.rerun()
            else: st.error("Identifiants incorrects.")
    with tab2:
        nu = st.text_input("Nouveau Pseudo")
        np = st.text_input("Mot de passe", type="password")
        if st.button("S'inscrire"):
            if nu and np:
                requests.patch(URL_USERS, json={nu: {"mdp": np, "pfp": "", "amis": {}}})
                st.success("Compte créé !")

# --- 5. LOGIQUE DES PAGES ---
else:
    me = st.session_state.user
    my_pfp = get_pfp(me, users_data)
    
    page = st.sidebar.selectbox("Aller vers", ["🏠 Mur Mondial", "💬 Direct Messages", "⚙️ Paramètres"])

    # --- PAGE 1 : MUR MONDIAL ---
    if page == "🏠 Mur Mondial":
        st.header("🏠 Mur Mondial")
        with st.expander("📝 Créer une publication"):
            t = st.text_area("Légende...")
            i = st.text_input("URL de l'image")
            if st.button("Partager"):
                requests.post(URL_MSG, json={"u": me, "m": t, "i": i, "d": "mondial", "t": time.time()})
                st.rerun()
        
        msgs = charger(URL_MSG)
        for k in reversed(list(msgs.keys())):
            v = msgs[k]
            if v.get("d") == "mondial":
                p = get_pfp(v['u'], users_data)
                st.markdown(f"<div class='message-card'><img src='{p}' class='pfp-mini'><b>{v['u']}</b></div>", unsafe_allow_html=True)
                if v.get("m"): st.write(v["m"])
                if v.get("i"): st.image(v["i"])
                
                # Option de suppression si c'est MON post
                if v.get("u") == me:
                    if st.button(f"🗑️ Supprimer mon post", key=f"del_{k}"):
                        supprimer_post(k)
                        st.rerun()

    # --- PAGE 2 : MESSAGES PRIVÉS ---
    elif page == "💬 Direct Messages":
        st.markdown(f"<img src='{my_pfp}' class='pfp-large'>", unsafe_allow_html=True)
        st.markdown(f"<h2 style='text-align: center;'>{me}</h2>", unsafe_allow_html=True)
        
        st.divider()
        search = st.text_input("🔍 Rechercher ou ajouter un contact...")
        if search and st.button(f"Discuter avec {search}"):
            st.session_state.chat_with = search
            requests.patch(f"{URL_BASE}utilisateurs/{me}/amis.json", json={search: True})
            st.rerun()

        mes_amis = users_data.get(me, {}).get("amis", {})
        if mes_amis:
            st.write("### Vos Discussions")
            for ami_nom in mes_amis.keys():
                pfp_ami = get_pfp(ami_nom, users_data)
                col_a, col_b = st.columns([1, 5])
                col_a.image(pfp_ami, width=45)
                if col_b.button(f"{ami_nom}", key=f"chat_{ami_nom}"):
                    st.session_state.chat_with = ami_nom
                    st.rerun()

        if st.session_state.chat_with:
            st.divider()
            target = st.session_state.chat_with
            st.subheader(f"💬 Conversation : {target}")
            
            msg_input = st.text_input("Votre message...", key="msg_input")
            if st.button("Envoyer"):
                if msg_input:
                    requests.post(URL_MSG, json={"u": me, "m": msg_input, "d": target, "t": time.time()})
                    st.rerun()
            
            msgs = charger(URL_MSG)
            for k in reversed(list(msgs.keys())):
                v = msgs[k]
                if (v.get("u") == me and v.get("d") == target) or (v.get("u") == target and v.get("d") == me):
                    # CORRECTION : TOUT À GAUCHE
                    color = btn if v['u'] == me else "#333333"
                    pseudo_label = "Moi" if v['u'] == me else v['u']
                    st.markdown(f"""
                        <div style='text-align: left; margin-bottom: 5px;'>
                            <span style='background-color:{color}; color:white; padding:8px 12px; border-radius:12px; display:inline-block;'>
                                <small><b>{pseudo_label}:</b></small><br>{v['m']}
                            </span>
                        </div>
                    """, unsafe_allow_html=True)

    # --- PAGE 3 : PARAMÈTRES ---
    elif page == "⚙️ Paramètres":
        st.header("⚙️ Paramètres")
        new_pfp = st.text_input("Lien de ta photo de profil (URL)", value=my_pfp)
        if st.button("Mettre à jour le profil"):
            requests.patch(f"{URL_BASE}utilisateurs/{me}.json", json={"pfp": new_pfp})
            st.success("C'est fait !")
        
        st.divider()
        c1, c2 = st.columns(2)
        if c1.button("🌙 Sombre"): st.session_state.theme = "sombre"; st.rerun()
        if c2.button("☀️ Clair"): st.session_state.theme = "clair"; st.rerun()
        
        if st.button("🚪 Se déconnecter"):
            st.session_state.user = None
            st.rerun()

    time.sleep(10)
    st.rerun()
