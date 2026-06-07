"""
System rozmyty 3: **Ocena ryzyka dostaw**

Cel: oszacować ryzyko łańcucha dostaw na podstawie niezawodności dostawcy
oraz deklarowanego czasu dostawy. Dominującym czynnikiem jest niezawodność
dostawcy; długi czas dostawy dodatkowo zwiększa ryzyko.
"""

from __future__ import annotations

from .fuzzy_core import MF, Rule, SystemSpec, Variable

# --- Wejście 1: Niezawodnosc_dostawcy [0, 100] % terminowych dostaw ---------
NIEZAWODNOSC = Variable(
    name="Niezawodnosc_dostawcy",
    unit="%",
    vmin=0,
    vmax=100,
    mfs=[
        MF("N", "trap", [0, 0, 20, 45]),
        MF("S", "tri", [35, 55, 75]),
        MF("W", "trap", [65, 85, 100, 100]),
    ],
    labels_pl={"N": "niska", "S": "średnia", "W": "wysoka"},
)

# --- Wejście 2: Czas_dostawy [0, 60] dni -----------------------------------
CZAS_DOSTAWY = Variable(
    name="Czas_dostawy",
    unit="dni",
    vmin=0,
    vmax=60,
    mfs=[
        MF("K", "trap", [0, 0, 10, 25]),
        MF("S", "tri", [15, 30, 45]),
        MF("D", "trap", [35, 50, 60, 60]),
    ],
    labels_pl={"K": "krótki", "S": "średni", "D": "długi"},
)

# --- Wyjście: Ryzyko_dostaw [0, 100] % -------------------------------------
RYZYKO = Variable(
    name="Ryzyko_dostaw",
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
# Logika eksperta: niska niezawodność dostawcy = wysokie ryzyko niezależnie
# od czasu; przy wysokiej niezawodności ryzyko jest niskie, a długi czas
# dostawy podnosi je jedynie umiarkowanie.
RULES = [
    Rule(("N", "K"), "S"),  # niska niezawodność, krótki czas  -> średnie
    Rule(("N", "S"), "W"),  # niska niezawodność, średni czas  -> wysokie
    Rule(("N", "D"), "W"),  # niska niezawodność, długi czas   -> wysokie
    Rule(("S", "K"), "N"),  # średnia niezawodność, krótki     -> niskie
    Rule(("S", "S"), "S"),  # średnia niezawodność, średni     -> średnie
    Rule(("S", "D"), "W"),  # średnia niezawodność, długi      -> wysokie
    Rule(("W", "K"), "N"),  # wysoka niezawodność, krótki      -> niskie
    Rule(("W", "S"), "N"),  # wysoka niezawodność, średni      -> niskie
    Rule(("W", "D"), "S"),  # wysoka niezawodność, długi       -> średnie
]

SPEC = SystemSpec(
    key="dostawy",
    title="Ocena ryzyka dostaw",
    goal=(
        "Oszacowanie ryzyka łańcucha dostaw na podstawie niezawodności dostawcy "
        "oraz deklarowanego czasu dostawy."
    ),
    input1=NIEZAWODNOSC,
    input2=CZAS_DOSTAWY,
    output=RYZYKO,
    rules=RULES,
)

TEST_CASES = [
    (20, 8),     # niska niezawodność, krótki czas
    (15, 50),    # niska niezawodność, długi czas
    (55, 30),    # średnia niezawodność, średni czas
    (95, 7),     # wysoka niezawodność, krótki czas
    (90, 55),    # wysoka niezawodność, długi czas
]
