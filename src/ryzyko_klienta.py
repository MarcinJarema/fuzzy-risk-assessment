"""
System rozmyty 1: **Ocena ryzyka klienta (kredytowego)**

Cel: oszacować ryzyko związane z udzieleniem klientowi kredytu/limitu
kupieckiego na podstawie jego dochodu oraz oceny historii kredytowej.
Im niższy dochód i gorsza historia, tym wyższe ryzyko.
"""

from __future__ import annotations

from .fuzzy_core import MF, Rule, SystemSpec, Variable

# --- Wejście 1: Dochod [0, 20000] zł/mies. ---------------------------------
DOCHOD = Variable(
    name="Dochod",
    unit="zł/mies.",
    vmin=0,
    vmax=20000,
    mfs=[
        MF("N", "trap", [0, 0, 4000, 8000]),
        MF("S", "tri", [5000, 10000, 15000]),
        MF("W", "trap", [12000, 16000, 20000, 20000]),
    ],
    labels_pl={"N": "niski", "S": "średni", "W": "wysoki"},
)

# --- Wejście 2: Historia_kredytowa [0, 100] pkt (scoring) -------------------
HISTORIA = Variable(
    name="Historia_kredytowa",
    unit="pkt",
    vmin=0,
    vmax=100,
    mfs=[
        MF("Z", "trap", [0, 0, 20, 40]),
        MF("P", "tri", [30, 50, 70]),
        MF("D", "trap", [60, 80, 100, 100]),
    ],
    labels_pl={"Z": "zła", "P": "przeciętna", "D": "dobra"},
)

# --- Wyjście: Ryzyko [0, 100] % --------------------------------------------
RYZYKO = Variable(
    name="Ryzyko",
    unit="%",
    vmin=0,
    vmax=100,
    mfs=[
        MF("N", "tri", [0, 0, 50]),
        MF("S", "tri", [0, 50, 100]),
        MF("W", "tri", [50, 100, 100]),
    ],
    labels_pl={"N": "niskie", "S": "średnie", "W": "wysokie"},
)

# --- Baza reguł (9 = wszystkie kombinacje) ---------------------------------
# Logika eksperta: niski dochód lub zła historia podnoszą ryzyko; wysoki
# dochód i dobra historia je obniżają. Historia ma duży wpływ przy niskim
# dochodzie, dochód „ratuje” sytuację przy przeciętnej historii.
RULES = [
    Rule(("N", "Z"), "W"),  # niski dochód, zła historia      -> wysokie
    Rule(("N", "P"), "W"),  # niski dochód, przeciętna         -> wysokie
    Rule(("N", "D"), "S"),  # niski dochód, dobra historia     -> średnie
    Rule(("S", "Z"), "W"),  # średni dochód, zła historia      -> wysokie
    Rule(("S", "P"), "S"),  # średni dochód, przeciętna        -> średnie
    Rule(("S", "D"), "N"),  # średni dochód, dobra historia    -> niskie
    Rule(("W", "Z"), "S"),  # wysoki dochód, zła historia      -> średnie
    Rule(("W", "P"), "N"),  # wysoki dochód, przeciętna        -> niskie
    Rule(("W", "D"), "N"),  # wysoki dochód, dobra historia    -> niskie
]

SPEC = SystemSpec(
    key="klient",
    title="Ocena ryzyka klienta (kredytowego)",
    goal=(
        "Oszacowanie ryzyka udzielenia klientowi kredytu/limitu kupieckiego na "
        "podstawie miesięcznego dochodu oraz punktowej oceny historii kredytowej."
    ),
    input1=DOCHOD,
    input2=HISTORIA,
    output=RYZYKO,
    rules=RULES,
)

# Przypadki testowe do weryfikacji (krok 6 schematu).
TEST_CASES = [
    (2000, 15),    # bardzo niski dochód, zła historia
    (3000, 80),    # niski dochód, ale dobra historia
    (10000, 50),   # średni dochód, przeciętna historia
    (16000, 90),   # wysoki dochód, dobra historia
    (18000, 10),   # wysoki dochód, zła historia
]
