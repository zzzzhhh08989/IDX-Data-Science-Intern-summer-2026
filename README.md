# California Property Close-Price Prediction — IDX Data Science Intern

Predict the **close price** (final sale price) of any single-family residential property in California
from its characteristics, using historical CRMLS sold data pulled from the Trestle / CoreLogic API.

Shipped model: **XGBoost on `log(ClosePrice)`**, trained on a rolling 24-month window.

| Metric on the held-out test month (2026-05, 11,976 sales) | Value |
|---|---|
| **MdAPE** (median absolute % error) | **7.78 %** |
| Homes priced within 10 % / 20 % of the true price | **59.8 % / 84.5 %** |
| MAE | **\$176,423** |
| R² | **0.779** |
| Median bias | −0.9 % (essentially unbiased) |
| Agent rule of thumb (district median \$/sqft × sqft), same month | MdAPE 15.8 % |

The model roughly **halves** the error of the back-of-the-envelope calculation it has to beat.

---

## Repository layout

```
.
├── 01_exploration.ipynb          Week 2  EDA on the sold data
├── 02_preprocessing.ipynb        Week 3  cleaning, encoding, the time-based split
├── 03_baseline_model.ipynb       Week 4  linear regression baseline + training-window sweep
├── 04_model_comparison.ipynb     Week 5  decision tree & random forest vs. baseline
├── 05_feature_engineering.ipynb  Week 6  engineered features + school-district spatial join
├── 06_advanced_models.ipynb      Week 7  XGBoost / LightGBM, tuning, log-target, final model
├── 07_evaluation.ipynb           Week 8  MAPE / MdAPE, segment breakdowns, quote intervals
│
├── app.py                        Week 9  Streamlit pricing app
├── pipeline/                     shared feature and prediction code
│   ├── config.py                   paths, feature groups, and cleaning rules
│   ├── features.py                 feature engineering + leakage-safe encoders
│   └── predict.py                  price one property (used by app.py)
│
├── models/                       committed model artifacts
│   ├── best_model.joblib           estimator + train-only encoders + metadata (6 MB)
│   ├── quote_interval.json         empirical quote multipliers from Week 8
│   └── app_defaults.json           per-district defaults for the app (556 districts)
│
├── scripts/                      original data-pull / Tableau-prep scripts (Weeks 1-2)
├── resources/                    Trestle metadata PDF, ML template notebooks
├── data/                         licensed CRMLS data — NOT in git (see .gitignore)
│   ├── sold/                       CRMLSSold<YYYYMM>.csv monthly extracts
│   ├── listing/                    CRMLSListing<YYYYMM>.csv (used for market analysis, not the model)
│   ├── external/                   CA school district boundaries (auto-downloaded)
│   └── processed/                  sold_clean.csv, sold_features.csv, metric tables
└── analysis/                     Tableau workbooks — NOT in git (too large)
```

---

## Quickstart

### 1. Environment

```bash
uv venv .venv --python 3.12                     # or: python3 -m venv .venv
uv pip install --python .venv/bin/python \
    pandas numpy scikit-learn matplotlib xgboost lightgbm \
    geopandas shapely pyogrio joblib streamlit jupyterlab ipykernel
brew install libomp                             # macOS only — XGBoost/LightGBM need OpenMP
.venv/bin/python -m ipykernel install --user --name idx-ds --display-name "Python 3 (IDX venv)"
```

The notebooks are saved against the **`Python 3 (IDX venv)`** kernel.

### 2. Data

Licensed CRMLS data is not in the repo. Pull it with FileZilla (see `Data Science v.4.pdf`):

- Host `199.250.207.194`, user `data@idxexchange.com`, port 21, folder `raw/California`
- Copy at least 6 months of `CRMLSSold*.csv` into `data/sold/`
- Do **not** modify anything in the remote `raw/` folder

