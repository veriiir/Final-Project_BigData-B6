import itertools, os, io, altair as alt, pandas as pd, s3fs, streamlit as st
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score, mean_absolute_error
import numpy as np

# ── MinIO config ──
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "http://minio:9000")
MINIO_KEY = os.getenv("MINIO_KEY", "minioadmin")
MINIO_SECRET = os.getenv("MINIO_SECRET", "minioadmin")
BUCKET = os.getenv("S3_BUCKET", "fashion-lakehouse")
PARQUET_GLOB = f"{BUCKET}/*/*/*/*/*.parquet"

# ── Data loader (cache 2 m) ──
@st.cache_data(ttl=120, show_spinner="Loading data …")
def load_data():
    fs = s3fs.S3FileSystem(
        key=MINIO_KEY,
        secret=MINIO_SECRET,
        client_kwargs={"endpoint_url": MINIO_ENDPOINT},
    )
    files = fs.glob(PARQUET_GLOB)
    if not files:
        return pd.DataFrame()
    return pd.concat(
        [pd.read_parquet(f"s3://{f}", filesystem=fs) for f in files],
        ignore_index=True,
    )

st.set_page_config("Fashion Dashboard", layout="wide")
st.markdown(
    """
    <style>
      .stApp {padding:1rem;}
      .gallery-img img{border-radius:12px;transition:.3s ease;}
      .gallery-img img:hover{transform:scale(1.05);}
      section[data-testid="stSidebar"]{background:#777B7E;}
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Header row ──
left_head, right_head = st.columns([1, 1])
left_head.title("Fashion Product Dashboard")

df = load_data()

if df.empty:
    st.info("No data found in MinIO bucket.")
    st.stop()

# ── KPI ──
k1, k2, k3 = st.columns(3)
k1.metric("Total SKUs", f"{len(df):,}")
k2.metric("Categories", df["Category"].nunique())
k3.metric("Avg. Rating", f"{df['rating'].mean():.2f}")
st.divider()

# ── Sidebar filters ──
st.sidebar.header("Filter Products")
sel_gender = st.sidebar.multiselect("Gender", sorted(df["Gender"].unique()), default=df["Gender"].unique())
sel_category = st.sidebar.multiselect("Category", sorted(df["Category"].unique()), default=df["Category"].unique())
sel_colour = st.sidebar.multiselect("Colour", sorted(df["Colour"].unique()), default=df["Colour"].unique())
sel_usage = st.sidebar.multiselect("Usage", sorted(df["Usage"].unique()), default=df["Usage"].unique())
search_term = st.sidebar.text_input("Search Product Title")

if st.sidebar.button("Reset Filters"):
    sel_gender = df["Gender"].unique()
    sel_category = df["Category"].unique()
    sel_colour = df["Colour"].unique()
    sel_usage = df["Usage"].unique()
    search_term = ""

mask = (
    df["Gender"].isin(sel_gender)
    & df["Category"].isin(sel_category)
    & df["Colour"].isin(sel_colour)
    & df["Usage"].isin(sel_usage)
)
if search_term:
    mask &= df["ProductTitle"].str.contains(search_term, case=False, na=False)

filt = df[mask]

csv_buf = io.StringIO()
filt.to_csv(csv_buf, index=False)
st.download_button("Download filtered CSV", csv_buf.getvalue(), "filtered_products.csv", "text/csv")

# ── Tabs ──
tab_gallery, tab_top, tab_insight, tab_cat, tab_pred = st.tabs(
    ["Gallery", "Top Sold", "Insights", "Category Sales", "Prediction"]
)

with tab_gallery:
    st.subheader("Product Gallery")
    if filt.empty:
        st.warning("No products match current filters.")
    else:
        cols_count = 5 if st.columns else 3
        cols_cycle = itertools.cycle(st.columns(cols_count))
        for _, row in filt.iterrows():
            with next(cols_cycle):
                st.markdown('<div class="gallery-img">', unsafe_allow_html=True)
                st.image(row["ImageURL"], caption=row.get("ProductTitle"), use_container_width=True)
                st.markdown("</div>", unsafe_allow_html=True)

with tab_top:
    st.subheader("Top 10 Best-Selling Products")
    if "sold_count" not in filt.columns or filt.empty:
        st.info("Sales data unavailable.")
    else:
        top = filt.nlargest(10, "sold_count")[["ProductTitle", "sold_count", "rating"]]
        st.bar_chart(top.set_index("ProductTitle")["sold_count"])
        st.dataframe(top, use_container_width=True)

with tab_insight:
    a, b = st.columns(2)
    dist = filt["Category"].value_counts().reset_index()
    dist.columns = ["Category", "Count"]
    donut = (
        alt.Chart(dist)
        .mark_arc(innerRadius=50)
        .encode(theta="Count", color="Category", tooltip=["Category", "Count"])
    )
    a.altair_chart(donut, use_container_width=True)
    a.caption("Distribution by Category")

    if not filt.empty:
        heat_df = filt.groupby(["Gender", "Category"])["rating"].mean().reset_index()
        heat = (
            alt.Chart(heat_df)
            .mark_rect()
            .encode(
                x="Category:N",
                y="Gender:N",
                color=alt.Color("rating:Q", scale=alt.Scale(scheme="greens")),
                tooltip=["Gender", "Category", alt.Tooltip("rating:Q", format=".2f")],
            )
        )
        b.altair_chart(heat, use_container_width=True)
        b.caption("Average Rating Heat-map")

# ---------- Category Sales ----------
with tab_cat:
    st.subheader("Total sold_count per Category")
    if "sold_count" not in filt.columns:
        st.info("Sales data unavailable.")
    else:
        cat_sum = (
            filt.groupby("Category")["sold_count"]
            .sum()
            .sort_values(ascending=False)
            .reset_index()
        )
        bar = (
            alt.Chart(cat_sum)
            .mark_bar()
            .encode(
                x=alt.X("sold_count:Q", title="Total Sold"),
                y=alt.Y("Category:N", sort="-x"),
                tooltip=["Category", "sold_count"]
            )
        )
        st.altair_chart(bar, use_container_width=True)
        st.dataframe(cat_sum, use_container_width=True)

# ---------- Prediction ----------
with tab_pred:
    st.subheader("Predict Future Sales")

    products = df["ProductTitle"].dropna().unique()
    prod_name = st.selectbox("Choose product", sorted(products))

    prod_row = df[df["ProductTitle"] == prod_name].iloc[0]
    prod_rating = float(prod_row["rating"])
    st.write(f"Current rating: **{prod_rating:.2f}**")

    sold_now = st.number_input(
        "Current sold_count (historical sales)",
        min_value=0, step=1, value=int(prod_row["sold_count"])
    )

    X = df[["rating", "sold_count"]]
    y = df["sold_count"]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    reg = LinearRegression().fit(X_train, y_train)

    if st.button("Predict"):
        pred = reg.predict(np.array([[prod_rating, sold_now]]))[0]
        uplift = pred - sold_now
        st.success(
            f"Estimated future sold_count ≈ **{pred:,.0f}** "
            f"({'+' if uplift>=0 else ''}{uplift:,.0f} vs current)"
        )

    r2 = r2_score(y_test, reg.predict(X_test))
    mae = mean_absolute_error(y_test, reg.predict(X_test))
    m1, m2 = st.columns(2)
    m1.metric("R²", f"{r2:.2f}")
    m2.metric("MAE", f"{mae:,.1f}")

    scat = (
        alt.Chart(df)
        .mark_circle(size=40, opacity=0.3)
        .encode(x="rating:Q", y="sold_count:Q")
    )
    st.altair_chart(scat, use_container_width=True)

st.caption("Built with Streamlit")
