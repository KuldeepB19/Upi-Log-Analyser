"""
UPI LOG ANALYZER — Rewritten
Clean, modern, professional Streamlit dashboard
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random
import warnings
warnings.filterwarnings('ignore')

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="UPI Log Analyzer",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Theme & CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:wght@300;400;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'IBM Plex Sans', sans-serif;
}

/* Hide default Streamlit elements */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 1.5rem 2rem; max-width: 1400px; }

/* Color variables via root-level CSS */
:root {
    --bg:        #0a0e1a;
    --surface:   #111827;
    --surface2:  #1a2235;
    --border:    #1e2d45;
    --accent:    #3b82f6;
    --accent2:   #06b6d4;
    --danger:    #ef4444;
    --warning:   #f59e0b;
    --success:   #10b981;
    --text:      #e2e8f0;
    --muted:     #64748b;
}

/* KPI Cards */
.kpi {
    background: #111827;
    border: 1px solid #1e2d45;
    border-radius: 10px;
    padding: 20px 22px;
    border-top: 3px solid;
    margin-bottom: 6px;
}
.kpi-val  { font-family:'IBM Plex Mono',monospace; font-size:2rem; font-weight:600; margin:0; }
.kpi-lbl  { font-size:0.78rem; color:#64748b; text-transform:uppercase; letter-spacing:.08em; margin:0; }

/* Alert cards */
.alert {
    border-radius: 8px;
    padding: 14px 18px;
    margin: 6px 0;
    border-left: 3px solid;
    font-size: 0.9rem;
}
.alert-critical { background:#1f0f0f; border-color:#ef4444; color:#fca5a5; }
.alert-warning  { background:#1f1700; border-color:#f59e0b; color:#fcd34d; }
.alert-ok       { background:#0f1f14; border-color:#10b981; color:#6ee7b7; }

/* Section headers */
.sec-title {
    font-size:0.75rem; font-weight:600; text-transform:uppercase;
    letter-spacing:.12em; color:#64748b;
    border-bottom:1px solid #1e2d45; padding-bottom:8px; margin-bottom:16px;
}

/* Anomaly items */
.anomaly-item {
    background:#111827; border:1px solid #1e2d45; border-radius:8px;
    padding:12px 16px; margin:6px 0;
    display:flex; justify-content:space-between; align-items:center;
}
.badge {
    font-family:'IBM Plex Mono',monospace; font-size:0.7rem;
    padding:3px 8px; border-radius:4px; font-weight:600;
}
.badge-red    { background:#1f0f0f; color:#ef4444; border:1px solid #ef4444; }
.badge-yellow { background:#1f1700; color:#f59e0b; border:1px solid #f59e0b; }
.badge-green  { background:#0f1f14; color:#10b981; border:1px solid #10b981; }
</style>
""", unsafe_allow_html=True)

# ── Chart defaults ─────────────────────────────────────────────────────────────
CHART_DEFAULTS = dict(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font_color='#94a3b8',
    font_family='IBM Plex Sans',
    margin=dict(t=30, b=20, l=10, r=10),
)
GRID = dict(gridcolor='#1e2d45', zerolinecolor='#1e2d45')

# ── Data generation ────────────────────────────────────────────────────────────
def _ts(n, base, hours=24):
    out = []
    for _ in range(n):
        out.append((base + timedelta(seconds=random.randint(0, hours * 3600)))
                   .strftime('%Y-%m-%d %H:%M:%S'))
    return out

def _ip():
    return f"{random.randint(1,255)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,255)}"

