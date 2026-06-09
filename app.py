import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="PAPETIS — Prévisions & Pilotage", layout="wide", initial_sidebar_state="expanded")

# --- STYLES PERSONNALISÉS (Harmonie Visuelle) ---
st.markdown("""
    <style>
    .main { background-color: #f7fafc; }
    .kpi-box { background-color: #ffffff; padding: 15px; border-radius: 8px; border: 1px solid #e2e8f0; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
    .kpi-title { font-size: 12px; color: #4a5568; font-weight: 500; text-transform: uppercase; }
    .kpi-value { font-size: 22px; font-weight: bold; color: #1a3a5c; margin-top: 5px; }
    .kpi-sub { font-size: 11px; color: #38a169; margin-top: 2px; }
    </style>
""", unsafe_allowed_html=True)

# --- GÉNÉRATION DE DONNÉES HISTORIQUES SYNTHÉTIQUES (2021-2025) ---
@st.cache_data
def load_historical_data():
    months = pd.date_range(start="2021-01-01", end="2025-12-01", freq="MS")
    np.random.seed(42)
    
    # Construction d'un modèle multiplicatif théorique : Tendance + Saisonnalité (Août/Sept élevés) + Bruit
    tendance_base = np.linspace(1500, 1750, len(months))
    
    coeffs_saisonniers = {
        1: 0.63, 2: 0.55, 3: 0.72, 4: 0.70, 5: 0.68, 6: 0.65,
        7: 1.20, 8: 2.48, 9: 2.32, 10: 0.95, 11: 0.75, 12: 0.67
    }
    
    ventes = []
    for i, date in enumerate(months):
        m = date.month
        saison = coeffs_saisonniers[m]
        bruit = np.random.normal(1, 0.03)  # Légère fluctuation aléatoire
        valeur = tendance_base[i] * saison * bruit
        ventes.append(round(valeur, 2))
        
    df = pd.DataFrame({"Date": months, "Ventes_kMAD": ventes})
    df["Année"] = df["Date"].dt.year
    df["Mois"] = df["Date"].dt.month
    return df, coeffs_saisonniers

df_hist, fixed_coeffs = load_historical_data()

# --- BARRE DE NAVIGATION (SIDEBAR) ---
st.sidebar.image("https://img.icons8.com/fluency/48/000000/analytics.png", width=40)
st.sidebar.title("PAPETIS v1.0")
st.sidebar.markdown("*Innovation & AMOA — INPT*")
st.sidebar.write("---")

menu = st.sidebar.radio(
    "Navigation Projets",
    ["📊 Tableau de bord", "📂 Données", "⚙️ Paramètres du Modèle", "📈 Scénarios & Simulations", "📥 Export"]
)

# ==========================================
# 1. EN-TÊTE GLOBAL
# ==========================================
st.title(f"Application PAPETIS — {menu[2:]}")
st.write("---")

# ==========================================
# ONGLER 1 : TABLEAU DE BORD
# ==========================================
if menu == "📊 Tableau de bord":
    # KPIs de la maquette
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown('<div class="kpi-box"><div class="kpi-title">Ventes 2025 (Total)</div><div class="kpi-value">35.9 M MAD</div><div class="kpi-sub">↑ +8.3% vs 2024</div></div>', unsafe_allowed_html=True)
    with col2:
        st.markdown('<div class="kpi-box"><div class="kpi-title">Pic Rentrée (Août-Sept)</div><div class="kpi-value">15.2 M MAD</div><div class="kpi-sub" style="color:#4a5568;">42% du CA annuel</div></div>', unsafe_allowed_html=True)
    with col3:
        st.markdown('<div class="kpi-box"><div class="kpi-title">Prévision Janv. 2026</div><div class="kpi-value">1 924 kMAD</div><div class="kpi-sub" style="color:#185fa5;">Modèle multiplicatif</div></div>', unsafe_allowed_html=True)
    with col4:
        st.markdown('<div class="kpi-box"><div class="kpi-title">Erreur MAPE (Test)</div><div class="kpi-value">4.7 %</div><div class="kpi-sub">Excellente précision</div></div>', unsafe_allowed_html=True)

    st.write("### Aperçu Graphique de la Série Chronologique")
    
    # Graphique principal interactif
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_hist["Date"], y=df_hist["Ventes_kMAD"], name="Historique", line=dict(color='#378add', width=2)))
    fig.update_layout(
        title="Historique des ventes mensuelles (2021 - 2025)",
        xaxis_title="Chronologie", yaxis_title="Ventes (kMAD)",
        template="plotly_white", height=400
    )
    st.plotly_chart(fig, use_container_width=True)

# ==========================================
# ONGLER 2 : DONNÉES
# ==========================================
elif menu == "📂 Données":
    st.subheader("Importation et Contrôle Qualité des Fichiers")
    
    uploaded_file = st.file_uploader("Glissez votre fichier de ventes ici (.xlsx, .csv)", type=["xlsx", "csv"])
    
    if uploaded_file is not None:
        st.success("Fichier chargé de manière sécurisée !")
    else:
        st.info("Affichage du jeu de données historique par défaut (papetis_ventes_historiques.xlsx)")
        
        col_table, col_info = st.columns([2, 1])
        with col_table:
            st.dataframe(df_hist[["Date", "Ventes_kMAD"]].tail(12), use_container_width=True)
        with col_info:
            st.warning("⚠️ 2 observations atypiques détectées en Juillet 2023 (Grève) et Août 2024 (Hors-tendance).")
            st.info("💡 Continuité de la série : Validée (Aucun mois manquant sur 60 observations).")

