// ==================
// Check Transaction
// ==================
async function checkTransaction() {

    // Get all form values
    const type          = document.getElementById('type').value
    const amount        = document.getElementById('amount').value
    const step          = document.getElementById('step').value
    const oldbalanceOrg = document.getElementById('oldbalanceOrg').value
    const newbalanceOrig= document.getElementById('newbalanceOrig').value
    const oldbalanceDest= document.getElementById('oldbalanceDest').value
    const newbalanceDest= document.getElementById('newbalanceDest').value

    // ==================
    // Validate Inputs
    // ==================
    if (!type) {
        showError('Please select a transaction type')
        return
    }
    if (!amount || parseFloat(amount) <= 0) {
        showError('Please enter a valid transaction amount')
        return
    }
    if (!step || parseInt(step) <= 0) {
        showError('Please enter a valid step value')
        return
    }
    if (oldbalanceOrg === '' || oldbalanceOrg === null) {
        showError('Please enter sender balance before transaction')
        return
    }
    if (newbalanceOrig === '' || newbalanceOrig === null) {
        showError('Please enter sender balance after transaction')
        return
    }
    if (oldbalanceDest === '' || oldbalanceDest === null) {
        showError('Please enter receiver balance before transaction')
        return
    }
    if (newbalanceDest === '' || newbalanceDest === null) {
        showError('Please enter receiver balance after transaction')
        return
    }

    // ==================
    // Show Loading
    // ==================
    showLoading()

    // ==================
    // Build Request Data
    // ==================
    const requestData = {
        type          : type,
        amount        : parseFloat(amount),
        step          : parseInt(step),
        oldbalanceOrg : parseFloat(oldbalanceOrg),
        newbalanceOrig: parseFloat(newbalanceOrig),
        oldbalanceDest: parseFloat(oldbalanceDest),
        newbalanceDest: parseFloat(newbalanceDest)
    }

    try {
        // ==================
        // Send to Flask API
        // ==================
        const response = await fetch('/predict', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestData)
        })

        const data = await response.json()

        if (response.ok) {
            showResult(data)
        } else {
            showError(data.error || 'Something went wrong')
        }

    } catch (error) {
        console.error('Full error:', error)
        showError('Error: ' + error.message)
    }
}

// ==================
// Show Loading State
// ==================
function showLoading() {
    // Hide all cards
    document.getElementById('formCard').style.display    = 'none'
    document.getElementById('resultCard').style.display  = 'none'
    document.getElementById('errorCard').style.display   = 'none'

    // Show loading
    document.getElementById('loadingCard').style.display = 'block'

    // Scroll to loading
    document.getElementById('loadingCard').scrollIntoView({
        behavior: 'smooth'
    })
}

