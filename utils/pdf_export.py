# ============================================
# EXPORT PDF - Rapports Professionnels
# MASI Futures Pro Simulator
# ============================================

from fpdf import FPDF
import datetime
import config

class PDFReport(FPDF):
    """Classe PDF personnalisée pour les rapports MASI Futures"""
    
    def header(self):
        # En-tête avec logo et titre
        self.set_font('Arial', 'B', 16)
        self.set_fill_color(30, 58, 95)  # Bleu institutionnel #1E3A5F
        self.set_text_color(255, 255, 255)
        self.cell(0, 15, f'  {config.APP_NAME}', 0, 1, 'L', fill=True)
        
        # Sous-titre
        self.set_font('Arial', 'I', 10)
        self.set_text_color(100, 100, 100)
        self.cell(0, 8, f'  Rapport généré le {datetime.datetime.now().strftime("%d/%m/%Y à %H:%M")}', 0, 1, 'L')
        
        # Ligne de séparation
        self.set_draw_color(30, 58, 95)
        self.line(10, 35, 200, 35)
        self.ln(10)
    
    def footer(self):
        # Pied de page
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f'  Page {self.page_no()}', 0, 0, 'L')
        self.cell(0, 10, f'{config.APP_NAME} v{config.APP_VERSION}  ', 0, 1, 'R')
    
    def chapter_title(self, title):
        # Titre de section
        self.set_font('Arial', 'B', 14)
        self.set_fill_color(240, 240, 240)
        self.set_text_color(30, 58, 95)
        self.cell(0, 10, f'  {title}', 0, 1, 'L', fill=True)
        self.ln(5)
    
    def chapter_body(self, body):
        # Corps de texte
        self.set_font('Arial', '', 11)
        self.set_text_color(0, 0, 0)
        self.multi_cell(0, 7, body)
        self.ln(5)
    
    def add_metric(self, label, value, unit=''):
        # Affiche une métrique
        self.set_font('Arial', 'B', 11)
        self.set_text_color(30, 58, 95)
        self.cell(70, 8, f'{label}:', 0, 0)
        self.set_font('Arial', '', 11)
        self.set_text_color(0, 0, 0)
        self.cell(0, 8, f'{value} {unit}', 0, 1)
    
    def add_info_box(self, text):
        # Boîte d'information
        self.set_fill_color(239, 246, 255)
        self.set_draw_color(30, 58, 95)
        self.set_font('Arial', 'I', 10)
        self.multi_cell(0, 6, text, 1, 'L', fill=True)
        self.ln(5)

# ────────────────────────────────────────────
# FONCTIONS D'EXPORT PAR MODULE
# ────────────────────────────────────────────

def export_pricing_pdf(spot, r, q, jours, F0, valeur_not, prime, cout_port, 
                       prix_marche=None, signal=None, strategie=None, filename=None):
    """
    Export PDF pour le module Pricing
    """
    if filename is None:
        filename = f"MASI_Futures_Pricing_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    
    pdf = PDFReport()
    pdf.add_page()
    
    # Titre
    pdf.chapter_title('Valorisation de Contrat Future MASI')
    
    # Paramètres
    pdf.chapter_body('Paramètres de Valorisation')
    pdf.add_metric('Niveau Spot (S₀)', f'{spot:,.2f}', 'points')
    pdf.add_metric('Taux sans risque (r)', f'{r*100:.2f}', '%')
    pdf.add_metric('Rendement dividendes (q)', f'{q*100:.2f}', '%')
    pdf.add_metric('Maturité (T)', f'{jours}', 'jours')
    pdf.ln(5)
    
    # Résultats
    pdf.chapter_body('Résultats')
    pdf.add_metric('Prix Future Théorique (F₀)', f'{F0:,.2f}', 'points')
    pdf.add_metric('Valeur Notionnelle', f'{valeur_not:,.0f}', 'MAD')
    pdf.add_metric('Prime vs Spot', f'{prime*100:+.2f}', '%')
    pdf.add_metric('Coût de Portage', f'{cout_port*100:+.2f}', '%')
    pdf.ln(5)
    
    # Arbitrage
    if prix_marche and signal:
        pdf.chapter_body('Analyse d\'Arbitrage')
        pdf.add_metric('Prix Marché Observé', f'{prix_marche:,.2f}', 'points')
        pdf.add_metric('Signal', signal, '')
        pdf.add_metric('Stratégie', strategie, '')
        pdf.ln(5)
    
    # Info box
    pdf.add_info_box(
        'Formule utilisée: F₀ = S₀ × e^((r−q)T)\n'
        'Document de référence: §7.1 - Introduction des Contrats Futures sur les Indices MASI et MASI20'
    )
    
    pdf.output(filename)
    return filename

