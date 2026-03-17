import streamlit as st
import requests
import time

# --- 1. CONFIGURATION ---
# Ton lien Firebase (vérifie bien le .json à la fin)
URL_BASE = "https://classconect-f1767-default-rtdb.europe-west1.firebasedatabase.app/"
URL_MSG = f"{URL_BASE}messages.json"
URL_USERS = f"{URL_BASE}utilisateurs.json"

st.set_page_config(page_title="BCF Network", page_icon="🚀")

# --- 2. INITIALISATION DE LA SESSION ---
if 'user' not in st.session_state:
    st.session_state.user = None
if 'page_auth' not in st.session_state:
    st.session_state.page_auth = "login"

# --- 3. FONCTIONS DE LA "WAR MACHINE" ---
def recuperer_utilisateurs():
    r = requests.get(URL_USERS).json()
    return r if r else {}

def creer_compte(pseudo, mdp):
    users = recuperer_utilisateurs()
    if pseudo in users:
        return False
    # On enregistre le nouvel utilisateur
    requests.patch(URL_USERS, json={pseudo: {"mdp": mdp}})
    return True

def verifier_connexion(pseudo, mdp):
    users = recuperer_utilisateurs()
    if pseudo in users and users[pseudo]["mdp"] == mdp:
        return True
    return False

# --- 4. INTERFACE D'AUTHENTIFICATION ---
if st.session_state.user is None:
    st.title("🛡️ BCF Security Center")
    
    tab1, tab2 = st.tabs(["Se connecter", "Créer un compte"])
    
    with tab1:
        u_log = st.text_input("Pseudo", key="log_u")
        p_log = st.text_input("Mot de passe", type="password", key="log_p")
        if st.button("Connexion 🔑"):
            if verifier_connexion(u_log, p_log):
                st.session_state.user = u_log
                st.success(f"Bienvenue {u_log} !")
                time.sleep(1)
                st.rerun()
            else:
                st.error("Pseudo ou mot de passe incorrect.")

    with tab2:
        u_reg = st.text_input("Choisis un pseudo", key="reg_u")
        p_reg = st.text_input("Choisis un mot de passe", type="password", key="reg_p")
        if st.button("S'inscrire 📝"):
            if u_reg and p_reg:
                if creer_compte(u_reg, p_reg):
                    st.success("Compte créé ! Connecte-toi maintenant.")
                else:
                    st.error("Ce pseudo est déjà pris.")
            else:
                st.warning("Remplis toutes les cases !")

# --- 5. INTERFACE PRINCIPALE (UNE FOIS CONNECTÉ) ---
else:
    st.sidebar.title(f"⚽ {st.session_state.user}")
    menu = st.sidebar.selectbox("Navigation", ["🌍 Chat Mondial", "🔒 Messages Privés", "🎨 Thèmes & Infos"])

    # LOGIQUE CHAT
    if menu == "🌍 Chat Mondial":
        st.header("Chat Mondial")
        msg = st.text_input("Message...", placeholder="Dis quelque chose à la classe")
        if st.button("Envoyer"):
            if msg:
                requests.post(URL_MSG, json={
                    "u": st.session_state.user,
                    "m": msg,
                    "d": "mondial",
                    "t": time.time()
                })
                st.rerun()

        st.divider()
        data = requests.get(URL_MSG).json()
        if data:
            for k in reversed(list(data.keys())):
                v = data[k]
                if v.get("d") == "mondial":
                    with st.chat_message("user"):
                        st.write(f"**{v['u']}** : {v['m']}")

    elif menu == "🔒 Messages Privés":
        st.header("Messages Privés")
        ami = st.text_input("Nom de l'ami :")
        if ami:
            msg_p = st.text_input(f"Message pour {ami}...")
            if st.button("Envoyer en privé"):
                requests.post(URL_MSG, json={
                    "u": st.session_state.user,
                    "m": msg_p,
                    "d": ami,
                    "t": time.time()
                })
                st.success("Envoyé !")

            st.divider()
            data = requests.get(URL_MSG).json()
            if data:
                for k in reversed(list(data.keys())):
                    v = data[k]
                    # On affiche si : (Moi vers Ami) OU (Ami vers Moi)
                    if (v.get("u") == st.session_state.user and v.get("d") == ami) or \
                       (v.get("u") == ami and v.get("d") == st.session_state.user):
                        with st.chat_message("user"):
                            st.write(f"**{v['u']}** : {v['m']}")

    elif menu == "🎨 Thèmes & Infos":
        st.info("💡 Mode Sombre/Clair : Va dans Settings > Theme en haut à droite.")
        if st.button("Se déconnecter"):
            st.session_state.user = None
            st.rerun()