// ==================
// Show Result
// ==================
function showResult(data) {

    // Hide loading
    document.getElementById('loadingCard').style.display = 'none'

    // Show result card
    document.getElementById('resultCard').style.display  = 'block'

    const isFraud = data.prediction === 1

    // ==================
    // Set Result Badge
    // ==================
    const badge = document.getElementById('resultBadge')
    if (isFraud) {
    badge.innerText = "HIGH RISK OF FRAUD";
    }
    else {
        badge.innerText = "LOW RISK TRANSACTION";
    }

    // ==================
    // Set Risk Level
    // ==================
    const riskDiv = document.getElementById('riskLevel')
    const risk    = data.risk_level

    if (risk === 'HIGH') {
        riskDiv.textContent = '🔴 HIGH RISK'
        riskDiv.className   = 'risk-level risk-high'
    } else if (risk === 'MEDIUM') {
        riskDiv.textContent = '🟡 MEDIUM RISK'
        riskDiv.className   = 'risk-level risk-medium'
    } else {
        riskDiv.textContent = '🟢 LOW RISK'
        riskDiv.className   = 'risk-level risk-low'
    }

    // ==================
// Set Confidence Bar
// ==================
const confidence        = data.confidence
const fill              = document.getElementById('confidenceFill')

// For legitimate transactions show 0% on bar
// Backend sends 1% for legitimate (needed for AI analysis)
// Frontend displays 0% so user sees clean result
const displayConfidence = isFraud ? confidence : 0

document.getElementById('confidenceText').textContent =
    `${displayConfidence}%`

// Animate bar after small delay
setTimeout(() => {
    fill.style.width = displayConfidence + '%'
    fill.className   = isFraud
        ? 'confidence-fill fill-fraud'
        : 'confidence-fill fill-legit'
}, 100)

    const aiText = document.getElementById('aiText')
    if (data.ai_explanation) {
        aiText.textContent = data.ai_explanation
        document.getElementById('aiExplanation')
            .style.display = 'block'
    } else {
        document.getElementById('aiExplanation')
            .style.display = 'none'
    }

    // ==================
    // Set Detail Items
    // ==================
    document.getElementById('predictionLabel').textContent =
        isFraud ? 'HIGH RISK' : 'LOW RISK'

    document.getElementById('predictionLabel').style.color =
        isFraud ? '#c53030' : '#276749'

    document.getElementById('typeLabel').textContent =
        data.transaction_type

    document.getElementById('amountLabel').textContent =
        new Intl.NumberFormat('en-IN', {
            style                : 'currency',
            currency             : 'INR',
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        }).format(data.amount_inr)

    document.getElementById('riskLabel').textContent =
        data.risk_level

    document.getElementById('riskLabel').style.color =
        risk === 'HIGH'   ? '#c53030' :
        risk === 'MEDIUM' ? '#c05621' : '#276749'

    document.getElementById('confidenceLabel').textContent =
    `${displayConfidence}%`

    // ==================
    // Scroll to Result
    // ==================
    document.getElementById('resultCard').scrollIntoView({
        behavior: 'smooth'
    })
}

// ==================
// Show Error
// ==================
function showError(message) {

    // Hide all cards
    document.getElementById('loadingCard').style.display  = 'none'
    document.getElementById('resultCard').style.display   = 'none'

    // Show form and error
    document.getElementById('formCard').style.display     = 'block'
    document.getElementById('errorCard').style.display    = 'block'

    // Set error message
    document.getElementById('errorMessage').textContent   = message

    // Scroll to error
    document.getElementById('errorCard').scrollIntoView({
        behavior: 'smooth'
    })
}

// ==================
// Reset Form
// ==================
function resetForm() {

    // Clear all inputs
    document.getElementById('type').value           = ''
    document.getElementById('amount').value         = ''
    document.getElementById('step').value           = ''
    document.getElementById('oldbalanceOrg').value  = ''
    document.getElementById('newbalanceOrig').value = ''
    document.getElementById('oldbalanceDest').value = ''
    document.getElementById('newbalanceDest').value = ''
    document.getElementById('aiText').textContent = ''

    // Reset confidence bar
    document.getElementById('confidenceFill').style.width = '0%'

    // Show form card only
    document.getElementById('formCard').style.display    = 'block'
    document.getElementById('loadingCard').style.display = 'none'
    document.getElementById('resultCard').style.display  = 'none'
    document.getElementById('errorCard').style.display   = 'none'
    document.getElementById('aiExplanation').style.display = 'none'

    // Scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' })
}

