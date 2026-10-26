## Použitie

```bash
pip install requests
python main.py
```

`main.py` postupne spustí crawler, parser, indexer a vyhľadávanie. Crawler a parser preskočia už stiahnuté súbory, takže ďalšie spustenie je rýchlejšie. Po zaindexovaní sa v slučke pýta na dopyt a tri voľby:

| Voľba | Hodnoty | Význam |
|---|---|---|
| `Look for (or exit)` | ľubovoľný text, `exit` | Dopyt sa rozdelí na tokeny (malé písmená, bez interpunkcie). `exit` ukončí program. |
| `Search for movies or actors?` | `movies` / `actors` | Určuje, ktorý index sa prehľadáva: filmy alebo osoby. |
| `Use classic or smoothed IDF?` | `classic` / `smoothed` | Metóda výpočtu IDF. `classic`: ln(N / df), `smoothed`: ln((N+1) / (df+1)) + 1. |
| `How many top results (1-5)?` | celé číslo 1 až 5 | Počet zobrazených výsledkov. |

Výsledky sú zoradené podľa skóre Σ TF × IDF. Pri neplatnej hodnote voľby program vypíše chybu a skončí.

Príklad:

```
Look for (or exit): dead evil
Search for movies or actors? movies
Use classic or smoothed IDF? smoothed
How many top results (1-5)? 3
```

### Poznámky

- Vyhľadávanie je textové: porovnáva tokeny, nie čísla ani štruktúrované podmienky (`age over 40` nefunguje ako filter).
- Nepoužíva sa stemming ani stop slová, takže `sport` a `sports` sú rôzne tokeny.
- Index sa buduje v pamäti pri každom spustení a neukladá sa na disk.
