# 🛡️ KYC / AML Customer Risk Screening Tool

An interactive **web app** that risk-rates a customer, screens their name against a sanctions/PEP watchlist, monitors their activity, and returns a compliance recommendation — built with Python and Streamlit, and deployed live.

### ▶️ Live app: [Open the tool](https://your-app-link.streamlit.app)
*(Replace with your Streamlit link once deployed.)*

## 📌 Overview

Enter a customer's details — country, occupation, product, PEP status, source of funds and more — and the app instantly returns a **risk rating (Low / Medium / High)**, a transparent **score breakdown**, a **sanctions/PEP screening result** (with fuzzy matching to catch spelling variants), an **activity check**, and a clear **Customer Due Diligence recommendation**. It turns the KYC analyst workflow into a single, usable tool.

![App screenshot](screenshot.png)
*(Add a screenshot of your running app here.)*

## 🧭 Business context

Financial institutions must assess and document the risk of every customer, screen them against government watchlists (OFAC, UN, EU), and apply the right level of due diligence. This app demonstrates that end-to-end decision — automated, transparent and auditable — the way a KYC/AML analyst or onboarding system would.

## 🔧 Tools & methods

- **Python** — the scoring engine, fuzzy name matching (`difflib`), data handling (pandas)
- **Streamlit** — the interactive web interface
- **Streamlit Community Cloud** — free public hosting

## ✨ What it does

- **Risk rating** — a weighted, explainable score across 8 factors (country, occupation, product, PEP, adverse media, channel, source of funds, ID verification)
- **Sanctions / PEP screening** — fuzzy-matches the customer name to a watchlist, catching variant spellings (e.g. "Petroff" → "Petrov") and flagging potential hits
- **Activity monitoring** — compares actual vs expected activity and flags spikes
- **Recommendation** — outputs Simplified / Standard / Enhanced Due Diligence based on the combined result

## 🖥️ Run it locally

​```bash
pip install streamlit pandas
streamlit run app.py
​```

## 📂 Files

- `app.py` — the Streamlit application
- `watchlist.csv` — sample sanctions/PEP watchlist (OFAC/UN/EU)
- `requirements.txt` — dependencies for deployment

## 🔮 What I'd do next

- Add secondary matching (date of birth, nationality) to reduce screening false positives.
- Allow batch screening of an uploaded customer file.
- Connect to a live watchlist feed and log every screening decision for audit.

> *Illustrative tool for demonstration; screening uses a sample watchlist. A production system would connect to live sanctions data and add secondary identifiers.*

---
*Part of my data analytics portfolio — [github.com/Ajiboye-Adegboyega-Luqman](https://github.com/Ajiboye-Adegboyega-Luqman)*