// ==================
// Print Result
// ==================
function printResult() {

    const badge      = document.getElementById('resultBadge').innerText
    const riskLevel  = document.getElementById('riskLevel').innerText
    const confidence = document.getElementById('confidenceText').innerText
    const fillWidth  = document.getElementById('confidenceFill').style.width
    const fillClass  = document.getElementById('confidenceFill').className

    const prediction = document.getElementById('predictionLabel').innerText
    const type       = document.getElementById('typeLabel').innerText
    const amount     = document.getElementById('amountLabel').innerText
    const risk       = document.getElementById('riskLabel').innerText
    const conf       = document.getElementById('confidenceLabel').innerText

    const aiBox      = document.getElementById('aiExplanation')
    const aiText     = document.getElementById('aiText').innerText
    const showAI     = aiBox.style.display !== 'none'

    const isFraud    = prediction.includes('HIGH')

    const badgeStyle = isFraud
        ? 'background:#fff5f5;color:#b91c1c;border:2px solid #fca5a5;'
        : 'background:#f0fdf4;color:#15803d;border:2px solid #86efac;'

    const riskStyle  = isFraud
        ? 'background:#fff5f5;color:#b91c1c;border:1.5px solid #fca5a5;'
        : 'background:#f0fdf4;color:#15803d;border:1.5px solid #86efac;'

    const barColor   = isFraud ? '#b91c1c' : '#15803d'

    const now = new Date().toLocaleString('en-IN', {
        dateStyle: 'medium',
        timeStyle: 'short'
    })

    const html = `
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Fraud Detection Report</title>
    <style>
        * { margin:0; padding:0; box-sizing:border-box; }

        body {
            font-family : 'Segoe UI', sans-serif;
            background  : white;
            color       : #0f172a;
            padding     : 40px;
            line-height : 1.6;
        }

        .report-header {
            display        : flex;
            justify-content: space-between;
            align-items    : center;
            padding-bottom : 16px;
            border-bottom  : 2px solid #e2e8f0;
            margin-bottom  : 28px;
        }

        .report-title {
            font-size  : 1rem;
            font-weight: 700;
            color      : #64748b;
        }

        .report-date {
            font-size: 0.85rem;
            color    : #94a3b8;
        }

        .result-badge {
            padding      : 18px 24px;
            border-radius: 14px;
            font-size    : 1.4rem;
            font-weight  : 800;
            margin-bottom: 20px;
            ${badgeStyle}
        }

        .risk-level {
            padding       : 12px 20px;
            border-radius : 10px;
            font-size     : 0.9rem;
            font-weight   : 700;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom : 20px;
            display       : inline-block;
            width         : 100%;
            text-align    : center;
            ${riskStyle}
        }

        .confidence-section { margin-bottom:24px; }

        .confidence-header {
            display        : flex;
            justify-content: space-between;
            font-weight    : 600;
            margin-bottom  : 10px;
        }

        .confidence-bar {
            width        : 100%;
            height       : 14px;
            background   : #e2e8f0;
            border-radius: 999px;
            overflow     : hidden;
        }

        .confidence-fill {
            height          : 100%;
            width           : ${fillWidth};
            border-radius   : 999px;
            background      : ${barColor};
        }

        .result-details {
            background   : #f8fafc;
            border       : 1px solid #e2e8f0;
            border-radius: 14px;
            padding      : 20px;
            margin-bottom: 24px;
        }

        .result-details h3 {
            font-size     : 0.78rem;
            color         : #64748b;
            text-transform: uppercase;
            letter-spacing: 1px;
            font-weight   : 700;
            margin-bottom : 14px;
        }

        .detail-item {
            display        : flex;
            justify-content: space-between;
            padding        : 12px 0;
            border-bottom  : 1px solid #e2e8f0;
            font-size      : 0.92rem;
        }

        .detail-item:last-child { border-bottom: none; }
        .detail-label           { color: #64748b; }
        .detail-value           { font-weight: 700; }

        .ai-section {
            background   : #f0f9ff;
            border       : 1px solid #bae6fd;
            border-radius: 14px;
            padding      : 20px;
        }

        .ai-title {
            font-size    : 0.95rem;
            font-weight  : 700;
            color        : #0369a1;
            margin-bottom: 10px;
        }

        .ai-text {
            color      : #0c4a6e;
            font-size  : 0.9rem;
            line-height: 1.7;
        }

        .report-footer {
            margin-top  : 32px;
            padding-top : 16px;
            border-top  : 1px solid #e2e8f0;
            font-size   : 0.78rem;
            color       : #94a3b8;
            text-align  : center;
        }
    </style>
</head>
<body>

    <div class="report-header">
        <span class="report-title">🔒 AI Fraud Detection System — Transaction Report</span>
        <span class="report-date">${now}</span>
    </div>

    <div class="result-badge">${badge}</div>

    <div class="risk-level">${riskLevel}</div>

    <div class="confidence-section">
        <div class="confidence-header">
            <span>Fraud Probability</span>
            <span>${confidence}</span>
        </div>
        <div class="confidence-bar">
            <div class="confidence-fill"></div>
        </div>
    </div>

    <div class="result-details">
        <h3>Transaction Summary</h3>
        <div class="detail-item">
            <span class="detail-label">Result</span>
            <span class="detail-value">${prediction}</span>
        </div>
        <div class="detail-item">
            <span class="detail-label">Transaction Type</span>
            <span class="detail-value">${type}</span>
        </div>
        <div class="detail-item">
            <span class="detail-label">Amount</span>
            <span class="detail-value">${amount}</span>
        </div>
        <div class="detail-item">
            <span class="detail-label">Risk Level</span>
            <span class="detail-value">${risk}</span>
        </div>
        <div class="detail-item">
            <span class="detail-label">Confidence</span>
            <span class="detail-value">${conf}</span>
        </div>
    </div>

    ${showAI ? `
    <div class="ai-section">
        <div class="ai-title">🤖 AI Analysis</div>
        <div class="ai-text">${aiText}</div>
    </div>
    ` : ''}

    <div class="report-footer">
        Generated by AI Fraud Detection System &nbsp;|&nbsp; ${now}
    </div>

</body>
</html>`

    const printWindow = window.open('', '_blank', 'width=800,height=700')
    printWindow.document.write(html)
    printWindow.document.close()

    // Wait for content to load then print
    printWindow.onload = function() {
        printWindow.print()
        printWindow.onafterprint = function() {
            printWindow.close()
        }
    }
}


