// ==================
// Handle File Select
// ==================
function handleFileSelect(event) {
    const file = event.target.files[0]
    if (file) displayPreview(file)
}

// ==================
// Handle Drag Over
// ==================
function handleDragOver(event) {
    event.preventDefault()
    document.getElementById('uploadArea')
        .classList.add('dragover')
}

// ==================
// Handle Drag Leave
// ==================
function handleDragLeave(event) {
    document.getElementById('uploadArea')
        .classList.remove('dragover')
}

// ==================
// Handle Drop
// ==================
function handleDrop(event) {
    event.preventDefault()
    document.getElementById('uploadArea')
        .classList.remove('dragover')
    const file = event.dataTransfer.files[0]
    if (file) displayPreview(file)
}

// ==================
// Display Preview
// ==================
function displayPreview(file) {

    const validTypes = [
        'image/jpeg',
        'image/png',
        'image/webp',
        'image/jpg'
    ]

    if (!validTypes.includes(file.type)) {
        showReceiptError('Please upload JPG, PNG or WEBP image')
        return
    }

    if (file.size > 5 * 1024 * 1024) {
        showReceiptError('File too large. Maximum size is 5MB')
        return
    }

    // Store file in the hidden input
    const dataTransfer = new DataTransfer()
    dataTransfer.items.add(file)
    document.getElementById('receiptInput').files
        = dataTransfer.files

    // Read and show preview
    const reader  = new FileReader()
    reader.onload = function(e) {

        document.getElementById('previewImg').src
            = e.target.result

        document.getElementById('imagePreview').style.display
            = 'block'

        document.getElementById('uploadArea').style.display
            = 'none'

        document.getElementById('analyzeBtn').disabled
            = false

        // Show filename — element exists in updated HTML
        const fileNameEl = document.getElementById('fileName')
        if (fileNameEl) fileNameEl.textContent = file.name
    }

    reader.readAsDataURL(file)
}

// ==================
// Remove Image
// ==================
function removeImage() {

    document.getElementById('receiptInput').value = ''
    document.getElementById('previewImg').src     = ''

    document.getElementById('imagePreview').style.display
        = 'none'

    document.getElementById('uploadArea').style.display
        = 'block'

    document.getElementById('analyzeBtn').disabled = true

    const fileNameEl = document.getElementById('fileName')
    if (fileNameEl) fileNameEl.textContent = ''

    // Hide any previous results or errors
    document.getElementById('receiptResultCard').style.display
        = 'none'

    document.getElementById('receiptErrorCard').style.display
        = 'none'
}

// ==================
// Analyze Receipt
// ==================
async function analyzeReceipt() {

    const fileInput = document.getElementById('receiptInput')
    const file      = fileInput.files[0]

    if (!file) {
        showReceiptError('Please upload a receipt image first')
        return
    }

    // Show loading, hide everything else
    document.getElementById('receiptCard').style.display
        = 'none'
    document.getElementById('receiptLoadingCard').style.display
        = 'block'
    document.getElementById('receiptResultCard').style.display
        = 'none'
    document.getElementById('receiptErrorCard').style.display
        = 'none'

    document.getElementById('receiptLoadingCard')
        .scrollIntoView({ behavior: 'smooth' })

    const formData = new FormData()
    formData.append('receipt', file)

    try {
        const response = await fetch('/analyze-receipt', {
            method: 'POST',
            body  : formData
        })

        const data = await response.json()

        if (response.ok && data.success) {
            showReceiptResult(data)
        } else {
            showReceiptError(data.error || 'Analysis failed')
        }

    } catch (error) {
        console.error('Receipt analysis error:', error)
        showReceiptError('Could not connect to server')
    }
}

