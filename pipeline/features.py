"""Feature engineering + leakage-safe encoders.

Mirrors `05_feature_engineering.ipynb` (Week 6) and the split logic from `02_preprocessing.ipynb`
(Week 3). Every encoder is *fit* on training rows only and *applied* to anything else.
"""
import numpy as np
import pandas as pd

from . import config as C


# --------------------------------------------------------------------------------------------
# property-level engineered features (Week 6)
# --------------------------------------------------------------------------------------------
def add_engineered_features(df, as_of_year=None, as_of_month=None):
    """Add the Week 6 property-level features in place-safe fashion (returns a new frame).

    `as_of_year` / `as_of_month` let a live query be priced "as of" today instead of a close date:
    for training rows they come from `CloseDate`, for a Streamlit query from the current date.
    """
    d = df.copy()

    d["bed_bath_ratio"] = d["BedroomsTotal"] / d["BathroomsTotalInteger"].replace(0, np.nan)
    d["living_area_per_bed"] = d["LivingArea"] / d["BedroomsTotal"].replace(0, np.nan)
    d["lot_to_living_ratio"] = d["LotSizeSquareFeet"] / d["LivingArea"].replace(0, np.nan)
    d["total_rooms"] = d["BedroomsTotal"] + d["BathroomsTotalInteger"]

    year = d["CloseDate"].dt.year if as_of_year is None else as_of_year
    month = d["CloseDate"].dt.month if as_of_month is None else as_of_month

    d["property_age"] = (year - d["YearBuilt"]).clip(lower=0)
    d["is_new_build"] = (d["property_age"] <= 1).astype(int)
    d["has_garage"] = (d["GarageSpaces"].fillna(0) > 0).astype(int)
    d["has_fireplace"] = (d["FireplacesTotal"].fillna(0) > 0).astype(int)
    d["close_month_sin"] = np.sin(2 * np.pi * month / 12)
    d["close_month_cos"] = np.cos(2 * np.pi * month / 12)
    return d


# --------------------------------------------------------------------------------------------
# encoders — fit on train, apply anywhere
# --------------------------------------------------------------------------------------------
def fit_encoders(train, numeric, categorical=None):
    """Learn medians, frequency maps and district price encodings from training rows only."""
    categorical = C.CATEGORICAL if categorical is None else categorical

    enc = {"medians": train[numeric].median().to_dict(),
           "freq": {c: train[c].value_counts(normalize=True).to_dict() for c in categorical}}

    ppsf = train[C.TARGET] / train["LivingArea"].replace(0, np.nan)
    stats = (pd.DataFrame({"district": train["SchoolDistrict"], "ppsf": ppsf, "price": train[C.TARGET]})
             .groupby("district")
             .agg(n=("price", "size"), ppsf=("ppsf", "median"), price=("price", "median")))
    stats = stats[stats["n"] >= C.MIN_DISTRICT_N]

    enc["district_ppsf"] = stats["ppsf"].to_dict()
    enc["district_price"] = stats["price"].to_dict()
    enc["global_ppsf"] = float(ppsf.median())
    enc["global_price"] = float(train[C.TARGET].median())
    return enc


def apply_encoders(frame, enc, feature_cols, numeric, categorical=None):
    """Build the model matrix for `frame` using already-fitted encoders."""
    categorical = C.CATEGORICAL if categorical is None else categorical

    out = frame.copy()
    out[numeric] = out[numeric].fillna(pd.Series(enc["medians"])).fillna(0.0)
    for c in categorical:
        out[f"{c}_freq"] = out[c].map(enc["freq"][c]).fillna(0.0)
    out["district_ppsf_enc"] = out["SchoolDistrict"].map(enc["district_ppsf"]).fillna(enc["global_ppsf"])
    out["district_price_enc"] = out["SchoolDistrict"].map(enc["district_price"]).fillna(enc["global_price"])
    return out[feature_cols]


def feature_columns(numeric, categorical=None):
    categorical = C.CATEGORICAL if categorical is None else categorical
    return numeric + [f"{c}_freq" for c in categorical] + C.SCHOOL_ENCODED


# --------------------------------------------------------------------------------------------
# time-based split
# --------------------------------------------------------------------------------------------
def build_split(d, X=C.DEFAULT_TRAIN_WINDOW, val_months=0):
    """test = most recent month; train = the X months before it.

    The last `val_months` of the training window are also returned separately, for early stopping
    and hyperparameter selection — the test month is never involved in either.
    """
    if "month_key" not in d.columns:
        d = d.assign(month_key=d["CloseDate"].dt.to_period("M"))

    months = sorted(d["month_key"].dropna().unique())
    test_month, train_months = months[-1], months[-(X + 1):-1]
    if len(train_months) < X:
        raise ValueError(f"Only {len(months) - 1} months before the test month; X={X} is too large.")

    numeric = C.numeric_features(d.columns)
    feat_cols = feature_columns(numeric)

    train_all = d[d.month_key.isin(train_months)]
    test = d[d.month_key == test_month]

    enc = fit_encoders(train_all, numeric)
    out = {
        "enc": enc, "feature_cols": feat_cols, "numeric": numeric, "categorical": C.CATEGORICAL,
        "X_train": apply_encoders(train_all, enc, feat_cols, numeric), "y_train": train_all[C.TARGET],
        "X_test": apply_encoders(test, enc, feat_cols, numeric), "y_test": test[C.TARGET],
        "test_month": str(test_month), "train_months": [str(m) for m in train_months],
        "train_rows": len(train_all), "test_rows": len(test),
    }

    if val_months:
        fit_months, v_months = train_months[:-val_months], train_months[-val_months:]
        sub, val = d[d.month_key.isin(fit_months)], d[d.month_key.isin(v_months)]
        enc_sub = fit_encoders(sub, numeric)
        out.update({
            "X_fit": apply_encoders(sub, enc_sub, feat_cols, numeric), "y_fit": sub[C.TARGET],
            "X_val": apply_encoders(val, enc_sub, feat_cols, numeric), "y_val": val[C.TARGET],
            "val_months": [str(m) for m in v_months],
        })
    return out