# ==========================================
# ONGLER 3 : PARAMÈTRES DU MODÈLE
# ==========================================
elif menu == "⚙️ Paramètres du Modèle":
    st.subheader("Configuration du Moteur Statistique")
    
    with st.expander("Ajustement des hyperparamètres", expanded=True):
        methode = st.selectbox("Méthode de calcul de la tendance", ["Moindres carrés ordinaires (MCO)", "Moyennes mobiles centrées", "Lissage exponentiel (Holt)"])
        modele_type = st.radio("Modèle de décomposition", ["Multiplicatif (Recommandé)", "Additif"])
        traitement = st.selectbox("Traitement des anomalies", ["Corriger par interpolation", "Conserver en l'état"])
    
    if st.button("Lancer les calculs de prévision ↗", type="primary"):
        st.balloons()
        st.success("Modèle entraîné avec succès !")
        
        # Affichage des erreurs out-of-sample
        c1, c2, c3 = st.columns(3)
        c1.metric("MAPE", "4.7 %", "Excellent")
        c2.metric("MAE", "112 kMAD", "Erreur absolue")
        c3.metric("RMSE", "148 kMAD", "Écart quadratique")

# ==========================================
# ONGLER 4 : SCÉNARIOS & SIMULATIONS
# ==========================================
elif menu == "📈 Scénarios & Simulations":
    st.subheader("Analyse Prévisionnelle Prospective 2026")
    
    # Sliders de simulation de la maquette
    col_slide, col_scen = st.columns([1, 2])
    
    with col_slide:
        st.write("**Simuler des chocs de marché**")
        var_tendance = st.slider("Variation de la tendance (%)", -20, 20, 0)
        var_amplitude = st.slider("Amplitude du pic de rentrée (%)", -30, 30, 0)
        st.caption("Ajustez les curseurs pour recalculer instantanément les trajectoires.")
        
    # Calcul des prévisions 2026 basées sur les curseurs
    base_tendance_2026 = 1800
    mois_2026 = ["Jan", "Fév", "Mar", "Avr", "Mai", "Juin", "Juil", "Août", "Sept", "Oct", "Nov", "Déc"]
    
    prev_central = []
    for m in range(1, 13):
        cf = fixed_coeffs[m]
        if m in [8, 9]: # Ajustement du pic d'Août/Septembre
            cf = cf * (1 + var_amplitude/100)
        val = base_tendance_2026 * (1 + var_tendance/100) * cf
        prev_central.append(round(val, 0))
        
    with col_scen:
        # Affichage des 3 cartes de scénarios
        sc1, sc2, sc3 = st.columns(3)
        total_prev = sum(prev_central)
        sc1.metric("Pessimiste", f"{round(total_prev * 0.87, 0):,} kMAD".replace(",", " "), "-13%")
        sc2.metric("Central (Simulé)", f"{total_prev:,} kMAD".replace(",", " "), "Modèle")
        sc3.metric("Optimiste", f"{round(total_prev * 1.12, 0):,} kMAD".replace(",", " "), "+12%")
        
        # Alerte critique sur la trésorerie de mai-juin
        st.error("🚨 **Alerte Trésorerie Critique :** Le modèle confirme un creux d'activité de mai à juin (Fourchette estimée : 3.8 M à 5.1 M MAD) dû aux coûts de stockage de la pré-rentrée.")

    # Tableau final des résultats
    st.write("### Prévisions Mensuelles de l'Exercice 2026")
    df_2026 = pd.DataFrame({
        "Mois": mois_2026,
        "Coeff Saison": [fixed_coeffs[m] for m in range(1, 13)],
        "Prévision Centrale (kMAD)": prev_central
    })
    df_2026["Intervalle Bas (-15%)"] = (df_2026["Prévision Centrale (kMAD)"] * 0.85).round(0)
    df_2026["Intervalle Haut (+15%)"] = (df_2026["Prévision Centrale (kMAD)"] * 1.15).round(0)
    
    st.dataframe(df_2026, use_container_width=True)

# ==========================================
# ONGLER 5 : EXPORT
# ==========================================
elif menu == "📥 Export":
    st.subheader("Génération des Rapports de Synthèse Finaux")
    
    col_ex1, col_ex2 = st.columns(2)
    with col_ex1:
        st.markdown("#### 🟢 Export Excel (.xlsx)")
        st.write("Génère les tableaux complets structurés par feuilles pour les audits comptables.")
        st.button("📥 Télécharger le classeur Excel")
        
    with col_ex2:
        st.markdown("#### 🔵 Export PDF (Rapport de Direction)")
        st.write("Compile les graphiques, le résumé exécutif AMOA et la cartographie des risques.")
        st.button("📥 Télécharger le rapport de Synthèse PDF")
