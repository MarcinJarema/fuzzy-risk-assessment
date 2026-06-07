"""
Runner projektu — systemy rozmyte do oceny ryzyka biznesowego.

Przykłady użycia::

    # pełna analiza: wykresy MF, powierzchnie sterowania, tabele testów
    python main.py

    # bez generowania wykresów (sama analiza liczbowa)
    python main.py --no-plots

    # pojedyncze zapytanie do wybranego systemu
    python main.py --system klient --query 3000 80
    python main.py --system inwestycja --query 15 50
    python main.py --system dostawy --query 90 55
"""

from __future__ import annotations

import argparse
from pathlib import Path

from src import SPECS, TEST_CASES
from src.fuzzy_core import (
    FuzzySystem,
    SystemSpec,
    plot_membership,
    plot_surface,
    run_tests,
)

RESULTS_DIR = Path(__file__).parent / "results"


def _spec_by_key(key: str) -> SystemSpec:
    for spec in SPECS:
        if spec.key == key:
            return spec
    raise SystemExit(f"Nieznany system: {key!r}. Dostępne: {[s.key for s in SPECS]}")


def _print_test_table(spec: SystemSpec, rows: list[dict]) -> str:
    headers = [spec.input1.name, spec.input2.name, spec.output.name]
    lines = [
        f"### {spec.title}",
        "",
        f"| {headers[0]} [{spec.input1.unit}] | {headers[1]} [{spec.input2.unit}] "
        f"| {headers[2]} [{spec.output.unit}] |",
        "|---|---|---|",
    ]
    for r in rows:
        lines.append(f"| {r[headers[0]]:g} | {r[headers[1]]:g} | {r[headers[2]]:g} |")
    table = "\n".join(lines)
    print("\n" + table)
    return table


def run_query(key: str, x1: float, x2: float) -> None:
    spec = _spec_by_key(key)
    system = FuzzySystem(spec)
    y = system.infer(x1, x2)
    print(f"\n=== {spec.title} ===")
    print(f"{spec.input1.name} = {x1:g} {spec.input1.unit}")
    print(f"{spec.input2.name} = {x2:g} {spec.input2.unit}")
    print(f"-> {spec.output.name} = {y:.2f} {spec.output.unit}")


def run_all(make_plots: bool = True) -> None:
    RESULTS_DIR.mkdir(exist_ok=True)
    md_tables: list[str] = ["# Tabele testów systemów rozmytych\n"]

    for spec in SPECS:
        print(f"\n{'=' * 70}\n{spec.title}\n{'=' * 70}")
        print(spec.goal)
        system = FuzzySystem(spec)

        rows = run_tests(system, TEST_CASES[spec.key])
        md_tables.append(_print_test_table(spec, rows) + "\n")

        if make_plots:
            mf_path = RESULTS_DIR / f"mf_{spec.key}.png"
            surf_path = RESULTS_DIR / f"surface_{spec.key}.png"
            plot_membership(spec, system, mf_path)
            plot_surface(spec, system, surf_path)
            print(f"  [wykres] {mf_path.name}, {surf_path.name}")

    (RESULTS_DIR / "tabela_testow.md").write_text("\n".join(md_tables), encoding="utf-8")
    print(f"\nWyniki zapisane w: {RESULTS_DIR}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Systemy rozmyte do oceny ryzyka biznesowego.")
    parser.add_argument(
        "--system",
        choices=[s.key for s in SPECS],
        help="klucz systemu do zapytania pojedynczego",
    )
    parser.add_argument(
        "--query",
        nargs=2,
        type=float,
        metavar=("WEJSCIE1", "WEJSCIE2"),
        help="wartości dwóch wejść dla wybranego systemu",
    )
    parser.add_argument("--no-plots", action="store_true", help="pomiń generowanie wykresów")
    args = parser.parse_args()

    if args.system and args.query:
        run_query(args.system, args.query[0], args.query[1])
    elif args.system or args.query:
        parser.error("--system i --query muszą być podane razem")
    else:
        run_all(make_plots=not args.no_plots)


if __name__ == "__main__":
    main()