def export_couverture_pdf(portefeuille, beta, spot, N_contrats, result, filename=None):
    """
    Export PDF pour le module Couverture
    """
    if filename is None:
        filename = f"MASI_Futures_Couverture_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    
    pdf = PDFReport()
    pdf.add_page()
    
    # Titre
    pdf.chapter_title('Stratégie de Couverture par Futures MASI')
    
    # Paramètres
    pdf.chapter_body('Paramètres du Portefeuille')
    pdf.add_metric('Valeur du Portefeuille (P)', f'{portefeuille:,.0f}', 'MAD')
    pdf.add_metric('Bêta (β)', f'{beta}', '')
    pdf.add_metric('Niveau MASI (S₀)', f'{spot:,.0f}', 'points')
    pdf.add_metric('Multiplicateur', f'{config.MULTIPLICATEUR}', 'MAD/point')
    pdf.ln(5)
    
    # Résultats
    pdf.chapter_body('Résultats de la Couverture')
    pdf.add_metric('Nombre de Contrats (N*)', f'{N_contrats:,}', 'contrats')
    pdf.add_metric('Valeur Notionnelle/Contrat', f'{spot * config.MULTIPLICATEUR:,.0f}', 'MAD')
    pdf.add_metric('Efficacité de Couverture', f'{result["efficacite"]*100:.1f}', '%')
    pdf.ln(5)
    
    # Simulation
    pdf.chapter_body('Simulation (Variation Marché)')
    pdf.add_metric('Variation Portefeuille', f'{result["variation_pf_pct"]:+.1f}', '%')
    pdf.add_metric('Perte/Gain Actions', f'{result["perte_portefeuille"]:+,.0f}', 'MAD')
    pdf.add_metric('Gain/Perte Futures', f'{result["gain_future"]:+,.0f}', 'MAD')
    pdf.add_metric('Valeur Finale Couverte', f'{result["valeur_finale"]:,.0f}', 'MAD')
    pdf.ln(5)
    
    # Info box
    pdf.add_info_box(
        f'Formule utilisée: N* = β × P / A\n'
        f'Où A = {spot:,.0f} × {config.MULTIPLICATEUR} = {spot * config.MULTIPLICATEUR:,.0f} MAD\n'
        f'Document de référence: §6.2 - Introduction des Contrats Futures sur les Indices MASI et MASI20'
    )
    
    pdf.output(filename)
    return filename

