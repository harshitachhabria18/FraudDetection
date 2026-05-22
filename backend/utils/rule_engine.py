"""
rule_engine.py
--------------
Relative Rule Engine for Receipt Fraud Detection.

Key principle:
  NEVER use absolute thresholds like "amount > 50000 = fraud"
  ALWAYS score relative to context: document type, vendor
  category, platform norms, and internal consistency.
"""

# ============================================================
# BASELINE DATA — average (mean) and std-dev per category INR
# In production, load from DB based on real user history.
# ============================================================

CATEGORY_BASELINES = {
    "grocery"      : {"mean": 1500,    "std": 800},
    "restaurant"   : {"mean": 800,     "std": 400},
    "fuel"         : {"mean": 3000,    "std": 1500},
    "medical"      : {"mean": 2500,    "std": 2000},
    "construction" : {"mean": 75000,   "std": 50000},
    "electronics"  : {"mean": 15000,   "std": 12000},
    # Bank transfers: average Indian NEFT/IMPS transfers
    "transfer"     : {"mean": 25000,   "std": 40000},
    "unknown"      : {"mean": 5000,    "std": 4000},
}

# Expected tax % range per category
# Transfers and bank receipts have no tax — skip tax check
CATEGORY_TAX_RANGE = {
    "INR": {
        "grocery"      : (0, 5),
        "restaurant"   : (5, 18),
        "fuel"         : (0, 3),
        "medical"      : (0, 12),
        "construction" : (12, 28),
        "electronics"  : (18, 28),
        "unknown"      : (0, 28),
    },
    "USD": {
        "grocery"      : (0, 12),
        "restaurant"   : (5, 15),
        "fuel"         : (0, 5),
        "medical"      : (0, 10),
        "construction" : (5, 15),
        "electronics"  : (5, 12),
        "unknown"      : (0, 15),
    },
    "DEFAULT": {
        "grocery"      : (0, 15),
        "restaurant"   : (0, 20),
        "fuel"         : (0, 10),
        "medical"      : (0, 15),
        "construction" : (0, 30),
        "electronics"  : (0, 30),
        "unknown"      : (0, 30),
    }
}

# Document types that are bank transfers (no vendor expected)
TRANSFER_DOC_TYPES = [
    "bank_statement",
    "payment_screenshot",
    "qr_payment"
]

# ============================================================
# HELPER: Detect if this is a bank transfer
# Bank transfers: no vendor, no tax, different amount norms
# ============================================================

def _is_bank_transfer(receipt_data: dict) -> bool:

    doc_type = (receipt_data.get("document_type") or "").lower()
    category = (receipt_data.get("vendor_category") or "").lower()
    txn_type = (receipt_data.get("transaction_type") or "").lower()

    return (
        doc_type in TRANSFER_DOC_TYPES or
        category == "transfer"         or
        "transfer" in txn_type         or
        "neft"     in txn_type         or
        "imps"     in txn_type
    )

# ============================================================
# MAIN SCORING FUNCTION
# Input : extracted JSON from Gemini OCR
# Output: score (0-100), signals list, verdict
# ============================================================

