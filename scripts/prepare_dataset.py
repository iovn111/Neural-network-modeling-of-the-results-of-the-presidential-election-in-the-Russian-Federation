"""Воспроизводимая подготовка числовых выборок. Python 3, без зависимостей."""
import csv
from collections import Counter
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
OUT = ROOT / "data" / "processed"
FIELDS = ["X1", "X2", "X3", "X4", "D1"]

def read(name):
    with (RAW / name).open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))

def write(name, fields, rows):
    with (OUT / name).open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        w.writeheader()
        w.writerows(rows)

def main():
    results = read("election_results.csv")
    births = {r["candidate"]: r for r in read("candidate_birth_dates.csv")}
    offices = {r["candidate"]: r for r in read("office_review.csv")}
    assert len(results) == 48 and len(births) == len(offices) == 33
    assert len({(r["year"], r["candidate"]) for r in results}) == 48
    assert set(births) == set(offices) == {r["candidate"] for r in results}
    incumbents = {1996: "Ельцин Борис Николаевич", **{y: "Путин Владимир Владимирович" for y in (2000, 2004, 2018, 2024)}}
    seen = Counter()
    output = []
    for r in sorted(results, key=lambda r: int(r["year"])):
        name = r["candidate"]
        election = date.fromisoformat(r["election_date"])
        y = election.year
        bio = births[name]
        born = date.fromisoformat(bio["birth_date"])
        office = offices[name]
        start = office["qualifying_start_year"]
        age = y - born.year - ((election.month, election.day) < (born.month, born.day))
        vote = float(r["vote_share_pct"])
        assert 0 <= vote <= 100
        # Все даты начала квалифицирующих должностей предшествуют голосованию
        # в соответствующем году; для Жириновского это 19 января 2000.
        result_source = {1996: "https://stepanov01.narod.ru/library/organs/election.pres.96.htm",
                         2004: "https://www.kommersant.ru/doc/973179"}.get(y, r["result_source"])
        biography_source = bio["biography_source"]
        if name.startswith("Федоров"):
            biography_source = "https://isee.ru/news/95-letie-so-dnya-rozhdeniya-svyatoslava-nikolaevicha-fedorova/"
        if name.startswith("Собчак"):
            biography_source = "https://www.kommersant.ru/doc/3541029"
        output.append(dict(year=y, election_date=r["election_date"], candidate=name,
                           birth_date=bio["birth_date"], X1=age,
                           X2=int(incumbents.get(y) == name), X3=seen[name],
                           X4=int(bool(start) and int(start) <= y), D1=f"{vote:.2f}",
                           split="train" if y <= 2012 else "validation" if y == 2018 else "test",
                           result_source=result_source, biography_source=biography_source,
                           position_source=office["position_source"]))
        seen[name] += 1
    OUT.mkdir(parents=True, exist_ok=True)
    write("candidates.csv", list(output[0]), output)
    for split, expected in [("train", 36), ("validation", 8), ("test", 4)]:
        rows = [r for r in output if r["split"] == split]
        assert len(rows) == expected
        write(split + ".csv", FIELDS, rows)

if __name__ == "__main__":
    main()
