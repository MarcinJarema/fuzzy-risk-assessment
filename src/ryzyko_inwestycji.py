"""
System rozmyty 2: **Ocena ryzyka inwestycji**

Cel: oszacować ryzyko instrumentu/projektu inwestycyjnego na podstawie
oczekiwanej stopy zwrotu oraz zmienności (wahań) rynku. Dominującym
czynnikiem jest zmienność; bardzo wysoka obiecywana stopa zwrotu również
sygnalizuje podwyższone ryzyko.
"""

from __future__ import annotations

from .fuzzy_core import MF, Rule, SystemSpec, Variable

# --- Wejście 1: Stopa_zwrotu [0, 30] % rocznie -----------------------------
STOPA_ZWROTU = Variable(
    name="Stopa_zwrotu",
    unit="% rocznie",
    vmin=0,
    vmax=30,
    mfs=[
        MF("N", "trap", [0, 0, 6, 12]),
        MF("S", "tri", [8, 15, 22]),
        MF("W", "trap", [18, 24, 30, 30]),
    ],
    labels_pl={"N": "niska", "S": "średnia", "W": "wysoka"},
)

# --- Wejście 2: Zmiennosc [0, 100] (wahania rynku) -------------------------
ZMIENNOSC = Variable(
    name="Zmiennosc",
    unit="indeks",
    vmin=0,
    vmax=100,
    mfs=[
        MF("M", "trap", [0, 0, 20, 40]),
        MF("S", "tri", [30, 50, 70]),
        MF("D", "trap", [60, 80, 100, 100]),
    ],
    labels_pl={"M": "mała", "S": "średnia", "D": "duża"},
)

# --- Wyjście: Ryzyko_inwestycji [0, 100] % ---------------------------------
RYZYKO = Variable(
    name="Ryzyko_inwestycji",
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
# Logika eksperta: ryzyko rośnie przede wszystkim ze zmiennością rynku.
# Wysoka oczekiwana stopa zwrotu przy małej zmienności bywa „zbyt piękna”,
# więc lekko podnosi ryzyko (premia za ryzyko).
RULES = [
    Rule(("N", "M"), "N"),  # niska stopa, mała zmienność   -> niskie
    Rule(("N", "S"), "S"),  # niska stopa, średnia          -> średnie
    Rule(("N", "D"), "W"),  # niska stopa, duża zmienność   -> wysokie
    Rule(("S", "M"), "N"),  # średnia stopa, mała           -> niskie
    Rule(("S", "S"), "S"),  # średnia stopa, średnia        -> średnie
    Rule(("S", "D"), "W"),  # średnia stopa, duża           -> wysokie
    Rule(("W", "M"), "S"),  # wysoka stopa, mała zmienność  -> średnie
    Rule(("W", "S"), "S"),  # wysoka stopa, średnia         -> średnie
    Rule(("W", "D"), "W"),  # wysoka stopa, duża            -> wysokie
]

SPEC = SystemSpec(
    key="inwestycja",
    title="Ocena ryzyka inwestycji",
    goal=(
        "Oszacowanie ryzyka instrumentu/projektu inwestycyjnego na podstawie "
        "oczekiwanej stopy zwrotu oraz zmienności (wahań) rynku."
    ),
    input1=STOPA_ZWROTU,
    input2=ZMIENNOSC,
    output=RYZYKO,
    rules=RULES,
)

TEST_CASES = [
    (4, 15),    # niska stopa, mała zmienność
    (8, 85),    # niska stopa, duża zmienność
    (15, 50),   # średnia stopa, średnia zmienność
    (27, 20),   # wysoka stopa, mała zmienność
    (27, 90),   # wysoka stopa, duża zmienność
]
