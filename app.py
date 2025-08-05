"""
AIRA FAQ Manager - Simplified Version
Focus on Create FAQ, Edit FAQ, and AI Enhancement
"""

import streamlit as st
import sys
import os

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models import FAQManager, EnhancedFAQ, EnhancedFAQManager
from ai_helper import AIHelper

# Import page modules
from pages.add_faq import render_add_faq_page
from pages.enhanced_faqs import render_enhanced_faqs_page


# Page configuration
st.set_page_config(
    page_title="AIRA FAQ Manager",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Minimal dark theme CSS
st.markdown("""
<style>
    /* Dark theme */
    .stApp {
        background-color: #1e1e1e;
        color: #ffffff;
    }

    /* Sidebar styling */
    div[data-testid="stSidebar"] {
        background-color: #2a2a2a;
    }

    div[data-testid="stSidebar"] .css-1d391kg {
        background-color: #2a2a2a;
    }

    /* Minimal buttons */
    .stButton > button {
        background-color: #333333;
        color: #ffffff;
        border: 1px solid #555555;
        border-radius: 4px;
        padding: 0.5rem 1rem;
        transition: all 0.2s ease;
    }

    .stButton > button:hover {
        background-color: #444444;
        border-color: #666666;
    }

    /* Navigation buttons */
    div[data-testid="stSidebar"] .stButton > button {
        width: 100%;
        margin: 0.25rem 0;
        border-radius: 4px;
        border: 1px solid #555555;
        background-color: #333333;
        color: #ffffff;
        font-weight: 400;
        transition: all 0.2s ease;
    }

    div[data-testid="stSidebar"] .stButton > button:hover {
        background-color: #444444;
        border-color: #666666;
    }

    /* Active navigation button */
    div[data-testid="stSidebar"] .stButton > button[kind="primary"] {
        background-color: #000000;
        border-color: #333333;
        color: #ffffff;
    }

    /* Text inputs */
    .stTextInput > div > div > input {
        background-color: #2a2a2a;
        color: #ffffff;
        border: 1px solid #555555;
        border-radius: 4px;
    }

    .stTextArea > div > div > textarea {
        background-color: #2a2a2a;
        color: #ffffff;
        border: 1px solid #555555;
        border-radius: 4px;
    }

    /* Sidebar text */
    div[data-testid="stSidebar"] * {
        color: #ffffff !important;
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize session state variables"""
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "Create FAQ"

    if 'selected_faq_id' not in st.session_state:
        st.session_state.selected_faq_id = None


def create_simple_navigation():
    """Create minimal sidebar navigation"""
    # Simple sidebar header
    st.sidebar.markdown("""
    <div style="text-align: center; padding: 1rem; color: white;">
        <h2>The Hire Hub</h2>
        <p>FAQ Management Dashboard</p>
        <small>AI-Powered ATS System</small>
    </div>
    """, unsafe_allow_html=True)

    # Navigation section
    st.sidebar.markdown("### Navigation")

    pages = [
        {"name": "View FAQs", "key": "view"},
        {"name": "Enhanced FAQs", "key": "enhanced"},
        {"name": "Create FAQ", "key": "create"},
        {"name": "Edit FAQ", "key": "edit"}
    ]

    current_page = st.session_state.get('current_page', "Create FAQ")  # Default to Create FAQ

    # Create navigation buttons
    for page in pages:
        # Check if this is the current page
        is_current = (current_page == page["name"])

        # Use different styling for current page
        if is_current:
            button_type = "primary"
        else:
            button_type = "secondary"

        if st.sidebar.button(
            page["name"],
            key=f"nav_{page['key']}",
            type=button_type,
            use_container_width=True
        ):
            if current_page != page["name"]:
                st.session_state.current_page = page["name"]
                st.rerun()

    return current_page


def show_ai_status(ai_helper):
    """Show minimal AI status in sidebar"""
    st.sidebar.markdown("---")
    if ai_helper.is_configured():
        st.sidebar.markdown("""
        <div style="background-color: #333333; padding: 1rem; border-radius: 4px; text-align: center; color: white; border: 1px solid #555555;">
            <h4>AI Status</h4>
            <p>Ready to create FAQs</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.sidebar.markdown("""
        <div style="background-color: #333333; padding: 1rem; border-radius: 4px; text-align: center; color: white; border: 1px solid #555555;">
            <h4>AI Status</h4>
            <p>Set OPENAI_API_KEY to enable AI</p>
        </div>
        """, unsafe_allow_html=True)


def main():
    """Main application function"""
    initialize_session_state()

    # Initialize managers
    faq_manager = FAQManager()
    ai_helper = AIHelper()

    # Sidebar navigation
    current_page = create_simple_navigation()
    show_ai_status(ai_helper)

    # Main content
    if current_page == "View FAQs":
        render_view_faqs(faq_manager, ai_helper)

    elif current_page == "Enhanced FAQs":
        render_enhanced_faqs_page(ai_helper)

    elif current_page == "Create FAQ":
        render_add_faq_page(faq_manager, ai_helper)

    elif current_page == "Edit FAQ":
        render_edit_faq(faq_manager, ai_helper)

    else:
        st.error(f"Unknown page: {current_page}")


def render_view_faqs(faq_manager: FAQManager, ai_helper: AIHelper):
    """FAQ viewing and management - supports both old and enhanced formats"""
    st.header("View & Manage FAQs")

    # Initialize enhanced FAQ manager
    enhanced_manager = EnhancedFAQManager()

    # Toggle between old and enhanced FAQs
    col1, col2 = st.columns(2)
    with col1:
        view_mode = st.radio(
            "View Mode:",
            ["Legacy FAQs", "Enhanced FAQs", "Both"],
            horizontal=True
        )

    # Get FAQs based on view mode
    legacy_faqs = faq_manager.get_all_faqs()
    enhanced_faqs = enhanced_manager.get_all_enhanced_faqs()

    if view_mode == "Legacy FAQs":
        faqs_to_show = legacy_faqs
        faq_type = "legacy"
    elif view_mode == "Enhanced FAQs":
        faqs_to_show = enhanced_faqs
        faq_type = "enhanced"
    else:  # Both
        faqs_to_show = legacy_faqs + enhanced_faqs
        faq_type = "both"

    # Show counts
    st.markdown(f"**Legacy FAQs:** {len(legacy_faqs)} | **Enhanced FAQs:** {len(enhanced_faqs)} | **Total:** {len(legacy_faqs) + len(enhanced_faqs)}")

    faqs = faqs_to_show

    if not faqs:
        st.info("No FAQs found. Create your first FAQ!")
        if st.button("Create First FAQ", type="primary"):
            st.session_state.current_page = "Create FAQ"
            st.rerun()
        return

    # Top controls
    col1, col2 = st.columns([3, 1])

    with col1:
        # Simple search
        search = st.text_input("Search FAQs", placeholder="Search questions and answers...")

    with col2:
        # Download buttons
        col2a, col2b = st.columns(2)

        with col2a:
            # Download appropriate format
            import json
            if view_mode == "Enhanced FAQs":
                enhanced_data = enhanced_manager.export_to_json()
                st.download_button(
                    label="Download Enhanced JSON",
                    data=enhanced_data,
                    file_name="hire_hub_enhanced_faqs.json",
                    mime="application/json",
                    use_container_width=True
                )
            else:
                # Download legacy format
                faq_data = [{"question": faq.question, "answer": faq.answer} for faq in legacy_faqs if hasattr(faq, 'question')]
                json_str = json.dumps(faq_data, indent=2)

                st.download_button(
                    label="Download Legacy JSON",
                    data=json_str,
                    file_name="hire_hub_legacy_faqs.json",
                    mime="application/json",
                    use_container_width=True
                )

        with col2b:
            # Convert to Enhanced Format button (only show for legacy FAQs)
            if len(legacy_faqs) > 0:
                if st.button("Convert Legacy to Enhanced", use_container_width=True):
                    st.session_state.show_conversion = True
                    st.rerun()
            else:
                st.markdown("*No legacy FAQs to convert*")

    # Filter FAQs
    if search:
        filtered_faqs = []
        for faq in faqs:
            # Handle both legacy and enhanced FAQs
            if hasattr(faq, 'tags'):  # Enhanced FAQ
                if (search.lower() in faq.question.lower() or
                    search.lower() in faq.answer.lower() or
                    any(search.lower() in tag.lower() for tag in faq.tags) or
                    any(search.lower() in alt_q.lower() for alt_q in faq.alternate_questions)):
                    filtered_faqs.append(faq)
            else:  # Legacy FAQ
                if (search.lower() in faq.question.lower() or
                    search.lower() in faq.answer.lower()):
                    filtered_faqs.append(faq)
    else:
        filtered_faqs = faqs

    st.write(f"**{len(filtered_faqs)} FAQs found**")

    # Display FAQs
    for i, faq in enumerate(filtered_faqs):
        # Determine FAQ type and display accordingly
        if hasattr(faq, 'tags'):  # Enhanced FAQ
            with st.expander(f"🔹 {faq.question}", expanded=False):
                st.write(f"**Answer:** {faq.answer}")

                # Show enhanced fields
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"**Category:** {faq.category}")
                    st.markdown(f"**ID:** `{faq.id}`")
                with col2:
                    if faq.tags:
                        st.markdown(f"**Tags:** {', '.join(faq.tags)}")

                if faq.alternate_questions:
                    with st.expander("Alternate Questions", expanded=False):
                        for alt_q in faq.alternate_questions:
                            st.write(f"• {alt_q}")

                # Enhanced FAQ actions
                col1, col2, col3 = st.columns([1, 1, 3])
                with col1:
                    if st.button("Edit Enhanced", key=f"edit_enhanced_{i}"):
                        st.info("Enhanced FAQ editing coming soon!")

                with col2:
                    if st.button("Delete Enhanced", key=f"delete_enhanced_{i}"):
                        st.info("Enhanced FAQ deletion coming soon!")

        else:  # Legacy FAQ
            with st.expander(f"📄 {faq.question}", expanded=False):
                st.write(f"**Answer:** {faq.answer}")

                col1, col2, col3 = st.columns([1, 1, 3])
                with col1:
                    if st.button("Edit", key=f"edit_{faq.id}"):
                        st.session_state.selected_faq_id = faq.id
                        st.session_state.current_page = "Edit FAQ"
                        st.rerun()

                with col2:
                    if st.button("Delete", key=f"delete_{faq.id}"):
                        if faq_manager.delete_faq(faq.id):
                            st.success("FAQ deleted!")
                            st.rerun()
                        else:
                            st.error("Failed to delete FAQ")

    # Show conversion interface if requested
    if st.session_state.get('show_conversion', False):
        render_faq_conversion(faq_manager, ai_helper)


def render_edit_faq(faq_manager: FAQManager, ai_helper: AIHelper):
    """Enhanced edit FAQ functionality"""
    st.header("Edit FAQ")

    selected_id = st.session_state.get('selected_faq_id')
    if selected_id is None:
        st.warning("No FAQ selected for editing.")
        if st.button("Back to FAQs"):
            st.session_state.current_page = "View FAQs"
            st.rerun()
        return

    faq = faq_manager.get_faq_by_id(selected_id)
    if not faq:
        st.error("FAQ not found.")
        return

    st.info(f"Editing FAQ #{selected_id + 1}")

    with st.form("edit_faq_form"):
        # Question input
        question = st.text_area(
            "Question *",
            value=faq.question,
            help="Edit the question",
            key="edit_question"
        )

        # Answer input
        answer = st.text_area(
            "Answer *",
            value=faq.answer,
            height=150,
            help="Edit the answer",
            key="edit_answer"
        )

        # AI enhancement options
        if ai_helper.is_configured():
            st.markdown("**AI Enhancement:**")
            col1, col2 = st.columns(2)
            with col1:
                enhance_question = st.checkbox("Enhance question with AI")
            with col2:
                enhance_answer = st.checkbox("Enhance answer with AI")
        else:
            enhance_question = enhance_answer = False

        # Form buttons
        col1, col2, col3 = st.columns(3)

        with col1:
            submitted = st.form_submit_button("Save Changes", type="primary")

        with col2:
            if st.form_submit_button("Cancel"):
                st.session_state.selected_faq_id = None
                st.session_state.current_page = "View FAQs"
                st.rerun()

        with col3:
            if st.form_submit_button("Delete FAQ"):
                if faq_manager.delete_faq(selected_id):
                    st.success("FAQ deleted!")
                    st.session_state.selected_faq_id = None
                    st.session_state.current_page = "View FAQs"
                    st.rerun()

        if submitted:
            if question.strip() and answer.strip():
                # Apply AI enhancements if requested
                final_question = question.strip()
                final_answer = answer.strip()

                if enhance_question and ai_helper.is_configured():
                    with st.spinner("Enhancing question..."):
                        enhanced_q = ai_helper.enhance_question(question.strip())
                        if enhanced_q:
                            final_question = enhanced_q

                if enhance_answer and ai_helper.is_configured():
                    with st.spinner("Enhancing answer..."):
                        enhanced_a = ai_helper.enhance_answer(question.strip(), answer.strip())
                        if enhanced_a:
                            final_answer = enhanced_a

                # Update FAQ
                from models import FAQ
                updated_faq = FAQ(final_question, final_answer)

                if faq_manager.update_faq(selected_id, updated_faq):
                    st.success("FAQ updated successfully!")
                    st.session_state.selected_faq_id = None
                    st.session_state.current_page = "View FAQs"
                    st.rerun()
                else:
                    st.error("Failed to update FAQ")
            else:
                st.error("Please fill in both question and answer fields.")


def render_faq_conversion(faq_manager: FAQManager, ai_helper: AIHelper):
    """Render FAQ conversion interface"""
    st.markdown("---")
    st.markdown("### Convert FAQs to Enhanced Format")
    st.markdown("*Transform your existing FAQs into the new structured format with categories, tags, and alternate questions*")

    # Initialize enhanced FAQ manager
    enhanced_manager = EnhancedFAQManager()

    # Get all current FAQs
    faqs = faq_manager.get_all_faqs()

    if not faqs:
        st.warning("No FAQs found to convert.")
        return

    # Show conversion options
    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        st.markdown(f"**{len(faqs)} FAQs ready for conversion**")

    with col2:
        if st.button("Convert All FAQs", type="primary"):
            st.session_state.converting_all = True
            st.session_state.conversion_progress = 0
            st.rerun()

    with col3:
        if st.button("Close Conversion"):
            st.session_state.show_conversion = False
            if 'converting_all' in st.session_state:
                del st.session_state.converting_all
            if 'conversion_progress' in st.session_state:
                del st.session_state.conversion_progress
            st.rerun()

    # Show conversion progress
    if st.session_state.get('converting_all', False):
        progress = st.session_state.get('conversion_progress', 0)

        if progress < len(faqs):
            # Convert next FAQ
            current_faq = faqs[progress]

            st.markdown(f"**Converting FAQ {progress + 1} of {len(faqs)}**")
            st.markdown(f"*Question: {current_faq.question[:100]}...*")

            # Show progress bar
            progress_bar = st.progress(progress / len(faqs))

            with st.spinner("Converting FAQ with AI..."):
                # Get enhanced structure from AI
                enhanced_data = ai_helper.enhance_faq_to_structured_format(
                    current_faq.question,
                    current_faq.answer
                )

                if enhanced_data:
                    # Create enhanced FAQ
                    enhanced_faq = EnhancedFAQ(
                        question=current_faq.question,
                        answer=current_faq.answer,
                        category=enhanced_data.get('category', 'general'),
                        tags=enhanced_data.get('tags', []),
                        alternate_questions=enhanced_data.get('alternate_questions', [])
                    )

                    # Add to enhanced manager
                    if enhanced_manager.add_enhanced_faq(enhanced_faq):
                        st.success(f"✅ Converted: {current_faq.question[:50]}...")
                    else:
                        st.warning(f"⚠️ Skipped duplicate: {current_faq.question[:50]}...")
                else:
                    st.error(f"❌ Failed to convert: {current_faq.question[:50]}...")

                # Update progress
                st.session_state.conversion_progress = progress + 1

                # Auto-continue to next FAQ
                import time
                time.sleep(1)  # Brief pause to show progress
                st.rerun()

        else:
            # Conversion complete
            st.success("🎉 All FAQs converted successfully!")

            # Show download button for enhanced format
            enhanced_faqs = enhanced_manager.get_all_enhanced_faqs()
            if enhanced_faqs:
                enhanced_json = enhanced_manager.export_to_json()

                st.download_button(
                    label="Download Enhanced FAQs JSON",
                    data=enhanced_json,
                    file_name="hire_hub_enhanced_faqs.json",
                    mime="application/json",
                    type="primary"
                )

                # Show sample of converted FAQ
                st.markdown("### Sample Converted FAQ")
                sample_faq = enhanced_faqs[0]
                st.json(sample_faq.to_dict())

            # Reset conversion state
            if st.button("Start New Conversion"):
                st.session_state.conversion_progress = 0
                st.rerun()


if __name__ == "__main__":
    main()
