"""
nlp_extractor.py
Automatic Document Understanding (ADU) for IntelliLoan.
Extracts loan-relevant fields from PDF text using regex + keyword NLP.
"""

import re
import fitz  # PyMuPDF


# ─────────────────────────────────────────────────────────────────────────────
#  PDF → Text
# ─────────────────────────────────────────────────────────────────────────────
def extract_text_from_pdf(file_bytes: bytes) -> str:
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    full_text = ""
    for page in doc:
        full_text += page.get_text()
    doc.close()
    return full_text


# ─────────────────────────────────────────────────────────────────────────────
#  Helpers
# ─────────────────────────────────────────────────────────────────────────────
def _find_number(patterns: list[str], text: str, default=None):
    """Return first numeric match from a list of regex patterns."""
    for pat in patterns:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            # Remove commas, return float
            raw = re.sub(r"[,\s]", "", m.group(1))
            try:
                return float(raw)
            except ValueError:
                continue
    return default


def _find_keyword(patterns: list[str], yes_words: list[str],
                  no_words: list[str], text: str, default=None):
    """Return 1/0 based on keyword presence near matched pattern."""
    for pat in patterns:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            context = text[max(0, m.start()-30): m.end()+60].lower()
            for w in yes_words:
                if w in context:
                    return 1
            for w in no_words:
                if w in context:
                    return 0
    return default


