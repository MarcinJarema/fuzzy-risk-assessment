# Analiza operatorów — porównanie metod defuzyfikacji

Wynik [%] dla tych samych przykładów przy różnych metodach wyostrzania (centroid, bisector, mom, som, lom). Operatory wnioskowania pozostają stałe: AND = min, implikacja = min, agregacja = max.

### Ocena ryzyka klienta (kredytowego)

| Dochod | Historia_kredytowa | centroid | bisector | mom | som | lom |
|---|---|---|---|---|---|---|
| 2000 | 15 | 83.33 | 85.36 | 100 | 100 | 100 |
| 3000 | 80 | 50 | 50 | 50 | 50 | 50 |
| 10000 | 50 | 50 | 50 | 50 | 50 | 50 |
| 16000 | 90 | 16.67 | 14.64 | 0 | 0 | 0 |
| 18000 | 10 | 50 | 50 | 50 | 50 | 50 |

### Ocena ryzyka inwestycji

| Stopa_zwrotu | Zmiennosc | centroid | bisector | mom | som | lom |
|---|---|---|---|---|---|---|
| 4 | 15 | 16.67 | 14.64 | 0 | 0 | 0 |
| 8 | 85 | 81.94 | 83.33 | 91.52 | 83.33 | 100 |
| 15 | 50 | 50 | 50 | 50 | 50 | 50 |
| 27 | 20 | 50 | 50 | 50 | 50 | 50 |
| 27 | 90 | 83.33 | 85.36 | 100 | 100 | 100 |

### Ocena ryzyka dostaw

| Niezawodnosc_dostawcy | Czas_dostawy | centroid | bisector | mom | som | lom |
|---|---|---|---|---|---|---|
| 20 | 8 | 50 | 50 | 50 | 50 | 50 |
| 15 | 50 | 83.33 | 85.36 | 100 | 100 | 100 |
| 55 | 30 | 50 | 50 | 50 | 50 | 50 |
| 95 | 7 | 16.67 | 14.64 | 0 | 0 | 0 |
| 90 | 55 | 50 | 50 | 50 | 50 | 50 |