def export_marges_pdf(prix_entree, n_contrats, multiplicateur, n_jours, 
                      marge_initiale, marge_maintenance, simulation, filename=None):
    """
    Export PDF pour le module Marges
    """
    if filename is None:
        filename = f"MASI_Futures_Marges_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    
    pdf = PDFReport()
    pdf.add_page()
    
    # Titre
    pdf.chapter_title('Gestion des Marges et Appels de Marge')
    
    # Paramètres
    pdf.chapter_body('Paramètres de la Position')
    pdf.add_metric('Prix d\'Entrée', f'{prix_entree:,.0f}', 'points')
    pdf.add_metric('Nombre de Contrats', f'{n_contrats:,}', 'contrats')
    pdf.add_metric('Multiplicateur', f'{multiplicateur}', 'MAD/point')
    pdf.add_metric('Valeur Notionnelle', f'{prix_entree * n_contrats * multiplicateur:,.0f}', 'MAD')
    pdf.add_metric('Période de Simulation', f'{n_jours}', 'jours')
    pdf.ln(5)
    
    # Marges
    pdf.chapter_body('Exigences de Marge')
    pdf.add_metric('Marge Initiale', f'{marge_initiale:,.0f}', 'MAD')
    pdf.add_metric('Marge Maintenance', f'{marge_maintenance:,.0f}', 'MAD')
    pdf.ln(5)
    
    # Résultats simulation
    pdf.chapter_body('Résultats de la Simulation')
    pdf.add_metric('Nombre d\'Appels de Marge', f'{len(simulation["appels_marge"])}', 'appels')
    pdf.add_metric('Total Déposé', f'{simulation["total_depose"]:,.0f}', 'MAD')
    pdf.add_metric('P&L Total', f'{simulation["pnl_total"]:+,.0f}', 'MAD')
    pdf.ln(5)
    
    # Détails des appels
    if simulation['appels_marge']:
        pdf.chapter_body('Détail des Appels de Marge')
        for appel in simulation['appels_marge'][:5]:  # Max 5 pour éviter trop long
            pdf.add_metric(f'Jour {appel["jour"]}', f'{appel["montant"]:,.0f}', 'MAD')
        if len(simulation['appels_marge']) > 5:
            pdf.chapter_body(f'... et {len(simulation["appels_marge"]) - 5} autres appels')
    else:
        pdf.add_info_box('Aucun appel de marge détecté sur la période simulée.')
    
    pdf.ln(5)
    
    # Info box
    pdf.add_info_box(
        'Le marking-to-market ajuste quotidiennement les gains et pertes.\n'
        'Si le solde < marge maintenance → Appel de marge déclenché.\n'
        'Document de référence: §5.1 - Introduction des Contrats Futures sur les Indices MASI et MASI20'
    )
    
    pdf.output(filename)
    return filename

def export_risk_pdf(portefeuille_value, beta, volatilite, risk_analysis, filename=None):
    """
    Export PDF pour le module Risk Dashboard
    """
    if filename is None:
        filename = f"MASI_Futures_Risk_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    
    pdf = PDFReport()
    pdf.add_page()
    
    # Titre
    pdf.chapter_title('Risk Dashboard — Analyse de Risque de Marché')
    
    # Paramètres
    pdf.chapter_body('Paramètres du Portefeuille')
    pdf.add_metric('Valeur du Portefeuille', f'{portefeuille_value:,.0f}', 'MAD')
    pdf.add_metric('Bêta (β)', f'{beta}', '')
    pdf.add_metric('Volatilité Annuelle', f'{volatilite*100:.1f}', '%')
    pdf.ln(5)
    
    # Synthèse
    pdf.chapter_body('Synthèse du Risque')
    pdf.add_metric('Risque Global', risk_analysis['risque_global'], '')
    pdf.add_metric('VaR 95% (1 jour)', f'{risk_analysis["var_95_1j"]:,.0f}', 'MAD')
    pdf.add_metric('VaR 99% (1 jour)', f'{risk_analysis["var_99_1j"]:,.0f}', 'MAD')
    pdf.add_metric('CVaR 95%', f'{risk_analysis["cvar_95"]:,.0f}', 'MAD')
    pdf.add_metric('Delta Équivalent', f'{risk_analysis["delta_equivalent"]:,.0f}', 'points MASI')
    pdf.ln(5)
    
    # Stress testing
    pdf.chapter_body('Stress Testing — Scénarios de Crise')
    stress_df = risk_analysis['stress']
    for _, row in stress_df.iterrows():
        pdf.add_metric(row['Scénario'], f'{row["Perte Estimée (MAD)"]:,.0f}', 'MAD')
    pdf.ln(5)
    
    # Info box
    pdf.add_info_box(
        'La VaR (Value at Risk) mesure la perte maximale attendue avec un niveau de confiance donné.\n'
        'Le stress testing évalue l\'impact de scénarios de crise extrêmes.\n'
        'Document de référence: §1.2 - Introduction des Contrats Futures sur les Indices MASI et MASI20'
    )
    
    pdf.output(filename)
    return filename
