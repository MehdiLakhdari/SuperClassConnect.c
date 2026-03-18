import streamlit as st
import requests
import time

# --- 1. CONFIGURATION PLEIN ÉCRAN & DESIGN ---
st.set_page_config(page_title="Connect Class Algeria", page_icon="⚽", layout="wide")

st.markdown("""
    <style>
    /* Super Plein Écran */
    header {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stApp { background-color: #0e1117; color: white; }
    
    /* LOGO ORANGE PRO */
    .logo-box {
        background: linear-gradient(135deg, #FF8C00 0%, #FF4500 100%);
        width: 60px; height: 60px; border-radius: 15px;
        display: flex; align-items: center; justify-content: center;
        margin: 0 auto; font-size: 40px; font-weight: bold; color: white;
        box-shadow: 0 5px 15px rgba(255, 69, 0, 0.3);
    }
    .logo-text { 
        font-family: 'Trebuchet MS', sans-serif;
        font-size: 22px; font-weight: bold; color: #FF8C00; 
        text-align: center; margin-top: 5px; text-transform: uppercase;
    }

    /* BOUTONS STABLES */
    .stButton>button { 
        background: linear-gradient(90deg, #FF8C00, #FF4500) !important; 
        color: white !important; border-radius: 10px; border: none; 
        font-weight: bold; width: 100%; height: 40px; transition: 0.2s;
    }
    .stButton>button:hover { transform: scale(1.03); box-shadow: 0 4px 12px rgba(255, 69, 0, 0.4); }
    
    /* CARTES DU MUR */
    .msg-card { 
        background: #1c1f26; padding: 15px; border-radius: 12px; 
        margin-bottom: 15px; border-left: 5px solid #FF8C00;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }

    /* Bulles de Chat */
    .chat-bubble { padding: 10px; border-radius: 12px; display: inline-block; margin: 5px; max-width: 80%; }
    .bubble-me { background-color: #FF8C00; color: white; float: right; }
    .bubble-them { background-color: #333; color: white; float: left; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. INITIALISATION & CACHE ---
URL_BASE = "https://classconect-f1767-default-rtdb.europe-west1.firebasedatabase.app/"
URL_MSG = f"{URL_BASE}messages.json"
URL_USERS = f"{URL_BASE}utilisateurs.json"

if 'user' not in st.session_state: st.session_state.user = None
if 'page' not in st.session_state: st.session_state.page = "Mur"
if 'chat_with' not in st.session_state: st.session_state.chat_with = None

# Cache de 10 secondes pour les données pour éviter le lag
@st.cache_data(ttl=10)
def charger(url):
    try:
        r = requests.get(url, timeout=5)
        return r.json() if r.status_code == 200 and r.json() else {}
    except: return {}

# --- 3. INTERFACE DE CONNEXION ---
data_u = charger(URL_USERS)

if st.session_state.user is None:
    st.markdown("<div class='logo-box'>C</div><div class='logo-text'>Class Connect Algeria</div>", unsafe_allow_html=True)
    tab_log, tab_reg = st.tabs(["Connexion", "Inscription"])
    
    with tab_log:
        u = st.text_input("Pseudo", key="l_u")
        p = st.text_input("Mot de passe", type="password", key="l_p")
        if st.button("REJOINDRE LE CLUB"):
            if u in data_u and str(data_u[u].get("mdp")) == str(p):
                st.session_state.user = u
                st.rerun()
            else: st.error("Identifiants incorrects.")

    with tab_reg:
        nu = st.text_input("Choisis un Pseudo unique", key="n_u")
        np = st.text_input("Choisis un Mot de passe", type="password", key="n_p")
        club = st.selectbox("Ton Club de cœur", ["Paris SG", "Juventus", "Arsenal"])
        if st.button("S'INSCRIRE & ENTRER DIRECTEMENT"):
            if nu and np:
                # Création du compte avec club et liste d'amis vide
                requests.patch(URL_USERS, json={nu: {"mdp": np, "club": club, "amis": {}}})
                # Auto-login
                st.session_state.user = nu
                st.balloons()
                st.rerun()

# --- 4. INTERFACE PRINCIPALE (SIDEBAR + PAGES) ---
else:
    me = st.session_state.user
    my_club = data_u.get(me, {}).get("club", "Fan")

    # BARRE LATÉRALE DE NAVIGATION ET CONTACTS
    with st.sidebar:
        st.markdown("<div class='logo-box' style='width:50px; height:50px; font-size:30px;'>C</div>", unsafe_allow_html=True)
        st.markdown(f"<h3 style='text-align:center;'>{me}</h3>", unsafe_allow_html=True)
        st.write(f"⚽ Club : **{my_club}**")
        st.divider()
        
        # Navigation principale
        if st.button("🏠 MUR MONDIAL", key="nav_mur"): 
            st.session_state.page = "Mur"
            st.rerun()
        if st.button("⚙️ PARAMÈTRES", key="nav_param"): 
            st.session_state.page = "Param"
            st.rerun()
        
        st.divider()
        st.write("👤 **Discussions Directes**")
        
        # Recherche/Ajout de contact
        new_contact = st.text_input("Ajouter un pseudo exact", key="add_contact")
        if st.button("Lancer Chat", key="btn_add_contact"):
            if new_contact in data_u and new_contact != me:
                # Ajouter à la liste d'amis dans Firebase
                requests.patch(f"{URL_BASE}utilisateurs/{me}/amis.json", json={new_contact: True})
                st.session_state.chat_with = new_contact
                st.session_state.page = "Chat"
                st.rerun()
            else: st.error("Utilisateur introuvable.")

        # Liste des contacts existants
        mes_amis = data_u.get(me, {}).get("amis", {})
        if mes_amis:
            for ami in mes_amis.keys():
                if st.button(f"Chat : {ami}", key=f"chat_{ami}"):
                    st.session_state.chat_with = ami
                    st.session_state.page = "Chat"
                    st.rerun()
        
        st.divider()
        if st.button("🚪 DÉCONNEXION", key="nav_logout"):
            st.session_state.user = None
            st.session_state.chat_with = None
            st.rerun()

    # --- LOGIQUE DES PAGES ---
    
    # PAGE 1 : LE MUR AVEC IMAGES
    if st.session_state.page == "Mur":
        st.title("🏠 Mur Mondial")
        with st.expander("📝 Publier (Texte + Image optionnelle)"):
            txt = st.text_area("Légende de ton post...")
            img_url = st.text_input("Lien URL de ton image (ex: ImgBB, PostImage)")
            if st.button("POSTER 🚀", key="btn_post_mur"):
                if txt or img_url:
                    requests.post(URL_MSG, json={"u": me, "c": my_club, "m": txt, "i": img_url, "d": "mondial", "t": time.time()})
                    # On force le rechargement du cache
                    st.cache_data.clear()
                    st.rerun()
        
        msgs = charger(URL_MSG)
        if msgs:
            for k in reversed(list(msgs.keys())):
                v = msgs[k]
                if v.get("d") == "mondial":
                    st.markdown(f"""
                        <div class='msg-card'>
                            <b style='color:#FF8C00;'>@{v['u']}</b> <small>({v.get('c','Fan')})</small><br>
                            <p style='margin-top:10px; font-size:16px;'>{v.get('m','')}</p>
                        </div>
                    """, unsafe_allow_html=True)
                    # Affichage de l'image si elle existe
                    if v.get("i"):
                        st.image(v["i"], use_container_width=True)
                    st.divider()

    # PAGE 2 : LE CHAT PRIVÉ
    elif st.session_state.page == "Chat":
        target = st.session_state.chat_with
        if target:
            st.title(f"💬 Chat avec {target}")
            
            # Flux messages
            msgs = charger(URL_MSG)
            st.markdown("<div style='overflow-y: auto; height: 400px;'>", unsafe_allow_html=True)
            if msgs:
                for k, v in msgs.items():
                    if (v.get("u") == me and v.get("d") == target) or (v.get("u") == target and v.get("d") == me):
                        side = "me" if v['u'] == me else "them"
                        cls = "bubble-me" if side == "me" else "bubble-them"
                        # Correction de l'alignement pour les bulles
                        st.markdown(f"<div style='text-align: {'right' if side == 'me' else 'left'};'><div class='chat-bubble {cls}'>{v['m']}</div></div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Envoi
            msg_in = st.text_input("Écrire...", key="chat_in_msg")
            if st.button("ENVOYER 📩", key="btn_send_chat"):
                if msg_in:
                    requests.post(URL_MSG, json={"u": me, "m": msg_in, "d": target, "t": time.time()})
                    st.cache_data.clear()
                    st.rerun()
        else:
            st.warning("Sélectionne un contact dans la barre latérale.")

    # PAGE 3 : PARAMÈTRES (Simple)
    elif st.session_state.page == "Param":
        st.title("⚙️ Paramètres")
        st.write(f"Utilisateur : **{me}**")
        st.write(f"Club : **{my_club}**")
        # Tu pourras ajouter ici le changement de photo de profil plus tard

# Refresh lent manuel pour la stabilité, mais cache de 10s pour charger()
time.sleep(10)
st.rerun()
