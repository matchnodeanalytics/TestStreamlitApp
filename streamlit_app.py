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
AD_ACCOUNT_ID = "act_692989704988816"  # Replace with your account ID

# --- INIT FACEBOOK API ---
FacebookAdsApi.init(APP_ID, APP_SECRET, ACCESS_TOKEN)

# --- HELPERS ---
def get_meta_insights(since, until):
    fields = [
        AdsInsights.Field.cost_per_conversion,
        AdsInsights.Field.spend,
        AdsInsights.Field.actions,
        AdsInsights.Field.action_values,
        AdsInsights.Field.cost_per_action_type,
        AdsInsights.Field.conversions,  # Include this to fetch conversion data
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

# --- SIDEBAR DATE PICKER ---
st.sidebar.markdown("### 📅 Date Range")
preset = st.sidebar.selectbox("Preset", ["Last 7 Days", "Last 14 Days", "Last 30 Days", "Custom"])

if preset == "Last 7 Days":
    start_date = datetime.now().date() - timedelta(days=7)
    end_date = datetime.now().date() - timedelta(days=1)
elif preset == "Last 14 Days":
    start_date = datetime.now().date() - timedelta(days=14)
    end_date = datetime.now().date() - timedelta(days=1)
elif preset == "Last 30 Days":
    start_date = datetime.now().date() - timedelta(days=30)
    end_date = datetime.now().date() - timedelta(days=1)
else:
    start_date = st.sidebar.date_input("Start Date", datetime.now().date() - timedelta(days=7))
    end_date = st.sidebar.date_input("End Date", datetime.now().date() - timedelta(days=1))

prev_start = start_date - timedelta(days=(end_date - start_date).days + 1)
prev_end = start_date - timedelta(days=1)

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
st.subheader("📘 Meta Performance")

cols = st.columns(4)

data = get_meta_insights(start_date, end_date)
data_prev = get_meta_insights(prev_start, prev_end)

if data:
    def pct_change(new, old):
        try:
            new, old = float(new), float(old)
            if old == 0: return "+∞%" if new > 0 else "0.0%"
            change = ((new - old) / old) * 100
            return f"{change:+.1f}%"
        except:
            return "-"

    actions = {d['action_type']: float(d['value']) for d in data.get('actions', [])}
    prev_actions = {d['action_type']: float(d['value']) for d in data_prev.get('actions', [])}
    cost_per_action = {d['action_type']: float(d['value']) for d in data.get('cost_per_action_type', [])}
    conversions = {d['action_type']: float(d['value']) for d in data.get('conversions', [])}
    prev_cost_per_action = {d['action_type']: float(d['value']) for d in data_prev.get('cost_per_action_type', [])}

    cost_per_conversion = {d['action_type']: float(d['value']) for d in data.get('cost_per_conversion', []) if 'value' in d}
    prev_cost_per_conversion = {d['action_type']: float(d['value']) for d in data_prev.get('cost_per_conversion', []) if 'value' in d}
    prev_conversions = {d['action_type']: float(d['value']) for d in data_prev.get('conversions', [])}

    spend = float(data.get("spend", 0))
    prev_spend = float(data_prev.get("spend", 0))

    link_clicks = actions.get("link_click", 0)
    prev_link_clicks = prev_actions.get("link_click", 0)
    cpc = (spend / link_clicks) if link_clicks > 0 else 0
    prev_cpc = (prev_spend / prev_link_clicks) if prev_link_clicks > 0 else 0

    metrics = [
        ("Total Amount Spent", f"${spend:,.2f}", pct_change(spend, prev_spend)),
        ("Complete Registration/Start", conversions.get("offsite_conversion.fb_pixel_custom.META_STEP_1", 0), pct_change(conversions.get("offsite_conversion.fb_pixel_custom.META_STEP_1", 0), prev_conversions.get("offsite_conversion.fb_pixel_custom.META_STEP_1", 0))),
        ("Added Phone Number", conversions.get("offsite_conversion.fb_pixel_custom.SUCCESSFULLY_ADDED_PHONE_NUMBER", 0), pct_change(conversions.get("offsite_conversion.fb_pixel_custom.SUCCESSFULLY_ADDED_PHONE_NUMBER", 0), prev_conversions.get("offsite_conversion.fb_pixel_custom.SUCCESSFULLY_ADDED_PHONE_NUMBER", 0))),
        ("Kickoff Scheduled/Thank You", conversions.get("offsite_conversion.fb_pixel_custom.META_THANK_YOU", 0), pct_change(conversions.get("offsite_conversion.fb_pixel_custom.META_THANK_YOU", 0), prev_conversions.get("offsite_conversion.fb_pixel_custom.META_THANK_YOU", 0))),
        ("Cost per Link Click", f"${cpc:.2f}", pct_change(cpc, prev_cpc)),
        ("Cost per Registration", f"${cost_per_conversion.get('offsite_conversion.fb_pixel_custom.META_STEP_1', 0):.2f}", pct_change(cost_per_conversion.get('offsite_conversion.fb_pixel_custom.META_STEP_1', 0), prev_cost_per_conversion.get('offsite_conversion.fb_pixel_custom.META_STEP_1', 0))),
        ("Cost per Phone Number", f"${cost_per_conversion.get('offsite_conversion.fb_pixel_custom.SUCCESSFULLY_ADDED_PHONE_NUMBER', 0):.2f}", pct_change(cost_per_conversion.get('offsite_conversion.fb_pixel_custom.SUCCESSFULLY_ADDED_PHONE_NUMBER', 0), prev_cost_per_conversion.get('offsite_conversion.fb_pixel_custom.SUCCESSFULLY_ADDED_PHONE_NUMBER', 0))),
        ("Cost per Kickoff", f"${cost_per_conversion.get('offsite_conversion.fb_pixel_custom.META_THANK_YOU', 0):.2f}", pct_change(cost_per_conversion.get('offsite_conversion.fb_pixel_custom.META_THANK_YOU', 0), prev_cost_per_conversion.get('offsite_conversion.fb_pixel_custom.META_THANK_YOU', 0))),
    ]

    for i, (label, value, delta) in enumerate(metrics):
        with cols[i % 4]:
            st.metric(label=label, value=value, delta=delta)
else:
    st.warning("No Meta Ads data available for this time period.")

# --- APPENDIX ---
with st.expander("📎 Appendix & Links"):
    st.markdown("""
    - [Meta Creative Dashboard](https://app.adnova.ai/analytics/...)
    - [Looker Studio Report](https://lookerstudio.google.com/...)
    - [Mixpanel Dashboard](https://mixpanel.com/project/...)
    """)
