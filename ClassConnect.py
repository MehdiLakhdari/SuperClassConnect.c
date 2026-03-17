import streamlit as st
import requests
import time

# --- 1. CONFIGURATION (METS TON LIEN ICI) ---
URL_FB = "https://classconect-f1767-default-rtdb.europe-west1.firebasedatabase.app/.json"

# --- 2. CONFIGURATION DE LA PAGE & THÈME ---
# Le mode sombre/clair se règle aussi dans les paramètres Streamlit (Haut à droite > Settings > Theme)
st.set_page_config(page_title="BCF Ultimate", page_icon="⚽", layout="centered")

# --- 3. INITIALISATION DE LA MÉMOIRE (SESSION) ---
if 'page' not in st.session_state:
    st.session_state.page = "login"
if 'pseudo' not in st.session_state:
    st.session_state.pseudo = ""

# --- 4. FONCTIONS UTILES ---
def envoyer_msg(destinataire, texte):
    data = {
        "expediteur": st.session_state.pseudo,
        "destinataire": destinataire, # "mondial" ou le nom d'un ami
        "msg": texte,
        "date": time.time()
    }
    requests.post(URL_FB, json=data)

# --- 5. PAGE DE CONNEXION (SIGN IN) ---
if st.session_state.page == "login":
    st.title("🔐 Connexion BCF")
    user = st.text_input("Pseudo")
    mdp = st.text_input("Mot de passe", type="password")
    
    if st.button("Se connecter"):
        # Tu peux changer "1234" par ton vrai mot de passe secret
        if mdp == "BCF2026": 
            st.session_state.pseudo = user
            st.session_state.page = "accueil"
            st.rerun()
        else:
            st.error("Mot de passe incorrect !")

# --- 6. INTERFACE PRINCIPALE ---
else:
    st.sidebar.title(f"⚽ {st.session_state.pseudo}")
    menu = st.sidebar.radio("Navigation", ["Chat Mondial", "Amis (Privé)", "Paramètres"])

    # --- SECTION : CHAT MONDIAL ---
    if menu == "Chat Mondial":
        st.header("🌍 Chat Mondial")
        with st.container():
            nouveau_msg = st.text_input("Ton message mondial...")
            if st.button("Envoyer 🚀"):
                if nouveau_msg:
                    envoyer_msg("mondial", nouveau_msg)
                    st.rerun()
        
        st.divider()
        # Affichage
        r = requests.get(URL_FB).json()
        if r:
            for key in reversed(list(r.keys())):
                item = r[key]
                if isinstance(item, dict) and item.get("destinataire") == "mondial":
                    with st.chat_message("user"):
                        st.write(f"**{item['expediteur']}**: {item['msg']}")

    # --- SECTION : AMIS (PRIVÉ) ---
    elif menu == "Amis (Privé)":
        st.header("👥 Discussions Privées")
        ami = st.text_input("Nom de l'ami avec qui discuter :")
        
        if ami:
            nouveau_prive = st.text_input(f"Message pour {ami}...")
            if st.button("Envoyer en privé"):
                if nouveau_prive:
                    envoyer_msg(ami, nouveau_prive)
                    st.success("Message envoyé !")
            
            st.divider()
            # Affichage uniquement des messages entre TOI et l'AMI
            r = requests.get(URL_FB).json()
            if r:
                for key in reversed(list(r.keys())):
                    item = r[key]
                    if isinstance(item, dict):
                        exp = item.get("expediteur")
                        dest = item.get("destinataire")
                        # On ne montre que si c'est entre vous deux
                        if (exp == st.session_state.pseudo and dest == ami) or (exp == ami and dest == st.session_state.pseudo):
                            with st.chat_message("user"):
                                st.write(f"**{exp}**: {item['msg']}")

    # --- SECTION : PARAMÈTRES ---
    elif menu == "Paramètres":
        st.header("⚙️ Paramètres")
        st.write("Pour changer le **Mode Sombre/Clair** :")
        st.info("Clique sur les 3 points en haut à droite > Settings > Theme > Light ou Dark.")
        if st.button("Se déconnecter"):
            st.session_state.page = "login"
            st.rerun()
