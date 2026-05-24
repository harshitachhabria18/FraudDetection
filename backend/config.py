# backend/config.py

# ==================
# Currency Config
# ==================

# Exchange rate (update periodically)
USD_TO_INR = 96.31

def inr_to_usd(amount_inr):
    """Convert INR to USD for display only"""
    return float(amount_inr) / USD_TO_INR

def usd_to_inr(amount_usd):
    """Convert USD to INR for display"""
    return float(amount_usd) * USD_TO_INR


# ==================
# Threshold Config
# ==================
# Calibrated via Precision-Recall curve on PaySim test set
# Best F1: 0.9108 | Precision: 0.9307 | Recall: 0.8917

FRAUD_THRESHOLD       = 0.5
HIGH_RISK_THRESHOLD   = 0.6
MEDIUM_RISK_THRESHOLD = 0.5

# ==================
# App Config
# ==================
DEBUG = True
PORT  = 5000