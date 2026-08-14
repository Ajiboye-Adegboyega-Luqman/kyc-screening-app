"""
KYC / AML Customer Risk Screening Tool
--------------------------------------
An interactive app that risk-rates a customer, screens their name against a
sanctions/PEP watchlist, checks their activity, and gives a compliance
recommendation. Built with Streamlit.
"""

import pandas as pd
from difflib import SequenceMatcher
import streamlit as st

st.set_page_config(page_title="KYC / AML Risk Screening", page_icon="🛡️", layout="wide")

COUNTRY_TIER = {
    **{c: "Low" for c in ["United Kingdom", "Germany", "Canada", "France", "Japan",
                          "United States", "Australia", "Netherlands", "Ireland", "Sweden"]},
    **{c: "Medium" for c in ["Nigeria", "India", "Brazil", "UAE", "South Africa",
                             "Turkey", "Mexico", "China", "Kenya"]},
    **{c: "High" for c in ["Russia", "Iran", "North Korea", "Syria", "Panama",
                           "Afghanistan", "Myanmar"]},
}
HIGH_OCC = ["Casino Operator", "Money Service Business", "Arms Dealer",
            "Cash-Intensive Business", "Precious Metals Dealer"]
MED_OCC = ["Retail Trader", "Real Estate Agent", "Car Dealer", "Jeweller", "Import/Export Trader"]
LOW_OCC = ["Teacher", "Software Engineer", "Nurse", "Accountant", "Civil Servant", "Doctor"]
HIGH_PROD = ["International Wire Transfers", "Crypto Wallet", "Private Banking", "Trade Finance"]
MED_PROD = ["Credit Card", "Personal Loan"]
LOW_PROD = ["Savings Account", "Current Account", "Fixed Deposit"]


@st.cache_data
def load_watchlist():
    return pd.read_csv("watchlist.csv")


def name_similarity(a, b):
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def screen_name(name, watchlist, threshold=0.85):
    best = {"score": 0}
    for _, row in watchlist.iterrows():
        s = name_similarity(name, row["watchlist_name"])
        if s > best["score"]:
            best = {"name": row["watchlist_name"], "score": s,
                    "type": row["list_type"], "source": row["source"]}
    best["hit"] = best["score"] >= threshold
    return best


def score_customer(inp):
    tier = {"Low": 0, "Medium": 15, "High": 40}
    b = {}
    b["Country risk"] = tier[COUNTRY_TIER.get(inp["country"], "Medium")]
    b["Occupation risk"] = 25 if inp["occupation"] in HIGH_OCC else (10 if inp["occupation"] in MED_OCC else 0)
    b["Product risk"] = 20 if inp["product"] in HIGH_PROD else (10 if inp["product"] in MED_PROD else 0)
    b["PEP status"] = 25 if inp["pep"] else 0
    b["Adverse media"] = 20 if inp["adverse"] else 0
    b["Non-face-to-face onboarding"] = 10 if inp["channel"] == "Online (non-face-to-face)" else 0
    b["Undisclosed source of funds"] = 15 if inp["sof"] == "Undisclosed" else 0
    b["Unverified ID"] = 15 if not inp["id_verified"] else 0
    return sum(b.values()), b


def rating_from_score(score):
    if score >= 60:
        return "High"
    elif score >= 25:
        return "Medium"
    return "Low"


st.title("🛡️ KYC / AML Customer Risk Screening Tool")
st.caption("Enter a customer's details to generate a risk rating, sanctions/PEP screening "
           "result, and a compliance recommendation. Built by Ajiboye Luqman Adegboyega.")

watchlist = load_watchlist()

