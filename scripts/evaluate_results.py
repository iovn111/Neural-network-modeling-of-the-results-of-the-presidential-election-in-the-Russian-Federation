"""Проверка метрик исторического тестирования по сохранённым данным."""
import csv
import math
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
def read(relative):
    with (ROOT / relative).open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))

def metrics(actual, estimate):
    errors = [a-b for a,b in zip(actual, estimate)]
    return statistics.mean(map(abs, errors)), math.sqrt(statistics.mean(e*e for e in errors))

def main():
    train = read("data/processed/train.csv")
    test = read("data/results/historical_test_results.csv")
    assert len(train) == 36 and len(test) == 4
    actual = [float(r["D1"]) for r in test]
    estimate = [float(r["Y1"]) for r in test]
    baseline = statistics.mean(float(r["D1"]) for r in train)
    for name, values in [("Модель", estimate), ("Среднее обучающей выборки", [baseline]*len(actual))]:
        mae, rmse = metrics(actual, values)
        print(f"{name}: MAE={mae:.4f}, RMSE={rmse:.4f} п. п.")

if __name__ == "__main__":
    main()
