# CTR Prediction - Real-Time Bidding

Projekt przewidywania prawdopodobieństwa kliknięcia reklamy (Click-Through Rate) w kontekście systemów Real-Time Bidding (RTB).

## Kontekst

W programmatic advertising każde wyświetlenie reklamy jest licytowane w czasie rzeczywistym (~100 ms). Kluczowym elementem decyzyjnym jest predykcja CTR - prawdopodobieństwa kliknięcia dla konkretnego bid requestu. Od jakości tej predykcji zależy, ile reklamodawca powinien zapłacić w aukcji, co bezpośrednio przekłada się na zwrot z inwestycji w kampanię.

## Cel projektu

Zbudowanie kompletnego pipeline'u CTR prediction z naciskiem na aspekty istotne w produkcyjnych systemach RTB:

- Praca z wysokokardynalnymi cechami kategorialnymi
- Walidacja chronologiczna (zamiast losowej)
- Kalibracja prawdopodobieństw (nie tylko ranking)
- Serwowanie predykcji w architekturze streamingowej

## Dataset

Avazu Click-Through Rate Prediction - publicznie dostępny dataset z mobilnej sieci reklamowej, zawierający ~40 mln bid requestów z 10 dni (21-30 października 2014).

Źródło: https://www.kaggle.com/c/avazu-ctr-prediction/data

## Stack technologiczny

- Python 3.11
- PySpark (wstępna agregacja dużych danych)
- scikit-learn, LightGBM (modelowanie)
- Pandas, NumPy (przetwarzanie)
- Docker, GitHub Actions (deployment i CI/CD)
- Apache Kafka (symulacja streamowania)

## Status

W trakcie realizacji.

## Struktura repozytorium

ctr-prediction/
├── data/               # dane (ignorowane przez git)
├── notebooks/          # notebooki do EDA i eksperymentów
├── src/                # moduły Pythona
│   ├── data/           # ładowanie i preprocessing
│   ├── features/       # feature engineering
│   ├── models/         # trening, ewaluacja, kalibracja
│   └── utils/          # funkcje pomocnicze
├── models/             # wytrenowane modele (ignorowane przez git)
├── reports/            # wykresy i metryki
├── tests/              # testy jednostkowe
├── environment.yml     # definicja środowiska conda
└── README.md           # ten plik

## Autor

Jagoda Budnik - [GitHub](https://github.com/xJadzix)