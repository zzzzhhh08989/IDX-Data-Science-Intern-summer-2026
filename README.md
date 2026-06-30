# IDX Data Science Intern

Data science work on California real estate market data (CRMLS / MLS) for IDX Exchange.
The project pulls property data from the Trestle / CoreLogic API, cleans and combines
multiple months of **listing** and **sold** records, and explores market trends to
support competitive and market analysis.

## Repository layout

```
.
├── 01_exploration.ipynb      # Main exploration notebook (load, clean, explore sold data)
├── scripts/                  # Data pull & analysis scripts
│   ├── 1. analysis_sold.py   # Combine monthly sold CSVs, clean, analyze
│   ├── 2. crmls_listed.py    # Pull listing data from the Trestle/CoreLogic API
│   └── 3. analysis_listed.py # Combine monthly listing CSVs, clean, analyze
├── resources/                # Reference material
│   ├── Trestle Property MetaData.pdf
│   └── ml templates/         # Regression model notebooks (linear, ridge, lasso,
│                             #   random forest, XGBoost, neural net, SVR, KNN, etc.)
├── data/                     # Licensed CRMLS data (not tracked — see .gitignore)
│   ├── listing/              # CRMLSListing<YYYYMM>.csv
│   └── sold/                 # CRMLSSold<YYYYMM>.csv
└── analysis/                 # Tableau workbooks (not tracked — large files)
```

## Workflow

1. **Pull** the latest monthly data from the Trestle/CoreLogic API
   (`scripts/2. crmls_listed.py`) or from the hosting `flaskapi/raw` folder.
2. **Combine & clean** the monthly CSVs into a single dataframe
   (`scripts/1. analysis_sold.py`, `scripts/3. analysis_listed.py`):
   concatenate months, handle differing schemas across `_filled` vs. raw files,
   and check for missing latitude/longitude.
3. **Explore** distributions and market trends in `01_exploration.ipynb`
   (filtered to single-family residential properties).
4. **Visualize** market and competitive analysis in the Tableau workbooks under `analysis/`.

## Notes on data

- Source data is **licensed CRMLS/MLS data** and is **not committed** to this repo.
  CSV files, Tableau workbooks (`.twbx`), and large PDFs are excluded via `.gitignore`.
- `_filled` months have latitude/longitude filled by geocoding; starting Aug 2024 the
  filling is done upstream at the hosting site, so newer files have a different column
  set. Take the **common columns before concatenating** to avoid all-NaN columns.

## Tech

Python (pandas, numpy, matplotlib), Jupyter, Tableau, Trestle/CoreLogic API.
