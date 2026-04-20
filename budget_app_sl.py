"""
Household Budget Tracker — Public Version
A Streamlit app for tracking shared household expenses.

Run:   streamlit run budget_app_sl.py
Needs: pip install streamlit pandas plotly openpyxl anthropic
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import json
from anthropic import Anthropic

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Household Budget Tracker",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    [data-testid="stMetricValue"] { font-size: 1.35rem; }
    [data-testid="stMetricLabel"] { font-size: 0.78rem; color: #94a3b8; }
    .block-container { padding-top: 1.5rem; }
    .stTabs [data-baseweb="tab"] { font-size: 0.85rem; }
    div[data-testid="stExpander"] { border: 1px solid #1e293b; border-radius: 8px; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────────────────────────────────────
EXPENSE_CATEGORIES = [
    "Housing — Rent / Mortgage",
    "Housing — Utilities",
    "Housing — Internet & Phone",
    "Housing — Insurance",
    "Groceries",
    "Dining & Takeout",
    "Coffee & Drinks",
    "Transportation — Gas & Fuel",
    "Transportation — Car Payment",
    "Transportation — Car Insurance",
    "Transportation — Transit & Tolls",
    "Transportation — Rideshare",
    "Shopping — Online",
    "Shopping — In-store",
    "Subscriptions & Streaming",
    "Entertainment & Leisure",
    "Health & Medical",
    "Fitness & Wellness",
    "Travel & Vacation",
    "Personal Care",
    "Education",
    "Gifts & Charity",
    "Kids & Family",
    "Pet Care",
    "Business & Work",
    "Miscellaneous",
    "Other",
]

CATEGORY_GROUPS = {
    "🏠 Housing":        ["Housing — Rent / Mortgage", "Housing — Utilities",
                          "Housing — Internet & Phone", "Housing — Insurance"],
    "🚗 Transport":      ["Transportation — Gas & Fuel", "Transportation — Car Payment",
                          "Transportation — Car Insurance", "Transportation — Transit & Tolls",
                          "Transportation — Rideshare"],
    "🛒 Food":           ["Groceries", "Dining & Takeout", "Coffee & Drinks"],
    "🛍️ Shopping":       ["Shopping — Online", "Shopping — In-store"],
    "📺 Subscriptions":  ["Subscriptions & Streaming"],
    "🎭 Lifestyle":      ["Entertainment & Leisure", "Travel & Vacation",
                          "Fitness & Wellness", "Personal Care"],
    "💊 Health":         ["Health & Medical"],
    "📚 Education":      ["Education"],
    "🐾 Other":          ["Gifts & Charity", "Kids & Family", "Pet Care",
                          "Business & Work", "Miscellaneous", "Other"],
}

KEYWORD_RULES = {
    "Groceries":                   ["costco", "whole foods", "trader joe", "wegman", "kroger",
                                    "safeway", "publix", "aldi", "lidl", "heb", "sprouts",
                                    "market", "grocery", "food lion", "giant", "harris teeter",
                                    "winn dixie", "fresh market", "meijer", "vons", "ralphs",
                                    "stop & shop", "food king", "piggly"],
    "Dining & Takeout":            ["restaurant", "grubhub", "doordash", "uber eats", "ubereats",
                                    "chick-fil", "mcdonald", "chipotle", "panera", "domino",
                                    "pizza", "sushi", "taco", "burger", "subway", "olive garden",
                                    "applebee", "chili's", "ihop", "denny's", "waffle house",
                                    "cracker barrel", "red lobster", "outback", "cheesecake factory",
                                    "first watch", "noodles", "panda express"],
    "Coffee & Drinks":             ["starbucks", "dunkin", "coffee", "espresso", "boba",
                                    "dutch bros", "peet's", "caribou", "biggby", "scooter's"],
    "Transportation — Gas & Fuel": ["chevron", "shell", "bp ", "exxon", "mobil", "sunoco",
                                    "marathon", "speedway", "circle k", "wawa", "casey's",
                                    "fuel", "76 gas", "phillips 66", "racetrac"],
    "Transportation — Rideshare":  ["uber", "lyft"],
    "Transportation — Transit & Tolls": ["mta", "bart", "metro", "transit", "e-zpass",
                                         "sunpass", "peach pass", "quick pass", "toll",
                                         "cta", "septa", "wmata", "trimet"],
    "Shopping — Online":           ["amazon", "ebay", "etsy", "wayfair", "zappos",
                                    "chewy", "wish.com", "shein", "temu", "shopify"],
    "Shopping — In-store":         ["target", "walmart", "best buy", "home depot", "lowe's",
                                    "ikea", "tj maxx", "marshalls", "ross", "old navy",
                                    "gap", "h&m", "zara", "macy's", "nordstrom", "kohl's",
                                    "burlington", "dollar tree", "dollar general", "five below"],
    "Subscriptions & Streaming":   ["netflix", "spotify", "hulu", "disney", "peacock",
                                    "apple.com/bill", "apple services", "youtube premium",
                                    "paramount", "max.com", "prime video", "amazon prime",
                                    "sling", "fubo", "crunchyroll", "adobe", "microsoft 365",
                                    "google one", "dropbox", "icloud", "linkedin premium",
                                    "peloton", "calm", "headspace"],
    "Entertainment & Leisure":     ["amc", "regal", "movie", "theatre", "theater", "concert",
                                    "museum", "ticketmaster", "eventbrite", "bowling",
                                    "dave & buster", "topgolf", "mini golf", "escape room",
                                    "paintball", "trampoline"],
    "Housing — Utilities":         ["electric", "duke energy", "enbridge", "pg&e", "con edison",
                                    "utility", "water bill", "sewer", "energy", "atmos",
                                    "centerpoint", "dominion", "pge", "nstar"],
    "Housing — Internet & Phone":  ["comcast", "xfinity", "spectrum", "at&t", "verizon",
                                    "t-mobile", "tmobile", "gfiber", "google fiber", "cox",
                                    "frontier", "centurylink", "dish", "mint mobile"],
    "Housing — Insurance":         ["renters insurance", "homeowners insurance", "lemonade ins",
                                    "state farm home", "allstate home", "nationwide home"],
    "Housing — Rent / Mortgage":   ["rent payment", "mortgage", "lease payment", "property mgmt",
                                    "landlord", "apt rent", "apts rent"],
    "Transportation — Car Payment":["auto loan", "car payment", "honda financial", "toyota financial",
                                    "ford motor credit", "gm financial", "bmw financial",
                                    "hyundai motor", "nissan motor finance"],
    "Transportation — Car Insurance": ["geico", "progressive auto", "state farm auto",
                                       "allstate auto", "travelers", "usaa auto", "esurance"],
    "Health & Medical":            ["cvs", "walgreens", "rite aid", "pharmacy", "clinic",
                                    "hospital", "doctor", "dental", "vision", "health",
                                    "medical", "urgent care", "lab corp", "quest diagnostics",
                                    "minute clinic", "medstar"],
    "Fitness & Wellness":          ["gym", "planet fitness", "equinox", "ymca", "lifetime",
                                    "anytime fitness", "orangetheory", "crossfit"],
    "Personal Care":               ["salon", "haircut", "nail", "spa", "ulta", "sephora",
                                    "bath & body", "great clips", "fantastic sams"],
    "Travel & Vacation":           ["delta", "united", "american air", "southwest", "jetblue",
                                    "spirit", "frontier", "airbnb", "vrbo", "hotel",
                                    "marriott", "hilton", "hyatt", "expedia", "booking.com",
                                    "hotels.com", "priceline", "kayak"],
    "Education":                   ["tuition", "coursera", "udemy", "skillshare", "masterclass",
                                    "chegg", "pearson", "bookstore", "khan academy"],
    "Gifts & Charity":             ["charity", "donation", "gofundme", "aclu", "nrdc"],
    "Pet Care":                    ["petco", "petsmart", "chewy pet", "banfield", "vet",
                                    "pet supplies", "pet hospital"],
    "Kids & Family":               ["daycare", "babysitter", "school supplies", "children"],
}

BANK_PROFILES = {
    "Chase": {
        "date_col": "Transaction Date", "desc_col": "Description",
        "amount_col": "Amount", "credit_col": None,
        "flip_sign": True, "filter_col": "Type",
        "keep_values": ["Sale"], "exclude_values": [],
        "notes": "Expenses stored as negatives — sign flipped. Filters to 'Sale' type only (excludes payments).",
    },
    "Amex / American Express": {
        "date_col": "Date", "desc_col": "Description",
        "amount_col": "Amount", "credit_col": None,
        "flip_sign": False, "filter_col": None,
        "keep_values": None, "exclude_values": [],
        "notes": "Positive = expense. Negative amounts (credits, payments) excluded automatically.",
    },
    "Bank of America": {
        "date_col": "Posted Date", "desc_col": "Payee",
        "amount_col": "Amount", "credit_col": None,
        "flip_sign": True, "filter_col": None,
        "keep_values": None,
        "exclude_values": ["DIRECT DEP", "PAYROLL", "ONLINE PMT", "CREDIT CARD PMT"],
        "notes": "Expenses stored as negatives — flipped. Payroll deposits and CC payments excluded.",
    },
    "Citi": {
        "date_col": "Date", "desc_col": "Description",
        "amount_col": "Debit", "credit_col": "Credit",
        "flip_sign": False, "filter_col": None,
        "keep_values": None, "exclude_values": [],
        "notes": "Debit column = expenses. Credit column = payments/refunds (excluded).",
    },
    "Capital One": {
        "date_col": "Transaction Date", "desc_col": "Description",
        "amount_col": "Debit", "credit_col": "Credit",
        "flip_sign": False, "filter_col": None,
        "keep_values": None, "exclude_values": [],
        "notes": "Debit = expense, Credit = payment (excluded).",
    },
    "Discover": {
        "date_col": "Trans. Date", "desc_col": "Description",
        "amount_col": "Amount", "credit_col": None,
        "flip_sign": False, "filter_col": None,
        "keep_values": None, "exclude_values": [],
        "notes": "Positive = expense. Negatives (payments/refunds) excluded automatically.",
    },
    "Wells Fargo": {
        "date_col": "Date", "desc_col": "Description",
        "amount_col": "Amount", "credit_col": None,
        "flip_sign": True, "filter_col": None,
        "keep_values": None,
        "exclude_values": ["DIRECT DEP", "PAYROLL", "ONLINE TRANSFER", "PAYMENT"],
        "notes": "Expenses stored as negatives — flipped. Deposits and transfers excluded.",
    },
    "US Bank": {
        "date_col": "Date", "desc_col": "Name",
        "amount_col": "Amount", "credit_col": None,
        "flip_sign": True, "filter_col": None,
        "keep_values": None, "exclude_values": ["DIRECT DEPOSIT", "PAYROLL"],
        "notes": "Expenses stored as negatives — flipped.",
    },
    "TD Bank": {
        "date_col": "Date", "desc_col": "Description",
        "amount_col": "Debit", "credit_col": "Credit",
        "flip_sign": False, "filter_col": None,
        "keep_values": None, "exclude_values": [],
        "notes": "Debit = expense, Credit = deposit/payment (excluded).",
    },
    "Apple Card": {
        "date_col": "Transaction Date", "desc_col": "Merchant",
        "amount_col": "Amount (USD)", "credit_col": None,
        "flip_sign": False, "filter_col": "Type",
        "keep_values": ["Purchase"], "exclude_values": [],
        "notes": "Keeps 'Purchase' rows only — Daily Cash and Payments excluded automatically.",
    },
    "Other / Map manually": {
        "date_col": None, "desc_col": None, "amount_col": None,
        "credit_col": None, "flip_sign": False, "filter_col": None,
        "keep_values": None, "exclude_values": [],
        "notes": "Map each column to the correct field manually below.",
    },
}

# ─────────────────────────────────────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────────────────────────────────────
def _init():
    defaults = {
        # Wizard
        "wizard_step":      0,
        "setup_done":       False,
        # Household
        "household_name":   "",
        "members":          [],          # [{"name": str, "role": "earner|spender|both"}]
        "income_sources":   [],          # [{"member", "label", "amount", "freq"}]
        "fixed_expenses":   [],          # [{"label", "amount", "category", "owner", "in_files": bool}]
        # Prefs
        "filter_payments":  True,
        "filter_deposits":  True,
        "filter_investments": True,
        # Data
        "transactions":     pd.DataFrame(),
        "anthropic_key":    "",
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

_init()

# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def load_file(f):
    if f.name.lower().endswith(".csv"):
        return pd.read_csv(f)
    return pd.read_excel(f)


def rule_categorize(desc: str) -> str:
    d = desc.lower()
    for cat, kws in KEYWORD_RULES.items():
        if any(kw in d for kw in kws):
            return cat
    return "Other"


def ai_categorize(descriptions: list, api_key: str) -> list:
    if not api_key or not descriptions:
        return ["Other"] * len(descriptions)
    try:
        client = Anthropic(api_key=api_key)
        resp = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            messages=[{"role": "user", "content": (
                f"Categorize each transaction into exactly one of:\n"
                f"{json.dumps(EXPENSE_CATEGORIES)}\n\n"
                f"Return ONLY a JSON array of strings, same order. No extra text.\n\n"
                f"Descriptions:\n{json.dumps(descriptions)}"
            )}],
        )
        cats = json.loads(resp.content[0].text.strip())
        return cats if len(cats) == len(descriptions) else ["Other"] * len(descriptions)
    except Exception:
        return ["Other"] * len(descriptions)


def check_missing(profile, cols):
    return [c for c in [profile["date_col"], profile["desc_col"], profile["amount_col"]]
            if c and c not in cols]


def normalize(raw, profile, overrides, bank, card_name, owner):
    """Convert raw bank file → standard schema using numpy masks (no alignment bugs)."""
    p = {**profile, **overrides}
    raw = raw.reset_index(drop=True).copy()
    n   = len(raw)

    dates = pd.to_datetime(raw[p["date_col"]], errors="coerce")
    descs = raw[p["desc_col"]].astype(str).str.strip()

    if p["credit_col"] and p["credit_col"] in raw.columns:
        debit   = pd.to_numeric(raw[p["amount_col"]], errors="coerce").fillna(0).astype(float)
        credit  = pd.to_numeric(raw[p["credit_col"]], errors="coerce").fillna(0).astype(float)
        amounts = debit - credit
    else:
        amt     = pd.to_numeric(raw[p["amount_col"]], errors="coerce").fillna(0).astype(float)
        amounts = -amt if p["flip_sign"] else amt

    # Row filter using numpy boolean arrays
    keep = np.ones(n, dtype=bool)
    if p["filter_col"] and p["filter_col"] in raw.columns:
        type_vals = raw[p["filter_col"]].astype(str).str.strip().values
        if p["keep_values"]:
            keep_set = set(p["keep_values"])
            keep    &= np.array([v in keep_set for v in type_vals], dtype=bool)
        if p["exclude_values"]:
            excl_l   = [ex.lower() for ex in p["exclude_values"]]
            keep    &= np.array([not any(ex in v.lower() for ex in excl_l) for v in type_vals], dtype=bool)

    # Apply user filter prefs
    if st.session_state.filter_payments:
        payment_kws = ["payment - thank you", "autopay payment", "online payment",
                       "credit card pmt", "ach payment", "online pmt"]
        pay_mask = np.array([not any(kw in d.lower() for kw in payment_kws) for d in descs.values], dtype=bool)
        keep    &= pay_mask

    if st.session_state.filter_deposits:
        deposit_kws = ["direct dep", "payroll", "direct deposit", "dd employer"]
        dep_mask = np.array([not any(kw in d.lower() for kw in deposit_kws) for d in descs.values], dtype=bool)
        keep    &= dep_mask

    if st.session_state.filter_investments:
        inv_kws = ["you bought", "dividend", "reinvestment", "you sold", "brokerage", "investment"]
        inv_mask = np.array([not any(kw in d.lower() for kw in inv_kws) for d in descs.values], dtype=bool)
        keep    &= inv_mask

    # Expenses only
    keep &= (amounts.values > 0)

    df = pd.DataFrame({
        "date":        dates.values[keep],
        "description": descs.values[keep],
        "amount":      amounts.values[keep].astype(float),
    })
    df["category"] = df["description"].apply(rule_categorize)
    df["bank"]     = bank
    df["card"]     = card_name
    df["owner"]    = owner
    df["is_fixed"] = False
    df["notes"]    = ""
    return df.dropna(subset=["date"]).reset_index(drop=True)


def apply_fixed_tags(df, fixed_list):
    for item in fixed_list:
        if item.get("in_files", False):
            mask = df["description"].str.contains(item["label"], case=False, na=False)
            df.loc[mask, "category"] = item["category"]
            df.loc[mask, "is_fixed"] = True
    return df


def get_expenses(view):
    df = st.session_state.transactions.copy()
    if df.empty:
        return df
    if view != "Everyone":
        df = df[df["owner"] == view]
    return df[df["amount"] > 0]


def monthly_income(view):
    sources = st.session_state.income_sources
    multiplier = {"monthly": 1, "biweekly": 26/12, "weekly": 52/12, "annual": 1/12}
    total = 0.0
    for s in sources:
        if view == "Everyone" or s["member"] == view:
            total += s["amount"] * multiplier.get(s["freq"], 1)
    return total


def group_of(cat):
    for g, cats in CATEGORY_GROUPS.items():
        if cat in cats:
            return g
    return "🐾 Other"


# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    hname = st.session_state.household_name or "My Household"
    st.markdown(f"## 🏠 {hname}")
    st.caption("Household Budget Tracker")
    st.divider()

    st.markdown("#### 🤖 AI Categorization *(optional)*")
    api_key = st.text_input(
        "Anthropic API Key", type="password",
        value=st.session_state.anthropic_key,
        help="Enables Claude AI to categorize transactions the keyword rules miss. Leave blank to use rules only.",
    )
    st.session_state.anthropic_key = api_key

    st.divider()

    # View selector
    members = [m["name"] for m in st.session_state.members]
    view_options = ["Everyone"] + members
    view_mode = st.radio("👤 View spending for", view_options)

    st.divider()

    # Quick stats
    if not st.session_state.transactions.empty:
        df_all = st.session_state.transactions
        st.caption(f"**{len(df_all):,}** transactions loaded")
        st.caption(f"**{df_all['date'].dt.to_period('M').nunique()}** months covered")
        st.caption(f"**{df_all['card'].nunique()}** accounts")
        if st.button("🗑️ Clear all data", use_container_width=True):
            st.session_state.transactions = pd.DataFrame()
            st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────────────────────────────────────
tab_how, tab_setup, tab_upload, tab_dash, tab_trends, tab_txns = st.tabs([
    "📖 How to Use",
    "👥 Household Setup",
    "📁 Upload & Import",
    "📊 Dashboard",
    "📈 Trends",
    "🧾 Transactions",
])


# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — HOW TO USE
# ══════════════════════════════════════════════════════════════════════════════
with tab_how:
    st.markdown("# 🏠 Household Budget Tracker")
    st.markdown("*Track where your money goes — across all your cards, accounts, and family members.*")
    st.divider()

    col1, col2, col3 = st.columns(3)
    col1.metric("⏱️ Setup time", "5 min")
    col2.metric("💳 Accounts supported", "Chase, Amex, BofA, Citi + more")
    col3.metric("👥 Household size", "1 to unlimited")

    st.divider()

    st.markdown("## 🚀 Getting Started")

    with st.expander("**Step 1 — Set up your household** (👥 Household Setup tab)", expanded=True):
        st.markdown("""
