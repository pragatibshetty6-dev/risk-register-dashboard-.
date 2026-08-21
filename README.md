# AI Governance Risk Register & Smart Routing Dashboard

A Flask + SQLite prototype for AI governance risk management.

## Key feature: query-first smart routing
Type a natural-language service/risk query on the dashboard. The explainable routing engine recommends a primary department such as ICT, Cybersecurity, HR, Human Services, Data Protection, Legal & Compliance, Procurement, Finance, or AI Governance. It also suggests related departments, explains why they are involved, shows detected signals, and recommends the next action.

This prototype uses deterministic keyword/rule-based classification so the result is explainable and reproducible. It can later be replaced by an ML/LLM classifier without changing the dashboard workflow.

## Run
1. Create/activate the venv.
2. `pip install -r requirements.txt`
3. `python app.py`
4. Open `http://127.0.0.1:5000`

## Example queries
- `Employee AI chatbot is collecting staff personal data and may expose it externally` → HR / Data Protection / AI Governance
- `AI application has weak authentication and access controls` → Cybersecurity / AI Governance
- `Vendor AI platform needs contract and compliance review` → Procurement / Legal & Compliance / AI Governance
- `AI system API integration is failing in the production network` → ICT / AI Governance
- `AI model is being used to automate employee performance decisions` → HR / AI Governance
