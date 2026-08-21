from flask import Flask, render_template, request, redirect, url_for, jsonify
import sqlite3
from datetime import datetime

app = Flask(__name__)
DB = "risk_register.db"

def db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = db()
    conn.execute("""
    CREATE TABLE IF NOT EXISTS risks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        risk_id TEXT UNIQUE NOT NULL,
        title TEXT NOT NULL,
        description TEXT,
        department TEXT NOT NULL,
        related_department TEXT,
        relationship_reason TEXT,
        category TEXT,
        likelihood INTEGER DEFAULT 1,
        impact INTEGER DEFAULT 1,
        score INTEGER DEFAULT 1,
        level TEXT DEFAULT 'Low',
        owner TEXT,
        reported_by TEXT,
        status TEXT DEFAULT 'Open',
        resolution TEXT,
        solved_by TEXT,
        how_solved TEXT,
        root_cause TEXT,
        evidence TEXT,
        created_at TEXT,
        updated_at TEXT
    )
    """)
    count = conn.execute("SELECT COUNT(*) FROM risks").fetchone()[0]
    if count == 0:
        sample = [
            ("AI-RISK-001","Unauthorized AI Tool Usage",
             "An unapproved AI service is being used for organizational work.",
             "ICT","Cybersecurity",
             "The request involves organizational data and requires security review.",
             "Security",4,5,"ICT Manager","Governance Analyst","Open"),
            ("AI-RISK-002","Missing Data Privacy Assessment",
             "AI service request does not contain a completed privacy assessment.",
             "Data Protection","Legal & Compliance",
             "The system may process personal or sensitive organizational data.",
             "Compliance",4,4,"Data Protection Officer","Governance Analyst","In Progress"),
            ("AI-RISK-003","Invalid Service Request",
             "Submitted SR is missing mandatory governance information.",
             "ICT","AI Governance",
             "Invalid SRs are automatically routed to governance for validation.",
             "Governance",3,4,"ICT Manager","Service Desk","Resolved"),
            ("AI-RISK-004","Weak Access Controls",
             "AI application does not meet required access-control standards.",
             "Application Team","Cybersecurity",
             "Identity, authentication and authorization controls are security responsibilities.",
             "Cybersecurity",5,4,"Security Lead","Risk Analyst","Open"),
            ("AI-RISK-005","Third-Party AI Vendor Risk",
             "External AI provider has not completed vendor risk review.",
             "Procurement","Legal & Compliance",
             "Contractual, regulatory and third-party obligations require compliance review.",
             "Third Party",3,5,"Procurement Manager","Governance Analyst","In Progress")
        ]
        for r in sample:
            score = r[7] * r[8]
            level = "Critical" if score >= 16 else "High" if score >= 10 else "Medium" if score >= 5 else "Low"
            conn.execute("""INSERT INTO risks
                (risk_id,title,description,department,related_department,relationship_reason,
                 category,likelihood,impact,score,level,owner,reported_by,status,created_at,updated_at)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (*r[:7],r[7],r[8],score,level,*r[9:],datetime.now().strftime("%Y-%m-%d %H:%M"),datetime.now().strftime("%Y-%m-%d %H:%M")))
    conn.commit()
    conn.close()


# Smart Governance Routing Engine
# This is a deterministic, explainable triage engine for the prototype.
ROUTING_RULES = [
    ("HR", ["employee", "employee data", "recruitment", "hiring", "payroll", "salary", "leave", "performance", "workforce", "staff", "candidate", "cv", "resume", "hr"],
     "The query concerns employees, candidates, workforce processes, or HR data."),
    ("Human Services", ["customer support", "customer service", "citizen", "patient", "beneficiary", "human service", "case management", "complaint", "public service", "welfare"],
     "The query concerns people-facing services, cases, support, or human-service delivery."),
    ("Cybersecurity", ["cyber", "security", "phishing", "malware", "ransomware", "password", "authentication", "access control", "vulnerability", "breach", "attack", "firewall", "endpoint", "soc", "zero trust"],
     "The query contains security, access-control, threat, or incident indicators."),
    ("Data Protection", ["personal data", "pii", "privacy", "sensitive data", "gdpr", "consent", "retention", "data protection", "biometric", "health data"],
     "The query involves personal, sensitive, privacy, consent, or data-protection requirements."),
    ("Legal & Compliance", ["legal", "contract", "regulation", "regulatory", "compliance", "policy", "audit", "license", "licence", "terms", "law", "gdpr"],
     "The query contains regulatory, contractual, policy, legal, or audit requirements."),
    ("Procurement", ["vendor", "supplier", "third party", "third-party", "purchase", "procurement", "contractor", "external provider", "software license", "licence"],
     "The query concerns an external supplier, vendor, purchasing, or third-party service."),
    ("Finance", ["payment", "invoice", "budget", "finance", "financial", "cost", "revenue", "bank", "transaction", "expense"],
     "The query concerns financial processes, transactions, payments, budgets, or costs."),
    ("ICT", ["system", "application", "software", "server", "network", "database", "cloud", "api", "integration", "infrastructure", "it", "ict", "technical"],
     "The query primarily concerns technology, systems, infrastructure, applications, or integrations."),
    ("AI Governance", ["ai", "artificial intelligence", "generative ai", "genai", "llm", "chatbot", "machine learning", "model", "copilot", "automation", "governance", "risk"],
     "The query concerns AI use, AI governance, model risk, or AI decision-making."),
]

def classify_query(query):
    text = (query or "").strip().lower()
    scores = []
    for dept, keywords, reason in ROUTING_RULES:
        matches = [k for k in keywords if k in text]
        if matches:
            # Give exact phrase matches slightly more weight; cap to keep results explainable.
            score = min(100, 35 + len(matches) * 15)
            scores.append((score, dept, matches, reason))
    if not scores:
        return {
            "department": "AI Governance",
            "related_departments": ["ICT"],
            "category": "Governance Review",
            "confidence": 45,
            "risk_level": "Review Required",
            "reason": "No specific departmental trigger was detected, so the query should first be reviewed by AI Governance and ICT.",
            "matched_keywords": [],
            "action": "Send for governance validation before approval."
        }
    scores.sort(reverse=True)
    top = scores[0]
    related = [x[1] for x in scores[1:3] if x[1] != top[1]]
    # AI Governance is a mandatory oversight route for AI/risk queries.
    if top[1] != "AI Governance" and ("ai" in text or "artificial intelligence" in text or "generative ai" in text or "risk" in text or "governance" in text):
        if "AI Governance" not in related:
            related.append("AI Governance")
    if not related and top[1] != "AI Governance":
        related = ["AI Governance"]
    confidence = min(98, top[0] + (10 if len(scores) > 1 else 0))
    level = "High Review Priority" if top[0] >= 65 else "Medium Review Priority"
    return {
        "department": top[1],
        "related_departments": related,
        "category": top[1],
        "confidence": confidence,
        "risk_level": level,
        "reason": top[3],
        "matched_keywords": top[2],
        "action": f"Route to {top[1]} for initial assessment" + (f" and involve {', '.join(related)}." if related else ".")
    }

@app.route("/triage", methods=["POST"])
def triage():
    query = request.form.get("query", "")
    result = classify_query(query)
    return render_template("dashboard.html", **get_dashboard_data(), triage_query=query, triage_result=result)

def get_dashboard_data():
    conn = db()
    risks = conn.execute("SELECT * FROM risks ORDER BY score DESC, id DESC").fetchall()
    total = conn.execute("SELECT COUNT(*) FROM risks").fetchone()[0]
    critical = conn.execute("SELECT COUNT(*) FROM risks WHERE level='Critical'").fetchone()[0]
    high = conn.execute("SELECT COUNT(*) FROM risks WHERE level='High'").fetchone()[0]
    open_count = conn.execute("SELECT COUNT(*) FROM risks WHERE status='Open'").fetchone()[0]
    progress = conn.execute("SELECT COUNT(*) FROM risks WHERE status='In Progress'").fetchone()[0]
    resolved = conn.execute("SELECT COUNT(*) FROM risks WHERE status='Resolved'").fetchone()[0]
    cross_dept = conn.execute("SELECT COUNT(*) FROM risks WHERE related_department IS NOT NULL AND related_department != ''").fetchone()[0]
    departments = conn.execute("SELECT department, COUNT(*) count FROM risks GROUP BY department ORDER BY count DESC").fetchall()
    levels = conn.execute("SELECT level, COUNT(*) count FROM risks GROUP BY level").fetchall()
    conn.close()
    return dict(risks=risks, total=total, critical=critical, high=high, open_count=open_count,
        progress=progress, resolved=resolved, cross_dept=cross_dept, departments=departments, levels=levels)

@app.route("/")
def dashboard():
    return render_template("dashboard.html", **get_dashboard_data())

@app.route("/risk/new", methods=["GET","POST"])
def new_risk():
    if request.method == "POST":
        f = request.form
        likelihood = int(f.get("likelihood",1)); impact = int(f.get("impact",1))
        score = likelihood * impact
        level = "Critical" if score >= 16 else "High" if score >= 10 else "Medium" if score >= 5 else "Low"
        conn = db()
        next_num = conn.execute("SELECT COUNT(*) FROM risks").fetchone()[0] + 1
        risk_id = f"AI-RISK-{next_num:03d}"
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        conn.execute("""INSERT INTO risks
        (risk_id,title,description,department,related_department,relationship_reason,category,
         likelihood,impact,score,level,owner,reported_by,status,created_at,updated_at)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (risk_id,f["title"],f["description"],f["department"],f["related_department"],
         f["relationship_reason"],f["category"],likelihood,impact,score,level,
         f["owner"],f["reported_by"],"Open",now,now))
        conn.commit(); conn.close()
        return redirect(url_for("dashboard"))
    return render_template("risk_form.html")

