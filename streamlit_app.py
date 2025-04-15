import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.adsinsights import AdsInsights

# --- CONFIG ---
APP_ID = st.secrets["meta_app_id"]
APP_SECRET = st.secrets["meta_app_secret"]
ACCESS_TOKEN = st.secrets["meta_access_token"]
AD_ACCOUNT_ID = "act_XXXXXXXXXXXX"  # Replace with your account ID

# --- INIT FACEBOOK API ---
FacebookAdsApi.init(APP_ID, APP_SECRET, ACCESS_TOKEN)

# --- HELPERS ---
def get_meta_insights(time_range_days=7):
    today = datetime.now().date()
    since = today - timedelta(days=time_range_days)
    until = today - timedelta(days=1)

    fields = [
        AdsInsights.Field.spend,
        AdsInsights.Field.actions,
        AdsInsights.Field.cpc,
        AdsInsights.Field.cost_per_action_type,
    ]
    params = {
        'time_range': {
            'since': str(since),
            'until': str(until),
        },
        'level': 'account',
    }

    insights = AdAccount(AD_ACCOUNT_ID).get_insights(fields=fields, params=params)
    return insights[0] if insights else {}

# --- PAGE SETUP ---
st.set_page_config(page_title="Little Otter Dashboard", layout="wide")
st.title("Little Otter Weekly Dashboard")
st.caption("Live Meta Ads Insights")

# --- SIDEBAR NOTES ---
st.sidebar.header("📝 Topics to Discuss")
st.sidebar.markdown("""
- Emily OOO → Sam is POC
- March CAC $907 (+20% MoM)
- PA +46%, FL +20%, MN impact
- Budget normalization → better efficiencies
- Net-new state conversions showing promise
""")

# --- METRICS ---
st.subheader("📘 Meta Performance (Last 7 Days)")

data = get_meta_insights()

if data:
    spend = float(data.get("spend", 0))
    cpc = float(data.get("cpc", 0))
    st.metric("Total Spend", f"${spend:,.2f}")
    st.metric("Cost Per Click (CPC)", f"${cpc:,.2f}")

    # Extract actions
    actions = {d['action_type']: int(float(d['value'])) for d in data.get('actions', [])}
    cost_per_action = {d['action_type']: float(d['value']) for d in data.get('cost_per_action_type', [])}

    st.metric("Complete Registrations", actions.get("complete_registration", 0))
    st.metric("Phone Numbers Added", actions.get("add_phone_number", 0))
    st.metric("Kickoffs Scheduled", actions.get("schedule", 0))
    st.metric("Cost per Registration", f"${cost_per_action.get('complete_registration', 0):.2f}")
    st.metric("Cost per Phone Number", f"${cost_per_action.get('add_phone_number', 0):.2f}")
    st.metric("Cost per Kickoff", f"${cost_per_action.get('schedule', 0):.2f}")
else:
    st.warning("No Meta Ads data available for this time period.")

# --- APPENDIX ---
with st.expander("📎 Appendix & Links"):
    st.markdown("""
    - [Meta Creative Dashboard](https://app.adnova.ai/analytics/...)
    - [Looker Studio Report](https://lookerstudio.google.com/...)
    - [Mixpanel Dashboard](https://mixpanel.com/project/...)
    """)
