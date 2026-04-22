# CTR Prediction - Real-Time Bidding

A click-through rate (CTR) prediction pipeline for Real-Time Bidding (RTB) advertising systems.

## Context

In programmatic advertising, each ad impression is auctioned in real time (~100 ms). A key decision component is CTR prediction - the probability that a user will click on an ad for a given bid request. The quality of this prediction directly determines how much an advertiser should bid in the auction, which translates into campaign ROI.

## Project Goal

Building a complete CTR prediction pipeline with emphasis on aspects that matter in production RTB systems:

- Handling high-cardinality categorical features
- Chronological validation (instead of random splits)
- Probability calibration (not just ranking quality)
- Serving predictions in a streaming architecture

## Dataset

Avazu Click-Through Rate Prediction - a publicly available dataset from a mobile ad network, containing ~40M bid requests from 10 days (October 21-30, 2014).

Source: https://www.kaggle.com/c/avazu-ctr-prediction/data

## Tech Stack

- Python 3.11
- PySpark (large-scale data aggregation)
- scikit-learn, LightGBM (modeling)
- Pandas, NumPy (data processing)
- Docker, GitHub Actions (deployment and CI/CD)
- Apache Kafka (streaming simulation)

## Status

Work in progress. Current phase: exploratory data analysis completed.

### Completed

- Project setup with conda environment, Git, and SSH authentication
- Data loading and schema verification (Avazu, 40M rows, 24 columns)
- Exploratory data analysis
    - Baseline CTR, temporal patterns, column cardinalities
    - Placeholder identification (app vs site traffic split)
    - Predictive power assessment of features (banner position, device type, connection type, anonymized C columns)
    - Correlation analysis of suspected duplicate features
- Data conversion to Parquet format for faster iteration
- Chronological train/validation split (days 21-28 vs 29-30)

### Next steps
- Feature engineering (time features, traffic type flag, categorical encoding)
- Baseline logistic regression model
- LightGBM with native categorical handling
- Deployment setup (Docker, CI/CD)
- Real-time serving simulation with Kafka

## Repository Structure

ctr-prediction/
|-- data/               # datasets (git-ignored)
|-- notebooks/          # Jupyter notebooks for EDA and experiments
|-- src/                # Python modules
|   |-- data/           # data loading and preprocessing
|   |-- features/       # feature engineering
|   |-- models/         # training, evaluation, calibration
|   `-- utils/          # helper functions
|-- models/             # trained models (git-ignored)
|-- reports/            # figures and metrics
|-- tests/              # unit tests
|-- environment.yml     # conda environment definition
`-- README.md           # this file

## Author

Jagoda Budnik - [GitHub](https://github.com/xJadzix)
