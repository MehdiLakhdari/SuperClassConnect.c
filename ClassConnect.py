import streamlit as st
import requests
import time

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Connect Class", page_icon="😊", layout="wide")

st.markdown("""
    <style>
    header {visibility: hidden;}
    .stApp { background-color: #050505; color: white; }
    .nav-bar { background: #111; padding: 10px; border-radius: 10px; border-bottom: 3px solid #D32F2F; margin-bottom: 20px; text-align:center; }
    
    /* BOUTONS NAVIGATION - ORANGE CC */
    div[data-testid="stColumn"] .stButton>button { 
        background: linear-gradient(90deg, #FF8C00, #FF4500) !important; 
        color: white !important; border-radius: 8px; font-weight: bold; height: 50px; border: none;
    }

    /* NOTIF FLASH ROUGE */
    @keyframes blink { 0% {box-shadow: 0 0 5px #FF0000;} 50% {box-shadow: 0 0 20px #FF0000;} 100% {box-shadow: 0 0 5px #FF0000;} }
    .notif-active button { animation: blink 1s infinite !important; border: 1px solid white !important; }

    /* CARTES */
    .msg-card { background: #111; padding: 15px; border-radius: 10px; border
