# backend/config.py

# ==================
# Currency Config
# ==================

# Exchange rate (update periodically)
USD_TO_INR = 96.31                    

def inr_to_usd(amount_inr):                 
    """Convert INR to USD for model"""
    return float(amount_inr) / USD_TO_INR

def usd_to_inr(amount_usd):                 
    """Convert USD to INR for display"""
    return float(amount_usd) * USD_TO_INR

# ==================
# Threshold Config   
# ==================
FRAUD_THRESHOLD       = 0.5                 
HIGH_RISK_THRESHOLD   = 0.7                 
MEDIUM_RISK_THRESHOLD = 0.4                 

# ==================
# App Config
# ==================
DEBUG = True                                
PORT  = 5000                                