// ==================
// Enter Key Submit
// ==================
document.addEventListener('keydown', function(event) {
    if (event.key === 'Enter') {
        const formCard = document.getElementById('formCard')
        if (formCard.style.display !== 'none') {
            checkTransaction()
        }
    }
})

function formatINR(amount) {
    return new Intl.NumberFormat('en-IN', {
        style                : 'currency',
        currency             : 'INR',
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    }).format(amount)
}

function copyResult() {

    const result = document.getElementById('predictionLabel').innerText;
    const type = document.getElementById('typeLabel').innerText;
    const amount = document.getElementById('amountLabel').innerText;
    const risk = document.getElementById('riskLabel').innerText;
    const confidence = document.getElementById('confidenceLabel').innerText;
    const aiText = document.getElementById('aiText').innerText;

    // Convert result label into cleaner wording
    let finalResult = result;

    if (result.toUpperCase().includes("HIGH")) {
    finalResult = "High Risk Transaction";
    }
    else if (result.toUpperCase().includes("LOW")) {
        finalResult = "Low Risk Transaction";
    }

    // Current date and time
    const now = new Date();

    const formattedDate = now.toLocaleString('en-IN', {
        dateStyle: 'medium',
        timeStyle: 'short'
    });

    // Final copied text
    const textToCopy = `
Fraud Detection Result

Result: ${finalResult}
Transaction Type: ${type}
Amount: ${amount}
Risk Level: ${risk}
Confidence: ${confidence}

AI Analysis:
${aiText}

Generated At: ${formattedDate}

Generated by AI Fraud Detection System
`;

    navigator.clipboard.writeText(textToCopy)
        .then(() => {
            alert("Result copied to clipboard!");
        })
        .catch(err => {
            console.error("Copy failed:", err);
            alert("Failed to copy result.");
        });
}