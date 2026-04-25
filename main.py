from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
import joblib
import numpy as np
import warnings
warnings.filterwarnings("ignore")

from nlp_extractor import extract_text_from_pdf, extract_loan_fields

app = FastAPI(title="IntelliLoan API")
model = joblib.load("ML_model.joblib")

FEATURE_ORDER = [
    "Married", "Dependents", "Education", "Self_Employed",
    "ApplicantIncome", "CoapplicantIncome", "LoanAmount",
    "Loan_Amount_Term", "Credit_History", "Gender_Female",
    "Property_Area_Rural", "Property_Area_Semiurban", "Property_Area_Urban"
]

class LoanApplication(BaseModel):
    Married: int
    Dependents: int
    Education: int
    Self_Employed: int
    ApplicantIncome: float
    CoapplicantIncome: float
    LoanAmount: float
    Loan_Amount_Term: float
    Credit_History: int
    Gender_Female: int
    Property_Area_Rural: int
    Property_Area_Semiurban: int
    Property_Area_Urban: int


def run_prediction(data: dict):
    features = np.array([[data[f] for f in FEATURE_ORDER]])
    prediction = model.predict(features)[0]
    probability = model.predict_proba(features)[0]
    return {
        "approved": bool(prediction),
        "approval_probability": round(float(probability[1]) * 100, 2),
        "rejection_probability": round(float(probability[0]) * 100, 2)
    }


@app.post("/predict")
def predict(data: LoanApplication):
    return run_prediction(data.model_dump())


@app.post("/predict-document")
async def predict_from_document(file: UploadFile = File(...)):
    """Upload a PDF document → extract fields via NLP → return prediction."""
    file_bytes = await file.read()
    text = extract_text_from_pdf(file_bytes)

    if not text.strip():
        return {"error": "Could not extract text from document. Try a text-based PDF."}

    extracted, notes = extract_loan_fields(text)
    result = run_prediction(extracted)

    return {
        **result,
        "extracted_fields": extracted,
        "extraction_notes": notes,
        "raw_text_preview": text[:500]
    }


@app.get("/health")
def health():
    return {"status": "ok"}
