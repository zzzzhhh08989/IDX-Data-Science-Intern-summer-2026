"""California SFR close-price estimator — Streamlit app (Week 9).

Run from the project root:

    streamlit run app.py

Loads the model bundle trained in `06_advanced_models.ipynb` (Week 7) and the empirical quote
interval measured in `07_evaluation.ipynb` (Week 8), and prices one property at a time.
"""
import json
from datetime import date

import pandas as pd
import streamlit as st

from pipeline import config as C
from pipeline.predict import Predictor

st.set_page_config(page_title="CA Close-Price Estimator", page_icon="🏠", layout="wide")


@st.cache_resource
def load_predictor():
    return Predictor.load()


@st.cache_data
def load_band_accuracy():
    """Week 8's per-price-band accuracy — the reliability panel and the bias warning read this.

    Prefers the freshly evaluated table, so a retrain updates the warnings; falls back to the copy
    shipped in `models/`, because `data/` is git-ignored and a clone without the licensed CRMLS
    extract would otherwise lose the guardrails entirely.
    """
    try:
        return pd.read_csv(C.PROCESSED_DIR / "eval_by_price_band.csv", index_col=0)
    except Exception:
        pass
    try:
        return pd.DataFrame(json.loads(C.EVAL_BY_BAND.read_text())).set_index("band")
    except Exception:
        return None


PRICE_BANDS = [(0, 400e3, "<$400k"), (400e3, 600e3, "$400-600k"), (600e3, 800e3, "$600-800k"),
               (800e3, 1e6, "$800k-1M"), (1e6, 1.5e6, "$1-1.5M"), (1.5e6, 2.5e6, "$1.5-2.5M"),
               (2.5e6, 5e6, "$2.5-5M"), (5e6, float("inf"), ">$5M")]


def band_of(price):
    for lo, hi, label in PRICE_BANDS:
        if lo <= price < hi:
            return label
    return PRICE_BANDS[-1][2]


try:
    predictor = load_predictor()
except FileNotFoundError:
    st.error("No trained model found. Run `06_advanced_models.ipynb` (or `python -m pipeline.train`) "
             "and then `python -m pipeline.app_defaults` first.")
    st.stop()

bundle = predictor.bundle
band_acc = load_band_accuracy()

st.title("🏠 California Single-Family Close-Price Estimator")
st.caption(
    f"**{bundle['model_name']}** trained on CRMLS sold data "
    f"{bundle['train_months'][0]} → {bundle['train_months'][-1]} "
    f"({bundle['train_window_X']} months), held-out test month **{bundle['test_month']}** — "
    f"test R² {bundle['test_metrics']['R2']:.3f}, MAE ${bundle['test_metrics']['MAE']:,.0f}"
)

# ------------------------------------------------------------------ inputs
with st.sidebar:
    st.header("Property")
    living_area = st.number_input("Living area (sqft)", 200, 20_000, 1_800, step=50)
    col_a, col_b = st.columns(2)
    beds = col_a.number_input("Bedrooms", 0, 12, 3)
    baths = col_b.number_input("Bathrooms", 0, 12, 2)
    lot_size = st.number_input("Lot size (sqft)", 0, 871_200, 6_000, step=500)
    year_built = st.number_input("Year built", 1850, date.today().year, 1985)

    with st.expander("Optional details"):
        stories = st.selectbox("Stories", ["(unknown)", 1, 2, 3])
        garage = st.selectbox("Garage spaces", ["(unknown)", 0, 1, 2, 3, 4])

    st.header("Location")
    counties = ["All counties"] + predictor.defaults.get("counties", [])
    county_filter = st.selectbox("Filter districts by county", counties)

    districts = predictor.districts
    if county_filter != "All counties":
        districts = [d for d in districts
                     if predictor.district_info(d).get("county") == county_filter] or districts

    district = st.selectbox("School district", districts,
                            index=districts.index("Palo Alto Unified") if "Palo Alto Unified" in districts else 0,
                            help="School district is the model's strongest location signal — "
                                 "stronger than city or ZIP.")

    st.caption("Blank optional fields are filled with training-set medians and flagged as missing, "
               "exactly as during training.")

info = predictor.district_info(district)

result = predictor.predict(
    living_area=living_area, beds=beds, baths=baths, lot_size=lot_size, year_built=year_built,
    district=district,
    stories=None if stories == "(unknown)" else float(stories),
    garage_spaces=None if garage == "(unknown)" else float(garage),
)
price = result["price"]

