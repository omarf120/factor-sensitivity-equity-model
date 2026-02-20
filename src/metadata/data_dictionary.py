DATA_DICTIONARY = {
    # -----------------------------
    # CRSP identifiers
    # -----------------------------
    "PERMNO": "Permanent security identifier from CRSP",
    "date": "Week-ending date (Wednesday frequency)",
    "gvkey": "Compustat firm identifier",
    "GVKEY": "Compustat link table GVKEY",
    "tic": "Ticker symbol",
    "cusip": "CUSIP security identifier",

    # -----------------------------
    # CRSP price & trading data
    # -----------------------------
    "PRC": "Raw CRSP closing price (signed; use abs value)",
    "CFACPR": "CRSP price adjustment factor (splits/dividends)",
    "SHROUT": "Shares outstanding (thousands, CRSP daily)",
    "CFACSHR": "CRSP share adjustment factor",
    "VOL": "Trading volume",

    "adj_prc": "Split-adjusted price",
    "adj_prc_lag": "Lagged adjusted price",
    "shares": "Shares outstanding in actual units (after scaling)",
    "mktcap": "Market capitalization in USD",
    "mktcap_m": "Market capitalization in millions USD",

    # -----------------------------
    # Returns
    # -----------------------------
    "weekly_ret_price_only": "Weekly simple return (price only)",
    "weekly_log_ret_total": "Weekly log return including dividends",
    "weekly_log_ret_price_only": "Weekly log return (price only)",

    # -----------------------------
    # Dividends
    # -----------------------------
    "D_t_adj": "Adjusted dividend per share in week",
    "div_trailing": "Trailing 53-week dividend sum per share",
    "div_yield": "Trailing dividend yield (div_trailing / price)",

    # -----------------------------
    # Compustat fundamentals
    # -----------------------------
    "datadate": "Quarter-end reporting date",
    "rdq": "Earnings report announcement date",
    "info_date": "Information date used for merge (rdq if available)",

    "atq": "Total assets (quarterly, millions USD)",
    "ltq": "Total liabilities (quarterly, millions USD)",
    "ceqq": "Common equity (quarterly, millions USD)",
    "seqq": "Shareholders' equity (quarterly, millions USD)",
    "cshoq": "Common shares outstanding (quarterly, millions of shares)",
    "epspxq": "Earnings per share excluding extraordinary items",
    "niq": "Net income (quarterly, millions USD)",
    "saleq": "Sales or revenue (quarterly, millions USD)",
    "oancfy": "Operating cash flow (quarterly YTD, millions USD)",

    # -----------------------------
    # Industry classifications
    # -----------------------------
    "gind": "Global Industry Classification (GICS industry)",
    "gsector": "Global Industry Classification sector",
    "gsubind": "Global Industry Classification sub-industry",

    # -----------------------------
    # CRSP-Compustat link table
    # -----------------------------
    "LINKDT": "Start date of CRSP-Compustat link",
    "LINKENDDT": "End date of CRSP-Compustat link",

    # -----------------------------
    # Derived valuation & profitability metrics
    # -----------------------------
    "cf_ps": "Cash-flow per share",
    "sales_ps": "Sales per share",
    "bv_ps": "Book value per share",
    "ep": "Earnings-to-price ratio",
    "cfp": "Cash-flow-to-price ratio",
    "sp": "Sales-to-price ratio",
    "roe": "Return on equity",
    "roa": "Return on assets",
    "cf_sales": "Cash-flow-to-sales ratio",
    "bvp": "Book-value-to-price ratio",

    # -----------------------------
    # Compustat metadata
    # -----------------------------
    "costat": "Company status (active/inactive)",
    "curcdq": "Currency code",
    "datafmt": "Data format (e.g., STD)",
    "indfmt": "Industry format",
    "consol": "Consolidation level"
}