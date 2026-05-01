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

Project complete.

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
- Hyperparameter tuning experiments for LightGBM
  - Experiment 1: lower learning_rate (0.05) - marginal improvement, AUC 0.7472
  - Experiment 2: larger trees (num_leaves=127) - slightly worse than default
  - Experiment 3: aggressive tuning (low LR + larger trees + stronger regularization) - marginal improvement, AUC 0.7469
  - Conclusion: default LightGBM parameters were close to optimal for this dataset, model from experiment 1 will be treated as final
- Model persistence
  - All trained models saved to disk (LightGBM as .txt, sklearn models as .pkl via joblib)
  - Encoders also saved (OneHotEncoder for logistic regression, OrdinalEncoder for LightGBM)
- DART boosting experiment
  - Alternative gradient boosting type with dropout mechanism
  - Trained for 205 minutes vs 21 min for GBDT
  - Result: AUC 0.7442 (worse than GBDT 0.7466) and log loss 0.3907 (worse than 0.3889)
  - Conclusion: DART not suitable for this problem - significantly slower with worse results
- Probability calibration
  - Split validation set into calibration set (4M rows) and new validation set (4M rows)
  - Tested two methods: Platt scaling and isotonic regression
  - Platt scaling worsened results (ECE 0.0224 vs 0.0045 uncalibrated, log loss 0.3935)
  - Isotonic regression improved calibration significantly (ECE 0.0007, 6x better than uncalibrated)
  - Final pipeline: ordinal_encoder + lightgbm_final + isotonic_calibrator saved to disk
- A/B test simulation comparing logistic regression and calibrated LightGBM
  - Used 4M unbiased rows (not seen by either model during training/calibration)
  - Top-K analysis at multiple thresholds (1%, 5%, 10%, 20%, 50%)
  - LightGBM achieved +6.82% relative lift in click rate at top 5% threshold
  - Statistical significance: Z-statistic 20.14, P-value < 10^-80
  - 95% CI for relative lift: [6.16%, 7.48%]
  - Power analysis: sample size 51.7x larger than required for 80% power
  - Cohen's h effect size: 0.0635 (small, but significant in RTB context)
- Production-ready serving with FastAPI and Docker
  - REST API with endpoints: /health, /info, /predict
  - Pydantic validation for request/response schemas
  - Loads model, encoder, and calibrator at startup
  - Containerized with Docker (Python 3.11-slim base + libgomp1 for LightGBM)
- CI/CD pipeline with GitHub Actions
  - Automated Docker build on every push to main
  - Container startup verification
  - Endpoint testing (health and predict)
- Real-time streaming pipeline with Apache Kafka
  - Kafka broker running in KRaft mode via Docker
  - Producer reads ad impressions from val_split.parquet and publishes to ad-impressions topic
  - Consumer subscribes to topic and loads model components (model, ordinal encoder and isotonic calibrator) at startup
  - Real-time CTR predictions with raw and calibrated values
  - Complete pipeline: data --> Kafka --> ML predictions


## Repository Structure

```
ctr-prediction/
├── .github/
│   └── workflows/ # GitHub Actions CI/CD
├── data/ # datasets (git-ignored)
├── notebooks/ # Jupyter notebooks for EDA, training, and experiments
├── models/ # trained models (git-ignored, except production models)
├── serving/ # FastAPI application and Docker configuration
│   ├── app.py
│   ├── Dockerfile
│   └── requirements.txt
├── streaming/ # Kafka streaming pipeline
│   ├── docker-compose.yml
│   ├── producer.py
│   └── consumer.py
├── environment.yml # conda environment definition
└── README.md # this file
```

## Author

Jagoda Budnik - [GitHub](https://github.com/xJadzix)
