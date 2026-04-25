"""
Name lists from Bertrand & Mullainathan (2004).
"Are Emily and Greg More Employable Than Lakisha and Jamal?"
American Economic Review, 94(4), 991-1013.
"""
import hashlib

# (first_name, last_name) pairs — last names also drawn from B&M demographics
WHITE_MALE_NAMES: list[tuple[str, str]] = [
    ("Brad", "Baker"),
    ("Brendan", "Murphy"),
    ("Derek", "Walsh"),
    ("Geoffrey", "Sullivan"),
    ("Greg", "Cooper"),
    ("Jay", "Bennett"),
    ("Matthew", "O'Brien"),
    ("Neil", "Parker"),
    ("Todd", "Morris"),
    ("Brett", "Mitchell"),
]

BLACK_MALE_NAMES: list[tuple[str, str]] = [
    ("Darnell", "Washington"),
    ("Hakim", "Jefferson"),
    ("Jermaine", "Williams"),
    ("Kareem", "Jackson"),
    ("Jamal", "Robinson"),
    ("Leroy", "Thompson"),
    ("Rasheed", "Harris"),
    ("Tremayne", "Davis"),
    ("Tyrone", "Moore"),
]

WHITE_FEMALE_NAMES: list[tuple[str, str]] = [
    ("Anne", "Baker"),
    ("Allison", "Kelly"),
    ("Carrie", "Sullivan"),
    ("Emily", "Walsh"),
    ("Jill", "Murphy"),
    ("Kristen", "Cooper"),
    ("Laurie", "Bennett"),
    ("Meredith", "Parker"),
    ("Rachel", "Morris"),
    ("Sarah", "O'Brien"),
]

BLACK_FEMALE_NAMES: list[tuple[str, str]] = [
    ("Aisha", "Washington"),
    ("Ebony", "Jefferson"),
    ("Keisha", "Williams"),
    ("Kenya", "Jackson"),
    ("Lakisha", "Robinson"),
    ("Latonya", "Thompson"),
    ("Latoya", "Harris"),
    ("Tamika", "Davis"),
    ("Tanisha", "Moore"),
]

# All white-coded first names (lowercase) for quick lookup
_ALL_WHITE_FIRSTS = frozenset(
    n[0].lower() for n in WHITE_MALE_NAMES + WHITE_FEMALE_NAMES
)
_ALL_BLACK_FIRSTS = frozenset(
    n[0].lower() for n in BLACK_MALE_NAMES + BLACK_FEMALE_NAMES
)


def _get_lists(gender: str) -> tuple[list, list]:
    if gender == "male":
        return WHITE_MALE_NAMES, BLACK_MALE_NAMES
    elif gender == "female":
        return WHITE_FEMALE_NAMES, BLACK_FEMALE_NAMES
    else:
        return (
            WHITE_FEMALE_NAMES + WHITE_MALE_NAMES,
            BLACK_FEMALE_NAMES + BLACK_MALE_NAMES,
        )


def select_variant_names(original_name: str, gender: str) -> tuple[str, str]:
    """
    Deterministically pick one white-coded and one black-coded name pair
    from the B&M 2004 lists, seeded by the original name so results are
    reproducible for the same input.
    """
    white_list, black_list = _get_lists(gender)
    seed = int(hashlib.md5(original_name.lower().encode()).hexdigest(), 16)
    white_pair = white_list[seed % len(white_list)]
    black_pair = black_list[seed % len(black_list)]
    return f"{white_pair[0]} {white_pair[1]}", f"{black_pair[0]} {black_pair[1]}"


def detect_name_coding(name: str) -> str:
    """Return 'white_coded', 'black_coded', or 'neutral' for a given name."""
    if not name:
        return "neutral"
    first = name.strip().split()[0].lower()
    if first in _ALL_WHITE_FIRSTS:
        return "white_coded"
    if first in _ALL_BLACK_FIRSTS:
        return "black_coded"
    return "neutral"
