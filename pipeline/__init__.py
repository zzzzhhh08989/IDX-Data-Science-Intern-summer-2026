"""Reusable pipeline behind the weekly notebooks, packaged so the app never rebuilds a prediction
by hand.

    config        paths, column groups, cleaning rules — the single source of truth
    features      Week 6 feature engineering + leakage-safe encoders + the time-based split
    predict       price a single property (used by app.py)

The offline halves of the pipeline — preprocess, train, evaluate, app_defaults — arrive with the
Week 12 handoff; until then those steps live in the notebooks that produced `models/`.
"""