@st.cache_data(show_spinner=False)
def generate_data():
    np.random.seed(42); random.seed(42)
    base = datetime(2026, 2, 1)
    users  = [f"USR{str(i).zfill(4)}" for i in range(1, 301)]
    sus    = [f"SUS{str(i).zfill(4)}" for i in range(1, 51)]
    norm_ips = [_ip() for _ in range(200)]
    sus_ips  = [_ip() for _ in range(30)]
    browsers = ['Chrome', 'Firefox', 'Safari', 'Edge', 'Mobile App']
    services = ['UPI Transfer', 'Bill Payment', 'Mobile Recharge', 'DTH Recharge',
                'Money Request', 'QR Payment', 'Merchant Payment', 'International Transfer']
    banks    = ['SBI', 'HDFC', 'ICICI', 'Axis', 'Kotak', 'PNB', 'BOB']
    plans    = ['Basic', 'Premium', 'Gold', 'Enterprise']
    reasons  = ['Invalid Credentials', 'Expired Token', 'Missing Auth Header',
                'Brute Force Detected', 'Account Locked', 'Invalid OTP']

    # Login logs
    rows = []
    for _ in range(500):
        legit = random.random() < 0.85
        rows.append({
            'timestamp'    : (_ts(1, base)[0]),
            'user_id'      : random.choice(users if legit else sus),
            'ip_address'   : random.choice(norm_ips if legit else sus_ips),
            'login_status' : np.random.choice(['success','failed'], p=[0.95,0.05] if legit else [0.30,0.70]),
            'browser'      : random.choice(browsers),
        })
    df_login = pd.DataFrame(rows).sort_values('timestamp').reset_index(drop=True)

    # Session logs
    rows = []
    for i in range(500):
        start = base + timedelta(seconds=random.randint(0, 24*3600))
        legit = random.random() < 0.80
        dur   = random.randint(5, 60) if legit else (
                random.randint(1, 3) if random.random() < .5 else random.randint(180, 480))
        rows.append({
            'session_id'       : f"SES{str(i).zfill(5)}",
            'user_id'          : random.choice(users if legit else sus),
            'start_time'       : start.strftime('%Y-%m-%d %H:%M:%S'),
            'end_time'         : (start + timedelta(minutes=dur)).strftime('%Y-%m-%d %H:%M:%S'),
            'duration_minutes' : dur,
        })
    df_session = pd.DataFrame(rows).sort_values('start_time').reset_index(drop=True)

    # Unauth logs
    rows = []
    for _ in range(500):
        legit = random.random() < 0.70
        rows.append({
            'timestamp'    : (_ts(1, base)[0]),
            'ip_address'   : random.choice(norm_ips if legit else sus_ips),
            'auth_status'  : 'authenticated' if legit else 'unauthenticated',
            'attempt_count': 1 if legit else random.randint(1, 15),
            'failure_reason': 'None' if legit else random.choice(reasons),
        })
    df_unauth = pd.DataFrame(rows).sort_values('timestamp').reset_index(drop=True)

    # Request logs
    rows = []
    for _ in range(500):
        r = random.random()
        if r < 0.75:
            ip, rtype, size, code = random.choice(norm_ips), 'normal', random.randint(100,5000), np.random.choice([200,400],p=[.95,.05])
        elif r < 0.90:
            ip, rtype, size, code = random.choice(sus_ips), 'blank', random.randint(0,50), np.random.choice([400,403],p=[.6,.4])
        else:
            ip, rtype, size, code = random.choice(sus_ips), 'dos_attack', random.randint(10000,50000), np.random.choice([429,503],p=[.7,.3])
        rows.append({'timestamp':_ts(1,base)[0], 'ip_address':ip, 'request_type':rtype,
                     'payload_size':size, 'status_code':code})
    df_req = pd.DataFrame(rows).sort_values('timestamp').reset_index(drop=True)

    # Service logs
    rows = []
    for _ in range(500):
        legit = random.random() < 0.85
        rows.append({
            'user_id'          : random.choice(users if legit else sus),
            'service_name'     : random.choice(services),
            'subscription_date': (base - timedelta(days=random.randint(0,180))).strftime('%Y-%m-%d'),
            'status'           : np.random.choice(['active','inactive'], p=[.9,.1]) if legit else
                                 np.random.choice(['active','inactive','suspended','pending'], p=[.3,.2,.4,.1]),
            'plan_type'        : random.choice(plans),
            'bank'             : random.choice(banks),
        })
    df_svc = pd.DataFrame(rows).sort_values('subscription_date').reset_index(drop=True)

    return df_login, df_session, df_unauth, df_req, df_svc

