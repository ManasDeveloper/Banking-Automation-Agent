"""
Banking Automation Dashboard - Streamlit Application
Main interface for the banking email processing automation system.
"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import json
from datetime import datetime
from typing import Dict, Any, List, Optional

# Import our modules
from src.email_processor import EmailProcessor
from src.ocr_engine import OCREngine
from src.classifier import IntentClassifier
from src.response_generator import ResponseGenerator
from src.llm_agent import LLMAgent
from src.database import get_db_manager, DatabaseManager

# Page configuration
st.set_page_config(
    page_title="Banking Automation Agent",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .status-badge {
        padding: 0.25rem 0.75rem;
        border-radius: 0.25rem;
        font-weight: bold;
        font-size: 0.875rem;
    }
    .status-critical { background-color: #ff4b4b; color: white; }
    .status-high { background-color: #ffa500; color: white; }
    .status-medium { background-color: #4a90e2; color: white; }
    .status-low { background-color: #90ee90; color: black; }
</style>
""", unsafe_allow_html=True)


class BankingDashboard:
    """Main dashboard application class"""

    def __init__(self):
        """Initialize dashboard with all components"""
        self.email_processor = EmailProcessor()
        self.ocr_engine = OCREngine()
        self.classifier = IntentClassifier()
        self.response_generator = ResponseGenerator()
        self.db_manager = get_db_manager()

        # Initialize database
        self.db_manager.init_db()

        # Initialize session state
        if 'processed_emails' not in st.session_state:
            st.session_state.processed_emails = []
        if 'selected_email_id' not in st.session_state:
            st.session_state.selected_email_id = None
        if 'processing_complete' not in st.session_state:
            st.session_state.processing_complete = False

    def run(self):
        """Main application entry point"""
        # Header
        st.markdown('<h1 class="main-header">🏦 AI-Powered Banking Automation Agent</h1>', unsafe_allow_html=True)

        # Sidebar
        self.render_sidebar()

        # Main content area
        tab1, tab2, tab3, tab4 = st.tabs(["📧 Email Processing", "📊 Analytics", "⚙️ Settings", "ℹ️ About"])

        with tab1:
            self.render_email_processing_tab()

        with tab2:
            self.render_analytics_tab()

        with tab3:
            self.render_settings_tab()

        with tab4:
            self.render_about_tab()

    def render_sidebar(self):
        """Render sidebar with email list and controls"""
        st.sidebar.title("📥 Email Inbox")

        # Load emails button
        if st.sidebar.button("🔄 Load Emails", use_container_width=True):
            with st.spinner("Loading emails..."):
                emails = self.email_processor.load_all_emails()
                st.session_state.emails = emails
                st.success(f"Loaded {len(emails)} emails")

        # Process all emails button
        if st.sidebar.button("⚡ Process All Emails", use_container_width=True, type="primary"):
            self.process_all_emails()

        st.sidebar.markdown("---")

        # Display email list
        if 'emails' in st.session_state:
            st.sidebar.subheader(f"Emails ({len(st.session_state.emails)})")

            for email in st.session_state.emails:
                priority = email.get('priority', 'medium')
                priority_colors = {
                    'critical': '🔴',
                    'high': '🟠',
                    'medium': '🔵',
                    'low': '🟢'
                }
                priority_icon = priority_colors.get(priority, '⚪')

                # Email preview button
                button_label = f"{priority_icon} {email['subject'][:30]}..."
                if st.sidebar.button(button_label, key=f"email_{email['email_id']}", use_container_width=True):
                    st.session_state.selected_email_id = email['email_id']

    def process_all_emails(self):
        """Process all loaded emails through the pipeline"""
        if 'emails' not in st.session_state:
            st.error("Please load emails first!")
            return

        emails = st.session_state.emails
        progress_bar = st.progress(0)
        status_text = st.empty()

        processed_results = []

        for i, email in enumerate(emails):
            status_text.text(f"Processing {i+1}/{len(emails)}: {email['subject']}")

            try:
                # Process email through pipeline
                result = self.process_single_email(email)
                processed_results.append(result)

            except Exception as e:
                st.error(f"Error processing email {email['email_id']}: {str(e)}")

            progress_bar.progress((i + 1) / len(emails))

        status_text.text("Processing complete!")
        st.session_state.processed_emails = processed_results
        st.session_state.processing_complete = True
        st.success(f"✅ Successfully processed {len(processed_results)} emails!")

    def process_single_email(self, email: Dict[str, Any]) -> Dict[str, Any]:
        """Process a single email through the complete pipeline"""
        result = {
            'email': email,
            'extracted_data': None,
            'classification': None,
            'response': None,
            'action': None
        }

        # Step 1: Extract data from attachments (if any)
        attachments = email.get('attachments', [])
        if attachments:
            extracted_data = {'all_text': '', 'structured_data': {}}
            for attachment in attachments:
                pdf_path = Path("data/sample_pdfs") / attachment
                if pdf_path.exists():
                    ocr_result = self.ocr_engine.process_pdf(str(pdf_path))
                    extracted_data['all_text'] += ocr_result['raw_text'] + "\n"
                    extracted_data['structured_data'] = ocr_result['structured_data']
            result['extracted_data'] = extracted_data

        # Step 2: Classify intent
        classification = self.classifier.classify(email, result['extracted_data'])
        result['classification'] = classification

        # Step 3: Generate response
        response = self.response_generator.generate(
            email,
            classification['intent'],
            result['extracted_data']
        )
        result['response'] = response

        # Step 4: Determine action
        action = self.classifier.llm_agent.determine_action(
            email,
            classification['intent'],
            classification['confidence']
        )
        result['action'] = action

        return result

    def render_email_processing_tab(self):
        """Render main email processing interface"""
        st.header("Email Processing Pipeline")

        if not st.session_state.processing_complete:
            st.info("👈 Click 'Load Emails' in the sidebar to start, then 'Process All Emails' to run the pipeline.")
            return

        # Select email to view
        if 'processed_emails' not in st.session_state or not st.session_state.processed_emails:
            st.warning("No processed emails yet. Click 'Process All Emails' in the sidebar.")
            return

        # Email selector
        email_options = {
            result['email']['email_id']: f"{result['email']['subject']} - {result['email']['sender_name']}"
            for result in st.session_state.processed_emails
        }

        selected_id = st.selectbox(
            "Select Email to View",
            options=list(email_options.keys()),
            format_func=lambda x: email_options[x]
        )

        # Find selected email result
        selected_result = next(
            (r for r in st.session_state.processed_emails if r['email']['email_id'] == selected_id),
            None
        )

        if not selected_result:
            return

        # Display email details in columns
        col1, col2 = st.columns([1, 1])

        with col1:
            st.subheader("📧 Original Email")
            self.render_email_view(selected_result['email'])

            if selected_result['extracted_data']:
                st.subheader("📄 Extracted Data")
                self.render_extracted_data(selected_result['extracted_data'])

        with col2:
            st.subheader("🎯 Classification")
            self.render_classification(selected_result['classification'])

            st.subheader("💬 Generated Response")
            self.render_response(selected_result['response'])

            st.subheader("⚡ Recommended Action")
            self.render_action(selected_result['action'])

    def render_email_view(self, email: Dict[str, Any]):
        """Render email details"""
        priority = email.get('priority', 'medium')
        priority_badge = f'<span class="status-badge status-{priority}">{priority.upper()}</span>'

        st.markdown(f"""
        **From:** {email.get('sender_name', '')} &lt;{email['sender']}&gt;
        **Subject:** {email['subject']}
        **Priority:** {priority_badge}
        **Attachments:** {', '.join(email.get('attachments', [])) or 'None'}
        """, unsafe_allow_html=True)

        with st.expander("📝 Email Body", expanded=True):
            st.text_area("", value=email['body'], height=200, disabled=True, label_visibility="collapsed")

    def render_extracted_data(self, extracted_data: Dict[str, Any]):
        """Render extracted data from attachments"""
        if not extracted_data:
            st.info("No attachments to process")
            return

        structured = extracted_data.get('structured_data', {})

        col1, col2 = st.columns(2)

        with col1:
            if structured.get('account_numbers'):
                st.metric("Account Numbers", len(structured['account_numbers']))
                for acc in structured['account_numbers']:
                    st.code(acc)

            if structured.get('amounts'):
                st.metric("Amounts Found", len(structured['amounts']))
                for amt in structured['amounts'][:5]:
                    st.write(f"${amt:,.2f}")

        with col2:
            if structured.get('dates'):
                st.metric("Dates Found", len(structured['dates']))
                for date in structured['dates'][:5]:
                    st.write(date)

            if structured.get('names'):
                st.metric("Names Found", len(structured['names']))
                for name in structured['names'][:5]:
                    st.write(name)

    def render_classification(self, classification: Dict[str, Any]):
        """Render classification results"""
        intent = classification['intent']
        confidence = classification['confidence']

        col1, col2 = st.columns(2)

        with col1:
            st.metric("Intent", intent.replace('_', ' ').title())

        with col2:
            confidence_color = "🟢" if confidence >= 0.8 else "🟡" if confidence >= 0.6 else "🔴"
            st.metric("Confidence", f"{confidence:.1%} {confidence_color}")

        if classification.get('sub_category'):
            st.info(f"**Sub-category:** {classification['sub_category']}")

        with st.expander("🤔 Reasoning"):
            st.write(classification.get('reasoning', 'N/A'))

    def render_response(self, response: Dict[str, Any]):
        """Render generated response"""
        response_text = response['response_text']

        # Editable text area
        edited_response = st.text_area(
            "Response (editable)",
            value=response_text,
            height=300,
            key=f"response_{hash(response_text)}"
        )

        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("✅ Approve & Send", use_container_width=True, type="primary"):
                st.success("Response approved!")

        with col2:
            if st.button("📝 Save Draft", use_container_width=True):
                st.info("Response saved as draft")

        with col3:
            if st.button("⚠️ Escalate", use_container_width=True):
                st.warning("Escalated to human review")

        # Quality metrics
        with st.expander("📊 Response Quality Metrics"):
            quality = self.response_generator.evaluate_response_quality(response)
            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("Quality Score", f"{quality['quality_score']}/100")
            with col2:
                st.metric("Word Count", response['word_count'])
            with col3:
                st.metric("Quality Level", quality['quality_level'].upper())

    def render_action(self, action: Dict[str, Any]):
        """Render recommended action"""
        action_type = action['action_type']
        priority = action['priority']

        action_icons = {
            'reply': '💬',
            'escalate': '⚠️',
            'log': '📝',
            'forward': '↗️'
        }

        icon = action_icons.get(action_type, '📌')

        st.markdown(f"""
        **Action:** {icon} {action_type.upper()}
        **Priority:** {priority.upper()}
        **Assigned To:** {action['assigned_to']}
        **Reason:** {action['reason']}
        """)

    def render_analytics_tab(self):
        """Render analytics and statistics"""
        st.header("📊 Analytics Dashboard")

        if not st.session_state.processing_complete:
            st.info("Process emails first to see analytics")
            return

        processed = st.session_state.processed_emails

        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total Emails", len(processed))

        with col2:
            avg_confidence = sum(r['classification']['confidence'] for r in processed) / len(processed)
            st.metric("Avg Confidence", f"{avg_confidence:.1%}")

        with col3:
            high_conf = sum(1 for r in processed if r['classification']['confidence'] >= 0.8)
            st.metric("High Confidence", f"{high_conf}/{len(processed)}")

        with col4:
            escalations = sum(1 for r in processed if r['action']['action_type'] == 'escalate')
            st.metric("Escalations", escalations)

        st.markdown("---")

        # Charts
        col1, col2 = st.columns(2)

        with col1:
            # Intent distribution
            st.subheader("Intent Distribution")
            intent_counts = {}
            for result in processed:
                intent = result['classification']['intent']
                intent_counts[intent] = intent_counts.get(intent, 0) + 1

            fig = px.pie(
                values=list(intent_counts.values()),
                names=[i.replace('_', ' ').title() for i in intent_counts.keys()],
                title="Email Intents"
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Action distribution
            st.subheader("Action Distribution")
            action_counts = {}
            for result in processed:
                action = result['action']['action_type']
                action_counts[action] = action_counts.get(action, 0) + 1

            fig = px.bar(
                x=list(action_counts.keys()),
                y=list(action_counts.values()),
                title="Recommended Actions",
                labels={'x': 'Action Type', 'y': 'Count'}
            )
            st.plotly_chart(fig, use_container_width=True)

        # Priority heatmap
        st.subheader("Priority vs Intent Heatmap")
        priority_intent_matrix = {}
        for result in processed:
            priority = result['email'].get('priority', 'medium')
            intent = result['classification']['intent']
            key = (priority, intent)
            priority_intent_matrix[key] = priority_intent_matrix.get(key, 0) + 1

        # Create matrix for heatmap
        priorities = ['critical', 'high', 'medium', 'low']
        intents = list(set(r['classification']['intent'] for r in processed))

        matrix = [[priority_intent_matrix.get((p, i), 0) for i in intents] for p in priorities]

        fig = go.Figure(data=go.Heatmap(
            z=matrix,
            x=[i.replace('_', ' ').title() for i in intents],
            y=[p.upper() for p in priorities],
            colorscale='Blues'
        ))
        fig.update_layout(title="Email Distribution: Priority vs Intent")
        st.plotly_chart(fig, use_container_width=True)

    def render_settings_tab(self):
        """Render settings and configuration"""
        st.header("⚙️ Settings")

        st.subheader("API Configuration")
        api_key = st.text_input("OpenAI API Key", type="password", placeholder="sk-...")

        if api_key:
            st.success("✅ API Key configured")
        else:
            st.warning("⚠️ No API key configured. Set OPENAI_API_KEY in .env file")

        st.markdown("---")

        st.subheader("Processing Options")

        col1, col2 = st.columns(2)

        with col1:
            st.checkbox("Enable OCR processing", value=True)
            st.checkbox("Auto-approve low-risk responses", value=False)

        with col2:
            st.slider("Confidence threshold for auto-approval", 0.0, 1.0, 0.9, 0.05)
            st.selectbox("Default response tone", ["Professional", "Friendly", "Empathetic"])

        st.markdown("---")

        st.subheader("System Actions")

        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("🗑️ Clear Database", use_container_width=True):
                st.warning("This will delete all processed data!")

        with col2:
            if st.button("📤 Export Results", use_container_width=True):
                st.info("Export functionality coming soon")

        with col3:
            if st.button("🔄 Reset Session", use_container_width=True):
                st.session_state.clear()
                st.experimental_rerun()

    def render_about_tab(self):
        """Render about/help information"""
        st.header("ℹ️ About Banking Automation Agent")

        st.markdown("""
        ## Overview
        This AI-powered banking automation system processes customer emails, extracts information,
        classifies intent, and generates professional responses automatically.

        ## Features
        - 📧 **Email Processing**: Load and parse banking customer emails
        - 🔍 **OCR Extraction**: Extract text and data from PDF attachments
        - 🎯 **Intent Classification**: Automatically categorize emails using AI
        - 💬 **Response Generation**: Create context-aware professional responses
        - ⚡ **Action Determination**: Recommend appropriate next steps
        - 📊 **Analytics**: View processing statistics and insights

        ## Intent Categories
        1. **Loan Request**: Customer loan applications (home, auto, business)
        2. **KYC Update**: Customer information updates
        3. **Account Issue**: Account access or transaction problems
        4. **Fraud Complaint**: Security concerns and fraud reports
        5. **General Inquiry**: Questions about products and services

        ## Workflow
        1. Load emails from the sample data
        2. Process emails through the AI pipeline
        3. Review classifications and generated responses
        4. Approve, edit, or escalate responses
        5. Analyze processing metrics and patterns

        ## Technology Stack
        - **Frontend**: Streamlit
        - **AI/LLM**: OpenAI GPT-4
        - **OCR**: pdfplumber + pytesseract
        - **Database**: SQLite + SQLAlchemy
        - **Visualization**: Plotly

        ## Getting Started
        1. Set your OpenAI API key in `.env` file
        2. Click "Load Emails" in the sidebar
        3. Click "Process All Emails" to run the pipeline
        4. Review results in the Email Processing tab
        5. View analytics in the Analytics tab

        ---
        **Version**: 1.0.0
        **Author**: Banking Automation Team
        **License**: MIT
        """)


def main():
    """Main entry point for Streamlit app"""
    dashboard = BankingDashboard()
    dashboard.run()


if __name__ == "__main__":
    main()
