import os
from groq import Groq
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

api_key = os.environ.get('GROQ_API_KEY')
print(f"API Key loaded: {api_key[:10] if api_key else 'NOT FOUND'}")

# Initialize Groq client
client = Groq(
    api_key=os.environ.get('GROQ_API_KEY')
)

def explain_prediction(
    prediction,
    confidence,
    risk_level,
    transaction_type,
    amount_inr,
    step,
    oldbalanceOrg,
    newbalanceOrig,
    oldbalanceDest,
    newbalanceDest
):
    try:
        # Build prompt
        prompt = f"""
        You are a fraud detection expert at an Indian bank.
        Analyze this transaction and explain the result
        in simple English that anyone can understand.

        Transaction Details:
        - Type: {transaction_type}
        - Amount: ₹{amount_inr:,.2f}
        - Step (Hour): {step}
        - Sender Balance Before: ₹{oldbalanceOrg:,.2f}
        - Sender Balance After: ₹{newbalanceOrig:,.2f}
        - Receiver Balance Before: ₹{oldbalanceDest:,.2f}
        - Receiver Balance After: ₹{newbalanceDest:,.2f}

        Model Prediction: {prediction}
        Risk Level: {risk_level}

        Instructions:
        1. Explain in 3-4 sentences the reason for this prediction
        2. If LEGITIMATE: explain why transaction is safe and reassure customer
        If FRAUD: mention specific suspicious patterns found
        3. Give a clear recommendation
        4. Keep language simple and friendly
        5. Do not use technical ML terms
        6. Write as if explaining to a bank customer
        7. Keep response under 100 words
        """

        # Call Groq API
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    'role'   : 'user',
                    'content': prompt
                }
            ],
            model      = 'llama-3.3-70b-versatile',
            temperature= 0.3,
            max_tokens = 200
        )

        # Extract response
        explanation = chat_completion.choices[0]\
                      .message.content.strip()

        return {
            'success'    : True,
            'explanation': explanation
        }

    except Exception as e:
        print(f"Groq Error: {e}") 
        return {
            'success'    : False,
            'explanation': 'AI explanation unavailable'
        }
        
def explain_batch_results(
    total_processed,
    total_fraud,
    total_legit,
    fraud_percentage,
    results
):
    try:
        fraud_by_type  = {}
        high_risk_rows = []

        for r in results:
            if r['label'] == 'FRAUD':                 
                t = r['type']
                fraud_by_type[t] = fraud_by_type.get(t, 0) + 1
                if r['risk_level'] == 'HIGH':
                    high_risk_rows.append(r['row'])

        fraud_type_text = '\n'.join([
            f'- {t}: {c} fraud(s)'
            for t, c in fraud_by_type.items()
        ]) if fraud_by_type else '- None'

        high_risk_text = (
            ', '.join(map(str, high_risk_rows[:10]))
            + ('...' if len(high_risk_rows) > 10 else '')
        ) if high_risk_rows else 'None'

        prompt = f"""
        You are a fraud analyst at an Indian bank.
        Summarize the results of a batch fraud detection
        analysis in simple, clear language.

        === BATCH ANALYSIS RESULTS ===
        Total Transactions : {total_processed}
        Fraud Detected     : {total_fraud}
        Legitimate         : {total_legit}
        Fraud Rate         : {fraud_percentage}%

        Fraud by Transaction Type:
        {fraud_type_text}

        High Risk Transaction Rows:
        {high_risk_text}

        === YOUR TASK ===
        Write a clear batch analysis summary
        (under 150 words) structured like this:

        📊 Batch Summary:
        [One sentence overview of results]

        🚨 Fraud Analysis:
        [2-3 sentences about fraud patterns found]

        ⚠️ High Risk Transactions:
        [Mention specific row numbers if any]

        💡 Recommendation:
        [What should the bank do next?]

        Keep language simple and professional.
        Do not use technical ML terms.
        """

        response = client.chat.completions.create(
            messages=[
                {
                    'role'   : 'system',
                    'content': (
                        'You are a concise fraud analyst. '
                        'Summarize batch results clearly. '
                        'Keep under 150 words.'
                    )
                },
                {
                    'role'   : 'user',
                    'content': prompt
                }
            ],
            model      = 'llama-3.3-70b-versatile',
            temperature= 0.3,
            max_tokens = 300
        )

        return {
            'success'    : True,
            'explanation': response.choices[0]
                           .message.content.strip()
        }

    except Exception as e:
        print(f"Batch Explanation Error: {e}")
        return {
            'success'    : False,
            'explanation': (
                f'📊 Batch Summary: {total_processed} '
                f'transactions analyzed.\n\n'
                f'🚨 Fraud Analysis: {total_fraud} fraudulent '
                f'transactions detected ({fraud_percentage}% '
                f'fraud rate).\n\n'
                f'💡 Recommendation: Review all flagged '
                f'transactions immediately.'
            )
        }