# ── Fraud score ────────────────────────────────────────────────────────────────
def fraud_score(df_login, df_unauth, df_req):
    fl = len(df_login[df_login.login_status=='failed']) / len(df_login) * 100
    ua = len(df_unauth[df_unauth.auth_status=='unauthenticated']) / len(df_unauth) * 100
    at = len(df_req[df_req.request_type.isin(['blank','dos_attack'])]) / len(df_req) * 100
    score = fl*.3 + ua*.4 + at*.3
    if score < 15:   return score, 'LOW',      '#10b981'
    if score < 30:   return score, 'MEDIUM',   '#f59e0b'
    if score < 50:   return score, 'HIGH',     '#f97316'
    return score, 'CRITICAL', '#ef4444'

# ── KPI helper ─────────────────────────────────────────────────────────────────
def kpi(col, label, value, color):
    col.markdown(f"""
    <div class="kpi" style="border-top-color:{color}">
      <p class="kpi-lbl">{label}</p>
      <p class="kpi-val" style="color:{color}">{value}</p>
    </div>""", unsafe_allow_html=True)

# ── Chart helpers ──────────────────────────────────────────────────────────────
COLORS = {'normal':'#10b981','blank':'#f59e0b','dos_attack':'#ef4444',
          'success':'#10b981','failed':'#ef4444',
          'authenticated':'#10b981','unauthenticated':'#ef4444'}

def chart_login_trend(df):
    df = df.copy(); df['hour'] = pd.to_datetime(df.timestamp).dt.hour
    g = df.groupby(['hour','login_status']).size().reset_index(name='count')
    fig = px.line(g, x='hour', y='count', color='login_status',
                  color_discrete_map=COLORS,
                  labels={'hour':'Hour','count':'Attempts','login_status':'Status'})
    fig.update_layout(**CHART_DEFAULTS, xaxis=GRID, yaxis=GRID, height=320,
                      legend=dict(orientation='h',y=-0.25))
    fig.update_traces(line_width=2)
    return fig

def chart_session_hist(df):
    fig = px.histogram(df, x='duration_minutes', nbins=50,
                       color_discrete_sequence=['#3b82f6'],
                       labels={'duration_minutes':'Duration (min)'})
    fig.add_vline(x=3,   line_dash='dash', line_color='#ef4444', annotation_text='< 3 min')
    fig.add_vline(x=180, line_dash='dash', line_color='#f59e0b', annotation_text='> 180 min')
    fig.update_layout(**CHART_DEFAULTS, xaxis=GRID, yaxis=GRID, height=320)
    return fig

def chart_auth_pie(df):
    c = df.auth_status.value_counts()
    fig = px.pie(values=c.values, names=c.index, hole=0.55,
                 color=c.index, color_discrete_map=COLORS)
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(**CHART_DEFAULTS, height=320,
                      legend=dict(orientation='h', y=-0.1))
    return fig

def chart_request_types(df):
    c = df.request_type.value_counts()
    fig = px.bar(x=c.index, y=c.values, color=c.index,
                 color_discrete_map=COLORS,
                 labels={'x':'Request Type','y':'Count'})
    fig.update_layout(**CHART_DEFAULTS, xaxis=GRID, yaxis=GRID,
                      height=320, showlegend=False)
    return fig

