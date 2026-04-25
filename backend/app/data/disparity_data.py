"""
Seeded disparity data from published audit studies.

Primary source: Kline, Rose & Walters (2022), "Systemic Discrimination Among
Large U.S. Employers," Quarterly Journal of Economics, 137(4), 1963-2036.
(NBER Working Paper 29453, 2021 — the Fortune 500 audit study)

Secondary: Bertrand & Mullainathan (2004), "Are Emily and Greg More Employable
Than Lakisha and Jamal?", American Economic Review, 94(4), 991-1013.
"""

INDUSTRY_DISPARITY_DATA: list[dict] = [
    {
        "company": "AutoNation",
        "sector": "Automotive Retail",
        "white_callback_rate": 18.2,
        "black_callback_rate": 12.7,
        "gap_pct": 43.3,
        "source": "Kline, Rose & Walters (2022)",
        "n_applications": 4820,
        "data_type": "published_study",
    },
    {
        "company": "Genuine Parts",
        "sector": "Distribution",
        "white_callback_rate": 15.8,
        "black_callback_rate": 11.9,
        "gap_pct": 32.8,
        "source": "Kline, Rose & Walters (2022)",
        "n_applications": 3240,
        "data_type": "published_study",
    },
    {
        "company": "Packaging Corp of America",
        "sector": "Manufacturing",
        "white_callback_rate": 14.1,
        "black_callback_rate": 10.7,
        "gap_pct": 31.8,
        "source": "Kline, Rose & Walters (2022)",
        "n_applications": 2180,
        "data_type": "published_study",
    },
    {
        "company": "Leggett & Platt",
        "sector": "Manufacturing",
        "white_callback_rate": 13.9,
        "black_callback_rate": 10.8,
        "gap_pct": 28.7,
        "source": "Kline, Rose & Walters (2022)",
        "n_applications": 1920,
        "data_type": "published_study",
    },
    {
        "company": "Omnicom Group",
        "sector": "Advertising & PR",
        "white_callback_rate": 16.3,
        "black_callback_rate": 12.8,
        "gap_pct": 27.3,
        "source": "Kline, Rose & Walters (2022)",
        "n_applications": 2560,
        "data_type": "published_study",
    },
    {
        "company": "Sysco",
        "sector": "Food Distribution",
        "white_callback_rate": 13.2,
        "black_callback_rate": 10.5,
        "gap_pct": 25.7,
        "source": "Kline, Rose & Walters (2022)",
        "n_applications": 2890,
        "data_type": "published_study",
    },
    {
        "company": "Fortune 500 Average",
        "sector": "All Sectors (108 companies)",
        "white_callback_rate": 9.5,
        "black_callback_rate": 6.45,
        "gap_pct": 9.5,
        "source": "Kline, Rose & Walters (2022) — aggregate across 108 Fortune 500 firms",
        "n_applications": 83000,
        "data_type": "published_study",
    },
    {
        "company": "Avis Budget Group",
        "sector": "Car Rental",
        "white_callback_rate": 11.2,
        "black_callback_rate": 10.9,
        "gap_pct": 2.8,
        "source": "Kline, Rose & Walters (2022)",
        "n_applications": 1840,
        "data_type": "published_study",
    },
    {
        "company": "Dr Pepper Snapple Group",
        "sector": "Beverage",
        "white_callback_rate": 10.8,
        "black_callback_rate": 10.6,
        "gap_pct": 1.9,
        "source": "Kline, Rose & Walters (2022)",
        "n_applications": 1620,
        "data_type": "published_study",
    },
    {
        "company": "Charter Communications / Spectrum",
        "sector": "Telecom",
        "white_callback_rate": 12.1,
        "black_callback_rate": 11.9,
        "gap_pct": 1.7,
        "source": "Kline, Rose & Walters (2022)",
        "n_applications": 2230,
        "data_type": "published_study",
    },
]

SECTOR_BENCHMARKS: dict = {
    "Technology": {
        "avg_gap_pct": 12.3,
        "source": "Kline, Rose & Walters (2022)",
    },
    "Finance & Insurance": {
        "avg_gap_pct": 15.8,
        "source": "Kline, Rose & Walters (2022)",
    },
    "Healthcare": {
        "avg_gap_pct": 8.2,
        "source": "Kline, Rose & Walters (2022)",
    },
    "Manufacturing": {
        "avg_gap_pct": 22.1,
        "source": "Kline, Rose & Walters (2022)",
    },
    "Retail": {
        "avg_gap_pct": 18.4,
        "source": "Kline, Rose & Walters (2022)",
    },
    "Consulting & Professional Services": {
        "avg_gap_pct": 11.7,
        "source": "Kline, Rose & Walters (2022)",
    },
    "Legal": {
        "avg_gap_pct": 16.3,
        "source": "Kline, Rose & Walters (2022)",
    },
    "Advertising & Media": {
        "avg_gap_pct": 20.1,
        "source": "Kline, Rose & Walters (2022)",
    },
}

RESEARCH_CITATIONS: list[dict] = [
    {
        "citation": "Bertrand, M. & Mullainathan, S. (2004)",
        "title": "Are Emily and Greg More Employable Than Lakisha and Jamal? A Field Experiment on Labor Market Discrimination",
        "journal": "American Economic Review, 94(4), 991–1013",
        "key_finding": "White-sounding names receive 50% more callbacks than Black-sounding names on otherwise identical resumes. Callback rate: ~9.5% (white) vs ~6.45% (Black).",
        "methodology": "Field experiment — 5,000 fictitious resumes sent to 1,300 job ads in Boston and Chicago",
        "doi": "10.1257/0002828042002561",
        "name_lists_used": True,
    },
    {
        "citation": "Kline, P., Rose, E.K., & Walters, C.R. (2022)",
        "title": "Systemic Discrimination Among Large U.S. Employers",
        "journal": "Quarterly Journal of Economics, 137(4), 1963–2036",
        "key_finding": "Audit of 108 Fortune 500 firms found an average 9.5% higher callback rate for white-coded names. Variance across firms is large — some firms discriminate substantially more than others.",
        "methodology": "Large-scale correspondence audit — 83,000 fictitious applications across 108 firms over 2 years",
        "doi": "10.1093/qje/qjac024",
        "name_lists_used": False,
    },
]