@app.route("/risk/<int:rid>", methods=["GET","POST"])
def risk_detail(rid):
    conn = db()
    if request.method == "POST":
        f=request.form
        conn.execute("""UPDATE risks SET status=?,resolution=?,solved_by=?,how_solved=?,
                        root_cause=?,evidence=?,updated_at=? WHERE id=?""",
                     (f["status"],f["resolution"],f["solved_by"],f["how_solved"],
                      f["root_cause"],f["evidence"],datetime.now().strftime("%Y-%m-%d %H:%M"),rid))
        conn.commit()
    risk=conn.execute("SELECT * FROM risks WHERE id=?",(rid,)).fetchone()
    conn.close()
    if not risk: return "Risk not found",404
    return render_template("risk_detail.html",risk=risk)

@app.route("/api/risks")
def api_risks():
    conn=db(); rows=conn.execute("SELECT * FROM risks ORDER BY id DESC").fetchall(); conn.close()
    return jsonify([dict(r) for r in rows])

if __name__ == "__main__":
    init_db()
    app.run(debug=True)


# TIMELINE_ENHANCEMENT
# Resolution timeline fields:
# resolved_at: exact date/time when a risk is marked Resolved
# resolution_duration: elapsed time between risk creation and resolution
# resolution_method: how the risk was resolved
# resolved_by: person/team responsible for resolution
