import streamlit as st
import requests
import time

# --- 1. CONFIGURATION ---
# Ton lien Firebase (vérifie bien le .json à la fin)
URL_BASE = "https://classconect-f1767-default-rtdb.europe-west1.firebasedatabase.app/"
URL_MSG = f"{URL_BASE}messages.json"
URL_USERS = f"{URL_BASE}utilisateurs.json"

st.set_page_config(page_title="ClassConnect - BCF Network", page_icon="🚀", layout="centered")

# --- 2. STYLE PERSONNALISÉ (JAUNE & VERT) ---
st.markdown("""
    <style>
    /* Fond de l'application */
    .stApp { background-color: #f0f8ff; color: #1e3d1e; }
    
    /* Titres principaux */
    h1, h2, h3 { color: #1e3d1e; }

    /* Boutons personnalisés (Jaune Éclair) */
    .stButton>button { 
        background-color: #ffeb3b; /* Jaune */
        color: #1e3d1e; /* Texte Vert foncé */
        border-radius: 10px; 
        border: 2px solid #ffeb3b;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #fbc02d; /* Jaune plus foncé au survol */
        border: 2px solid #fbc02d;
    }

    /* Cartes de message (Vert Forêt clair) */
    .message-card { 
        background-color: #e8f5e9; /* Vert très clair */
        padding: 15px; 
        border-radius: 15px; 
        border-left: 5px solid #4caf50; /* Bordure Vert clair */
        margin-bottom: 10px; 
        color: #1e3d1e;
    }
    
    /* Input fields (Champs de texte) */
    .stTextInput>div>div>input {
        background-color: #ffffff;
        color: #1e3d1e;
        border: 1px solid #4caf50;
    }

    /* Sidebar (Menu latéral) */
    .css-1634w35 { background-color: #4caf50; } /* Fond Vert */
    .css-1634w35 .css-qri22k { color: #ffffff; } /* Texte Blanc */
    </style>
    """, unsafe_allow_html=True)

# --- 3. LOGO DE L'APPLICATION ---
def afficher_logo():
    # Remplace l'URL ci-dessous par l'URL de ton image de logo si tu en as une.
    # Sinon, voici une représentation textuelle stylisée.
    st.markdown("""
        <div style='text-align: center; margin-bottom: 20px;'>
            <h1 style='font-size: 50px; margin: 0;'>
                <span style='color: #ffeb3b;'>C</span><span style='color: #4caf50;'>C</span>
            </h1>
            <p style='font-size: 18px; color: #1e3d1e; font-weight: bold;'>ClassConnect</p>
        </div>
    """, unsafe_allow_html=True)

# --- 4. INITIALISATION DE LA SESSION ---
if 'user' not in st.session_state:
    st.session_state.user = None

# --- 5. FONCTIONS DE LA "WAR MACHINE" ---
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

def ajouter_like(msg_key):
    # Récupérer le message actuel
    url_msg_specifique = f"{URL_BASE}messages/{msg_key}.json"
    msg_data = requests.get(url_msg_specifique).json()
    if msg_data:
        # Incrémenter les likes
        current_likes = msg_data.get("l", 0)
        # Mettre à jour avec PATCH
        requests.patch(url_msg_specifique, json={"l": current_likes + 1})
        st.success("Cœur ❤️ ajouté !")

# --- 6. INTERFACE D'AUTHENTIFICATION ---
if st.session_state.user is None:
    afficher_logo()
    
    tab1, tab2 = st.tabs(["🔑 Se connecter", "📝 Créer un compte"])
    
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

# --- 7. INTERFACE PRINCIPALE (UNE FOIS CONNECTÉ) ---
else:
    afficher_logo()
    
    # Sidebar
    st.sidebar.markdown(f"<h2>⚽ <span style='color: #ffeb3b;'>{st.session_state.user}</span></h2>", unsafe_allow_html=True)
    menu = st.sidebar.selectbox("Navigation", ["🌍 Chat Mondial", "🔒 Messages Privés", "🎨 Thèmes & Infos"])

    # LOGIQUE CHAT
    if menu == "🌍 Chat Mondial":
        st.header("🌍 Chat Mondial")
        msg = st.text_input("Message...", placeholder="Dis quelque chose à la classe", key="global_msg")
        if st.button("Envoyer sur le mur 🚀"):
            if msg:
                requests.post(URL_MSG, json={
                    "u": st.session_state.user,
                    "m": msg,
                    "d": "mondial",
                    "t": time.time(),
                    "l": 0 # Initialiser les likes
                })
                st.rerun()

        st.divider()
        data = requests.get(URL_MSG).json()
        if data:
            for k in reversed(list(data.keys())):
                v = data[k]
                if v.get("d") == "mondial":
                    with st.container():
                        st.markdown(f"<div class='message-card'>", unsafe_allow_html=True)
                        st.write(f"👤 **{v['u']}** : {v['m']}")
                        
                        # Système de Like ❤️
                        current_likes = v.get("l", 0)
                        if st.button(f"❤️ {current_likes} Likes", key=f"like_{k}"):
                            ajouter_like(k)
                            st.rerun() # Rafraîchir pour voir le nouveau compte
                        
                        st.markdown("</div>", unsafe_allow_html=True)

    elif menu == "🔒 Messages Privés":
        st.header("🔒 Messages Privés")
        ami = st.text_input("Nom de l'ami :")
        if ami:
            msg_p = st.text_input(f"Message pour {ami}...", key="private_msg")
            if st.button("Envoyer en privé 🔒"):
                requests.post(URL_MSG, json={
                    "u": st.session_state.user,
                    "m": msg_p,
                    "d": ami,
                    "t": time.time(),
                    "l": 0
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
                        with st.container():
                            st.markdown(f"<div class='message-card'>", unsafe_allow_html=True)
                            st.write(f"👤 **{v['u']}** : {v['m']}")
                            
                            # Système de Like ❤️
                            current_likes = v.get("l", 0)
                            if st.button(f"❤️ {current_likes} Likes", key=f"like_{k}"):
                                ajouter_like(k)
                                st.rerun()
                                
                            st.markdown("</div>", unsafe_allow_html=True)

    elif menu == "🎨 Thèmes & Infos":
        st.info("💡 Mode Sombre/Clair : Va dans Settings > Theme en haut à droite.")
        if st.sidebar.button("Se déconnecter"):
            st.session_state.user = None
            st.rerun()
