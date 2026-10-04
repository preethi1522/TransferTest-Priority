# TransferTest Priority: Banking Regression Test Recommendations
Individual PE6201 prototype by Preethi. All data is fictional. The dataset and labels are **drafts for domain review**, not validated banking evidence.

## Run in Google Colab
1. Download and open `Banking_Test_Priority_Colab.ipynb` in Colab.
2. Run the first cell, and upload `data/test_cases.csv` and `data/past_defects.csv` together.
3. Run through the ranking cells. Upload `data/answer_key.csv` **only when the evaluation cell asks for it**.
4. Check the recommended tests and missed defect links. Edit `release_change` to try another change; run ranking and evaluation again.

To regenerate the exact sample data: `python make_data.py`. Keep the answer key fixed while testing rankings. Never copy answer-key fields into model prompts or ranking data.

## Current limits and next work
- The main ranking uses TF-IDF word matching and explicit weights. TF-IDF is a statistical text model. The optional LLM call drafts explanations after the ranking; it does not change the top 20.
- The evaluation answer key is synthetic and should be inspected by a banking QA reviewer before treating the result as meaningful. The answer key covers the fictional fund-transfer release only. For other release changes, define and freeze a separate key first.
- Evaluation revision log: The first generated `defect_description` repeated the test scenario; after a first 10/20 vs 10/20 run, it was rewritten as distinct fictional failure narratives. The defect-to-test links stayed the same. This is **not** an independently blinded evaluation; disclose the revision and seek a separate reviewer-authored holdout before any general claim.
- Some generic generated variants may be awkward in real testing; review the CSV rows and revise the generator **before freezing the evaluation set**.
- The optional last cell uses OpenRouter (`openai/gpt-4o-mini`) to explain the first five ranked tests with structured JSON and verified historical-defect IDs. It needs your own key and makes a paid API request. In the student's example run it took 4.36 seconds, used 391 input and 269 output tokens, and reported US$0.00022005 API cost. It does **not** change ranking or the 10/20 coverage result. The published notebook has no outputs or embedded API key.
- Next: review scenario realism, upload the code and analysis PDF to GitHub, and record the demo.
- Human QA review is mandatory. This tool does not deploy, roll back, or approve changes.