# ------------------------------------------------------------------ headline
left, right = st.columns([3, 2])

with left:
    st.subheader("Estimated close price")
    st.markdown(f"# ${price:,.0f}")
    if "lo80" in result:
        st.markdown(
            f"**80% of comparable homes land between "
            f"${result['lo80']:,.0f} and ${result['hi80']:,.0f}**  \n"
            f"50% range: ${result['lo50']:,.0f} – ${result['hi50']:,.0f}"
        )
    st.caption("Quote the range, not the point — the range is measured from this model's own errors "
               "on the held-out test month.")

    m1, m2, m3 = st.columns(3)
    m1.metric("$ / sqft", f"${result['price_per_sqft']:,.0f}")
    if info.get("median_ppsf"):
        delta = result["price_per_sqft"] / info["median_ppsf"] - 1
        m2.metric("District median $/sqft", f"${info['median_ppsf']:,.0f}", f"{delta:+.0%} vs. this home")
    if info.get("median_price"):
        m3.metric("District median sale", f"${info['median_price']:,.0f}")

with right:
    st.subheader("How reliable is this estimate?")
    band = band_of(price)
    if band_acc is not None and band in band_acc.index:
        row = band_acc.loc[band]
        st.metric(f"Typical error in the {band} band", f"{row['MdAPE %']:.1f}%",
                  f"{row['within 10%']:.0f}% of homes priced within 10%", delta_color="off")
        if abs(row["median bias %"]) >= 2:
            direction = "high" if row["median bias %"] > 0 else "low"
            st.warning(f"In this band the model runs **{abs(row['median bias %']):.1f}% {direction}** "
                       f"on average — adjust before quoting.")
        st.caption(f"Measured on {int(row['n']):,} sales in the test month {bundle['test_month']}.")
    else:
        st.info("Run `07_evaluation.ipynb` to show per-price-band accuracy here.")

    if not info.get("in_model", True):
        st.warning(f"**{district}** had fewer than {C.MIN_DISTRICT_N} sales in the training window, so "
                   "the model falls back to statewide medians for it. Treat this estimate as weak.")
    if price > 2.5e6:
        st.warning("Above ~$2.5M the model is biased low — tree models cannot extrapolate past the "
                   "prices they saw in training. Send high-end homes to human review.")

st.divider()

# ------------------------------------------------------------------ details
c1, c2 = st.columns(2)

with c1:
    st.subheader(f"About {district}")
    st.dataframe(pd.DataFrame({
        "value": {
            "County": info.get("county", "—"),
            "Main city": info.get("city", "—"),
            "District type": "Unified (K-12)" if info.get("is_unified") else "Elementary + High",
            "Enrollment": f"{info.get('enroll', 0):,.0f}" if info.get("enroll") else "—",
            "Socio-econ. disadvantaged": f"{info.get('sed_pct', 0):.0f}%" if info.get("sed_pct") else "—",
            "English learners": f"{info.get('el_pct', 0):.0f}%" if info.get("el_pct") else "—",
            "Sales in dataset": f"{info.get('n_sales', 0):,}",
            "Median sale price": f"${info['median_price']:,.0f}" if info.get("median_price") else "—",
        }
    }), width="stretch")

with c2:
    st.subheader("What the model was fed")
    feats = pd.Series(result["features"], name="value").to_frame()
    st.dataframe(feats.style.format("{:,.4g}"), width="stretch", height=320)
    st.caption("`district_price_enc` / `district_ppsf_enc` are the training-window medians for this "
               "district — the two features the model leans on most.")

with st.expander("Model card"):
    st.markdown(f"""
- **Estimator:** {bundle['model_name']} — trained on `log(ClosePrice)`, predictions exponentiated back
- **Training window:** {bundle['train_window_X']} months
  ({bundle['train_months'][0]} → {bundle['train_months'][-1]}), {len(bundle['feature_cols'])} features
- **Held-out test month:** {bundle['test_month']} — R² {bundle['test_metrics']['R2']:.4f},
  RMSE ${bundle['test_metrics']['RMSE']:,.0f}, MAE ${bundle['test_metrics']['MAE']:,.0f}
- **Scope:** `PropertyType = Residential`, `PropertySubType = SingleFamilyResidence`, California (CRMLS)
- **Not modelled:** condition/remodel quality, views, HOA, off-market discounts — the MLS extract has no
  reliable columns for them, which is a floor on how accurate any model here can be
- **Data source:** CRMLS via Trestle/CoreLogic; school districts from the CA Dept. of Education
  (2024-25 boundaries)
""")