Walk through a quick 5-step wizard to tell the app about your household:
- 👋 **Welcome** — Give your household a name
- 👥 **Members** — Add everyone who earns or spends (just you is fine too)
- 💵 **Income** — Enter each person's take-home pay and frequency
- 📌 **Fixed expenses** — Add rent, utilities, subscriptions — things that repeat every month
- ⚙️ **Preferences** — Choose what to automatically filter out (payments, deposits, etc.)

**Tip:** You can skip setup and jump straight to Upload if you just want to explore.
""")

    with st.expander("**Step 2 — Download your statements**"):
        st.markdown("""
Download CSV or Excel transaction exports from your bank's website:

| Bank | Where to find it |
|------|-----------------|
| **Chase** | Account → Download Activity → CSV |
| **Amex** | Statements → Download → Excel |
| **Bank of America** | Activity → Export → CSV |
| **Citi** | Account Activity → Download → CSV |
| **Capital One** | Transactions → Download |
| **Discover** | Activity → Download |
| **Apple Card** | Card → Transactions → Export |
| **Other** | Use "Map manually" option in the app |

Download **one file per account** per month (or across multiple months — up to you).
""")

    with st.expander("**Step 3 — Upload in the Upload & Import tab**"):
        st.markdown("""
1. Drop your files into the uploader (multiple at once is fine)
2. Select the bank for each file — the app auto-detects column layouts
3. Pick the card nickname and who it belongs to
4. Hit **Import** — transactions are categorized automatically

