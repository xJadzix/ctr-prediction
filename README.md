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

Work in progress. Current phase: baseline model complete, moving to LightGBM.

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
- Feature engineering
  - Temporal features (hour of day, day of week, is_weekend)
  - Traffic type flag (is_app)
  - Removal of non-generalizing columns (id, hour, day)
- Categorical encoding
  - One-hot encoding for low-to-medium cardinality features (23 columns)
  - Feature hashing for device_id and device_ip (10000 buckets each)
- Baseline logistic regression (SGDClassifier with log_loss)
  - Trained on full 32M rows, 51549 features
  - Log loss: 0.3970 (baseline 0.4452, 10.8% reduction)
  - AUC: 0.7321
  - Model calibration within 2 percentage points across probability bins
- LightGBM model with native categorical handling
  - Ordinal encoding of categorical columns (avoids memory issues with pandas category)
  - 21 categorical features + 2 boolean features (device_id, device_ip excluded due to high cardinality)
  - Trained on full 32M rows, stopped after 211 iterations via early stopping
  - Log loss: 0.3889 (2% improvement over logistic regression baseline)
  - AUC: 0.7466 (vs 0.7321 for logistic regression)
  - Better calibration than logistic regression without post-processing

### Next steps

- Probability calibration
- A/B test simulation and statistical power analysis
- Deployment setup (Docker, CI/CD)
- Real-time serving simulation with Kafka

## Repository Structure

'''
ctr-prediction/
├── data/ # datasets (git-ignored)
├── notebooks/ # Jupyter notebooks for EDA and experiments
├── src/ # Python modules
│ ├── data/ # data loading and preprocessing
│ ├── features/ # feature engineering
│ ├── models/ # training, evaluation, calibration
│ └── utils/ # helper functions
├── models/ # trained models (git-ignored)
├── reports/ # figures and metrics
├── tests/ # unit tests
├── environment.yml # conda environment definition
└── README.md # this file
'''

## Author

Jagoda Budnik - [GitHub](https://github.com/xJadzix)
