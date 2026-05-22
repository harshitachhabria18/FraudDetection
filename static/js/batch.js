// ========================
// Store results globally
// for download
// ========================
let batchResults = []

// ========================
// Download Template
// ========================
function downloadTemplate() {
    window.location.href = '/download-template'
}

// ========================
// Handle CSV Select
// ========================
function handleCSVSelect(event) {
    const file = event.target.files[0]
    if (file) validateAndShowCSV(file)
}

// ========================
// Validate and Show CSV
// ========================
function validateAndShowCSV(file) {

    if (!file.name.endsWith('.csv')) {
        showBatchError('Please upload a CSV file only')
        return
    }

    if (file.size > 10 * 1024 * 1024) {
        showBatchError('File too large. Maximum size is 10MB')
        return
    }

    document.getElementById('batchUploadArea').style.display
        = 'none'
    document.getElementById('csvFileName').style.display
        = 'flex'
    document.getElementById('csvFileNameText').textContent
        = `📄 ${file.name}`
    document.getElementById('processBatchBtn').disabled
        = false

    // Hide any previous results or errors
    document.getElementById('batchResultCard').style.display
        = 'none'
    document.getElementById('batchErrorCard').style.display
        = 'none'
}

// ========================
// Remove CSV
// ========================
function removeCSV() {
    document.getElementById('csvInput').value        = ''
    document.getElementById('csvFileName').style.display
        = 'none'
    document.getElementById('batchUploadArea').style.display
        = 'block'
    document.getElementById('processBatchBtn').disabled
        = true
    batchResults = []
}

// ========================
// Process Batch
// ========================
async function processBatch() {

    const fileInput = document.getElementById('csvInput')
    const file      = fileInput.files[0]

    if (!file) {
        showBatchError('Please upload a CSV file first')
        return
    }

    // Show loading, hide everything else
    document.getElementById('batchCard').style.display
        = 'none'
    document.getElementById('batchLoadingCard').style.display
        = 'block'
    document.getElementById('batchResultCard').style.display
        = 'none'
    document.getElementById('batchErrorCard').style.display
        = 'none'

    document.getElementById('batchLoadingCard')
        .scrollIntoView({ behavior: 'smooth' })

    const formData = new FormData()
    formData.append('csv_file', file)

    try {
        const response = await fetch('/batch-predict', {
            method: 'POST',
            body  : formData
        })

        const data = await response.json()

        if (response.ok && data.success) {
            batchResults = data.results
            showBatchResults(data)
        } else {
            showBatchError(data.error || 'Processing failed')
        }

    } catch (error) {
        console.error('Batch error:', error)
        showBatchError('Could not connect to server')
    }
}

// ========================
// Show Batch Results
// ========================
function showBatchResults(data) {

    // Hide loading, show result card
    document.getElementById('batchLoadingCard').style.display
        = 'none'
    document.getElementById('batchResultCard').style.display
        = 'block'

    // ========================
    // Summary Numbers
    // ========================
    document.getElementById('totalProcessed').textContent
        = data.total_processed
    document.getElementById('totalFraud').textContent
        = data.total_fraud
    document.getElementById('totalLegit').textContent
        = data.total_legit
    document.getElementById('fraudPercentage').textContent
        = `${data.fraud_percentage}%`

    // ========================
    // AI Explanation
    // ========================
    const explanationEl = document.getElementById('batchExplanation')
    explanationEl.style.display = 'block'
    const explanationText = document.getElementById('batchExplanationText')

    if (data.explanation && data.explanation !== 'Explanation unavailable') {
        explanationText.textContent = data.explanation
        explanationEl.style.display = 'block'
    } else {
        explanationEl.style.display = 'none'
    }

    // ========================
    // Results Table
    // ========================
    const tbody = document.getElementById('resultsTableBody')
    tbody.innerHTML = ''

    data.results.forEach(result => {

        const tr      = document.createElement('tr')

        tr.innerHTML = `
            <td>${result.row}</td>
            <td>${result.type}</td>
            <td>${formatBatchINR(result.amount_inr)}</td>
            <td>${result.confidence}%</td>
            <td>
                <span class="risk-badge-small
                    risk-${result.risk_level.toLowerCase()}">
                    ${result.risk_level}
                </span>
            </td>
        `
        tbody.appendChild(tr)
    })

    // ========================
    // Errors Section
    // ========================
    const errorsSection = document.getElementById('errorsSection')
    const errorsList    = document.getElementById('errorsList')

    if (data.errors && data.errors.length > 0) {
        errorsList.innerHTML = data.errors
            .map(e => `<li>Row ${e.row}: ${e.error}</li>`)
            .join('')
        errorsSection.style.display = 'block'
    } else {
        errorsSection.style.display = 'none'
    }

    document.getElementById('batchResultCard')
        .scrollIntoView({ behavior: 'smooth' })
}

// ========================
// Format INR
// ========================
function formatBatchINR(amount) {
    return new Intl.NumberFormat('en-IN', {
        style                : 'currency',
        currency             : 'INR',
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    }).format(amount)
}

// ========================
// Download Results
// ========================
async function downloadResults() {

    if (!batchResults || batchResults.length === 0) {
        alert('No results to download')
        return
    }

    try {
        const response = await fetch('/download-results', {
            method : 'POST',
            headers: { 'Content-Type': 'application/json' },
            body   : JSON.stringify({ results: batchResults })
        })

        if (response.ok) {
            const blob     = await response.blob()
            const url      = window.URL.createObjectURL(blob)
            const a        = document.createElement('a')
            a.href         = url
            a.download     = 'fraud_detection_results.csv'
            document.body.appendChild(a)
            a.click()
            document.body.removeChild(a)
            window.URL.revokeObjectURL(url)
        } else {
            alert('Download failed. Please try again.')
        }

    } catch (error) {
        console.error('Download error:', error)
        alert('Could not download results')
    }
}

// ========================
// Show Batch Error
// ========================
function showBatchError(message) {
    document.getElementById('batchLoadingCard').style.display
        = 'none'
    document.getElementById('batchCard').style.display
        = 'block'
    document.getElementById('batchResultCard').style.display
        = 'none'
    document.getElementById('batchErrorCard').style.display
        = 'block'
    document.getElementById('batchErrorMessage').textContent
        = message

    document.getElementById('batchErrorCard')
        .scrollIntoView({ behavior: 'smooth' })
}

// ========================
// Reset Batch
// ========================
function resetBatch() {

    removeCSV()
    batchResults = []

    document.getElementById('batchCard').style.display
        = 'block'
    document.getElementById('batchResultCard').style.display
        = 'none'
    document.getElementById('batchErrorCard').style.display
        = 'none'
    document.getElementById('batchLoadingCard').style.display
        = 'none'

    document.getElementById('batchCard')
        .scrollIntoView({ behavior: 'smooth' })
}