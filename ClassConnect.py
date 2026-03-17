import streamlit as st
import requests
import time

# --- 1. CONFIGURATION ---
URL_BASE = "https://classconect-f1767-default-rtdb.europe-west1.firebasedatabase.app/"
URL_MSG = f"{URL_BASE}messages.json"
URL_USERS = f"{URL_BASE}utilisateurs.json"

st.set_page_config(page_title="ClassConnect Official", page_icon="⚽", layout="wide")

# --- 2. ÉTAT DE LA SESSION ---
if 'theme' not in st.session_state: st.session_state.theme = "sombre"
if 'user' not in st.session_state: st.session_state.user = None
if 'chat_with' not in st.session_state: st.session_state.chat_with = None

# --- 3. DESIGN "STARTUP & INSTAGRAM" ---
st.markdown("""
    <style>
    /* Cacher les éléments Streamlit pour le mode Pro */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    .stApp { background-color: #000000; color: #ffffff; }
    
    /* LOGO PERSONNALISÉ STARTUP */
    .logo-container {
        display: flex;
        align-items: center;
        justify-content: center;
        margin-bottom: 25px;
    }
    .logo-circle {
        background: linear-gradient(135deg, #ff0000, #8b0000);
        width: 50px;
        height: 50px;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-size: 30px;
        font-weight: bold;
        margin-right: 15px;
        box-shadow: 0 4px 15px rgba(255, 0, 0, 0.3);
    }
    .logo-text {
        font-size: 28px;
        font-weight: 900;
        background: linear-gradient(to right, #ffffff, #888888);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    /* DESIGN MESSAGES (INSTA STYLE) */
    .pfp-insta {
        width: 110px; height: 110px; border-radius: 50%; 
        object-fit: cover; border: 3px solid #e1306c; 
        display: block; margin: 0 auto 10px auto;
    }
    .message-bubble {
        padding: 12px 16px;
        border-radius: 20px;
        margin-bottom: 10px;
        max-width: 80%;
        font-size: 15px;
        line-height: 1.4;
    }
    
    /* BOUTONS */
    .stButton>button {
        border-radius: 12px;
        font-weight: bold;
        background: #262626;
        color: white;
        border: 1px solid #333;
        transition: 0.3s;
    }
    .stButton>button:hover { border-color: #ff0000; }
    
    /* BOUTON ENVOYER BLEU (INSTA) */
    div.stButton > button:first-child[kind="secondary"] {
        background-color: #0095f6 !important;
        color: white !important;
        border: none !important;
        margin-top: 10px;
    }
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
    return u_info.get("pfp") if u_info.get("pfp") else "https://cdn-icons-png.flaticon.com/512/149/149071.png"

# --- 5. LOGIQUE D'AFFICHAGE ---
if st.session_state.user is None:
    st.markdown("""
        <div class='logo-container'>
            <div class='logo-circle'>C</div>
            <div class='logo-text'>CLASS CONNECT</div>
        </div>
    """, unsafe_allow_html=True)
    t1, t2 = st.tabs(["Connexion", "Inscription"])
    with t1:
        u = st.text_input("Pseudo", key="l_u")
        p = st.text_input("Mot de passe", type="password", key="l_p")
        if st.button("SE CONNECTER"):
            users_data = charger(URL_USERS)
            if u in users_data and str(users_data[u].get("mdp")) == str(p):
                st.session_state.user = u
                st.rerun()
    with t2:
        nu = st.text_input("Nouveau Pseudo", key="r_u")
        np = st.text_input("Mot de passe", type="password", key="r_p")
        if st.button("CRÉER MON COMPTE"):
            requests.patch(URL_USERS, json={nu: {"mdp": np, "pfp": "", "amis": {}}})
            st.success("Compte créé avec succès !")

else:
    users_data = charger(URL_USERS)
    # Sidebar avec Logo Startup
    st.sidebar.markdown("""
        <div class='logo-container' style='justify-content: flex-start;'>
            <div class='logo-circle' style='width:35px; height:35px; font-size:20px;'>C</div>
            <div class='logo-text' style='font-size:18px;'>CLASS CONNECT</div>
        </div>
    """, unsafe_allow_html=True)
    
    page = st.sidebar.selectbox("Navigation", ["🏠 Mur Mondial", "💬 Direct Messages", "⚙️ Paramètres"])

    # --- MUR MONDIAL ---
    if page == "🏠 Mur Mondial":
        st.header("🏠 Mur Mondial")
        with st.expander("📸 Partager un moment"):
            t = st.text_area("Légende...")
            i = st.text_input("Lien de l'image (URL)")
            if st.button("PUBLIER SUR LE MUR"):
                requests.post(URL_MSG, json={"u": st.session_state.user, "m": t, "i": i, "d": "mondial", "t": time.time()})
                st.rerun()
        
        msgs = charger(URL_MSG)
        for k in reversed(list(msgs.keys())):
            v = msgs[k]
            if v.get("d") == "mondial":
                p = get_pfp(v['u'], users_data)
                st.markdown(f"""
                    <div style='background-color:#121212; padding:15px; border-radius:12px; border:1px solid #262626; margin-bottom:15px;'>
                        <img src='{p}' style='width:35px; height:35px; border-radius:50%; vertical-align:middle;'> 
                        <b style='margin-left:10px;'>{v['u']}</b><br><br>
                        {v.get('m','')}
                    </div>
                """, unsafe_allow_html=True)
                if v.get("i"): st.image(v["i"])

    # --- MESSAGES PRIVÉS (INSTA STYLE) ---
    elif page == "💬 Direct Messages":
        me = st.session_state.user
        st.markdown(f"<img src='{get_pfp(me, users_data)}' class='pfp-insta'>", unsafe_allow_html=True)
        st.markdown(f"<h2 style='text-align: center; margin-top:0;'>{me}</h2>", unsafe_allow_html=True)
        
        # Répertoire des contacts (Horizontal comme les Stories)
        mes_amis = users_data.get(me, {}).get("amis", {})
        if mes_amis:
            st.write("### Vos contacts")
            for ami in mes_amis.keys():
                if st.sidebar.button(f"👤 {ami}", key=f"side_{ami}"):
                    st.session_state.chat_with = ami
                    st.rerun()

        st.divider()
        if st.session_state.chat_with:
            target = st.session_state.chat_with
            st.subheader(f"Discussion avec {target}")
            
            # Affichage des messages (WhatsApp/Insta Mix)
            chat_container = st.container()
            with chat_container:
                msgs = charger(URL_MSG)
                if msgs:
                    for k in list(msgs.keys()):
                        v = msgs[k]
                        if (v.get("u") == me and v.get("d") == target) or (v.get("u") == target and v.get("d") == me):
                            color = "#28a745" if v['u'] == me else "#6f42c1"
                            st.markdown(f"<div style='margin-bottom:8px;'><span style='background-color:{color}; color:white; padding:10px 15px; border-radius:18px; display:inline-block;'><b>{v['u']}:</b> {v['m']}</span></div>", unsafe_allow_html=True)
            
            # LE CHAMP DE TEXTE PUIS LE BOUTON EN DESSOUS
            st.write("---")
            m_in = st.text_input("Écrire un message...", key="m_in")
            if st.button("Envoyer 🚀", key="btn_send", type="secondary"):
                if m_in:
                    requests.post(URL_MSG, json={"u": me, "m": m_in, "d": target, "t": time.time()})
                    st.rerun()

    # --- PARAMÈTRES ---
    elif page == "⚙️ Paramètres":
        st.header("⚙️ Paramètres de l'entreprise")
        if st.button("🚪 Déconnexion"):
            st.session_state.user = None
            st.rerun()

# Auto-Refresh
time.sleep(10)
st.rerun()
