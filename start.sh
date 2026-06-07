#!/usr/bin/env bash
# Uruchamia interaktywny kreator oceny ryzyka:
# aktywuje wirtualne środowisko .venv i włącza interaktywny.py.
#
# Użycie:
#   ./start.sh        (po nadaniu uprawnień: chmod +x start.sh)
#   bash start.sh
set -euo pipefail

# Katalog, w którym leży ten skrypt — działa niezależnie od miejsca wywołania.
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

if [[ ! -d ".venv" ]]; then
  echo "Brak .venv — tworzę i instaluję zależności..."
  python3.12 -m venv .venv
  source .venv/bin/activate
  pip install -r requirements.txt
else
  source .venv/bin/activate
fi

python interaktywny.py
