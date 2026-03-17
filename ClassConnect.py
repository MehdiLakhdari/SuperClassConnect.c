import streamlit as st
import requests
import time
from datetime import datetime

# --- 1. CONFIGURATION ---
URL_BASE = "https://classconect-f1767-default-rtdb.europe-west1.firebasedatabase.app/"
URL_MSG = f"{URL_BASE}messages.json"
URL_USERS = f"{URL_BASE}utilisateurs.json"

st.set_page_config(page_title="ClassConnect VIP", page_icon="📱", layout="centered")

# --- 2. STYLE "ULTRA DARK" REPOSANT ---
st.markdown("""
    <style>
    .stApp { background-color: #0b0e11; color: #e9eaeb; }
    [data-testid="stSidebar"] { background-color: #15191d; }
    .stButton>button { 
        background-color: #f0b90b; color: #000; border-radius: 8px; 
        font-weight: bold; width: 100%; border: none;
    }
    .message-card { 
        background-color: #1e2329; padding: 15px; border-radius: 12px; 
        border-left: 4px solid #f0b90b; margin-bottom: 10px;
    }
    .stTextInput>div>div>input { background-color: #2b3139; color: white; border: none; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. GESTION DE LA MÉMOIRE ---
if 'user_data' not in st.session_state:
    st.session_state.user_data = None

# --- 4. FONCTIONS ---
def charger_donnees(url):
    try:
        r = requests.get(url)
        return r.json() if r.status_code == 200 else {}
    except: return {}

def ajouter_like(key):
    msg_url = f"{URL_BASE}messages/{key}.json"
    data = requests.get(msg_url).json()
    if data:
        requests.patch(msg_url, json={"l": data.get("l", 0) + 1})

# --- 5. AUTHENTIFICATION (INSCRIPTION / CONNEXION) ---
if st.session_state.user_data is None:
    st.title("🛡️ ClassConnect")
    choix = st.radio("Menu", ["Connexion", "Créer un compte"], horizontal=True)
    
    if choix == "Créer un compte":
        with st.form("inscription"):
            st.subheader("📝 Formulaire d'inscription")
            new_u = st.text_input("Pseudo")
            new_e = st.text_input("Email")
            new_p = st.text_input("Mot de passe", type="password")
            col1, col2 = st.columns(2)
            with col1:
                sex = st.selectbox("Sexe", ["Homme", "Femme"])
                age = st.number_input("Âge", min_value=10, max_value=99)
            with col2:
                pays = st.text_input("Pays", value="Algérie")
                reg = st.text_input("Région")
            
            if st.form_submit_button("S'inscrire"):
                if new_u and new_p and new_e:
                    users = charger_donnees(URL_USERS)
                    if new_u in users: st.error("Pseudo déjà pris !")
                    else:
                        requests.patch(URL_USERS, json={new_u: {
                            "mdp": new_p, "email": new_e, "sexe": sex, 
                            "age": age, "pays": pays, "region": reg
                        }})
                        st.success("Compte créé ! Connecte-toi.")
                else: st.warning("Remplis les champs obligatoires !")

    else:
        with st.form("connexion"):
            st.subheader("🔑 Connexion")
            u = st.text_input("Pseudo")
            p = st.text_input("Mot de passe", type="password")
            if st.form_submit_button("Entrer"):
                users = charger_donnees(URL_USERS)
                if u in users and users[u]["mdp"] == p:
                    st.session_state.user_data = users[u]
                    st.session_state.user_data["pseudo"] = u
                    st.rerun()
                else: st.error("Identifiants incorrects")

# --- 6. INTERFACE PRINCIPALE ---
else:
    u_pseudo = st.session_state.user_data["pseudo"]
    st.sidebar.title(f"👤 {u_pseudo}")
    page = st.sidebar.selectbox("Navigation", ["🌍 Mur Mondial", "🔒 Privé", "📊 Mon Profil", "🚪 Déconnexion"])

    # AUTO-REFRESH (Toutes les 10 secondes)
    if page in ["🌍 Mur Mondial", "🔒 Privé"]:
        time.sleep(10)
        st.rerun()

    if page == "🌍 Mur Mondial":
        st.header("🌍 Mur Mondial")
        with st.expander("➕ Créer un post"):
            text = st.text_area("Ton message...")
            img = st.text_input("Lien image (URL) optionnel")
            if st.button("Publier"):
                if text or img:
                    requests.post(URL_MSG, json={
                        "u": u_pseudo, "m": text, "i": img, 
                        "d": "mondial", "t": time.time(), "l": 0
                    })
                    st.rerun()

        st.divider()
        msgs = charger_donnees(URL_MSG)
        if msgs:
            for k in reversed(list(msgs.keys())):
                v = msgs[k]
                if v.get("d") == "mondial":
                    st.markdown(f"<div class='message-card'><b>{v['u']}</b><br>{v.get('m','')}", unsafe_allow_html=True)
                    if v.get("i"): st.image(v["i"])
                    st.markdown(f"<small>{datetime.fromtimestamp(v['t']).strftime('%H:%M')}</small></div>", unsafe_allow_html=True)
                    if st.button(f"❤️ {v.get('l', 0)}", key=k):
                        ajouter_like(k)
                        st.rerun()

    elif page == "🔒 Privé":
        ami = st.sidebar.text_input("Ami à contacter :")
        if ami:
            st.header(f"💬 Chat avec {ami}")
            msg_p = st.text_input("Message privé...")
            if st.button("Envoyer"):
                requests.post(URL_MSG, json={"u": u_pseudo, "m": msg_p, "d": ami, "t": time.time(), "l": 0})
                st.rerun()
            
            msgs = charger_donnees(URL_MSG)
            if msgs:
                for k in reversed(list(msgs.keys())):
                    v = msgs[k]
                    if (v.get("u")==u_pseudo and v.get("d")==ami) or (v.get("u")==ami and v.get("d")==u_pseudo):
                        st.markdown(f"<div class='message-card'><b>{v['u']}</b>: {v['m']}</div>", unsafe_allow_html=True)

    elif page == "📊 Mon Profil":
        st.header("Mon Profil")
        d = st.session_state.user_data
        st.write(f"**Pseudo:** {d['pseudo']}")
        st.write(f"**Email:** {d['email']}")
        st.write(f"**Localisation:** {d['region']}, {d['pays']}")
        st.write(f"**Âge:** {d['age']} ans")

    elif page == "🚪 Déconnexion":
        st.session_state.user_data = None
        st.rerun()
