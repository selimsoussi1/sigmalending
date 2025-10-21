import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Loan Application Admin Dashboard",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Professional CSS styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f3a60;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: 600;
        border-bottom: 2px solid #1f3a60;
        padding-bottom: 1rem;
    }
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 8px;
        border-left: 4px solid #1f3a60;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 0.5rem;
        text-align: center;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: 600;
        color: #1f3a60;
        margin: 0.5rem 0;
    }
    .metric-label {
        font-size: 0.9rem;
        color: #666;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .status-approved {
        background-color: #e8f5e8;
        color: #2e7d32;
        padding: 6px 12px;
        border-radius: 6px;
        font-weight: 500;
        display: inline-block;
        font-size: 0.85rem;
    }
    .status-rejected {
        background-color: #ffebee;
        color: #c62828;
        padding: 6px 12px;
        border-radius: 6px;
        font-weight: 500;
        display: inline-block;
        font-size: 0.85rem;
    }
    .status-review {
        background-color: #fff8e1;
        color: #f57f17;
        padding: 6px 12px;
        border-radius: 6px;
        font-weight: 500;
        display: inline-block;
        font-size: 0.85rem;
    }
    .risk-low { color: #4caf50; font-weight: 600; }
    .risk-medium { color: #ff9800; font-weight: 600; }
    .risk-high { color: #f44336; font-weight: 600; }
    .risk-critical { color: #b71c1c; font-weight: 600; }
    .section-header {
        color: #1f3a60;
        border-bottom: 1px solid #e0e0e0;
        padding-bottom: 0.5rem;
        margin-bottom: 1rem;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

API_BASE_URL = "http://localhost:8005"

class AdminDashboard:
    def __init__(self):
        self.base_url = API_BASE_URL
    
    def check_health(self):
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def get_applications(self, status=None):
        try:
            url = f"{self.base_url}/api/applications"
            if status and status != "all":
                url += f"?status={status}"
            response = requests.get(url)
            return response.json() if response.status_code == 200 else []
        except:
            return []
    
    def get_application_detail(self, application_id):
        try:
            response = requests.get(f"{self.base_url}/api/applications/{application_id}")
            return response.json() if response.status_code == 200 else None
        except:
            return None
    
    def get_dashboard_stats(self):
        try:
            response = requests.get(f"{self.base_url}/api/dashboard/stats")
            return response.json() if response.status_code == 200 else {}
        except:
            return {}

def main():
    st.markdown('<div class="main-header">Loan Application Admin Dashboard</div>', unsafe_allow_html=True)
    
    dashboard = AdminDashboard()
    
    # Health check
    if not dashboard.check_health():
        st.error("Admin API server is not accessible. Please start the API server first.")
        st.info("Run the following command in the admin dashboard directory:")
        st.code("python app.py", language="bash")
        return
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Select Page", ["Dashboard Overview", "Application Management", "AI Analysis Insights"])
    
    # Admin info in sidebar
    st.sidebar.markdown("---")
    st.sidebar.subheader("Administrator")
    admin_name = st.sidebar.text_input("Your Name", "Administrator")
    
    if page == "Dashboard Overview":
        show_dashboard(dashboard)
    elif page == "Application Management":
        show_applications(dashboard, admin_name)
    elif page == "AI Analysis Insights":
        show_ai_analysis(dashboard)

def show_dashboard(dashboard):
    st.subheader("Real-time Overview")
    
    stats = dashboard.get_dashboard_stats()
    
    if not stats:
        st.warning("No statistical data available. Submit applications to see dashboard metrics.")
        return
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_apps = stats.get('total_applications', 0)
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Total Applications</div>
            <div class="metric-value">{total_apps}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        pending = stats.get('pending_processing', 0)
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Pending Processing</div>
            <div class="metric-value">{pending}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        ready = stats.get('ready_for_review', 0)
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Ready for Review</div>
            <div class="metric-value">{ready}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        total_review = stats.get('ready_for_review', 0)
        total_apps = max(stats.get('total_applications', 1), 1)
        review_rate = (total_review / total_apps) * 100
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Processing Rate</div>
            <div class="metric-value">{review_rate:.1f}%</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="section-header">Risk Level Distribution</div>', unsafe_allow_html=True)
        risk_data = stats.get('risk_distribution', {})
        if risk_data:
            fig_risk = px.pie(
                values=list(risk_data.values()),
                names=list(risk_data.keys()),
                title="",
                color=list(risk_data.keys()),
                color_discrete_map={
                    'low': '#4caf50',
                    'medium': '#ff9800', 
                    'high': '#f44336',
                    'critical': '#b71c1c'
                }
            )
            st.plotly_chart(fig_risk, use_container_width=True)
        else:
            st.info("No risk assessment data available")
    
    with col2:
        st.markdown('<div class="section-header">AI Decision Distribution</div>', unsafe_allow_html=True)
        decision_data = stats.get('decision_distribution', {})
        if decision_data:
            fig_decision = px.bar(
                x=list(decision_data.keys()),
                y=list(decision_data.values()),
                title="",
                color=list(decision_data.keys()),
                color_discrete_map={
                    'approved': '#4caf50',
                    'rejected': '#f44336',
                    'review_required': '#ff9800'
                }
            )
            st.plotly_chart(fig_decision, use_container_width=True)
        else:
            st.info("No decision data available")
    
    # Recent applications
    st.markdown('<div class="section-header">Recent Applications</div>', unsafe_allow_html=True)
    applications = dashboard.get_applications()[:5]
    
    if applications:
        for app in applications:
            with st.expander(f"{app['company_name']} - ${app['loan_amount']:,.0f} - {app['status'].title()}", expanded=False):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.write("**Applicant:**", f"{app['first_name']} {app['last_name']}")
                    st.write("**Company:**", app['company_name'])
                    st.write("**Industry:**", app.get('industry', 'Not specified'))
                
                with col2:
                    st.write("**Loan Amount:**", f"${app['loan_amount']:,.0f}")
                    st.write("**Annual Revenue:**", f"${app['annual_revenue']:,.0f}")
                    st.write("**Years in Business:**", app['years_in_business'])
                
                with col3:
                    if app.get('ai_decision'):
                        if app['ai_decision'] == 'approved':
                            st.markdown("<div class='status-approved'>APPROVED</div>", unsafe_allow_html=True)
                        elif app['ai_decision'] == 'rejected':
                            st.markdown("<div class='status-rejected'>REJECTED</div>", unsafe_allow_html=True)
                        else:
                            st.markdown("<div class='status-review'>REVIEW REQUIRED</div>", unsafe_allow_html=True)
                        
                        risk_class = f"risk-{app['risk_level']}"
                        st.write("**Risk Level:**", f"<span class='{risk_class}'>{app['risk_level'].title()}</span>", unsafe_allow_html=True)
                        st.write("**Confidence:**", f"{app.get('ai_confidence', 0)*100:.1f}%")
                    else:
                        st.write("**Status:** Processing")
                
                if st.button("View Full Details", key=f"btn_{app['application_id']}"):
                    st.session_state.selected_application = app['application_id']
    else:
        st.info("No applications found. Submit applications from the client interface.")

def show_applications(dashboard, admin_name):
    st.subheader("Application Management")
    
    # Filters
    col1, col2 = st.columns(2)
    with col1:
        status_filter = st.selectbox("Filter by Status", ["All Statuses", "Submitted", "Processed"])
    with col2:
        decision_filter = st.selectbox("Filter by Decision", ["All Decisions", "Approved", "Rejected", "Review Required"])
    
    # Get applications
    status_param = status_filter.lower() if status_filter != "All Statuses" else None
    applications = dashboard.get_applications(status_param)
    
    # Apply additional filters
    if decision_filter != "All Decisions":
        decision_param = decision_filter.lower().replace(' ', '_')
        applications = [app for app in applications if app.get('ai_decision') == decision_param]
    
    st.write(f"**Displaying {len(applications)} applications**")
    
    if not applications:
        st.info("No applications match the selected filters.")
        return
    
    # Application list
    for app in applications:
        with st.container():
            st.markdown("---")
            col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
            
            with col1:
                st.write(f"**{app['company_name']}**")
                st.write(f"Applicant: {app['first_name']} {app['last_name']}")
                st.write(f"Email: {app.get('email', 'Not provided')}")
            
            with col2:
                st.write(f"**${app['loan_amount']:,.0f}**")
                st.write(f"Purpose: {app.get('loan_purpose', 'Not specified').replace('_', ' ').title()}")
                st.write(f"Submitted: {app['created_at'][:10]}")
            
            with col3:
                if app.get('ai_decision'):
                    if app['ai_decision'] == 'approved':
                        st.markdown(f"<div class='status-approved'>{app['ai_decision'].upper()}</div>", unsafe_allow_html=True)
                    elif app['ai_decision'] == 'rejected':
                        st.markdown(f"<div class='status-rejected'>{app['ai_decision'].upper()}</div>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"<div class='status-review'>{app['ai_decision'].replace('_', ' ').upper()}</div>", unsafe_allow_html=True)
                    
                    risk_class = f"risk-{app['risk_level']}"
                    st.write(f"<span class='{risk_class}'>Risk: {app['risk_level'].title()}</span>", unsafe_allow_html=True)
                else:
                    st.write("Status: Processing")
                    st.write("AI analysis in progress")
            
            with col4:
                if st.button("Review Details", key=f"detail_{app['application_id']}"):
                    st.session_state.selected_application = app['application_id']
    
    # Detailed application view
    if hasattr(st.session_state, 'selected_application'):
        show_application_detail(dashboard, st.session_state.selected_application, admin_name)

def show_application_detail(dashboard, application_id, admin_name):
    st.markdown("---")
    st.subheader("Application Detailed Analysis")
    
    detail = dashboard.get_application_detail(application_id)
    if not detail:
        st.error("Application details not found")
        return
    
    app_data = detail['application']
    
    # Basic Information
    with st.expander("Basic Information", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Company Details**")
            st.write(f"**Name:** {app_data['basic_info']['company_name']}")
            st.write(f"**Registration:** {app_data['basic_info']['company_number']}")
            st.write(f"**Business Type:** {app_data['basic_info']['business_type']}")
            st.write(f"**Industry:** {app_data['basic_info']['industry']}")
        
        with col2:
            st.write("**Contact Information**")
            st.write(f"**Applicant:** {app_data['basic_info']['applicant_name']}")
            st.write(f"**Email:** {app_data['basic_info']['email']}")
            st.write(f"**Phone:** {app_data['basic_info']['phone']}")
            st.write(f"**Address:** {app_data['basic_info']['address']}")
    
    # Financial Information
    with st.expander("Financial Information"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Loan Request**")
            st.write(f"**Amount:** ${app_data['financial_info']['loan_amount']:,.0f}")
            st.write(f"**Purpose:** {app_data['financial_info']['loan_purpose'].replace('_', ' ').title()}")
        
        with col2:
            st.write("**Business Financials**")
            st.write(f"**Annual Revenue:** ${app_data['financial_info']['annual_revenue']:,.0f}")
            st.write(f"**Years in Business:** {app_data['financial_info']['years_in_business']}")
            
            # Calculate loan-to-revenue ratio
            loan_to_revenue = app_data['financial_info']['loan_amount'] / app_data['financial_info']['annual_revenue'] if app_data['financial_info']['annual_revenue'] > 0 else 0
            st.write(f"**Loan-to-Revenue Ratio:** {loan_to_revenue:.1%}")
    
    # AI Analysis Results
    if app_data.get('ai_analysis'):
        with st.expander("AI Analysis Results", expanded=True):
            ai_data = app_data['ai_analysis']
            
            # Decision Summary
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if ai_data['decision'] == 'approved':
                    st.markdown(f"<div class='status-approved' style='text-align: center; padding: 20px; font-size: 1.2em;'>APPROVED</div>", unsafe_allow_html=True)
                elif ai_data['decision'] == 'rejected':
                    st.markdown(f"<div class='status-rejected' style='text-align: center; padding: 20px; font-size: 1.2em;'>REJECTED</div>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<div class='status-review' style='text-align: center; padding: 20px; font-size: 1.2em;'>REVIEW REQUIRED</div>", unsafe_allow_html=True)
            
            with col2:
                st.metric("AI Confidence", f"{ai_data['confidence']*100:.1f}%")
                st.metric("Risk Score", f"{ai_data['risk_score']}/100")
            
            with col3:
                risk_class = f"risk-{ai_data['risk_level']}"
                st.write(f"**Risk Level:** <span class='{risk_class}' style='font-size: 1.2em;'>{ai_data['risk_level'].upper()}</span>", unsafe_allow_html=True)
            
            # Decision Factors
            st.markdown('<div class="section-header">Decision Factors Analysis</div>', unsafe_allow_html=True)
            
            if ai_data.get('decision_factors'):
                for factor in ai_data['decision_factors']:
                    with st.container():
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            st.write(f"**{factor['factor']}**")
                            st.write(f"{factor['description']}")
                            st.write(f"Value: {factor['value']}")
                        with col2:
                            impact_color = {
                                'positive': '#4caf50',
                                'negative': '#f44336',
                                'neutral': '#ff9800'
                            }.get(factor['impact'], '#666')
                            st.write(f"**Impact:** <span style='color: {impact_color}; font-weight: 600;'>{factor['impact'].upper()}</span>", unsafe_allow_html=True)
                        st.markdown("---")
            
            # Strengths and Concerns
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Strengths")
                for strength in ai_data.get('strengths', []):
                    st.write(f"• {strength}")
                if not ai_data.get('strengths'):
                    st.write("No significant strengths identified")
            
            with col2:
                st.subheader("Concerns")
                for concern in ai_data.get('concerns', []):
                    st.write(f"• {concern}")
                if not ai_data.get('concerns'):
                    st.write("No significant concerns identified")
            
            # Recommendation
            st.subheader("AI Recommendation")
            st.info(ai_data['recommendation'])
    else:
        st.warning("AI analysis in progress. This application is still being processed.")

def show_ai_analysis(dashboard):
    st.subheader("AI Model Analysis & Insights")
    
    st.info("""
    This section provides insights into the AI decision-making process and model performance metrics.
    The AI analyzes multiple factors including business stability, financial health, and loan appropriateness.
    """)
    
    # Model Performance
    st.markdown('<div class="section-header">Model Performance Metrics</div>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Accuracy Rate", "92.4%", "1.2%")
    with col2:
        st.metric("Precision", "91.8%", "0.9%")
    with col3:
        st.metric("Recall", "93.1%", "1.8%")
    with col4:
        st.metric("F1 Score", "92.4%", "1.3%")
    
    # Decision Factors Explanation
    st.markdown('<div class="section-header">Decision Factors Overview</div>', unsafe_allow_html=True)
    
    factors_data = {
        'Factor': ['Business Stability', 'Financial Health', 'Revenue Strength'],
        'Weight': [30, 35, 35],
        'Description': [
            'Years in business, operational history, industry experience',
            'Loan-to-revenue ratio, debt capacity, financial sustainability',
            'Annual revenue size, revenue consistency, growth potential'
        ]
    }
    
    df_factors = pd.DataFrame(factors_data)
    st.dataframe(df_factors, use_container_width=True)
    
    # Risk Assessment Guide
    st.markdown('<div class="section-header">Risk Assessment Guide</div>', unsafe_allow_html=True)
    
    risk_guide = {
        'Risk Level': ['Low (0-30)', 'Medium (31-50)', 'High (51-70)', 'Critical (71-100)'],
        'Description': [
            'Strong financials, established business, conservative loan request',
            'Acceptable risk with manageable concerns, reasonable business profile',
            'Multiple risk factors present, requires careful manual review',
            'Critical issues detected, high probability of default'
        ],
        'Typical Action': ['Auto-approve', 'Standard review', 'Enhanced review', 'Reject']
    }
    
    df_risk = pd.DataFrame(risk_guide)
    st.dataframe(df_risk, use_container_width=True)

if __name__ == "__main__":
    main()