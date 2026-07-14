# 📈 Student FinTech Dashboard & Analytics

An enterprise-grade, full-stack personal finance web application specifically engineered for students to log expenses, set milestone savings goals, securely manage stock portfolios with real-time API integrations, and algorithmically split bills with roommates.

## 🔗 Live Project Links
* **Live Web Application:** [https://fintech-student-tracker-gzoh4n24ejyiułeklrzzhq.streamlit.app](https://fintech-student-tracker-gzoh4n24ejyiułeklrzzhq.streamlit.app)
* **Source Code Repository:** [https://github.com/ankeetjena2020-lgtm/fintech-student-tracker](https://github.com/ankeetjena2020-lgtm/fintech-student-tracker)

---

## 🚀 Key Features

### 1. 🔒 Multi-User Secure Access Gates
* Hashed credential authentication engine built using SHA-256 (`hashlib`).
* Strong database isolation ensuring absolute data confidentiality—users can only view, edit, or manipulate their own ledger metrics.

### 2. 📊 Interactive Financial Insights & Visualizations
* Real-time expense breakdown using beautiful donut/pie charts built on Plotly Express.
* Grouped bar charts contrasting user targets vs actual achieved savings dynamically tracking financial progression.

### 3. 📈 Real-Time Mock Stock Portfolio Engine
* Live tracking of Indian (`.NS`) and global tickers consuming current market variables via the Yahoo Finance API (`yfinance`).
* Automated algorithmic engine rendering Total Invested Capital, Current Portfolio Value, Net Returns (P&L), and percentage shifts dynamically.

### 4. 👥 Peer-to-Peer (P2P) Bill Splitter Utility
* Custom mathematical matrices executing expense sharing logistics between roommates.
* Dynamic ledger system instantly mapping "Who Owes Whom" net balances across split groups.

---

## 🛠️ Tech Stack & Architecture

* **Frontend UI:** Streamlit Framework
* **Data Visualizations:** Plotly Express & Pandas DataFrames
* **Backend Database:** Relational SQLite Database (with transactional state handling)
* **Real-time API Engine:** Yahoo Finance (`yfinance`)
* **Security & Encryption:** SHA-256 Hashing Encryption

---

## ⚙️ How to Run Locally

1. Clone this repository:
   ```bash
   git clone [https://github.com/ankeetjena2020-lgtm/fintech-student-tracker.git](https://github.com/ankeetjena2020-lgtm/fintech-student-tracker.git)
   