def chart_top_ips(df, n=10):
    sus = df[df.request_type.isin(['blank','dos_attack'])]
    top = sus.ip_address.value_counts().head(n)
    fig = px.bar(x=top.values, y=top.index, orientation='h',
                 color=top.values, color_continuous_scale='Reds',
                 labels={'x':'Attack Count','y':'IP Address'})
    fig.update_layout(**CHART_DEFAULTS, xaxis=GRID, yaxis=GRID,
                      height=380, coloraxis_showscale=False)
    return fig

def chart_attack_heatmap(df):
    df = df.copy()
    df['hour'] = pd.to_datetime(df.timestamp).dt.hour
    df['day']  = pd.to_datetime(df.timestamp).dt.day_name()
    atk = df[df.request_type.isin(['blank','dos_attack'])]
    piv = atk.groupby(['day','hour']).size().reset_index(name='count')\
             .pivot(index='day', columns='hour', values='count').fillna(0)
    fig = px.imshow(piv, color_continuous_scale='Reds',
                    labels=dict(x='Hour', y='Day', color='Attacks'),
                    aspect='auto')
    fig.update_layout(**CHART_DEFAULTS, height=320)
    return fig

def chart_fraud_gauge(score, level, color):
    fig = go.Figure(go.Indicator(
        mode='gauge+number',
        value=score,
        number={'suffix':'%', 'font':{'size':42,'color':color,'family':'IBM Plex Mono'}},
        title={'text':f"Fraud Risk Score<br><span style='font-size:.8em;color:{color}'>{level}</span>",
               'font':{'size':15,'color':'#94a3b8'}},
        gauge={
            'axis':{'range':[0,100],'tickcolor':'#1e2d45','tickfont':{'color':'#64748b'}},
            'bar':{'color':color,'thickness':0.25},
            'bgcolor':'#111827',
            'steps':[
                {'range':[0,15],  'color':'#0f1f14'},
                {'range':[15,30], 'color':'#1a1a0f'},
                {'range':[30,50], 'color':'#1f1200'},
                {'range':[50,100],'color':'#1f0f0f'},
            ],
            'threshold':{'line':{'color':color,'width':3},'thickness':0.75,'value':score}
        }
    ))
    fig.update_layout(**CHART_DEFAULTS, height=320)
    return fig

def chart_service_status(df):
    c = df.status.value_counts()
    clrs = {'active':'#10b981','inactive':'#64748b','suspended':'#ef4444','pending':'#f59e0b'}
    fig = px.pie(values=c.values, names=c.index, hole=0.5,
                 color=c.index, color_discrete_map=clrs)
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(**CHART_DEFAULTS, height=320,
                      legend=dict(orientation='h', y=-0.1))
    return fig

def chart_browser(df):
    c = df.browser.value_counts()
    fig = px.bar(x=c.values, y=c.index, orientation='h',
                 color=c.values, color_continuous_scale='Blues',
                 labels={'x':'Count','y':'Browser'})
    fig.update_layout(**CHART_DEFAULTS, xaxis=GRID, yaxis=GRID,
                      height=320, coloraxis_showscale=False)
    return fig

# ── Anomaly detection ──────────────────────────────────────────────────────────
def detect_anomalies(df_login, df_session, df_unauth, df_req, df_svc):
    anomalies = []

    # Brute force IPs
    bf = df_login[df_login.login_status=='failed'].groupby('ip_address').size()
    bf = bf[bf > 5]
    if len(bf):
        anomalies.append({'severity':'CRITICAL','category':'Brute Force',
                          'description':f'{len(bf)} IPs with >5 failed login attempts',
                          'count':len(bf)})

    # Suspicious sessions
    sus_s = df_session[(df_session.duration_minutes < 3) | (df_session.duration_minutes > 180)]
    if len(sus_s):
        anomalies.append({'severity':'WARNING','category':'Session Anomaly',
                          'description':f'{len(sus_s)} sessions with abnormal duration',
                          'count':len(sus_s)})

    # High attempt counts
    hi = df_unauth[df_unauth.attempt_count > 10]
    if len(hi):
        anomalies.append({'severity':'CRITICAL','category':'Credential Stuffing',
                          'description':f'{len(hi)} auth attempts with >10 retries',
                          'count':len(hi)})

    # DOS attacks
    dos = df_req[df_req.request_type=='dos_attack']
    if len(dos):
        anomalies.append({'severity':'CRITICAL','category':'DOS Attack',
                          'description':f'{len(dos)} DOS attack requests detected',
                          'count':len(dos)})

    # Suspended services
    sus_svc = df_svc[df_svc.status=='suspended']
    if len(sus_svc):
        anomalies.append({'severity':'WARNING','category':'Suspended Services',
                          'description':f'{len(sus_svc)} services in suspended state',
                          'count':len(sus_svc)})

    return anomalies

