"""Create reproducible fictional banking QA data. No real customer or bank records."""
import csv
from pathlib import Path

ROOT = Path(__file__).parent / "data"
ROOT.mkdir(exist_ok=True)

SCENARIOS = [
    ("Transfers", "Daily transfer limit", "daily transfer limit", 5),
    ("Transfers", "Monthly transfer limit", "monthly transfer limit", 4),
    ("Transfers", "PayNow mobile transfer", "PayNow mobile transfer", 5),
    ("Transfers", "PayNow NRIC transfer", "PayNow NRIC transfer", 4),
    ("Transfers", "Other bank transfer", "other bank transfer", 5),
    ("Transfers", "Own account transfer", "own account transfer", 4),
    ("Payees", "Add bank payee", "add bank payee", 4),
    ("Payees", "Add PayNow payee", "add PayNow payee", 4),
    ("Login", "Customer login", "customer login", 5),
    ("Cards", "Card payment", "card payment", 5),
    ("Cards", "Card limit", "card spending limit", 4),
    ("Cards", "Card lock", "card lock and unlock", 4),
    ("Appearance", "Theme", "app theme", 1),
]
STANDARD_VARIANTS = [
    "successful standard journey", "boundary value exactly at threshold",
    "value above allowed threshold", "invalid details rejected",
    "network interruption and retry", "duplicate request prevention",
    "newly enrolled user journey", "existing user journey",
]
def variants_for(feature):
    if feature == "Theme":
        return ["switch between light and dark", "retain preference after login",
                "show readable transfer confirmation", "display correctly after app restart"]
    if feature == "Customer login":
        return ["valid credentials", "invalid password rejected", "locked user blocked",
                "expired session requires sign-in", "new device verification",
                "retry after network failure", "sign-out invalidates session", "biometric failure fallback"]
    if feature == "Card lock":
        return ["lock active card", "unlock locked card", "payment rejected while locked",
                "duplicate lock request", "network failure during lock",
                "card status persists after login", "invalid card rejected", "status refresh after unlock"]
    if feature.startswith("Add "):
        return ["valid details accepted", "duplicate payee rejected", "invalid identifier rejected",
                "confirmation required", "network failure before saving",
                "payee available after approval", "unauthorised addition blocked", "details persist after login"]
    if feature == "Card payment":
        return ["successful payment", "insufficient funds rejected", "duplicate charge prevented",
                "network retry", "declined payment", "refund display",
                "payment after card lock rejected", "transaction alert generated"]
    return STANDARD_VARIANTS

tests = []
def severity_for(module, variant, impact):
    """Previous test priority: related to impact, but adjusted for this test's failure mode."""
    if module == "Appearance":
        return 1 if "switch" in variant or "restart" in variant else 2
    if any(word in variant for word in ("unauthorised", "above allowed", "duplicate charge", "payment rejected while locked")):
        return 5
    if any(word in variant for word in ("invalid", "locked", "duplicate", "network", "boundary", "threshold")):
        return min(5, max(3, impact))
    return min(5, max(2, impact - 1))

for module, feature, phrase, impact in SCENARIOS:
    for variant in variants_for(feature):
        if len(tests) == 100:
            break
        tests.append({
            "test_id": f"TC-{len(tests)+1:03d}", "module": module, "feature": feature,
            "test_description": f"Verify {phrase}: {variant}.",
            "business_impact": impact,
            "existing_severity": severity_for(module, variant, impact),
        })

# These records are visible to the ranking tool. They never contain answer-key IDs.
history = []
for j, idx in enumerate([0, 2, 4, 8, 10, 16, 18, 24, 32, 40, 48, 56, 64, 72, 80, 88], 1):
    row = tests[idx]
    history.append({"defect_id": f"H-{j:03d}", "module": row["module"],
                    "feature": row["feature"],
                    "defect_description": f"Earlier regression issue in {row['feature'].lower()} affecting {row['test_description'].split(': ')[1]}",
                    "severity": 4 if row["business_impact"] >= 4 else 2})

# Evaluation labels are NEVER passed to ranking. Every one of 20 defects maps
# to one distinct test. A QA reviewer must verify these synthetic assumptions.
target_indices = [1, 2, 3, 5, 6, 9, 11, 13, 17, 18, 19, 20, 21, 22, 24, 25, 26, 27, 29, 30]
eval_failures = [
    "Transfer of exactly S$1,000 is wrongly blocked when the daily cap is S$1,000.",
    "Transfer above the daily cap goes through instead of being stopped.",
    "Malformed transfer account number passes validation and reaches confirmation.",
    "Double tapping Submit creates two separate transfers and debits twice.",
    "New customer receives the wrong default daily transfer cap.",
    "Transfer exactly at the monthly cap is wrongly rejected.",
    "Invalid monthly limit amount is accepted during a transfer.",
    "Retrying a monthly-capped payment results in two debits.",
    "PayNow transfer exactly at the daily cap is incorrectly rejected.",
    "PayNow mobile transfer exceeds the permitted daily cap.",
    "Malformed mobile number is accepted as a PayNow recipient.",
    "After a network timeout the PayNow transfer posts, but the app shows failure.",
    "Retry after a PayNow timeout debits the account twice.",
    "Newly enrolled customer is given a PayNow cap meant for established users.",
    "PayNow NRIC transfer fails despite valid recipient and sufficient funds.",
    "PayNow NRIC transfer exactly at the limit is wrongly blocked.",
    "PayNow NRIC transfer above the daily cap is allowed.",
    "Invalid NRIC recipient reference is accepted without validation.",
    "Repeated PayNow NRIC confirmation sends the transfer twice.",
    "Newly enrolled customer's PayNow NRIC transfer skips the lower onboarding limit.",
]
answer_key = [{"release_id": "REL-TRANSFER-01", "eval_defect_id": f"E-{j:03d}", "test_id": tests[idx]["test_id"],
               "defect_severity": 5,
               "defect_description": eval_failures[j-1],
               "scenario": tests[idx]["test_description"]}
              for j, idx in enumerate(target_indices, 1)]

def save(name, rows):
    with (ROOT / name).open("w", newline="", encoding="utf-8") as fp:
        writer = csv.DictWriter(fp, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

save("test_cases.csv", tests)
save("past_defects.csv", history)
save("answer_key.csv", answer_key)
print(f"Created {len(tests)} test cases, {len(history)} visible historical defects, and {len(answer_key)} hidden evaluation links.")