def run_rule_engine(receipt_data: dict) -> dict:
    signals = []
    score   = 0

    if not receipt_data.get("is_receipt"):
        return {
            "score"  : 0,
            "verdict": "NOT_RECEIPT",
            "signals": ["Uploaded image is not a receipt"],
            "summary": "This image does not appear to be a financial document."
        }

    if receipt_data.get("image_quality") == "unreadable":
        return {
            "score"  : 50,
            "verdict": "INCONCLUSIVE",
            "signals": ["Image is unreadable, cannot verify"],
            "summary": "Image quality too poor to analyze."
        }

    is_transfer = _is_bank_transfer(receipt_data)

    category = "transfer" if is_transfer else \
               (receipt_data.get("vendor_category") or "unknown")

    amount   = receipt_data.get("amount")

    
    platform = (receipt_data.get("payment_platform") or "").lower()
    missing  = receipt_data.get("missing_fields") or []

    # ----------------------------------------------------------
    # SIGNAL 1: Editing artifacts
    # Weight: +30
    # ----------------------------------------------------------
    if receipt_data.get("editing_artifacts"):
        score += 30
        signals.append(
            "Visual editing artifacts detected in the image (+30)"
        )

    # ----------------------------------------------------------
    # SIGNAL 2: Missing critical fields
    # For transfers: vendor_name is NOT critical (they never have one)
    # For vendor receipts: vendor_name IS critical
    # ----------------------------------------------------------
    if is_transfer:
        # Bank transfers must have: amount, date, sender,
        # receiver, transaction_id
        critical_fields = [
            "amount", "date", "sender",
            "receiver", "transaction_id"
        ]
    else:
        # Vendor receipts must have: amount, date,
        # vendor_name, transaction_id
        critical_fields = [
            "amount", "date",
            "vendor_name", "transaction_id"
        ]

    for field in critical_fields:
        value      = receipt_data.get(field)
        is_missing = (value is None or field in missing)

        if is_missing:
            score += 5
            signals.append(
                f"Critical field missing: '{field}' (+5)"
            )

    # ----------------------------------------------------------
    # SIGNAL 3: Relative amount anomaly
    # z_score = (amount - category_mean) / category_std
    # z > 2 → unusual (+15)
    # z > 3 → highly unusual (+25)
    # ----------------------------------------------------------
    if amount is not None and amount > 0:

        baseline = CATEGORY_BASELINES.get(
            category,
            CATEGORY_BASELINES["unknown"]
        )

        mean    = baseline["mean"]
        std     = baseline["std"]
        z_score = (amount - mean) / std if std > 0 else 0

        if z_score > 3:
            score += 25
            signals.append(
                f"Amount ₹{amount:,.0f} is {z_score:.1f}σ above "
                f"normal for '{category}' transactions "
                f"(avg ₹{mean:,.0f}) (+25)"
            )
        elif z_score > 2:
            score += 15
            signals.append(
                f"Amount ₹{amount:,.0f} is {z_score:.1f}σ above "
                f"normal for '{category}' transactions "
                f"(avg ₹{mean:,.0f}) (+15)"
            )

        # Round number flag (only for large amounts)
        if amount % 1000 == 0 and amount >= 10000:
            score += 5
            signals.append(
                f"Amount ₹{amount:,.0f} is a suspiciously "
                f"round number (+5)"
            )

    # ----------------------------------------------------------
    # SIGNAL 4: Tax inconsistency
    # Skip entirely for bank transfers — they have no tax
    # ----------------------------------------------------------
    if not is_transfer:

        tax_pct = receipt_data.get("tax_percentage")
        tax_amt = receipt_data.get("tax_amount")

        # ----------------------------------------------------------
        # SIGNAL 4a: Tax % outside expected range for category
        # ----------------------------------------------------------
        if tax_pct is not None:

            currency  = receipt_data.get("currency", "INR").upper()
            tax_table = CATEGORY_TAX_RANGE.get(
                currency,
                CATEGORY_TAX_RANGE.get("DEFAULT", {})
            )
            range_for_cat = tax_table.get(category)

            if range_for_cat:
                min_tax, max_tax = range_for_cat
                if not (min_tax <= tax_pct <= max_tax):
                    score += 15
                    signals.append(
                        f"Tax {tax_pct}% is outside expected range "
                        f"{min_tax}%–{max_tax}% for '{category}' (+15)"
                    )

        # ----------------------------------------------------------
        # SIGNAL 4b: Tax amount doesn't match tax percentage
        #
        # FIX: Previously used `amount` (final total after
        # discount) as the tax base. This caused false positives
        # on receipts with discounts like:
        #   Subtotal ₹1100 → tax ₹55 (5%) → discount ₹100
        #   → final ₹1055
        # Old code: 5% of ₹1055 = ₹52.75 ≠ ₹55 → falsely flagged
        # New code: uses taxable_amount (pre-discount base) if
        # available, otherwise skips the check entirely to avoid
        # false positives.
        # ----------------------------------------------------------
        if tax_amt and tax_pct:

            taxable_amount = receipt_data.get("taxable_amount")

            if taxable_amount:
                # Use the explicit pre-discount taxable base
                expected_tax = round(taxable_amount * tax_pct / 100, 2)
                diff_pct     = abs(expected_tax - tax_amt) / expected_tax * 100

                if diff_pct > 2:
                    score += 15
                    signals.append(
                        f"Tax amount ₹{tax_amt} doesn't match "
                        f"computed {tax_pct}% of taxable "
                        f"₹{taxable_amount} "
                        f"(expected ₹{expected_tax:.2f}) (+15)"
                    )

            # If taxable_amount is None (Gemini couldn't extract it),
            # we skip the cross-check entirely.
            # Reason: we can't safely determine the tax base when
            # discounts, line-item taxes, or mixed rates are present.
            # A skip is safer than a false positive.

    # ----------------------------------------------------------
    # SIGNAL 5: Suspicious transaction time (1AM–4AM)
    # Weight: +10
    # Higher weight for large transfers at odd hours
    # ----------------------------------------------------------
    time_str = receipt_data.get("time")

    if time_str:
        try:
            hour = int(time_str.split(":")[0])
            if 1 <= hour <= 4:
                # Extra weight if it's also a large transfer
                extra  = 5 if (is_transfer and amount and amount > 100000) else 0
                weight = 10 + extra
                score += weight
                signals.append(
                    f"Transaction at {time_str} is during "
                    f"unusual hours (1AM–4AM) (+{weight})"
                )
        except:
            pass

    # ----------------------------------------------------------
    # SIGNAL 6: Large cash transaction
    # Weight: +10
    # ----------------------------------------------------------
    if platform == "cash" and amount and amount > 10000:
        score += 10
        signals.append(
            f"Cash transaction of ₹{amount:,.0f} "
            f"above ₹10,000 threshold (+10)"
        )

    # ----------------------------------------------------------
    # SIGNAL 7: Digital payment missing transaction ID
    # Weight: +10
    # ----------------------------------------------------------
    digital_platforms = ["upi", "neft", "imps", "card"]

    if platform in digital_platforms:
        if not receipt_data.get("transaction_id"):
            score += 10
            signals.append(
                f"Digital payment via {platform.upper()} "
                f"has no transaction ID (+10)"
            )

    # ----------------------------------------------------------
    # SIGNAL 8 (NEW): Large transfer to unknown receiver
    # Bank transfers above ₹1,00,000 to masked accounts
    # with no prior history = higher risk
    # Weight: +10
    # ----------------------------------------------------------
    if is_transfer and amount and amount >= 100000:
        receiver = receipt_data.get("receiver", "")
        if receiver and "****" in str(receiver):
            score += 10
            signals.append(
                f"Large transfer of ₹{amount:,.0f} to "
                f"masked account ({receiver}) (+10)"
            )

    # ----------------------------------------------------------
    # Cap at 100
    # ----------------------------------------------------------
    score = min(score, 100)

    # ----------------------------------------------------------
    # Verdict
    # ----------------------------------------------------------
    if   score >= 60: verdict = "HIGH_RISK"
    elif score >= 30: verdict = "MEDIUM_RISK"
    else:             verdict = "LOW_RISK"

    signals_text = " | ".join(signals) if signals else "No anomalies detected."

    return {
        "score"      : score,
        "verdict"    : verdict,
        "signals"    : signals,
        "is_transfer": is_transfer,
        "summary"    : (
            f"Risk Score: {score}/100 | Verdict: {verdict} | "
            f"Triggered Signals: {signals_text}"
        )
    }