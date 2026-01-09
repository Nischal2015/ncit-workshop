import os

from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore

from core import load_vault_env

load_vault_env()

raw_data = [
    # --- FINANCE (10 Docs) ---
    (
        "TRV-01",
        "finance",
        "meals",
        "Employees may expense up to $75 per person for team lunches. Client dinners require Director approval if over $300.",
    ),
    (
        "TRV-02",
        "finance",
        "travel",
        "Economy class only for flights under 6 hours. Business class allowed for international flights over 6 hours.",
    ),
    (
        "TRV-03",
        "finance",
        "hotels",
        "Hotel stays must not exceed $250 per night in non-major cities, and $400 per night in major metro areas (NYC, SF, London).",
    ),
    (
        "EXP-01",
        "finance",
        "expense_reporting",
        "All expenses over $25 must include a valid itemized receipt. Credit card statements are not accepted as proof of purchase.",
    ),
    (
        "EXP-02",
        "finance",
        "approval_limits",
        "Managers can approve expenses up to $1,000. VP approval is required for anything above $5,000.",
    ),
    (
        "EXP-03",
        "finance",
        "reimbursement",
        "Reimbursement claims must be submitted within 30 days of the expense date. Late submissions require CFO approval.",
    ),
    (
        "FIN-01",
        "finance",
        "corporate_cards",
        "Corporate credit cards are for business use only. Personal usage must be repaid within 5 business days.",
    ),
    (
        "FIN-02",
        "finance",
        "procurement",
        "Purchase orders are required for any vendor services exceeding $10,000 annually.",
    ),
    (
        "FIN-03",
        "finance",
        "gifts",
        "Gifts to government officials are strictly prohibited. Client gifts are capped at $50 USD value.",
    ),
    (
        "FIN-04",
        "finance",
        "subscriptions",
        "Recurring software subscriptions on corporate cards must be audited every quarter.",
    ),
    # --- IT & SECURITY (10 Docs) ---
    (
        "IT-01",
        "it_policy",
        "software",
        "No personal software subscriptions allowed. All software must be pre-approved by the CTO.",
    ),
    (
        "IT-02",
        "it_policy",
        "hardware",
        "Laptops must be refreshed every 3 years. Employees may choose between MacBook Pro or Dell XPS.",
    ),
    (
        "SEC-01",
        "it_policy",
        "passwords",
        "Passwords must be at least 14 characters long and include special characters. Rotated every 90 days.",
    ),
    (
        "SEC-02",
        "it_policy",
        "mfa",
        "Multi-Factor Authentication (MFA) is mandatory for all internal systems, including email and slack.",
    ),
    (
        "SEC-03",
        "it_policy",
        "vpn",
        "Access to the production database is only permitted via the corporate VPN with a secure certificate.",
    ),
    (
        "SEC-04",
        "it_policy",
        "data_classification",
        "Confidential data (PII) must never be stored on local drives or unencrypted USB sticks.",
    ),
    (
        "IT-03",
        "it_policy",
        "byod",
        "Bring Your Own Device (BYOD) is permitted for mobile phones only if MDM (Mobile Device Management) software is installed.",
    ),
    (
        "IT-04",
        "it_policy",
        "incident_response",
        "All security incidents must be reported to the InfoSec team within 1 hour of discovery.",
    ),
    (
        "IT-05",
        "it_policy",
        "access_control",
        "Employee access rights are reviewed quarterly. Access is revoked immediately upon termination.",
    ),
    (
        "IT-06",
        "it_policy",
        "wifi",
        "Guest Wi-Fi is for visitors only. Employees must use the secured 'Corp-Net' SSID.",
    ),
    # --- HR & PEOPLE (10 Docs) ---
    (
        "HR-01",
        "hr_policy",
        "pto",
        "Employees accrue 1.67 days of Paid Time Off (PTO) per month, totaling 20 days per year.",
    ),
    (
        "HR-02",
        "hr_policy",
        "sick_leave",
        "Sick leave is unlimited, but a doctor's note is required for absences exceeding 3 consecutive days.",
    ),
    (
        "HR-03",
        "hr_policy",
        "remote_work",
        "Hybrid policy: Employees are expected to be in the office 2 days a week (Tuesday and Thursday).",
    ),
    (
        "HR-04",
        "hr_policy",
        "probation",
        "New hires are subject to a 90-day probationary period during which notice periods are 1 week.",
    ),
    (
        "HR-05",
        "hr_policy",
        "performance",
        "Performance reviews occur bi-annually in June and December. Self-assessments are mandatory.",
    ),
    (
        "HR-06",
        "hr_policy",
        "benefits",
        "Health insurance coverage begins on the first day of employment. Dental and Vision are optional add-ons.",
    ),
    (
        "HR-07",
        "hr_policy",
        "code_of_conduct",
        "Respectful workplace policy strictly prohibits harassment or discrimination based on race, gender, or religion.",
    ),
    (
        "HR-08",
        "hr_policy",
        "referral_bonus",
        "Employees receive a $2,000 bonus for referring successful engineering candidates, payable after 3 months.",
    ),
    (
        "HR-09",
        "hr_policy",
        "sabbatical",
        "Employees are eligible for a 4-week paid sabbatical after 5 years of continuous service.",
    ),
    (
        "HR-10",
        "hr_policy",
        "training",
        "Each employee has an annual $1,000 budget for professional development and training courses.",
    ),
    # --- LEGAL & COMPLIANCE (10 Docs) ---
    (
        "LEG-01",
        "legal_policy",
        "nda",
        "Non-Disclosure Agreements (NDAs) must be signed by all external contractors before data access is granted.",
    ),
    (
        "LEG-02",
        "legal_policy",
        "gdpr",
        "Customer data deletion requests (Right to be Forgotten) must be processed within 30 days.",
    ),
    (
        "LEG-03",
        "legal_policy",
        "intellectual_property",
        "All code, designs, and documents created during work hours are the sole property of the company.",
    ),
    (
        "LEG-04",
        "legal_policy",
        "trading",
        "Insider trading policy prohibits trading company stock during 'blackout periods' prior to earnings calls.",
    ),
    (
        "LEG-05",
        "legal_policy",
        "social_media",
        "Employees must not post confidential company information on social media. Disclaimer required for personal opinions.",
    ),
    (
        "LEG-06",
        "legal_policy",
        "conflict_of_interest",
        "Employees must disclose any outside employment or board seats to the Legal department.",
    ),
    (
        "LEG-07",
        "legal_policy",
        "whistleblower",
        "Anonymous reporting of unethical behavior is protected. No retaliation is permitted against whistleblowers.",
    ),
    (
        "LEG-08",
        "legal_policy",
        "contract_signing",
        "Only C-level executives are authorized to sign binding contracts on behalf of the company.",
    ),
    (
        "LEG-09",
        "legal_policy",
        "export_control",
        "Software cannot be exported to countries on the US embargo list.",
    ),
    (
        "LEG-10",
        "legal_policy",
        "records_retention",
        "Financial records must be retained for 7 years. Email logs are retained for 2 years.",
    ),
    # --- ENGINEERING & OPS (10 Docs) ---
    (
        "ENG-01",
        "engineering_policy",
        "code_review",
        "All code changes require approval from at least one peer and one senior engineer before merging.",
    ),
    (
        "ENG-02",
        "engineering_policy",
        "deployment",
        "Production deployments are not allowed on Fridays after 2 PM local time.",
    ),
    (
        "ENG-03",
        "engineering_policy",
        "on_call",
        "Engineers on the PagerDuty rotation receive a flat stipend of $500 per week of rotation.",
    ),
    (
        "ENG-04",
        "engineering_policy",
        "open_source",
        "Use of AGPL-licensed libraries is strictly prohibited in proprietary codebases.",
    ),
    (
        "ENG-05",
        "engineering_policy",
        "cloud_resources",
        "Unused cloud instances must be terminated within 24 hours. Tagging is mandatory for cost allocation.",
    ),
    (
        "OPS-01",
        "operations_policy",
        "building_access",
        "Office access hours are 7 AM to 10 PM. Overnight stays are not permitted.",
    ),
    (
        "OPS-02",
        "operations_policy",
        "visitors",
        "All visitors must sign in at the front desk and wear a visible badge at all times.",
    ),
    (
        "OPS-03",
        "operations_policy",
        "emergency",
        "In case of fire alarm, evacuate immediately to the designated assembly point in the parking lot.",
    ),
    (
        "OPS-04",
        "operations_policy",
        "clean_desk",
        "Confidential documents must be locked in drawers when leaving the desk for more than 15 minutes.",
    ),
    (
        "OPS-05",
        "operations_policy",
        "shipping",
        "Personal packages may not be shipped to the office address.",
    ),
]

policy_docs = [
    Document(
        page_content=content,
        metadata={"category": category, "topic": topic, "policy_id": pid},
    )
    for pid, category, topic, content in raw_data
]


if __name__ == "__main__":
    # Load document into already existing Qdrant collection
    vector_store = QdrantVectorStore.from_existing_collection(
        collection_name="ncit-workshop-simple-rag",
        embedding=OpenAIEmbeddings(model="text-embedding-3-small"),
        url=os.getenv("QDRANT_URL"),
        api_key=os.getenv("QDRANT_API_KEY"),
    )
    vector_store.add_documents(policy_docs)
