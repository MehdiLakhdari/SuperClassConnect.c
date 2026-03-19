import streamlit as st
import requests
import time

# --- CONFIGURATION DU SON ---
# Si le son ne marche pas, c'est que le navigateur bloque l'autoplay. 
# L'utilisateur doit cliquer AU MOINS UNE FOIS sur la page pour activer le son.
URL_SON = "https://lasonotheque.org/moteur/telechargement.php?id=0162" # Son de notification clair

st.set_page_config(page_title="Connect Class", page_icon="🔔", layout="wide")

st.markdown(f"""
    <style>
    .stApp {{ background-color: #050505; color: white; }}
    
    /* 1. LA SOLUTION VISUELLE : LE BOUTON QUI CLIGNOTE ROUGE/ORANGE */
    @keyframes alerte {{
        0% {{ background-color: #FF8C00; box-shadow: 0 0 5px #FF8C00; }}
        50% {{ background-color: #D32F2F; box-shadow: 0 0 20px #D32F2F; border: 2px solid white; }}
        100% {{ background-color: #FF8C00; box-shadow: 0 0 5px #FF8C00; }}
    }}
    .btn-notif button {{
        animation: alerte 0.8s infinite !important;
        transform: scale(1.05);
    }}

    /* 2. STYLE DES CARTES */
    .msg-card {{ background: #111; padding: 15px; border-radius: 10px; border-left: 5px solid #D32F2F; margin-bottom: 10px; }}
    </style>
    """, unsafe_allow_html=True)

URL_BASE = "https://classconect-f1767-default-rtdb.europe-west1.firebasedatabase.app/"
URL_MSG = f"{URL_BASE}messages.json"
URL_USERS = f"{URL_BASE}utilisateurs.json"

if 'user' not in st.session_state: st.session_state.user = None
if 'last_count' not in st.session_state: st.session_state.last_count = 0

def get_db(url):
    try:
        r = requests.get(url, timeout=5)
        return r.json() if r.status_code == 200 else {}
    except: return {}

# --- LOGIQUE DE DÉTECTION ---
data_u = get_db(URL_USERS)
all_m = get_db(URL_MSG)
total_m = len(all_m) if all_m else 0

notif_active = False

if st.session_state.user:
    # Si un nouveau message est arrivé dans la base de données
    if total_m > st.session_state.last_count:
        derniere_cle = list(all_m.keys())[-1]
        dernier_msg = all_m[derniere_cle]
        
        # Si le message est pour MOI et que je ne suis pas déjà en train de le lire
        if dernier_msg.get("d") == st.session_state.user:
            notif_active = True
            # SOLUTION SONORE (Force l'audio)
            st.markdown(f'<audio autoplay><source src="{URL_SON}"></audio>', unsafe_allow_html=True)

if st.session_state.user is None:
    st.title("Connect Class 🔑")
    u = st.text_input("Pseudo")
    if st.button("Se connecter"):
        if u in data_u:
            st.session_state.user = u
            st.session_state.last_count = total_m # On ignore les vieux messages au début
            st.rerun()
else:
    me = st.session_state.user
    
    # NAVIGATION
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("🏠 MUR"): 
            st.session_state.last_count = total_m # On marque comme lu
            st.rerun()
            
    with c2:
        # 3. LA SOLUTION TEXTUELLE : LE COMPTEUR
        label = "💬 MESSAGES"
        if notif_active:
            label = "🔔 NOUVEAU MSG !"
            st.markdown('<div class="btn-notif">', unsafe_allow_html=True)
        
        if st.button(label):
            st.session_state.last_count = total_m # Reset la notif quand on clique
            st.rerun()
            
        if notif_active:
            st.markdown('</div>', unsafe_allow_html=True)

    # ... reste du code pour le chat ...
    st.write(f"Connecté en tant que : {me}")

# Rafraîchissement automatique toutes le 4 secondes
time.sleep(4)
st.rerun()