The school-district boundaries download themselves on first run
([CA School District Areas 2024-25](https://data.ca.gov/dataset/california-school-district-areas-2024-25)).

### 3. Reproduce the analysis

```bash
.venv/bin/jupyter lab
```

Run the notebooks in numerical order from `01_exploration.ipynb` through `07_evaluation.ipynb`.
Together they load and clean the raw files, build the time-based split, compare models, engineer the
school-district features, train the final model, and reproduce the evaluation tables.

### 4. Run the prediction app

```bash
.venv/bin/python -m pipeline.predict     # smoke-test the saved model
.venv/bin/streamlit run app.py           # open http://localhost:8501
```

The committed model bundle includes its training-only encoders, so the app runs without rebuilding the
licensed dataset first.

---

## Method

### Data

- **Scope:** `PropertyType = Residential`, `PropertySubType = SingleFamilyResidence` (per the task doc)
- **Volume:** 319,311 sales across 29 months (2024-01 → 2026-05) after cleaning
- Monthly files are concatenated on their **common columns** — schemas differ between the geocoded
  `_filled` months and the newer raw ones, and taking the intersection is what stops whole columns from
  arriving all-NaN

### Cleaning (Week 3)

Domain rules remove non-market transactions (\$1 intra-family transfers) and impossible values:
price outside \$10k-\$50M, living area outside 200-20,000 sqft, beds/baths outside 0-12, lot > 20 acres,
`YearBuilt` outside 1850-2026. Rows with no `ClosePrice` are dropped; numeric gaps are median-imputed
**from the training months only**, with `*_missing` flags where the null rate exceeds 2 %.

### Target leakage — what is deliberately excluded

`ListPrice`, `OriginalListPrice`, `DaysOnMarket` and anything else only knowable *after* a listing goes
live are **not** features. The task is to price a property that may not be for sale at all, so a model
that leans on list price would be useless in production (and would score misleadingly well offline).

### Features (34 built in Week 6 → **31 shipped**, after Week 7 dropped the three dead fireplace columns)

| Group | Features |
|---|---|
| Physical | living area, beds, baths, lot size, year built, garage spaces, stories |
| Location (raw) | latitude, longitude |
| Location (encoded) | county, city, ZIP, school district, high-school district — frequency-encoded |
| **School district layer** | district median \$/sqft & median price (train-only), enrollment, socio-economically disadvantaged %, English-learner %, unified vs. elementary+high |
| Engineered | bed/bath ratio, sqft per bedroom, lot-to-living ratio, total rooms, property age, is-new-build, has-garage, cyclical close month |

The **school-district layer** is the biggest single win in the project. Each property's coordinates are
spatially joined (`geopandas.sjoin`, point-in-polygon) to the CA Dept. of Education 2024-25 district
boundaries. CA districts overlap by design — a location is served either by one Unified (K-12) district
or by an Elementary + High *pair* — so the join is resolved into a K-8 authority and a 9-12 authority.
District median \$/sqft spans **10×** across the state (\$190 → \$1,919), which is exactly the signal
`City` and `PostalCode` were failing to capture.

### Validation protocol

Everything is **time-based**, never random:

- **test** = the most recent complete month
- **train** = the `X` months immediately before it (`X` is tuned, not fixed)
- **validation** = the last month *inside* the training window, used for early stopping and
  hyperparameter selection — so the test month influences no decision
- medians, frequency encodings, district price encodings and the scaler are fit on **training rows only**

A random split would leak future sales into the past and inflate every number reported here.

---

## Results

Test month 2026-05 throughout; `X` is the training-window length in months.

| Week | Model | Features | X | Test R² | MAE |
|---|---|---|---|---|---|
| 4 | Linear Regression | base (16) | 13 | 0.460 | \$512,873 |
| 5 | Decision Tree | base | 13 | 0.632 | \$317,811 |
| 5 | Random Forest | base | 13 | 0.738 | \$205,264 |
| 6 | Linear Regression | **+ engineered + school district (34)** | 13 | 0.630 | \$363,988 |
| 6 | Random Forest | + engineered + school district | 13 | 0.747 | \$198,313 |
| 7 | XGBoost (tuned) | 31 (dead columns dropped) | 13 | 0.755 | \$193,892 |
| 7 | LightGBM (tuned) | 31 | 13 | 0.750 | \$198,322 |
| **7** | **XGBoost, log target** | **31** | **24** | **0.779** | **\$176,423** |

Two findings worth keeping in mind:

1. **Features beat algorithms.** Adding the school-district layer moved linear regression from 0.46 to
   0.63 — a bigger jump than every model upgrade afterwards combined.
2. **Modelling `log(price)` matters more than tuning did.** Squared error on the raw scale spends the
   model's capacity on a handful of multi-million-dollar sales; on the log scale it optimises *relative*
   error, which is what the business actually cares about (MdAPE 8.4 % → 7.8 %, MAE −\$11k).

### Where the model is reliable (Week 8)

| Price band | MdAPE | Within 10 % | Median bias |
|---|---|---|---|
| < \$400k | 10.9 % | 47 % | +3.9 % |
| \$400-600k | **6.0 %** | 69 % | +0.4 % |
| \$600-800k | 6.1 % | 69 % | −0.1 % |
| \$800k-1M | 6.3 % | 69 % | −0.2 % |
| \$1-1.5M | 8.3 % | 58 % | −1.6 % |
| \$1.5-2.5M | 9.6 % | 52 % | −2.8 % |
| \$2.5-5M | 12.3 % | 42 % | −7.5 % |
| > \$5M | 20.7 % | 26 % | **−16.7 %** |

- **Sweet spot:** \$400k-1M mid-market homes, 20-40 years old, in Elementary+High districts.
- **Weak spots:** the top of the market (trees cannot extrapolate above prices they saw in training, so
  they are systematically low), homes under \$400k, and homes over 5,000 sqft (MdAPE 17 %).
- **Best districts:** Romoland Elementary 2.3 %, Antioch Unified 3.4 %, Etiwanda Elementary 3.6 %.
  **Worst:** Berkeley Unified 16.7 %, Oakland Unified 15.5 % — internally heterogeneous districts where
  a single district-level price signal cannot separate neighbourhoods.
- **Deployment guardrail:** quote the **range**, not the point. From the model's own test-month errors,
  80 % of homes land within ×0.84 – ×1.19 of the prediction; the app shows this by default and flags
  homes above \$2.5M for human review.

---

## Limitations

- **No condition or quality signal.** The MLS extract has no reliable remodel/condition/view columns, so
  two identical-on-paper homes — one renovated, one not — get the same prediction. This is the hard floor
  on accuracy here, and the main reason the luxury tier is unreliable.
- **`FireplacesTotal` is 100 % null** in this extract; it and its derived features were dropped in Week 7
  (confirmed at exactly 0.0000 importance in Week 6). If fireplace data matters, it must be re-pulled.
- **`district_price_enc` carries 64 % of total model importance.** That is a *target-derived* feature: it
  is safe here because it is fit on training months only, but it means the model is largely "the district
  median, adjusted for the house". Districts with < 20 training sales fall back to statewide medians and
  the app marks those estimates as weak.
- **One test month.** All numbers come from 2026-05. Re-running across several test months (rolling-origin
  evaluation) is the next validation step.
- **No geographic granularity below the district.** Census tract or block-group features would likely
  fix the Oakland/Berkeley failure mode.

## Next steps

1. Rolling-origin evaluation across the last 6 test months, to get error bars on every number above.
2. A second geographic layer (census tract) to split heterogeneous districts.
3. A dedicated model or a widened quote range for the > \$2.5M tier.
4. Automate the monthly Trestle pull → retrain → deploy loop.

---

## Deliverables completed through Week 10

| Week | Deliverable in the plan | File in this repo |
|---|---|---|
| 1 | Dataset access + column notes | FTP access confirmed; `resources/Trestle Property MetaData.pdf` |
| 2 | `01_exploration.ipynb` | [01_exploration.ipynb](01_exploration.ipynb) |
| 3 | `02_preprocessing.ipynb` + cleaned CSV | [02_preprocessing.ipynb](02_preprocessing.ipynb), `data/processed/sold_clean.csv` |
| 4 | `03_baseline_model.ipynb` | [03_baseline_model.ipynb](03_baseline_model.ipynb) |
| 5 | `04_model_comparison.ipynb` | [04_model_comparison.ipynb](04_model_comparison.ipynb) |
| 6 | Updated notebook + old-vs-new feature table | [05_feature_engineering.ipynb](05_feature_engineering.ipynb), `data/processed/feature_set_comparison.csv` |
| 7 | Advanced models notebook + test metrics | [06_advanced_models.ipynb](06_advanced_models.ipynb), `data/processed/advanced_model_results.csv` |
| 8 | Evaluation notebook + `metrics_summary.csv` | [07_evaluation.ipynb](07_evaluation.ipynb), `data/processed/metrics_summary.csv` |
| 9 | `app.py` (Streamlit) | [app.py](app.py) |
| 10 | README | this file |

> Notebook numbering runs one ahead of the plan's suggested filenames from Week 6 on: the plan assumed
> Week 6 would edit an existing notebook, but feature engineering earned its own (`05_…`), which shifts
> advanced models to `06_…` and evaluation to `07_…`. The deliverable contents are unchanged.

## Tech

Python 3.12 · pandas · scikit-learn · XGBoost · LightGBM · GeoPandas · Streamlit · Jupyter · Tableau ·
Trestle/CoreLogic API
