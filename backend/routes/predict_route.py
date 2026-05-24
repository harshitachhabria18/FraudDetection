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
        
        model_types     = ['CASH_OUT', 'TRANSFER']
        
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

        # ================================================================
        # RULE 1: CASH_IN, DEBIT, PAYMENT — never fraud in PaySim
        # Return LEGITIMATE immediately without calling model
        # ================================================================
        if transaction_type not in model_types:
            return jsonify({
                'prediction'      : 0,
                'label'           : 'LEGITIMATE',
                'confidence'      : 1.0,
                'risk_level'      : 'LOW',
                'threshold_used'  : FRAUD_THRESHOLD,
                'transaction_type': transaction_type,
                'amount_inr'      : round(amount_inr, 2),
                'amount_usd'      : round(inr_to_usd(amount_inr), 2),
                'step'            : step,
                'ai_explanation'  : (
                    f'{transaction_type} transactions are not associated '
                    f'with fraud. No suspicious activity detected.'
                )
            }), 200

        # ================================================================
        # RULE 2: Balance reconciliation check
        # If both sender and receiver balances add up correctly
        # the transaction is mathematically legitimate
        #
        # Legitimate: (oldbalanceOrg - amount) = newbalanceOrig
        #             (oldbalanceDest + amount) = newbalanceDest
        #
        # This rule catches small legitimate transfers that PaySim's
        # training data doesn't represent well (e.g. ₹1,000 transfers)
        # ================================================================
        tolerance          = 1.0  # ₹1 rounding tolerance
        balance_check_orig = abs((oldbalanceOrg_inr - amount_inr) - newbalanceOrig_inr)
        balance_check_dest = abs((newbalanceDest_inr - oldbalanceDest_inr) - amount_inr)
 
        if balance_check_orig <= tolerance and balance_check_dest <= tolerance:
            ai_explanation = explain_prediction(
                prediction       = 'LEGITIMATE',
                confidence       = 1.0,
                risk_level       = 'LOW',
                transaction_type = transaction_type,
                amount_inr       = amount_inr,
                step             = step,
                oldbalanceOrg    = oldbalanceOrg_inr,
                newbalanceOrig   = newbalanceOrig_inr,
                oldbalanceDest   = oldbalanceDest_inr,
                newbalanceDest   = newbalanceDest_inr
            )
            return jsonify({
                'prediction'      : 0,
                'label'           : 'LEGITIMATE',
                'confidence'      : 1.0,
                'risk_level'      : 'LOW',
                'threshold_used'  : FRAUD_THRESHOLD,
                'transaction_type': transaction_type,
                'amount_inr'      : round(amount_inr, 2),
                'amount_usd'      : round(inr_to_usd(amount_inr), 2),
                'step'            : step,
                'ai_explanation'  : ai_explanation['explanation']
            }), 200
            
              
        # ================================================================
        # RULE 3: PaySim fraud signature
        # Sender fully drained + amount equals balance + receiver unchanged
        # This is the exact fraud pattern in PaySim that the ML model
        # misses due to low confidence (26%) on TRANSFER fraud
        # ================================================================
        sender_drained     = newbalanceOrig_inr == 0
        amount_equals_bal  = abs(amount_inr - oldbalanceOrg_inr) <= tolerance
        receiver_unchanged = abs(newbalanceDest_inr - oldbalanceDest_inr) <= tolerance
        receiver_both_zero  = oldbalanceDest_inr == 0 and newbalanceDest_inr == 0
 
        if sender_drained and amount_equals_bal and receiver_unchanged and not receiver_both_zero:
            ai_explanation = explain_prediction(
                prediction       = 'FRAUD',
                confidence       = 95.0,
                risk_level       = 'HIGH',
                transaction_type = transaction_type,
                amount_inr       = amount_inr,
                step             = step,
                oldbalanceOrg    = oldbalanceOrg_inr,
                newbalanceOrig   = newbalanceOrig_inr,
                oldbalanceDest   = oldbalanceDest_inr,
                newbalanceDest   = newbalanceDest_inr
            )
            return jsonify({
                'prediction'      : 1,
                'label'           : 'FRAUD',
                'confidence'      : 95.0,
                'risk_level'      : 'HIGH',
                'threshold_used'  : FRAUD_THRESHOLD,
                'transaction_type': transaction_type,
                'amount_inr'      : round(amount_inr, 2),
                'amount_usd'      : round(inr_to_usd(amount_inr), 2),
                'step'            : step,
                'ai_explanation'  : ai_explanation['explanation']
            }), 200



        # ================================================================
        # ML MODEL: Balances don't reconcile → suspicious
        # Send to XGBoost for fraud probability scoring
        # This handles cases where:
        # → Sender balance didn't decrease correctly
        # → Receiver balance didn't increase correctly
        # → Amount doesn't match balance changes
        # ================================================================
        input_data = {
            'step'          : step,
            'amount'        : amount_inr,
            'oldbalanceOrg' : oldbalanceOrg_inr,
            'newbalanceOrig': newbalanceOrig_inr,
            'oldbalanceDest': oldbalanceDest_inr,
            'newbalanceDest': newbalanceDest_inr,
            'type_CASH_OUT' : 1 if transaction_type == 'CASH_OUT' else 0,
            'type_TRANSFER' : 1 if transaction_type == 'TRANSFER' else 0,
        }
 
        input_df    = pd.DataFrame([input_data])[feature_columns]
        probability = model.predict_proba(input_df)[0][1]
        prediction  = int(probability >= FRAUD_THRESHOLD)
 
        if probability >= HIGH_RISK_THRESHOLD:
            risk_level = 'HIGH'
        elif probability >= MEDIUM_RISK_THRESHOLD:
            risk_level = 'MEDIUM'
        else:
            risk_level = 'LOW'
 
        label = 'FRAUD' if prediction == 1 else 'LEGITIMATE'
 
        ai_explanation = explain_prediction(
            prediction       = label,
            confidence       = round(float(probability) * 100, 2),
            risk_level       = risk_level,
            transaction_type = transaction_type,
            amount_inr       = amount_inr,
            step             = step,
            oldbalanceOrg    = oldbalanceOrg_inr,
            newbalanceOrig   = newbalanceOrig_inr,
            oldbalanceDest   = oldbalanceDest_inr,
            newbalanceDest   = newbalanceDest_inr
        )
        
        return jsonify({
            'prediction'      : prediction,
            'label'           : label,
            'confidence'      : round(float(probability) * 100, 2),
            'risk_level'      : risk_level,
            'threshold_used'  : FRAUD_THRESHOLD,
            'transaction_type': transaction_type,
            'amount_inr'      : round(amount_inr, 2),
            'amount_usd'      : round(inr_to_usd(amount_inr), 2),
            'step'            : step,
            'ai_explanation'  : ai_explanation['explanation']
        }), 200
 
    except Exception as e:
        return jsonify({'error': str(e)}), 500