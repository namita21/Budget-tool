# 🏠 Household Budget Tracker

A Streamlit app that turns bank statement exports into household budget insights. Upload CSVs or Excel files from Chase, Amex, BofA, Citi, Apple Card, and more — transactions are auto-categorized by merchant rules and optionally by Claude AI. Supports multi-member households, fixed expense tracking, month-over-month trend analysis, and per-person spending splits.

---

## ✨ Features

- **Multi-member household support** — add everyone who earns or spends, assign transactions by person, and toggle between individual and combined views
- **Guided setup wizard** — 5-step onboarding to configure your household, income sources, fixed expenses, and filter preferences
- **Smart auto-categorization** — keyword rules cover 200+ common merchants out of the box; Claude AI handles the rest (optional)
- **10 banks supported** — Chase, Amex, Bank of America, Citi, Capital One, Discover, Wells Fargo, US Bank, TD Bank, Apple Card, plus manual column mapping for any other bank
- **Month-over-month trends** — visualize total spending trends, % change, and category breakdowns over time
- **Fixed vs. variable split** — mark recurring expenses (rent, utilities, subscriptions) and see how much of your budget is discretionary
- **Inline editing** — fix categories, reassign owners, and add notes directly in the app
- **CSV export** — download any filtered view of your transactions

---

## 🚀 Getting Started

### 1. Install dependencies

```bash
pip install streamlit pandas plotly openpyxl anthropic
```

### 2. Run the app

```bash
streamlit run budget_app_sl.py
```

### 3. Try it with demo data

The `/demo_data` folder includes 3 months of realistic dummy transactions for a 2-person household (Alex & Jordan):

| File | Bank | Owner |
|------|------|-------|
| `Chase_Alex_Jan_Mar_2025.csv` | Chase | Alex |
| `Amex_Jordan_Jan_Mar_2025.xlsx` | Amex | Jordan |
| `BofA_Joint_Jan_Mar_2025.csv` | Bank of America | Joint |

**To use:**
1. Go to **👥 Household Setup** → add Alex and Jordan as members
2. Go to **📁 Upload & Import** → upload each file, select the matching bank, assign the owner
3. Explore the Dashboard and Trends tabs

---

## 💳 How to Download Your Bank Statements

| Bank | Where to find the export |
|------|--------------------------|
| **Chase** | Account → Download Activity → CSV |
| **Amex** | Statements & Activity → Download → Excel |
| **Bank of America** | Account Activity → Download → CSV |
| **Citi** | Account Activity → Download → CSV |
| **Capital One** | Transactions → Download |
| **Discover** | Activity → Download Statements |
| **Wells Fargo** | Account Activity → Download |
| **Apple Card** | Card → Transactions → Export |
| **Other** | Use the "Other / Map manually" option in the app |

Download one file per account. The app handles multiple months in a single file.

---

## 🤖 Optional: AI Categorization

The app uses keyword rules to auto-categorize 200+ common merchants (Costco → Groceries, Spotify → Subscriptions, Shell → Gas, etc.) with no API key required.

For anything the rules can't match, you can optionally add an [Anthropic API key](https://console.anthropic.com) to enable Claude AI categorization. The import summary tells you what percentage was handled by rules vs. AI.

To use:
1. Get a free API key at [console.anthropic.com](https://console.anthropic.com)
2. Paste it into the **🤖 AI Categorization** field in the sidebar

---

## 📁 Project Structure

```
/
├── budget_app_sl.py          # Main app (public version)
├── requirements.txt
├── README.md
└── demo_data/
    ├── Chase_Alex_Jan_Mar_2025.csv
    ├── Amex_Jordan_Jan_Mar_2025.xlsx
    └── BofA_Joint_Jan_Mar_2025.csv
```

---

## 🔒 Privacy

This app runs entirely in your browser session via Streamlit. **No transaction data is stored on any server.** Refreshing the page clears everything. If you're using the AI categorization feature, only merchant/description names (not amounts or dates) are sent to the Anthropic API.

---

## 🛠️ Built With

- [Streamlit](https://streamlit.io) — app framework
- [Pandas](https://pandas.pydata.org) — data processing
- [Plotly](https://plotly.com) — charts and visualizations
- [Anthropic Claude API](https://www.anthropic.com) — AI categorization (optional)

---

## 💡 About

Monthly budgeting across 6–7 credit cards and a joint account used to take over 2 hours of manual spreadsheet work. This app cuts that down to under 10 minutes — upload your statements, review the auto-tagged categories, and get on with your life.

Built with Python and Claude Code.
