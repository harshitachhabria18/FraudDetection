from flask import Blueprint, request, jsonify
from backend.utils.model_loader import model, feature_columns
import numpy as np
import pandas as pd
from backend.utils.explainer import explain_prediction

# ================================
# CHANGED — Import from config 
# ================================
from backend.config import (
    inr_to_usd,                             
    FRAUD_THRESHOLD,                        
    HIGH_RISK_THRESHOLD,                    
    MEDIUM_RISK_THRESHOLD                   
)

# Create blueprint
predict_bp = Blueprint('predict', __name__)

@predict_bp.route('/predict', methods=['POST'])
def predict():
    try:
        # Get data from request
        data = request.get_json()

        if not data:
            return jsonify({
                'error': 'No data provided'
            }), 400

        # Extract fields from request
        transaction_type   = data.get('type')

        # ================================
        # CHANGED — All amounts in INR 
        # ================================
        amount_inr         = data.get('amount')        
        oldbalanceOrg_inr  = data.get('oldbalanceOrg') 
        newbalanceOrig_inr = data.get('newbalanceOrig')
        oldbalanceDest_inr = data.get('oldbalanceDest')
        newbalanceDest_inr = data.get('newbalanceDest')
        step               = data.get('step')

        # Validate all fields present
        if None in [transaction_type, amount_inr,
                    oldbalanceOrg_inr, newbalanceOrig_inr,
                    oldbalanceDest_inr, newbalanceDest_inr,
                    step]:
            return jsonify({
                'error': 'All fields are required'
            }), 400

        # Validate transaction type
        valid_types = ['CASH_IN', 'CASH_OUT',
                       'DEBIT', 'PAYMENT', 'TRANSFER']
        if transaction_type not in valid_types:
            return jsonify({
                'error': f'Invalid transaction type'
            }), 400

        # Validate numeric values
        try:
            # ================================
            # CHANGED — Parse as INR 
            # ================================
            amount_inr         = float(amount_inr)         
            oldbalanceOrg_inr  = float(oldbalanceOrg_inr)  
            newbalanceOrig_inr = float(newbalanceOrig_inr) 
            oldbalanceDest_inr = float(oldbalanceDest_inr) 
            newbalanceDest_inr = float(newbalanceDest_inr) 
            step               = int(step)
        except ValueError:
            return jsonify({
                'error': 'Invalid numeric values provided'
            }), 400

        # Validate amount
        if amount_inr <= 0:
            return jsonify({
                'error': 'Amount must be greater than 0'
            }), 400

        # Validate step
        if step <= 0:
            return jsonify({
                'error': 'Step must be greater than 0'
            }), 400

        # ================================
        # NEW — Convert INR to USD 
        # ================================
        amount         = inr_to_usd(amount_inr)         
        oldbalanceOrg  = inr_to_usd(oldbalanceOrg_inr)  
        newbalanceOrig = inr_to_usd(newbalanceOrig_inr) 
        oldbalanceDest = inr_to_usd(oldbalanceDest_inr) 
        newbalanceDest = inr_to_usd(newbalanceDest_inr) 

        # Build input dictionary
        input_data = {
            'step'          : step,
            'amount'        : amount,          
            'oldbalanceOrg' : oldbalanceOrg,   
            'newbalanceOrig': newbalanceOrig,  
            'oldbalanceDest': oldbalanceDest,
            'newbalanceDest': newbalanceDest,  
            'type_CASH_IN'  : 1 if transaction_type == 'CASH_IN'  else 0,
            'type_CASH_OUT' : 1 if transaction_type == 'CASH_OUT'  else 0,
            'type_DEBIT'    : 1 if transaction_type == 'DEBIT'     else 0,
            'type_PAYMENT'  : 1 if transaction_type == 'PAYMENT'   else 0,
            'type_TRANSFER' : 1 if transaction_type == 'TRANSFER'  else 0,
        }

        # Convert to dataframe
        input_df = pd.DataFrame([input_data])[feature_columns]

        # Get fraud probability
        probability = model.predict_proba(input_df)[0][1]

        # ================================
        # CHANGED — Use config values 
        # ================================
        prediction = int(probability >= FRAUD_THRESHOLD)  

        # ================================
        # CHANGED — Use config thresholds 
        # ================================
        if probability >= HIGH_RISK_THRESHOLD:            
            risk_level = 'HIGH'
        elif probability >= MEDIUM_RISK_THRESHOLD:        
            risk_level = 'MEDIUM'
        else:
            risk_level = 'LOW'
            
        label = 'FRAUD' if prediction == 1 else 'LEGITIMATE'
        
        ai_explanation = explain_prediction(
            prediction      = label,
            confidence      = round(float(probability) * 100, 2),
            risk_level      = risk_level,
            transaction_type= transaction_type,
            amount_inr      = amount_inr,
            step            = step,
            oldbalanceOrg   = oldbalanceOrg_inr,
            newbalanceOrig  = newbalanceOrig_inr,
            oldbalanceDest  = oldbalanceDest_inr,
            newbalanceDest  = newbalanceDest_inr
        )

        # ================================
        # CHANGED — Return INR amounts 
        # ================================
        result = {
            'prediction'      : prediction,
            'label'           : label,
            'confidence'      : round(float(probability) * 100, 2),
            'risk_level'      : risk_level,
            'threshold_used'  : FRAUD_THRESHOLD,
            'transaction_type': transaction_type,
            'amount_inr'      : round(amount_inr, 2),     
            'amount_usd'      : round(amount, 2),          
            'step'            : step,
            'ai_explanation'  : ai_explanation['explanation']
        }

        return jsonify(result), 200

    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500