import streamlit as st
import firebase_admin
from firebase_admin import credentials, auth, firestore
import datetime

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="Cabinet Médical Pro", page_icon="🏥", layout="wide")

# --- CONNEXION FIREBASE (Comme ClassConnect) ---
if not firebase_admin._apps:
    # Assure-toi que le fichier JSON est bien dans le dossier de ton projet
    cred = credentials.Certificate("serviceAccountKey.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()

# --- DESIGN CSS POUR LE CÔTÉ "MODERNE" ---
st.markdown("""
    <style>
    .main { background-color: #f8fafc; }
    .stButton>button { width: 100%; border-radius: 8px; background-color: #2563eb; color: white; border: none; }
    .stButton>button:hover { background-color: #1e40af; border: none; }
    .card { padding: 20px; border-radius: 15px; background-color: white; border: 1px solid #e2e8f0; }
    </style>
    """, unsafe_allow_html=True)

# --- BARRE LATÉRALE (NAVIGATION) ---
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/387/387561.png", width=100)
st.sidebar.title("Navigation")
page = st.sidebar.radio("Aller vers :", ["Accueil", "Biographie", "Prendre RDV", "Localisation", "Mon Compte"])

# --- SECTION : ACCUEIL ---
if page == "Accueil":
    st.title("🏥 Bienvenue au Cabinet Médical")
    st.write("Un service de santé moderne et connecté à Draria.")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('<div class="card"><h3>📅 RDV</h3><p>Réservez en ligne 24h/24.</p></div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="card"><h3>👨‍⚕️ Expert</h3><p>Une prise en charge complète.</p></div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="card"><h3>📍 Proche</h3><p>Situé au cœur de la ville.</p></div>', unsafe_allow_html=True)

# --- SECTION : BIOGRAPHIE ---
elif page == "Biographie":
    st.title("📖 À propos du Praticien")
    col_img, col_txt = st.columns([1, 2])
    with col_img:
        st.image("https://via.placeholder.com/300", caption="Dr. Nom du Médecin")
    with col_txt:
        st.subheader("Parcours & Expertise")
        st.write("""
        Diplômé de la Faculté de Médecine, le docteur propose des consultations spécialisées 
        depuis plus de 10 ans. Le cabinet utilise des technologies de pointe pour assurer 
        le meilleur suivi possible à chaque patient.
        """)

# --- SECTION : PRENDRE RDV ---
elif page == "Prendre RDV":
    st.title("📅 Réserver une consultation")
    with st.form("form_rdv"):
        nom = st.text_input("Nom complet du patient")
        date_rdv = st.date_input("Date souhaitée", min_value=datetime.date.today())
        heure_rdv = st.time_input("Heure souhaitée")
        message = st.text_area("Motif de la visite (optionnel)")
        
        submit = st.form_submit_button("Envoyer la demande")
        
        if submit:
            if nom:
                # Enregistrement dans la collection "rendez_vous" (Firestore)
                data = {
                    "nom": nom,
                    "date": str(date_rdv),
                    "heure": str(heure_rdv),
                    "motif": message,
                    "statut": "En attente",
                    "cree_le": datetime.datetime.now()
                }
                db.collection("rendez_vous").add(data)
                st.success(f"Merci {nom}, votre rendez-vous est enregistré !")
            else:
                st.error("Veuillez entrer votre nom.")

# --- SECTION : LOCALISATION ---
elif page == "Localisation":
    st.title("📍 Localisation du Cabinet")
    st.write("Adresse : 123 Rue Principale, Draria, Alger.")
    # Coordonnées approximatives de Draria
    map_data = {"lat":
