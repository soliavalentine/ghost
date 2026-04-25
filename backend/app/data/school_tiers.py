"""
School tier lookup for ATS scoring and bias proxy signal detection.

Tier 1 = Elite (Ivy League + MIT/Stanford/Caltech tier)
Tier 2 = Top ~25 nationally ranked
Tier 3 = Regional flagship state schools
Tier 4 = Other four-year institutions (default fallback)

HBCUs are flagged separately — they are quality institutions, not lower tier.
The HBCU flag surfaces as a bias proxy signal because research shows HBCU
graduates face additional screening penalties in biased systems (Kline et al. 2022).
"""

SCHOOL_TIERS: dict[str, int] = {
    # Tier 1
    "harvard": 1,
    "yale": 1,
    "princeton": 1,
    "mit": 1,
    "massachusetts institute of technology": 1,
    "stanford": 1,
    "caltech": 1,
    "california institute of technology": 1,
    "columbia": 1,
    "upenn": 1,
    "university of pennsylvania": 1,
    "dartmouth": 1,
    "brown": 1,
    "cornell": 1,
    "duke": 1,
    "northwestern": 1,
    "johns hopkins": 1,
    "rice": 1,
    "notre dame": 1,
    "vanderbilt": 1,
    "carnegie mellon": 1,
    "washington university in st. louis": 1,
    "washu": 1,
    "emory": 1,
    "georgetown": 1,
    "tufts": 1,
    # Tier 2
    "michigan": 2,
    "university of virginia": 2,
    "unc": 2,
    "university of north carolina": 2,
    "ucla": 2,
    "uc berkeley": 2,
    "university of california berkeley": 2,
    "usc": 2,
    "university of southern california": 2,
    "nyu": 2,
    "new york university": 2,
    "boston college": 2,
    "lehigh": 2,
    "villanova": 2,
    "brandeis": 2,
    "case western": 2,
    "tulane": 2,
    "fordham": 2,
    "rensselaer": 2,
    "rpi": 2,
    "georgia tech": 2,
    "georgia institute of technology": 2,
    "ut austin": 2,
    "university of texas": 2,
    "university of illinois": 2,
    "purdue": 2,
    "ohio state": 2,
    "penn state": 2,
    "university of wisconsin": 2,
    "university of minnesota": 2,
    "uc san diego": 2,
    "ucsd": 2,
    "uc davis": 2,
    "uc irvine": 2,
    "uc santa barbara": 2,
    "boston university": 2,
    "northeastern": 2,
    # Tier 3
    "university of florida": 3,
    "florida state": 3,
    "university of arizona": 3,
    "arizona state": 3,
    "university of colorado": 3,
    "university of oregon": 3,
    "university of washington": 3,
    "indiana university": 3,
    "university of iowa": 3,
    "michigan state": 3,
    "university of nebraska": 3,
    "university of kansas": 3,
    "university of kentucky": 3,
    "university of tennessee": 3,
    "university of south carolina": 3,
    "university of alabama": 3,
    "auburn": 3,
    "university of oklahoma": 3,
    "university of arkansas": 3,
    "west virginia university": 3,
    "university of connecticut": 3,
    "uconn": 3,
    "depaul": 3,
    "loyola": 3,
    "drexel": 3,
    "temple": 3,
    "rutgers": 3,
    "university of maryland": 3,
    "university of pittsburgh": 3,
    "university of delaware": 3,
}

# Historically Black Colleges and Universities
HBCUS: frozenset[str] = frozenset({
    "howard",
    "hampton",
    "spelman",
    "morehouse",
    "fisk",
    "tuskegee",
    "florida a&m",
    "famu",
    "north carolina a&t",
    "prairie view a&m",
    "xavier university of louisiana",
    "grambling",
    "alcorn",
    "bethune-cookman",
    "clark atlanta",
    "dillard",
    "lincoln university",
    "morgan state",
    "norfolk state",
    "shaw university",
    "southern university",
    "tennessee state",
    "virginia state",
    "west virginia state",
    "winston-salem state",
    "bowie state",
    "coppin state",
    "delaware state",
    "jackson state",
    "langston",
    "meharry",
    "miles college",
    "savannah state",
    "texas southern",
    "university of the district of columbia",
})


def get_school_tier(school_name: str) -> dict:
    """
    Return tier (1-4) and HBCU flag for a school name.
    Matching is substring-based so partial names resolve correctly.
    """
    name_lower = school_name.lower()

    is_hbcu = any(hbcu in name_lower for hbcu in HBCUS)

    tier: int | None = None
    for key, t in SCHOOL_TIERS.items():
        if key in name_lower:
            tier = t
            break

    if tier is None:
        tier = 2 if is_hbcu else 4

    return {
        "school": school_name,
        "tier": tier,
        "is_hbcu": is_hbcu,
        "recognized": tier <= 3 or is_hbcu,
    }