# ─────────────────────────────────────────────────────────────────────────────
#  Main extractor
# ─────────────────────────────────────────────────────────────────────────────
def extract_loan_fields(text: str) -> dict:
    """
    Extract all 13 ML model features from raw document text.
    Returns a dict with extracted values and confidence notes.
    """
    t = text  # full text for matching

    extracted = {}
    notes = {}

    # ── 1. Gender ──────────────────────────────────────────────────────────
    gender_female = 0
    gm = re.search(r"(gender|sex)\s*[:\-]?\s*(male|female|m\b|f\b)", t, re.IGNORECASE)
    if gm:
        val = gm.group(2).lower()
        gender_female = 1 if val.startswith("f") else 0
        notes["gender"] = f"Found: '{gm.group(0).strip()}'"
    else:
        # fallback: look for pronouns
        if re.search(r"\b(she|her|ms\.?|mrs\.?|miss)\b", t, re.IGNORECASE):
            gender_female = 1
            notes["gender"] = "Inferred Female from pronouns"
        else:
            notes["gender"] = "Assumed Male (default)"
    extracted["Gender_Female"] = gender_female

    # ── 2. Married ─────────────────────────────────────────────────────────
    married = _find_keyword(
        [r"(marital\s*status|married)\s*[:\-]?\s*\w+"],
        yes_words=["married", "yes", "spouse"],
        no_words=["unmarried", "single", "no", "divorced", "widowed"],
        text=t, default=0
    )
    if married is None:
        married = 1 if re.search(r"\b(married|spouse|husband|wife)\b", t, re.IGNORECASE) else 0
    extracted["Married"] = int(married)
    notes["married"] = "Detected from document"

    # ── 3. Dependents ──────────────────────────────────────────────────────
    dep = _find_number(
        [r"dependents?\s*[:\-]?\s*(\d+)",
         r"no\.?\s*of\s*dependents?\s*[:\-]?\s*(\d+)",
         r"(\d+)\s*dependents?"],
        t, default=0
    )
    extracted["Dependents"] = min(int(dep), 3)
    notes["dependents"] = f"Found: {int(dep)}"

    # ── 4. Education ───────────────────────────────────────────────────────
    edu = 0
    edu_match = re.search(
        r"(education|qualification|degree)\s*[:\-]?\s*([^\n,]{2,40})", t, re.IGNORECASE)
    if edu_match:
        edu_val = edu_match.group(2).lower()
        if any(w in edu_val for w in ["graduate", "bachelor", "master", "phd", "bsc", "msc",
                                       "b.sc", "m.sc", "b.e", "m.e", "university", "college"]):
            edu = 1
        notes["education"] = f"Found: '{edu_match.group(2).strip()}'"
    else:
        # fallback: check for degree keywords anywhere
        if re.search(r"\b(b\.?sc|m\.?sc|b\.?e|m\.?e|phd|bachelor|master|graduate|university)\b", t, re.IGNORECASE):
            edu = 1
            notes["education"] = "Degree keyword found in text"
        else:
            notes["education"] = "Not found, assumed Not Graduate"
    extracted["Education"] = edu

    # ── 5. Self Employed ───────────────────────────────────────────────────
    se = _find_keyword(
        [r"(self[- ]?employ|business\s*owner|self[- ]?employed)\s*[:\-]?\s*\w*"],
        yes_words=["yes", "self", "own", "business"],
        no_words=["no", "salaried", "employed by", "job"],
        text=t, default=0
    )
    if se is None:
        se = 1 if re.search(r"\b(self.?employ|own\s*business|freelanc|proprietor)\b", t, re.IGNORECASE) else 0
    extracted["Self_Employed"] = int(se)
    notes["self_employed"] = "Detected from document"

    # ── 6. Applicant Income ────────────────────────────────────────────────
    income = _find_number(
        [r"(?:applicant\s*)?(?:monthly\s*)?income\s*[:\-]?\s*(?:pkr|rs\.?|₨)?\s*([\d,]+)",
         r"(?:pkr|rs\.?|₨)\s*([\d,]+)\s*(?:per\s*month|\/month|pm\b|salary)",
         r"salary\s*[:\-]?\s*(?:pkr|rs\.?|₨)?\s*([\d,]+)",
         r"gross\s*income\s*[:\-]?\s*(?:pkr|rs\.?|₨)?\s*([\d,]+)"],
        t, default=45000
    )
    extracted["ApplicantIncome"] = float(income)
    notes["applicant_income"] = f"Extracted: {income:,.0f}"

    # ── 7. Co-Applicant Income ─────────────────────────────────────────────
    co_income = _find_number(
        [r"co[- ]?applicant\s*income\s*[:\-]?\s*(?:pkr|rs\.?|₨)?\s*([\d,]+)",
         r"spouse\s*income\s*[:\-]?\s*(?:pkr|rs\.?|₨)?\s*([\d,]+)"],
        t, default=0
    )
    extracted["CoapplicantIncome"] = float(co_income)
    notes["coapplicant_income"] = f"Extracted: {co_income:,.0f}"

    # ── 8. Loan Amount ─────────────────────────────────────────────────────
    loan_amt = _find_number(
        [r"loan\s*amount\s*[:\-]?\s*(?:pkr|rs\.?|₨)?\s*([\d,]+)",
         r"requested\s*(?:loan\s*)?amount\s*[:\-]?\s*(?:pkr|rs\.?|₨)?\s*([\d,]+)",
         r"amount\s*(?:required|requested|needed)\s*[:\-]?\s*(?:pkr|rs\.?|₨)?\s*([\d,]+)"],
        t, default=150
    )
    # If value > 10000, assume it's in full PKR, convert to thousands
    if loan_amt > 10000:
        loan_amt = loan_amt / 1000
    extracted["LoanAmount"] = float(loan_amt)
    notes["loan_amount"] = f"Extracted: {loan_amt:.1f}k"

    # ── 9. Loan Term ────────────────────────────────────────────────────────
    term = _find_number(
        [r"loan\s*(?:term|tenure|period|duration)\s*[:\-]?\s*([\d,]+)\s*(?:months?|mo\.?)?",
         r"repayment\s*(?:period|term)\s*[:\-]?\s*([\d,]+)\s*(?:months?)?",
         r"([\d,]+)\s*months?\s*(?:term|tenure|loan)"],
        t, default=360
    )
    # If in years, convert
    yr_match = re.search(
        r"(?:loan\s*)?(?:term|tenure|period)\s*[:\-]?\s*([\d]+)\s*years?", t, re.IGNORECASE)
    if yr_match and not _find_number([r"loan\s*(?:term|tenure)\s*[:\-]?\s*([\d,]+)\s*months?"], t):
        term = float(yr_match.group(1)) * 12
    extracted["Loan_Amount_Term"] = float(term)
    notes["loan_term"] = f"Extracted: {int(term)} months"

    # ── 10. Credit History ─────────────────────────────────────────────────
    credit = 1  # default good
    cm = re.search(r"credit\s*(?:history|score|rating)\s*[:\-]?\s*(\w+)", t, re.IGNORECASE)
    if cm:
        val = cm.group(1).lower()
        credit = 0 if val in ["bad", "poor", "no", "0", "none", "negative"] else 1
        notes["credit_history"] = f"Found: '{cm.group(0).strip()}'"
    else:
        # Score-based
        score_m = re.search(r"(?:cibil|credit)\s*score\s*[:\-]?\s*([\d]+)", t, re.IGNORECASE)
        if score_m:
            score = int(score_m.group(1))
            credit = 1 if score >= 600 else 0
            notes["credit_history"] = f"Score: {score} → {'Good' if credit else 'Bad'}"
        else:
            notes["credit_history"] = "Not found, assumed Good"
    extracted["Credit_History"] = int(credit)

    # ── 11. Property Area ──────────────────────────────────────────────────
    rural = semi = urban = 0
    area_m = re.search(
        r"property\s*(?:area|location|type)\s*[:\-]?\s*(\w+)", t, re.IGNORECASE)
    if area_m:
        area_val = area_m.group(1).lower()
        if "semi" in area_val:
            semi = 1
        elif "rural" in area_val or "village" in area_val:
            rural = 1
        else:
            urban = 1
        notes["property_area"] = f"Found: '{area_m.group(1)}'"
    else:
        # Check anywhere in text
        if re.search(r"\b(semiurban|semi.urban)\b", t, re.IGNORECASE):
            semi = 1
        elif re.search(r"\b(rural|village|town)\b", t, re.IGNORECASE):
            rural = 1
        else:
            urban = 1
            notes["property_area"] = "Defaulted to Urban"
    extracted["Property_Area_Rural"] = rural
    extracted["Property_Area_Semiurban"] = semi
    extracted["Property_Area_Urban"] = urban

    return extracted, notes