// ==================
// Show Receipt Result
// ==================
function showReceiptResult(data) {

    // Hide loading, show result
    document.getElementById('receiptLoadingCard').style.display
        = 'none'
    document.getElementById('receiptResultCard').style.display
        = 'block'

    // ==================
    // Verdict Badge
    // ==================
    const verdictEl = document.getElementById('receiptVerdict')

    const verdictMap = {
        'HIGH_RISK'  : { text: '⛔ HIGH RISK',      cls: 'receipt-verdict high'    },
        'MEDIUM_RISK': { text: '⚠️ MEDIUM RISK',    cls: 'receipt-verdict medium'  },
        'NOT_RECEIPT': { text: '❌ NOT A RECEIPT',  cls: 'receipt-verdict unknown' },
        'INCONCLUSIVE': { text: '🔍 INCONCLUSIVE',  cls: 'receipt-verdict unknown' },
    }

    const verdict = verdictMap[data.verdict] || {
        text: '✅ LOW RISK',
        cls : 'receipt-verdict low'
    }

    verdictEl.textContent = verdict.text
    verdictEl.className   = verdict.cls

    // ==================
    // Score Bar
    // ==================
    const score     = data.score || 0
    const scoreEl   = document.getElementById('receiptScore')
    const scoreFill = document.getElementById('receiptScoreFill')
    const scoreText = document.getElementById('receiptScoreText')

    scoreEl.textContent   = `Risk Score: ${score}/100`
    scoreText.textContent = `${score}%`

    setTimeout(() => {
        scoreFill.style.width = `${score}%`
        scoreFill.className   = 'receipt-score-fill ' + (
            score >= 60 ? 'high' : score >= 30 ? 'medium' : 'low'
        )
    }, 100)

    // ==================
    // Extracted Details
    // ==================
    const extracted = data.extracted || {}

    setField('extractedAmount',
        extracted.amount
            ? formatAmount(extracted.amount, extracted.currency)
            : 'Not detected'
    )
    setField('extractedType',
        extracted.document_type || 'Unknown'
    )
    setField('extractedVendor',
        extracted.vendor_name || 'Not detected'
    )
    setField('extractedDate',
        extracted.date || 'Not detected'
    )
    setField('extractedTime',
        extracted.time || 'Not detected'
    )
    setField('extractedPlatform',
        extracted.payment_platform || 'Unknown'
    )
    setField('extractedTxnId',
        extracted.transaction_id || 'Not detected'
    )
    setField('extractedQuality',
        extracted.image_quality || 'Unknown'
    )

    // ==================
    // Signals List
    // ==================
    const signalsSection = document.getElementById('signalsSection')
    const signalsList    = document.getElementById('receiptSignals')

    if (data.signals && data.signals.length > 0) {
        signalsList.innerHTML = data.signals
            .map(s => `<li>${s}</li>`)
            .join('')
        signalsSection.style.display = 'block'
    } else {
        signalsSection.style.display = 'none'
    }

    // ==================
    // AI Explanation
    // ==================
    setField('receiptAnalysis',
        data.analysis || 'No explanation available'
    )

    // Scroll to result
    document.getElementById('receiptResultCard')
        .scrollIntoView({ behavior: 'smooth' })
}

// ==================
// Helper — Set Field
// ==================
function setField(id, value) {
    const el = document.getElementById(id)
    if (el) el.textContent = value
}

// ==================
// Format Amount
// Shows USD or INR based on extracted currency
// ==================
function formatAmount(amount, currency) {

    const curr    = (currency || 'INR').toUpperCase()
    const locales = curr === 'USD' ? 'en-US' : 'en-IN'

    try {
        return new Intl.NumberFormat(locales, {
            style                : 'currency',
            currency             : curr,
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        }).format(amount)
    } catch {
        return `${curr} ${parseFloat(amount).toFixed(2)}`
    }
}

// ==================
// Show Receipt Error
// ==================
function showReceiptError(message) {

    document.getElementById('receiptLoadingCard').style.display
        = 'none'
    document.getElementById('receiptCard').style.display
        = 'block'
    document.getElementById('receiptResultCard').style.display
        = 'none'
    document.getElementById('receiptErrorCard').style.display
        = 'block'

    setField('receiptErrorMessage', message)

    document.getElementById('receiptErrorCard')
        .scrollIntoView({ behavior: 'smooth' })
}

// ==================
// Reset Receipt
// ==================
function resetReceipt() {

    removeImage()

    document.getElementById('receiptCard').style.display
        = 'block'
    document.getElementById('receiptResultCard').style.display
        = 'none'
    document.getElementById('receiptErrorCard').style.display
        = 'none'
    document.getElementById('receiptLoadingCard').style.display
        = 'none'

    // Reset score bar width
    const scoreFill = document.getElementById('receiptScoreFill')
    if (scoreFill) {
        scoreFill.style.width = '0%'
        scoreFill.className   = 'receipt-score-fill low'
    }

    document.getElementById('receiptCard')
        .scrollIntoView({ behavior: 'smooth' })
}