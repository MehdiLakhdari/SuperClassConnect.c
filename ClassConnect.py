import streamlit as st
import requests
import time

# --- CONFIGURATION (METS TON LIEN FIREBASE ICI) ---
URL_FB = "https://ton-projet.firebaseio.com/.json" 

st.set_page_config(page_title="BCF Connect", page_icon="⚽", layout="centered")

# --- STYLE PERSONNALISÉ (ROUGE ET NOIR) ---
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: white; }
    .stButton>button { background-color: #e63946; color: white; border-radius: 20px; width: 100%; }
    .message-card { background-color: #1b1e23; padding: 15px; border-radius: 15px; border-left: 5px solid #e63946; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- GESTION DE LA CONNEXION ---
if 'connecte' not in st.session_state:
    st.session_state.connecte = False

if not st.session_state.connecte:
    st.title("🔴 B.C.F CONNECT")
    st.subheader("Réseau Social Officiel - Bournemouth City")
    pseudo_input = st.text_input("Ton Pseudo :", placeholder="Ex: didou")
    
    if st.button("Entrer dans le Club 🚀"):
        if pseudo_input:
            st.session_state.pseudo = pseudo_input
            st.session_state.connecte = True
            st.rerun()
else:
    # --- INTERFACE PRINCIPALE ---
    st.title(f"⚽ Salut, {st.session_state.pseudo} !")
    
    # ZONE DE POST (Texte + Photo)
    with st.expander("Créer un nouveau post 📸", expanded=False):
        texte = st.text_area("Quoi de neuf dans le club ?")
        photo_url = st.text_input("Lien d'une photo (URL) :", placeholder="Colle un lien d'image ici...")
        
        if st.button("Publier sur le mur"):
            if texte or photo_url:
                data = {
                    "pseudo": st.session_state.pseudo,
                    "msg": texte,
                    "img": photo_url,
                    "likes": 0,
                    "date": time.time()
                }
                requests.post(URL_FB, json=data)
                st.success("Post envoyé !")
                time.sleep(1)
                st.rerun()

    st.divider()

    # --- FIL D'ACTUALITÉ ---
    st.subheader("Le Mur du Club")
    try:
        r = requests.get(URL_FB).json()
        if r:
            # On trie par date
            for key in reversed(list(r.keys())):
                item = r[key]
                if isinstance(item, dict) and ("msg" in item or "img" in item):
                    with st.container():
                        st.markdown(f"<div class='message-card'>", unsafe_allow_html=True)
                        st.write(f"👤 **{item.get('pseudo', 'Anonyme')}**")
                        
                        if item.get('msg'):
                            st.write(item['msg'])
                        
                        if item.get('img'):
                            st.image(item['img'], use_container_width=True)
                        
                        # SYSTÈME DE LIKE
                        nb_likes = item.get('likes', 0)
                        if st.button(f"❤️ {nb_likes} Likes", key=key):
                            # Mise à jour des likes dans Firebase
                            requests.patch(f"{URL_FB[:-5]}/{key}.json", json={"likes": nb_likes + 1})
                            st.rerun()
                        
                        st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.info("Aucun post pour le moment.")
    except Exception as e:
        st.error(f"Erreur : {e}")

    if st.sidebar.button("Déconnexion"):
        st.session_state.connecte = False
        st.rerun()