with st.sidebar:
    st.header("Customer details")
    full_name = st.text_input("Full name", "Ivan Petroff")
    country = st.selectbox("Country of residence", sorted(COUNTRY_TIER.keys()), index=0)
    occupation = st.selectbox("Occupation", LOW_OCC + MED_OCC + HIGH_OCC)
    product = st.selectbox("Product / service", LOW_PROD + MED_PROD + HIGH_PROD)
    channel = st.radio("Onboarding channel",
                       ["Branch (face-to-face)", "Online (non-face-to-face)"])
    sof = st.selectbox("Source of funds",
                       ["Salary", "Business Income", "Investment Returns",
                        "Inheritance", "Savings", "Property Sale", "Undisclosed"])
    pep = st.checkbox("Politically Exposed Person (PEP)")
    adverse = st.checkbox("Adverse media hit")
    id_verified = st.checkbox("Identity document verified", value=True)
    st.markdown("---")
    st.subheader("Activity")
    expected = st.number_input("Expected monthly activity (£)", min_value=0, value=2000, step=100)
    actual = st.number_input("Actual monthly activity (£)", min_value=0, value=2000, step=100)

inp = dict(country=country, occupation=occupation, product=product, channel=channel,
           sof=sof, pep=pep, adverse=adverse, id_verified=id_verified)

score, breakdown = score_customer(inp)
rating = rating_from_score(score)
match = screen_name(full_name, watchlist)
activity_ratio = (actual / expected) if expected > 0 else 0
activity_flag = activity_ratio >= 3

col1, col2, col3 = st.columns(3)
rating_colour = {"Low": "🟢", "Medium": "🟠", "High": "🔴"}
col1.metric("Risk rating", f"{rating_colour[rating]} {rating}")
col2.metric("Risk score", f"{score} / 145")
col3.metric("Activity vs expected", f"{activity_ratio:.1f}×",
            delta="Flagged" if activity_flag else "Normal",
            delta_color="inverse" if activity_flag else "normal")

st.markdown("---")
left, right = st.columns(2)

with left:
    st.subheader("📋 Risk score breakdown")
    bd = pd.DataFrame({"Risk factor": breakdown.keys(), "Points": breakdown.values()})
    bd = bd[bd["Points"] > 0].sort_values("Points", ascending=False)
    if len(bd):
        st.bar_chart(bd.set_index("Risk factor"), horizontal=True)
        st.dataframe(bd, hide_index=True, use_container_width=True)
    else:
        st.info("No risk factors triggered — this is a low-risk profile.")

with right:
    st.subheader("🔍 Sanctions / PEP screening")
    if match["hit"]:
        st.error(
            f"**POTENTIAL MATCH — escalate for review**\n\n"
            f"Closest watchlist entry: **{match['name']}** "
            f"({match['type']}, {match['source']})\n\n"
            f"Match confidence: **{match['score']*100:.0f}%**"
        )
    else:
        st.success(f"No watchlist match (closest: {match['score']*100:.0f}% — below the 85% threshold).")

    st.subheader("📈 Activity monitoring")
    if activity_flag:
        st.warning(f"Activity is **{activity_ratio:.1f}×** the expected level — review recommended.")
    else:
        st.info("Activity is in line with the customer's expected profile.")

st.markdown("---")
st.subheader("✅ Compliance recommendation")

if match["hit"] or rating == "High":
    st.error(
        "**Enhanced Due Diligence (EDD) required.** "
        "Escalate to a senior compliance officer. Obtain additional identity and "
        "source-of-funds evidence, confirm/clear any watchlist match, and apply "
        "ongoing enhanced monitoring before onboarding."
    )
elif rating == "Medium":
    st.warning(
        "**Standard Customer Due Diligence (CDD).** "
        "Verify identity and source of funds, document the risk assessment, and "
        "apply periodic review."
    )
else:
    st.success(
        "**Simplified Due Diligence (SDD).** "
        "Low-risk profile — standard identity checks and routine monitoring are sufficient."
    )

st.caption("Illustrative tool for demonstration. Screening uses fuzzy name matching against "
           "a sample OFAC/UN/EU-style watchlist; a production system would add secondary "
           "identifiers (DOB, nationality) and connect to live watchlist feeds.")
           