**How categorization works:**
- 🔑 **Keyword rules** match common merchants (Spotify → Subscriptions, Shell → Gas, etc.)
- 🤖 **AI fallback** — if you add an Anthropic API key, Claude categorizes anything the rules miss
- ✏️ **Manual edit** — fix any mis-tags in the Categories tab
""")

    with st.expander("**Step 4 — Explore your spending**"):
        st.markdown("""
- **📊 Dashboard** — Monthly summary: income vs expenses, net savings, category breakdown
- **📈 Trends** — Month-over-month changes, which categories are growing
- **🧾 Transactions** — Browse and filter all transactions, export to CSV
- **🏷️ Categories** — Inline editing to fix categories or add notes
""")

    st.divider()
    st.markdown("## 🧪 Try it with Demo Data")
    st.markdown("""
Download these 3 sample files to explore the app with realistic dummy data.
They represent a 2-person household (Alex & Jordan) over Jan–Mar 2025.

| File | Type | Owner |
|------|------|-------|
| `Chase_Alex_Jan_Mar_2025.csv` | Chase credit card | Alex |
| `Amex_Jordan_Jan_Mar_2025.xlsx` | Amex credit card | Jordan |
| `BofA_Joint_Jan_Mar_2025.csv` | Joint checking account | Joint |

