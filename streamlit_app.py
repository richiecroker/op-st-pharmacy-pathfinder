import logging

import pandas as pd
import streamlit as st

from google.cloud import bigquery
from google.oauth2 import service_account


# ============================================================
# CONFIGURATION
# ============================================================

BQ_TABLE = "ebmdatalab.richard.raw_prescribing_pharmacy_pathfinder"
CACHE_TTL = 86400  # 24 hours

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============================================================
# BIGQUERY CONNECTION
# ============================================================
# Authenticate using the service account in Streamlit secrets.

def _bq_client():
    credentials = service_account.Credentials.from_service_account_info(
        st.secrets["gcp_service_account"]
    )

    return bigquery.Client(
        credentials=credentials,
        project="ebmdatalab"
    )


# ============================================================
# LOAD AND CACHE DATA
# ============================================================
# Load the complete table into Pandas.
# Cache for 24 hours to avoid repeated BigQuery queries.

@st.cache_data(ttl=CACHE_TTL)
def get_data() -> pd.DataFrame:

    logger.info("Loading data from BigQuery: %s", BQ_TABLE)

    bq = _bq_client()

    sql = f"""
        SELECT *
        FROM `{BQ_TABLE}`
    """

    df = bq.query(sql).result().to_dataframe()

    logger.info(
        "Loaded %d rows and %d columns",
        len(df),
        len(df.columns)
    )

    return df


# ============================================================
# STREAMLIT PAGE
# ============================================================

st.set_page_config(
    page_title="Pharmacy Pathfinder",
    layout="wide"
)

st.title("Pharmacy Pathfinder")

with st.spinner("Loading prescribing data..."):
    df = get_data()


# ============================================================
# DATA PREVIEW
# ============================================================
# Temporary preview until filters and charts are added.

st.success(f"Loaded {len(df):,} records.")

st.dataframe(
    df.head(20),
    hide_index=True,
    use_container_width=True
)
