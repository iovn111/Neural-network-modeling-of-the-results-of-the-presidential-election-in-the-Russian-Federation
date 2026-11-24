"""Расчет X1, X2 и X3; X4 добавляется после проверки биографий.

Запуск из любой папки: python scripts/prepare_partial_features.py
Требуется только стандартная библиотека Python 3.
"""
import csv
from collections import Counter
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
OUT = ROOT / "data" / "intermediate" / "partial_features.csv"


def read_csv(name):
    with (RAW / name).open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def main():
    results = read_csv("election_results.csv")
    bios = read_csv("candidate_birth_dates.csv")
    births = {r["candidate"]: r for r in bios}
    assert len(births) == len(bios) == 33, "Повтор или отсутствие биографии"
    assert len(results) == 48, "Неожиданный объем исходной выборки"
    keys = {(r["year"], r["candidate"]) for r in results}
    assert len(keys) == len(results), "Дублирование наблюдения"
    assert {r["candidate"] for r in results} == set(births)
    assert Counter(int(r["year"]) for r in results) == {
        1996: 10, 2000: 11, 2004: 6, 2008: 4, 2012: 5, 2018: 8, 2024: 4
    }
    incumbents = {
        1996: "Ельцин Борис Николаевич",
        2000: "Путин Владимир Владимирович",
        2004: "Путин Владимир Владимирович",
        2018: "Путин Владимир Владимирович",
        2024: "Путин Владимир Владимирович",
    }
    # 2008 и 2012: действующий президент в голосовании не участвовал.
    # История должностей: https://www.kommersant.ru/doc/6524296
    # https://www.vedomosti.ru/person/1102678-medvedev-dmitrii
    seen = Counter()
    output = []
    for r in sorted(results, key=lambda r: (int(r["year"]), r["candidate"])):
        name = r["candidate"]
        election = date.fromisoformat(r["election_date"])
        bio = births[name]
        born = date.fromisoformat(bio["birth_date"])
        age = election.year - born.year - (
            (election.month, election.day) < (born.month, born.day)
        )
        assert 0 <= float(r["vote_share_pct"]) <= 100
        output.append({
            "year": r["year"], "election_date": r["election_date"],
            "candidate": name, "birth_date": bio["birth_date"],
            "X1": age, "X2": int(incumbents.get(election.year) == name),
            "X3": seen[name], "D1": r["vote_share_pct"],
            "result_source": r["result_source"],
            "biography_source": bio["biography_source"],
        })
        seen[name] += 1
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(output[0]))
        writer.writeheader()
        writer.writerows(output)
    print(f"Подготовлено {len(output)} строк: {OUT}")
    print("Промежуточный файл: не использовать для обучения до добавления X4.")


if __name__ == "__main__":
    main()
