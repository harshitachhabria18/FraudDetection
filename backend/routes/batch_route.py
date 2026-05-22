# backend/routes/batch_route.py

from flask import Blueprint, request, jsonify, Response
from backend.utils.model_loader import model, feature_columns
from backend.utils.explainer import explain_batch_results
from backend.config import (
    inr_to_usd,
    FRAUD_THRESHOLD,
    HIGH_RISK_THRESHOLD,
    MEDIUM_RISK_THRESHOLD
)
import pandas as pd
import io
import csv

batch_bp = Blueprint('batch', __name__)

# ----------------------------------------
# Template Download Route
# ----------------------------------------
@batch_bp.route('/download-template', methods=['GET'])
def download_template():
    try:
        # Sample template with example rows
        template_data = [
            ['type', 'amount', 'step', 'oldbalanceOrg',
             'newbalanceOrig', 'oldbalanceDest', 'newbalanceDest'],
            ['TRANSFER', 90000, 1, 90000, 0, 0, 89999],
            ['PAYMENT', 5000, 10, 50000, 45000, 0, 0],
            ['CASH_OUT', 150000, 2, 150000, 0, 0, 150000],
            ['CASH_IN', 10000, 5, 0, 10000, 50000, 40000],
            ['DEBIT', 2000, 20, 20000, 18000, 0, 0],
        ]

        # Build CSV in memory
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerows(template_data)
        csv_content = output.getvalue()

        return Response(
            csv_content,
            mimetype   = 'text/csv',
            headers    = {
                'Content-Disposition':
                    'attachment; filename=fraud_detection_template.csv'
            }
        )

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ----------------------------------------
# Batch Prediction Route
# ----------------------------------------
@batch_bp.route('/batch-predict', methods=['POST'])
def batch_predict():
    try:
        # ----------------------------------------
        # Step 1: Validate uploaded file
        # ----------------------------------------
        if 'csv_file' not in request.files:
            return jsonify({
                'error': 'No CSV file uploaded'
            }), 400

        file = request.files['csv_file']

        if file.filename == '':
            return jsonify({
                'error': 'No file selected'
            }), 400

        if not file.filename.endswith('.csv'):
            return jsonify({
                'error': 'Please upload a CSV file only'
            }), 400

        # ----------------------------------------
        # Step 2: Read CSV
        # ----------------------------------------
        try:
            df = pd.read_csv(file)
        except Exception as e:
            return jsonify({
                'error': f'Could not read CSV: {str(e)}'
            }), 400

        # ----------------------------------------
        # Step 3: Validate columns
        # ----------------------------------------
        required_columns = [
            'type', 'amount', 'step',
            'oldbalanceOrg', 'newbalanceOrig',
            'oldbalanceDest', 'newbalanceDest'
        ]

        missing_cols = [
            col for col in required_columns
            if col not in df.columns
        ]

        if missing_cols:
            return jsonify({
                'error': f'Missing columns: {missing_cols}. '
                         f'Please use the template provided.'
            }), 400

        # ----------------------------------------
        # Step 4: Validate row count
        # ----------------------------------------
        if len(df) == 0:
            return jsonify({
                'error': 'CSV file is empty'
            }), 400

        if len(df) > 1000:
            return jsonify({
                'error': 'Maximum 1000 rows allowed per upload'
            }), 400

        # ----------------------------------------
        # Step 5: Process each row
        # ----------------------------------------
        results = []
        errors  = []

        valid_types = [
            'CASH_IN', 'CASH_OUT',
            'DEBIT', 'PAYMENT', 'TRANSFER'
        ]

        for index, row in df.iterrows():
            try:
                # Validate type
                transaction_type = str(
                    row['type']
                ).upper().strip()

                if transaction_type not in valid_types:
                    errors.append({
                        'row'  : index + 2,
                        'error': f'Invalid type: {row["type"]}',
                        'data' : row.to_dict()  
                    })
                    continue

                # Parse amounts
                amount_inr         = float(row['amount'])
                oldbalanceOrg_inr  = float(row['oldbalanceOrg'])
                newbalanceOrig_inr = float(row['newbalanceOrig'])
                oldbalanceDest_inr = float(row['oldbalanceDest'])
                newbalanceDest_inr = float(row['newbalanceDest'])
                step               = int(row['step'])

                # Validate amount
                if amount_inr <= 0:
                    errors.append({
                        'row'  : index + 2,
                        'error': 'Amount must be greater than 0'
                    })
                    continue

                # Validate step
                if step <= 0:
                    errors.append({
                        'row'  : index + 2,
                        'error': 'Step must be greater than 0'
                    })
                    continue

                # Convert INR to USD
                amount         = inr_to_usd(amount_inr)
                oldbalanceOrg  = inr_to_usd(oldbalanceOrg_inr)
                newbalanceOrig = inr_to_usd(newbalanceOrig_inr)
                oldbalanceDest = inr_to_usd(oldbalanceDest_inr)
                newbalanceDest = inr_to_usd(newbalanceDest_inr)

                # Build input
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

                # Predict
                input_df    = pd.DataFrame(
                    [input_data]
                )[feature_columns]
                probability = model.predict_proba(
                    input_df
                )[0][1]
                prediction  = int(
                    probability >= FRAUD_THRESHOLD
                )

                # Risk level
                if probability >= HIGH_RISK_THRESHOLD:
                    risk_level = 'HIGH'
                elif probability >= MEDIUM_RISK_THRESHOLD:
                    risk_level = 'MEDIUM'
                else:
                    risk_level = 'LOW'

                results.append({
                    'row'       : index + 2,
                    'type'      : transaction_type,
                    'amount_inr': round(amount_inr, 2),
                    'step'      : step,
                    'prediction': prediction,
                    'label'     : 'FRAUD' if prediction == 1
                                  else 'LEGITIMATE',
                    'confidence': round(
                        float(probability) * 100, 2
                    ),
                    'risk_level': risk_level
                })

            except Exception as e:
                errors.append({
                    'row'  : index + 2,
                    'error': str(e)
                })

        # ----------------------------------------
        # Step 6: Build summary
        # ----------------------------------------
        total_processed  = len(results)
        total_fraud      = sum(
            1 for r in results if r['prediction'] == 1
        )
        total_legit      = total_processed - total_fraud
        fraud_percentage = round(
            (total_fraud / total_processed * 100)
            if total_processed > 0 else 0, 2
        )

        # ----------------------------------------
        # Step 7: Generate Groq explanation  
        # ----------------------------------------
        batch_explanation = explain_batch_results(
            total_processed  = total_processed,
            total_fraud      = total_fraud,
            total_legit      = total_legit,
            fraud_percentage = fraud_percentage,
            results          = results
        )

        return jsonify({
            'success'         : True,
            'total_rows'      : len(df),
            'total_processed' : total_processed,
            'total_fraud'     : total_fraud,
            'total_legit'     : total_legit,
            'fraud_percentage': fraud_percentage,
            'results'         : results,
            'errors'          : errors,
            'explanation': batch_explanation.get(
                'explanation',
                'Explanation unavailable'
            )
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ----------------------------------------
# Download Results Route
# ----------------------------------------
@batch_bp.route('/download-results', methods=['POST'])
def download_results():
    try:
        data    = request.get_json()
        results = data.get('results', [])

        if not results:
            return jsonify({
                'error': 'No results to download'
            }), 400

        # Build CSV
        output = io.StringIO()
        writer = csv.DictWriter(
            output,
            fieldnames = [
                'row', 'type', 'amount_inr', 'step',
                'label', 'confidence', 'risk_level'
            ],
            extrasaction = 'ignore'
        )
        writer.writeheader()
        writer.writerows(results)
        csv_content = output.getvalue()

        return Response(
            csv_content,
            mimetype = 'text/csv',
            headers  = {
                'Content-Disposition':
                    'attachment; filename=fraud_detection_results.csv'
            }
        )

    except Exception as e:
        return jsonify({'error': str(e)}), 500