# ══════════════════════════════════════════════════════════════════════════════
#  MAIN APP
# ══════════════════════════════════════════════════════════════════════════════
def main():

    # ── Sidebar ────────────────────────────────────────────────────────────────
    with st.sidebar:
        st.markdown("## 🔐 UPI Log Analyzer")
        st.caption("Security Intelligence Dashboard")
        st.divider()

        st.markdown("**Data Source**")
        source = st.radio("", ["Generate Synthetic Data", "Upload CSV Files"],
                          label_visibility='collapsed')

        if source == "Upload CSV Files":
            st.markdown("**Upload Log Files**")
            up_login   = st.file_uploader("Login Logs",   type='csv', key='l')
            up_session = st.file_uploader("Session Logs", type='csv', key='s')
            up_unauth  = st.file_uploader("Unauth Logs",  type='csv', key='u')
            up_req     = st.file_uploader("Request Logs", type='csv', key='r')
            up_svc     = st.file_uploader("Service Logs", type='csv', key='sv')
            btn = st.button("Analyze", type="primary", use_container_width=True)
        else:
            btn = st.button("Generate & Analyze", type="primary", use_container_width=True)

        st.divider()
        st.markdown("""
        <div style="font-size:.78rem;color:#64748b;line-height:1.8">
        Analyzes 5 log types:<br>
        · Login attempts<br>
        · Session durations<br>
        · Auth failures<br>
        · Request patterns<br>
        · Service subscriptions
        </div>
        """, unsafe_allow_html=True)

    # ── Load data ──────────────────────────────────────────────────────────────
    if btn:
        if source == "Upload CSV Files":
            if not all([up_login, up_session, up_unauth, up_req, up_svc]):
                st.error("Please upload all 5 CSV files.")
                return
            df_l = pd.read_csv(up_login);   df_s = pd.read_csv(up_session)
            df_u = pd.read_csv(up_unauth);  df_r = pd.read_csv(up_req)
            df_v = pd.read_csv(up_svc)
        else:
            with st.spinner("Generating data..."):
                df_l, df_s, df_u, df_r, df_v = generate_data()

        st.session_state.update({
            'df_l':df_l,'df_s':df_s,'df_u':df_u,'df_r':df_r,'df_v':df_v,'loaded':True
        })

    # ── Dashboard ──────────────────────────────────────────────────────────────
    if not st.session_state.get('loaded', False):
        st.markdown("## UPI Log Analyzer")
        st.markdown("Select a data source in the sidebar and click **Generate & Analyze** to begin.")
        return

    df_l = st.session_state.df_l; df_s = st.session_state.df_s
    df_u = st.session_state.df_u; df_r = st.session_state.df_r
    df_v = st.session_state.df_v

    score, level, color = fraud_score(df_l, df_u, df_r)
    anomalies = detect_anomalies(df_l, df_s, df_u, df_r, df_v)

    # Page title
    st.markdown("## UPI Log Analyzer")
    st.caption(f"Analysis run · {datetime.now().strftime('%d %b %Y, %H:%M')}")
    st.divider()

    # ── Tabs ───────────────────────────────────────────────────────────────────
    tab1, tab2, tab3, tab4 = st.tabs(["Overview", "Deep Dive", "Anomalies", "Export"])

    # ══ TAB 1: Overview ══
    with tab1:

        # Fraud gauge + top KPIs
        g_col, k_col = st.columns([1.4, 1])

        with g_col:
            st.plotly_chart(chart_fraud_gauge(score, level, color), use_container_width=True)

        with k_col:
            st.write("")
            k1, k2 = st.columns(2)
            kpi(k1, "Total Logins",      f"{len(df_l):,}",  "#3b82f6")
            kpi(k2, "Failed Logins",     f"{len(df_l[df_l.login_status=='failed']):,}", "#ef4444")
            k3, k4 = st.columns(2)
            kpi(k3, "DOS Attacks",       f"{len(df_r[df_r.request_type=='dos_attack']):,}", "#ef4444")
            kpi(k4, "Unauth Attempts",   f"{len(df_u[df_u.auth_status=='unauthenticated']):,}", "#f59e0b")
            k5, k6 = st.columns(2)
            kpi(k5, "Unique Users",      f"{df_l.user_id.nunique():,}", "#10b981")
            kpi(k6, "Anomalies Found",   f"{len(anomalies)}", color)

        st.divider()

        # Quick anomaly summary
        if anomalies:
            st.markdown('<p class="sec-title">Active Alerts</p>', unsafe_allow_html=True)
            for a in anomalies:
                badge_cls = 'badge-red' if a['severity']=='CRITICAL' else 'badge-yellow'
                st.markdown(f"""
                <div class="anomaly-item">
                    <span style="color:#e2e8f0">{a['category']} — {a['description']}</span>
                    <span class="badge {badge_cls}">{a['severity']}</span>
                </div>""", unsafe_allow_html=True)
            st.write("")

        st.divider()

        # 4 charts
        c1, c2 = st.columns(2)
        with c1:
            st.markdown('<p class="sec-title">Login Attempts by Hour</p>', unsafe_allow_html=True)
            st.plotly_chart(chart_login_trend(df_l), use_container_width=True)

            st.markdown('<p class="sec-title">Request Type Distribution</p>', unsafe_allow_html=True)
            st.plotly_chart(chart_request_types(df_r), use_container_width=True)

        with c2:
            st.markdown('<p class="sec-title">Auth Status Breakdown</p>', unsafe_allow_html=True)
            st.plotly_chart(chart_auth_pie(df_u), use_container_width=True)

            st.markdown('<p class="sec-title">Session Duration Distribution</p>', unsafe_allow_html=True)
            st.plotly_chart(chart_session_hist(df_s), use_container_width=True)

    # ══ TAB 2: Deep Dive ══
    with tab2:
        section = st.selectbox("Select Analysis", [
            "Login Analysis", "Session Analysis",
            "Attack Analysis", "Service Analysis"
        ])

        st.divider()

        if section == "Login Analysis":
            c1, c2 = st.columns(2)
            with c1:
                st.markdown('<p class="sec-title">Login Trend</p>', unsafe_allow_html=True)
                st.plotly_chart(chart_login_trend(df_l), use_container_width=True)
            with c2:
                st.markdown('<p class="sec-title">Browser Distribution</p>', unsafe_allow_html=True)
                st.plotly_chart(chart_browser(df_l), use_container_width=True)

            st.markdown('<p class="sec-title">Recent Failed Logins</p>', unsafe_allow_html=True)
            failed = df_l[df_l.login_status=='failed'].tail(15)
            st.dataframe(failed, use_container_width=True, height=320)

        elif section == "Session Analysis":
            c1, c2 = st.columns(2)
            with c1:
                st.markdown('<p class="sec-title">Session Duration Histogram</p>', unsafe_allow_html=True)
                st.plotly_chart(chart_session_hist(df_s), use_container_width=True)
            with c2:
                st.markdown('<p class="sec-title">Session Stats</p>', unsafe_allow_html=True)
                short = len(df_s[df_s.duration_minutes < 3])
                long_ = len(df_s[df_s.duration_minutes > 180])
                sus_s = short + long_
                st.metric("Suspicious Sessions", sus_s)
                st.metric("Very Short  (< 3 min)",  short)
                st.metric("Very Long  (> 180 min)", long_)
                st.metric("Avg Duration", f"{df_s.duration_minutes.mean():.1f} min")

            st.markdown('<p class="sec-title">Suspicious Sessions</p>', unsafe_allow_html=True)
            sus_df = df_s[(df_s.duration_minutes < 3) | (df_s.duration_minutes > 180)]
            st.dataframe(sus_df.head(20), use_container_width=True, height=320)

        elif section == "Attack Analysis":
            c1, c2 = st.columns(2)
            with c1:
                st.markdown('<p class="sec-title">Request Types</p>', unsafe_allow_html=True)
                st.plotly_chart(chart_request_types(df_r), use_container_width=True)
            with c2:
                st.markdown('<p class="sec-title">Top Attacking IPs</p>', unsafe_allow_html=True)
                st.plotly_chart(chart_top_ips(df_r), use_container_width=True)

            st.markdown('<p class="sec-title">Attack Heatmap — Hour × Day</p>', unsafe_allow_html=True)
            st.plotly_chart(chart_attack_heatmap(df_r), use_container_width=True)

            st.markdown('<p class="sec-title">Recent Attack Logs</p>', unsafe_allow_html=True)
            atk = df_r[df_r.request_type.isin(['blank','dos_attack'])].tail(15)
            st.dataframe(atk, use_container_width=True, height=320)

        elif section == "Service Analysis":
            c1, c2 = st.columns(2)
            with c1:
                st.markdown('<p class="sec-title">Service Status</p>', unsafe_allow_html=True)
                st.plotly_chart(chart_service_status(df_v), use_container_width=True)
            with c2:
                st.markdown('<p class="sec-title">Service Counts</p>', unsafe_allow_html=True)
                c = df_v.service_name.value_counts()
                fig = px.bar(x=c.values, y=c.index, orientation='h',
                             color=c.values, color_continuous_scale='Blues',
                             labels={'x':'Count','y':'Service'})
                fig.update_layout(**CHART_DEFAULTS, xaxis=GRID, yaxis=GRID,
                                  height=320, coloraxis_showscale=False)
                st.plotly_chart(fig, use_container_width=True)

            st.markdown('<p class="sec-title">Suspended / Inactive Services</p>', unsafe_allow_html=True)
            bad = df_v[df_v.status.isin(['suspended','inactive'])]
            st.dataframe(bad.head(20), use_container_width=True, height=320)

    # ══ TAB 3: Anomalies ══
    with tab3:
        st.markdown('<p class="sec-title">Detected Anomalies</p>', unsafe_allow_html=True)

        if not anomalies:
            st.success("No anomalies detected.")
        else:
            for a in anomalies:
                badge_cls = 'badge-red' if a['severity']=='CRITICAL' else 'badge-yellow'
                st.markdown(f"""
                <div class="anomaly-item">
                    <div>
                        <div style="color:#e2e8f0;font-weight:600">{a['category']}</div>
                        <div style="color:#64748b;font-size:.85rem">{a['description']}</div>
                    </div>
                    <span class="badge {badge_cls}">{a['severity']}</span>
                </div>""", unsafe_allow_html=True)

        st.divider()

        # Anomaly drill-downs
        with st.expander("Brute Force — IPs with >5 failed logins"):
            bf = df_l[df_l.login_status=='failed'].groupby('ip_address').size()
            bf = bf[bf > 5].sort_values(ascending=False).reset_index()
            bf.columns = ['IP Address', 'Failed Attempts']
            st.dataframe(bf, use_container_width=True)

        with st.expander("Suspicious Sessions — abnormal durations"):
            sus = df_s[(df_s.duration_minutes < 3) | (df_s.duration_minutes > 180)]
            st.dataframe(sus, use_container_width=True)

        with st.expander("High-Retry Auth Attempts — >10 retries"):
            hi = df_u[df_u.attempt_count > 10].sort_values('attempt_count', ascending=False)
            st.dataframe(hi, use_container_width=True)

        with st.expander("DOS Attack Logs"):
            dos = df_r[df_r.request_type=='dos_attack']
            st.dataframe(dos, use_container_width=True)

        with st.expander("Suspended Services"):
            sus_svc = df_v[df_v.status=='suspended']
            st.dataframe(sus_svc, use_container_width=True)

    # ══ TAB 4: Export ══
    with tab4:
        st.markdown('<p class="sec-title">Download CSV Files</p>', unsafe_allow_html=True)

        c1, c2, c3 = st.columns(3)
        with c1:
            st.download_button("Login Logs",   df_l.to_csv(index=False), "login_logs.csv",   "text/csv", use_container_width=True)
            st.download_button("Session Logs", df_s.to_csv(index=False), "session_logs.csv", "text/csv", use_container_width=True)
        with c2:
            st.download_button("Unauth Logs",  df_u.to_csv(index=False), "unauth_logs.csv",  "text/csv", use_container_width=True)
            st.download_button("Request Logs", df_r.to_csv(index=False), "request_logs.csv", "text/csv", use_container_width=True)
        with c3:
            st.download_button("Service Logs", df_v.to_csv(index=False), "service_logs.csv", "text/csv", use_container_width=True)

        st.divider()
        st.markdown('<p class="sec-title">Summary Report</p>', unsafe_allow_html=True)

        if st.button("Generate Text Report", use_container_width=True):
            report = f"""UPI LOG ANALYZER — SUMMARY REPORT
Generated : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
{'─'*60}

FRAUD RISK SCORE : {score:.1f} / 100   [{level}]

LOGIN ANALYSIS
  Total attempts     : {len(df_l):,}
  Successful         : {len(df_l[df_l.login_status=='success']):,}
  Failed             : {len(df_l[df_l.login_status=='failed']):,}
  Unique users       : {df_l.user_id.nunique():,}
  Failure rate       : {len(df_l[df_l.login_status=='failed'])/len(df_l)*100:.1f}%

SESSION ANALYSIS
  Total sessions     : {len(df_s):,}
  Avg duration       : {df_s.duration_minutes.mean():.1f} min
  Short sessions     : {len(df_s[df_s.duration_minutes<3]):,}
  Long sessions      : {len(df_s[df_s.duration_minutes>180]):,}

AUTH ANALYSIS
  Total attempts     : {len(df_u):,}
  Authenticated      : {len(df_u[df_u.auth_status=='authenticated']):,}
  Unauthenticated    : {len(df_u[df_u.auth_status=='unauthenticated']):,}

ATTACK ANALYSIS
  Total requests     : {len(df_r):,}
  Normal             : {len(df_r[df_r.request_type=='normal']):,}
  Blank requests     : {len(df_r[df_r.request_type=='blank']):,}
  DOS attacks        : {len(df_r[df_r.request_type=='dos_attack']):,}

SERVICE ANALYSIS
  Total services     : {len(df_v):,}
  Active             : {len(df_v[df_v.status=='active']):,}
  Suspended          : {len(df_v[df_v.status=='suspended']):,}
  Inactive           : {len(df_v[df_v.status=='inactive']):,}

ANOMALIES DETECTED : {len(anomalies)}
{'─'*60}
"""
            st.text_area("", report, height=420)
            st.download_button("Download Report", report, "summary_report.txt", "text/plain",
                               use_container_width=True)

if __name__ == "__main__":
    main()