**How to use them:**
1. Download all 3 files
2. Go to **👥 Household Setup** → add Alex and Jordan as members
3. Go to **📁 Upload & Import** → upload each file, select the matching bank, assign the owner
4. Explore the Dashboard and Trends tabs
""")

    st.info("💡 **Privacy note:** This app runs entirely in your browser session. "
            "No data is stored on any server. Refreshing the page clears everything.")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — HOUSEHOLD SETUP WIZARD
# ══════════════════════════════════════════════════════════════════════════════
with tab_setup:
    step = st.session_state.wizard_step

    # Progress bar
    steps_total = 5
    progress_labels = ["Welcome", "Members", "Income", "Fixed Expenses", "Preferences"]
    st.progress((step) / steps_total,
                text=f"Step {step + 1} of {steps_total} — **{progress_labels[min(step, steps_total-1)]}**")
    st.markdown("")

    # ── STEP 0: Welcome ───────────────────────────────────────────────────────
    if step == 0:
        st.markdown("## 👋 Welcome! Let's set up your budget.")
        st.markdown("This takes about 5 minutes. You can always come back and edit later.")
        st.markdown("")

        hname = st.text_input(
            "What should we call your household?",
            value=st.session_state.household_name,
            placeholder="e.g. The Smith Household, Our Apartment, Casa Rodriguez…",
        )
        st.caption("This is just a label — it appears in the sidebar.")

        col1, col2 = st.columns([1, 4])
        if col1.button("Next →", type="primary", use_container_width=True):
            if hname.strip():
                st.session_state.household_name = hname.strip()
                st.session_state.wizard_step = 1
                st.rerun()
            else:
                st.warning("Please enter a name for your household.")

    # ── STEP 1: Members ───────────────────────────────────────────────────────
    elif step == 1:
        st.markdown("## 👥 Who's in your household?")
        st.markdown("Add everyone who earns or spends money. You can always add just yourself.")

        # Add member form
        with st.form("add_member_form", clear_on_submit=True):
            c1, c2, c3 = st.columns([3, 2, 1])
            m_name = c1.text_input("Name", placeholder="e.g. Alex, Sam, Jordan…")
            m_role = c2.selectbox("Role", ["Earner & Spender", "Earner only", "Spender only"])
            submitted = c3.form_submit_button("Add", use_container_width=True)
            if submitted and m_name.strip():
                role_map = {"Earner & Spender": "both", "Earner only": "earner", "Spender only": "spender"}
                st.session_state.members.append({"name": m_name.strip(), "role": role_map[m_role]})
                st.rerun()

        if st.session_state.members:
            st.markdown("**Members added:**")
            for i, m in enumerate(st.session_state.members):
                c1, c2 = st.columns([5, 1])
                role_display = {"both": "👤 Earner & Spender", "earner": "💵 Earner only", "spender": "🛒 Spender only"}
                c1.markdown(f"**{m['name']}** — {role_display[m['role']]}")
                if c2.button("Remove", key=f"rm_m_{i}"):
                    st.session_state.members.pop(i)
                    st.rerun()
        else:
            st.info("No members added yet — add at least one person above, or click Next to track as a single household.")

        c1, c2 = st.columns([1, 1])
        if c1.button("← Back", use_container_width=True):
            st.session_state.wizard_step = 0
            st.rerun()
        if c2.button("Next →", type="primary", use_container_width=True):
            st.session_state.wizard_step = 2
            st.rerun()

    # ── STEP 2: Income ────────────────────────────────────────────────────────
    elif step == 2:
        st.markdown("## 💵 Income Sources")
        st.markdown("Add take-home (after tax) income for each earner. Used to calculate your monthly net savings.")

        earners = [m["name"] for m in st.session_state.members if m["role"] in ("both", "earner")]
        if not earners:
            earners = ["Household"]  # fallback if no members set up

        with st.form("add_income_form", clear_on_submit=True):
            c1, c2, c3, c4 = st.columns([2, 2, 1.5, 1])
            i_member = c1.selectbox("Person", earners)
            i_label  = c2.text_input("Source", placeholder="e.g. Salary, Freelance, Part-time")
            i_amount = c3.number_input("Amount ($)", min_value=0.0, step=100.0)
            i_freq   = c4.selectbox("Frequency", ["monthly", "biweekly", "weekly", "annual"])
            if st.form_submit_button("Add Income", use_container_width=True):
                if i_label.strip() and i_amount > 0:
                    st.session_state.income_sources.append({
                        "member": i_member, "label": i_label.strip(),
                        "amount": i_amount, "freq": i_freq,
                    })
                    st.rerun()

        if st.session_state.income_sources:
            st.markdown("**Income sources added:**")
            freq_display = {"monthly": "/mo", "biweekly": "/2wk", "weekly": "/wk", "annual": "/yr"}
            for i, s in enumerate(st.session_state.income_sources):
                c1, c2 = st.columns([5, 1])
                c1.markdown(f"**{s['member']}** — {s['label']}: **${s['amount']:,.0f}** {freq_display[s['freq']]}")
                if c2.button("✕", key=f"rm_inc_{i}"):
                    st.session_state.income_sources.pop(i)
                    st.rerun()
        else:
            st.caption("_No income added — you can skip this and enter it later._")

        c1, c2 = st.columns([1, 1])
        if c1.button("← Back", use_container_width=True):
            st.session_state.wizard_step = 1
            st.rerun()
        if c2.button("Next →", type="primary", use_container_width=True):
            st.session_state.wizard_step = 3
            st.rerun()

    # ── STEP 3: Fixed Expenses ────────────────────────────────────────────────
    elif step == 3:
        st.markdown("## 📌 Fixed Recurring Expenses")
        st.markdown("Add expenses that repeat every month — rent, utilities, subscriptions, car loans, etc.")

        member_names = [m["name"] for m in st.session_state.members] + (["Joint"] if len(st.session_state.members) > 1 else [])
        if not member_names:
            member_names = ["Household"]

        with st.form("add_fixed_form", clear_on_submit=True):
            c1, c2, c3, c4 = st.columns([2, 1.2, 1.8, 1])
            f_label    = c1.text_input("Name", placeholder="e.g. Rent, Netflix, Car Loan")
            f_amount   = c2.number_input("Amount ($)/mo", min_value=0.0, step=10.0)
            f_category = c3.selectbox("Category", EXPENSE_CATEGORIES)
            f_owner    = c4.selectbox("Who pays?", member_names)
            f_in_files = st.radio(
                "Will this show up in your uploaded bank statements?",
                ["Yes — auto-tag it when found in my files",
                 "No — I'll enter it manually (it pays from cash/not tracked)"],
                horizontal=True,
            )
            if st.form_submit_button("Add Fixed Expense", use_container_width=True):
                if f_label.strip():
                    st.session_state.fixed_expenses.append({
                        "label":    f_label.strip(),
                        "amount":   f_amount,
                        "category": f_category,
                        "owner":    f_owner,
                        "in_files": "Yes" in f_in_files,
                    })
                    st.rerun()

        if st.session_state.fixed_expenses:
            st.markdown("**Fixed expenses added:**")
            for i, fe in enumerate(st.session_state.fixed_expenses):
                tag = "📁 auto-tags" if fe["in_files"] else "✍️ manual"
                c1, c2 = st.columns([5, 1])
                c1.markdown(f"📌 **{fe['label']}** — ${fe['amount']:,.0f}/mo · {fe['owner']} · {tag}")
                if c2.button("✕", key=f"rm_fe_{i}"):
                    st.session_state.fixed_expenses.pop(i)
                    st.rerun()
        else:
            st.caption("_No fixed expenses added — you can skip this._")

        c1, c2 = st.columns([1, 1])
        if c1.button("← Back", use_container_width=True):
            st.session_state.wizard_step = 2
            st.rerun()
        if c2.button("Next →", type="primary", use_container_width=True):
            st.session_state.wizard_step = 4
            st.rerun()

    # ── STEP 4: Preferences ───────────────────────────────────────────────────
    elif step == 4:
        st.markdown("## ⚙️ Filter Preferences")
        st.markdown("Choose what to automatically remove from your imported transactions.")
        st.markdown("")

        st.session_state.filter_payments = st.checkbox(
            "🚫 Filter out credit card payments",
            value=st.session_state.filter_payments,
            help="Removes rows like 'PAYMENT - THANK YOU' or 'ACH PAYMENT'. Recommended — these aren't expenses.",
        )
        st.session_state.filter_deposits = st.checkbox(
            "🚫 Filter out payroll / direct deposits",
            value=st.session_state.filter_deposits,
            help="Removes salary deposits from checking accounts. Recommended — you're tracking spending, not income.",
        )
        st.session_state.filter_investments = st.checkbox(
            "🚫 Filter out investment transactions",
            value=st.session_state.filter_investments,
            help="Removes stock purchases, dividends, brokerage transfers. Recommended for pure spending tracking.",
        )
        st.markdown("")
        st.info("💡 You can always change these later via the Upload tab, and manually restore any filtered transactions in the Transactions tab.")

        c1, c2 = st.columns([1, 1])
        if c1.button("← Back", use_container_width=True):
            st.session_state.wizard_step = 3
            st.rerun()
        if c2.button("✅ Finish Setup", type="primary", use_container_width=True):
            st.session_state.setup_done = True
            st.session_state.wizard_step = 5
            st.rerun()

    # ── COMPLETE ──────────────────────────────────────────────────────────────
    elif step >= 5:
        st.markdown(f"## ✅ {st.session_state.household_name} is all set!")
        st.success("Setup complete! Head to **📁 Upload & Import** to add your bank statements.")

        if st.session_state.members:
            st.markdown("**Members:**")
            for m in st.session_state.members:
                st.markdown(f"- {m['name']}")

        total_monthly = monthly_income("Everyone")
        if total_monthly > 0:
            st.markdown(f"**Monthly income:** ${total_monthly:,.0f}")

        fixed_total = sum(fe["amount"] for fe in st.session_state.fixed_expenses)
        if fixed_total > 0:
            st.markdown(f"**Fixed monthly expenses:** ${fixed_total:,.0f}")

        st.markdown("")
        if st.button("✏️ Edit setup", use_container_width=False):
            st.session_state.wizard_step = 0
            st.session_state.setup_done = False
            st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — UPLOAD & IMPORT
# ══════════════════════════════════════════════════════════════════════════════
with tab_upload:
    st.subheader("Upload Bank Statements")
    st.caption(
        "Supports CSV and Excel. Pre-configured for Chase, Amex, BofA, Citi, Capital One, "
        "Discover, Wells Fargo, US Bank, TD Bank, Apple Card. Use 'Map manually' for any other bank."
    )

    # Filter prefs quick-toggle
    with st.expander("⚙️ Filter preferences"):
        st.session_state.filter_payments    = st.checkbox("Filter CC payments",    value=st.session_state.filter_payments,    key="fp_upload")
        st.session_state.filter_deposits    = st.checkbox("Filter direct deposits", value=st.session_state.filter_deposits,    key="fd_upload")
        st.session_state.filter_investments = st.checkbox("Filter investments",     value=st.session_state.filter_investments, key="fi_upload")

    uploaded = st.file_uploader(
        "Drop files here", type=["csv", "xlsx", "xls"],
        accept_multiple_files=True, label_visibility="collapsed",
    )

    member_options = ([m["name"] for m in st.session_state.members]
                      + (["Joint"] if len(st.session_state.members) > 1 else []))
    if not member_options:
        member_options = ["Me"]

    if uploaded:
        for uf in uploaded:
            with st.expander(f"📄  {uf.name}", expanded=True):
                try:
                    raw = load_file(uf)
                except Exception as e:
                    st.error(f"Could not read file: {e}")
                    continue

                raw_cols = list(raw.columns)
                c1, c2, c3 = st.columns(3)
                bank      = c1.selectbox("Bank / Issuer", list(BANK_PROFILES.keys()), key=f"bank_{uf.name}")
                card_name = c2.text_input("Card / account nickname", value=bank, key=f"card_{uf.name}")
                owner     = c3.selectbox("Belongs to", member_options, key=f"own_{uf.name}")

                profile = BANK_PROFILES[bank]
                if profile["notes"]:
                    st.info(f"ℹ️ {profile['notes']}")

                missing      = check_missing(profile, raw_cols)
                needs_manual = (bank == "Other / Map manually") or bool(missing)

                if missing and bank != "Other / Map manually":
                    st.warning(f"Expected columns not found: **{missing}**. File has: `{raw_cols}`. Map manually below.")

                overrides = {}
                if needs_manual:
                    m1, m2, m3, m4 = st.columns(4)
                    overrides["date_col"]   = m1.selectbox("Date col",        raw_cols, key=f"dc_{uf.name}")
                    overrides["desc_col"]   = m2.selectbox("Description col", raw_cols, key=f"dsc_{uf.name}")
                    overrides["amount_col"] = m3.selectbox("Amount col",      raw_cols, key=f"ac_{uf.name}")
                    cr = m4.selectbox("Credit col (opt)", ["None"] + raw_cols, key=f"cc_{uf.name}")
                    overrides["credit_col"] = None if cr == "None" else cr
                    overrides["flip_sign"]  = st.checkbox("Flip sign? (expenses are negative in this file)", key=f"flip_{uf.name}")

                fc = profile.get("filter_col")
                if fc and fc in raw_cols:
                    unique_types = sorted(raw[fc].dropna().unique().tolist())
                    with st.expander(f"⚙️ Type filter  (`{fc}` column)"):
                        if profile.get("keep_values"):
                            st.caption(f"✅ Keeping: `{profile['keep_values']}`")
                        custom_keep = st.multiselect("Override — keep only these", unique_types, key=f"ck_{uf.name}")
                        if custom_keep:
                            overrides["keep_values"]    = custom_keep
                            overrides["exclude_values"] = []

                st.dataframe(raw.head(5), use_container_width=True, hide_index=True)

                if st.button(f"✅ Import  {uf.name}", key=f"imp_{uf.name}", type="primary"):
                    with st.spinner("Processing…"):
                        try:
                            df_norm = normalize(raw, profile, overrides, bank, card_name, owner)
                            df_norm = apply_fixed_tags(df_norm, st.session_state.fixed_expenses)

                            needs_ai = df_norm["category"] == "Other"
                            if needs_ai.any() and st.session_state.anthropic_key:
                                with st.spinner(f"🤖 AI categorizing {needs_ai.sum()} transactions…"):
                                    descs = df_norm.loc[needs_ai, "description"].tolist()
                                    df_norm.loc[needs_ai, "category"] = ai_categorize(descs, st.session_state.anthropic_key)

                            master   = st.session_state.transactions
                            combined = pd.concat([master, df_norm], ignore_index=True) if not master.empty else df_norm
                            combined = combined.drop_duplicates(subset=["date", "description", "amount", "card"])
                            st.session_state.transactions = combined

                            if df_norm.empty:
                                st.warning(f"⚠️ No expense transactions found in {uf.name} after filtering. Check filter preferences above.")
                            else:
                                rule_pct = int(100 * (1 - needs_ai.mean())) if len(needs_ai) > 0 else 100
                                ai_note  = f", remainder by AI." if st.session_state.anthropic_key else "; add an API key to auto-categorize the rest."
                                st.success(f"✅ **{len(df_norm):,} transactions** from {uf.name} · 🏷️ {rule_pct}% auto-categorized{ai_note}")
                        except Exception as e:
                            st.error(f"Import failed: {e}")
                            st.exception(e)

    if not st.session_state.transactions.empty:
        st.divider()
        st.success(f"**{len(st.session_state.transactions):,} total transactions** loaded.")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
with tab_dash:
    df = get_expenses(view_mode)

    if df.empty:
        st.info("⬆️ Upload statements in **Upload & Import** first.")
    else:
        df["month"] = df["date"].dt.to_period("M")
        months = sorted(df["month"].unique(), reverse=True)
        sel_m  = st.selectbox("Select month", [str(m) for m in months], key="dash_month")
        mdf    = df[df["month"] == pd.Period(sel_m, "M")]

        income    = monthly_income(view_mode)
        total_exp = mdf["amount"].sum()
        fixed_exp = mdf[mdf["is_fixed"]]["amount"].sum()
        net       = income - total_exp if income > 0 else None

        st.markdown(f"### {sel_m}  ·  *{view_mode}*")
        cols = st.columns(5 if income > 0 else 4)
        if income > 0:
            cols[0].metric("💵 Income",        f"${income:,.0f}")
        cols[-4].metric("💳 Total Expenses", f"${total_exp:,.0f}")
        cols[-3].metric("📌 Fixed",           f"${fixed_exp:,.0f}")
        cols[-2].metric("🔄 Variable",        f"${total_exp - fixed_exp:,.0f}")
        if net is not None:
            cols[-1].metric("💰 Net Savings",  f"${net:,.0f}", delta=f"${net:,.0f}")

        st.divider()

        # Group roll-up
        st.markdown("**Spending by Group**")
        mdf2 = mdf.copy()
        mdf2["group"] = mdf2["category"].apply(group_of)
        grp_df = mdf2.groupby("group")["amount"].sum().reset_index().sort_values("amount", ascending=False)
        fig_g = px.bar(grp_df, x="group", y="amount", color="group",
                       labels={"amount": "$", "group": ""},
                       color_discrete_sequence=px.colors.qualitative.Pastel)
        fig_g.update_layout(showlegend=False, xaxis_tickangle=-20,
                            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_g, use_container_width=True)

        cl, cr = st.columns(2)
        with cl:
            st.markdown("**By Category**")
            cat_df = mdf.groupby("category")["amount"].sum().reset_index().sort_values("amount", ascending=True)
            fig = px.bar(cat_df, x="amount", y="category", orientation="h",
                         color="amount", color_continuous_scale="Blues",
                         labels={"amount": "$", "category": ""})
            fig.update_layout(coloraxis_showscale=False, height=480,
                              plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig, use_container_width=True)
        with cr:
            st.markdown("**By Account**")
            card_df = mdf.groupby("card")["amount"].sum().reset_index()
            fig2 = px.pie(card_df, values="amount", names="card", hole=0.45)
            fig2.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig2, use_container_width=True)

            # Per-member split
            if view_mode == "Everyone" and len(st.session_state.members) > 1:
                st.markdown("**By Member**")
                mem_df = mdf.groupby("owner")["amount"].sum().reset_index()
                fig3 = px.bar(mem_df, x="owner", y="amount", color="owner",
                              labels={"amount": "$", "owner": ""})
                fig3.update_layout(showlegend=False,
                                   plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(fig3, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 5 — TRENDS
# ══════════════════════════════════════════════════════════════════════════════
with tab_trends:
    df = get_expenses(view_mode)

    if df.empty:
        st.info("⬆️ Upload statements to see trends.")
    else:
        df["month"]     = df["date"].dt.to_period("M")
        df["month_str"] = df["date"].dt.strftime("%b %Y")

        monthly = df.groupby(["month","month_str"])["amount"].sum().reset_index().sort_values("month")
        monthly["pct_change"] = monthly["amount"].pct_change() * 100

        st.markdown("### Total Monthly Spending")
        fig = go.Figure()
        fig.add_trace(go.Bar(x=monthly["month_str"], y=monthly["amount"],
                             name="Spend", marker_color="#38bdf8", opacity=0.85))
        fig.add_trace(go.Scatter(x=monthly["month_str"], y=monthly["amount"],
                                 mode="lines+markers", name="Trend",
                                 line=dict(color="#f59e0b", width=2.5), marker=dict(size=7)))
        fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                          yaxis_title="$", hovermode="x unified",
                          legend=dict(orientation="h", y=1.08))
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("### Month-over-Month % Change")
        colors = ["#4ade80" if (pd.isna(v) or v <= 0) else "#f87171" for v in monthly["pct_change"]]
        fig2 = go.Figure(go.Bar(
            x=monthly["month_str"], y=monthly["pct_change"].fillna(0),
            marker_color=colors,
            text=[f"{v:.1f}%" if not pd.isna(v) else "—" for v in monthly["pct_change"]],
            textposition="outside",
        ))
        fig2.add_hline(y=0, line_dash="dash", line_color="#94a3b8")
        fig2.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                           yaxis_title="% vs prior month")
        st.plotly_chart(fig2, use_container_width=True)

        st.markdown("### Spending by Group Over Time")
        df["group"] = df["category"].apply(group_of)
        gm = df.groupby(["month_str","month","group"])["amount"].sum().reset_index()
        mo = gm.drop_duplicates("month").sort_values("month")["month_str"].tolist()
        gpiv = (gm.pivot_table(index="month_str", columns="group", values="amount", aggfunc="sum")
                .fillna(0)
                .reindex([m for m in mo if m in gm["month_str"].values]))
        all_groups = list(gpiv.columns)
        sel_g = st.multiselect("Groups", all_groups, default=all_groups)
        if sel_g:
            fig3 = px.line(gpiv[[g for g in sel_g if g in gpiv.columns]].reset_index(),
                           x="month_str", y=sel_g, markers=True,
                           labels={"month_str":"Month","value":"$","variable":"Group"})
            fig3.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                               hovermode="x unified", legend=dict(orientation="h", y=-0.25))
            st.plotly_chart(fig3, use_container_width=True)

        st.markdown("### Fixed vs Variable")
        fv = df.groupby(["month_str","month","is_fixed"])["amount"].sum().reset_index()
        fv["type"] = fv["is_fixed"].map({True:"Fixed", False:"Variable"})
        fig4 = px.bar(fv.sort_values("month"), x="month_str", y="amount", color="type",
                      color_discrete_map={"Fixed":"#94a3b8","Variable":"#38bdf8"},
                      barmode="stack", labels={"amount":"$","month_str":"Month","type":""})
        fig4.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                           legend=dict(orientation="h", y=1.08))
        st.plotly_chart(fig4, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 6 — TRANSACTIONS
# ══════════════════════════════════════════════════════════════════════════════
with tab_txns:
    df_all = st.session_state.transactions

    if df_all.empty:
        st.info("⬆️ Upload statements first.")
    else:
        st.subheader("Transactions")
        st.caption("Browse, filter, edit categories, and export.")

        df_all["month"] = df_all["date"].dt.to_period("M")
        expenses = df_all[df_all["amount"] > 0].copy()

        fc1, fc2, fc3, fc4 = st.columns(4)
        months_all = ["All"] + [str(m) for m in sorted(expenses["month"].unique(), reverse=True)]
        sel_month  = fc1.selectbox("Month", months_all, key="txn_month")
        sel_cat    = fc2.multiselect("Category", EXPENSE_CATEGORIES, placeholder="All categories")
        sel_card   = fc3.multiselect("Account", expenses["card"].unique().tolist(), placeholder="All accounts")
        min_a = float(expenses["amount"].min()); max_a = float(expenses["amount"].max())
        amt_r = fc4.slider("Amount ($)", min_a, max_a, (min_a, max_a))

        filt = expenses.copy()
        if sel_month != "All":
            filt = filt[filt["month"] == pd.Period(sel_month, "M")]
        if sel_cat:
            filt = filt[filt["category"].isin(sel_cat)]
        if sel_card:
            filt = filt[filt["card"].isin(sel_card)]
        filt = filt[(filt["amount"] >= amt_r[0]) & (filt["amount"] <= amt_r[1])]

        st.caption(f"**{len(filt):,} transactions** · Total: **${filt['amount'].sum():,.2f}**")

        display_cols = ["date","description","amount","card","owner","category","is_fixed","notes"]
        display_cols = [c for c in display_cols if c in filt.columns]

        edited = st.data_editor(
            filt[display_cols].sort_values("date", ascending=False),
            column_config={
                "date":        st.column_config.DateColumn("Date", disabled=True),
                "description": st.column_config.TextColumn("Description", disabled=True),
                "amount":      st.column_config.NumberColumn("Amount ($)", format="$%.2f", disabled=True),
                "card":        st.column_config.TextColumn("Account", disabled=True),
                "owner":       st.column_config.SelectboxColumn("Owner", options=member_options),
                "category":    st.column_config.SelectboxColumn("Category", options=EXPENSE_CATEGORIES),
                "is_fixed":    st.column_config.CheckboxColumn("Fixed?"),
                "notes":       st.column_config.TextColumn("Notes"),
            },
            use_container_width=True, hide_index=True, num_rows="fixed",
        )

        c1, c2 = st.columns([1, 4])
        if c1.button("💾 Save edits", type="primary"):
            for col in ["category","is_fixed","owner","notes"]:
                if col in edited.columns:
                    df_all.loc[filt.index, col] = edited[col].values
            st.session_state.transactions = df_all
            st.success("Saved!")

        csv_out = filt.to_csv(index=False).encode("utf-8")
        c2.download_button("⬇️ Export CSV", data=csv_out,
                           file_name=f"budget_{sel_month}.csv", mime="text/csv")
