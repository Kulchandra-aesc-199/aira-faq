import streamlit as st
from models import FAQ, FAQManager, EnhancedFAQ, EnhancedFAQManager
from ai_helper import AIHelper


def render_add_faq_page(faq_manager: FAQManager, ai_helper: AIHelper):
    """Minimal Create FAQ page with clean dark UI - Creates Enhanced FAQs"""

    # Initialize enhanced FAQ manager for new FAQs
    enhanced_manager = EnhancedFAQManager()

    # Minimal dark theme CSS
    st.markdown("""
    <style>
    .stApp {
        background-color: #1e1e1e;
        color: #ffffff;
    }
    
    .main-title {
        text-align: center;
        color: #ffffff;
        font-size: 1.8rem;
        font-weight: 500;
        margin-bottom: 1rem;
    }

    .subtitle {
        text-align: center;
        color: #cccccc;
        font-size: 0.9rem;
        margin-bottom: 2rem;
    }

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

    .stButton > button[data-baseweb="button"][kind="primary"] {
        background-color: #000000;
        color: #ffffff;
        border: 1px solid #333333;
    }

    .stButton > button[data-baseweb="button"][kind="primary"]:hover {
        background-color: #222222;
        border-color: #444444;
    }

    .stTextArea > div > div > textarea {
        background-color: #2a2a2a;
        color: #ffffff;
        border: 1px solid #555555;
        border-radius: 4px;
    }

    .stTextInput > div > div > input {
        background-color: #2a2a2a;
        color: #ffffff;
        border: 1px solid #555555;
        border-radius: 4px;
    }

    .stSelectbox > div > div > div {
        background-color: #2a2a2a;
        color: #ffffff;
        border: 1px solid #555555;
    }
    </style>
    """, unsafe_allow_html=True)

    # Clean header
    st.markdown('<h1 class="main-title">Create FAQ</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">FAQ Creation for The Hire Hub ATS</p>', unsafe_allow_html=True)

    # Simple mode selection
    if ai_helper.is_configured():
        st.markdown("### Choose Creation Method")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("AI-Powered Creation", type="primary", use_container_width=True):
                st.session_state.creation_mode = "ai"
                st.rerun()
                
        with col2:
            if st.button("Manual Creation", use_container_width=True):
                st.session_state.creation_mode = "manual"
                st.rerun()
                
        st.markdown("---")
    else:
        st.info("Set OPENAI_API_KEY environment variable to enable AI features")
        st.session_state.creation_mode = "manual"

    # Handle creation modes
    if hasattr(st.session_state, 'creation_mode'):
        if st.session_state.creation_mode == "ai":
            render_ai_creation(enhanced_manager, ai_helper)
        elif st.session_state.creation_mode == "manual":
            render_manual_creation(enhanced_manager, ai_helper)
    else:
        st.markdown("### Welcome")
        st.markdown("Choose a creation method above to get started.")


def render_ai_creation(enhanced_manager: EnhancedFAQManager, ai_helper: AIHelper):
    """AI-assisted Enhanced FAQ creation"""

    # Clean up any old session state
    if 'generated_faqs' in st.session_state:
        del st.session_state.generated_faqs

    # AI creation header
    st.markdown("### AI-Powered Enhanced FAQ Creation")
    st.markdown("*Creating professional structured FAQs for The Hire Hub ATS system*")

    # Show any existing generated FAQs first
    if 'generated_enhanced_faqs' in st.session_state and st.session_state.generated_enhanced_faqs:
        st.info(f"📝 You have {len(st.session_state.generated_enhanced_faqs)} generated enhanced FAQs ready to edit and save!")
        render_enhanced_faqs_editor(enhanced_manager)
        return

    # Topic-based generation
    st.markdown("#### Topic-Based FAQ Generation")
    
    topic = st.text_input(
        "Enter a topic for The Hire Hub ATS:",
        placeholder="candidate tracking, resume parsing, interview scheduling, reporting, analytics"
    )

    if st.button("Generate Enhanced FAQs", type="primary"):
        if topic.strip():
            try:
                with st.spinner("Generating Enhanced FAQs..."):
                    # Get existing FAQs for context (from both old and new systems)
                    from models import FAQManager
                    old_faq_manager = FAQManager()
                    existing_faqs = old_faq_manager.get_all_faqs()

                    st.info(f"📚 Using {len(existing_faqs)} existing FAQs for context")

                    # Generate basic FAQs first
                    generated_faqs = ai_helper.generate_faq_from_topic(topic.strip(), existing_faqs)

                    if generated_faqs:
                        st.success(f"✅ Generated {len(generated_faqs)} basic FAQs")

                        # Convert to enhanced format with AI
                        enhanced_faqs = []
                        for i, faq in enumerate(generated_faqs, 1):
                            with st.spinner(f"Enhancing FAQ {i}/{len(generated_faqs)}: {faq.question[:50]}..."):
                                try:
                                    enhanced_data = ai_helper.enhance_faq_to_structured_format(faq.question, faq.answer)

                                    if enhanced_data:
                                        enhanced_faq = EnhancedFAQ(
                                            question=faq.question,
                                            answer=faq.answer,
                                            category=enhanced_data.get('category', 'general'),
                                            tags=enhanced_data.get('tags', []),
                                            alternate_questions=enhanced_data.get('alternate_questions', [])
                                        )
                                        enhanced_faqs.append(enhanced_faq)
                                        st.success(f"✅ Enhanced FAQ {i}: {enhanced_faq.id}")
                                    else:
                                        st.warning(f"⚠️ Failed to enhance FAQ {i}, using basic format")
                                        # Create basic enhanced FAQ without AI enhancement
                                        enhanced_faq = EnhancedFAQ(
                                            question=faq.question,
                                            answer=faq.answer,
                                            category='general',
                                            tags=[],
                                            alternate_questions=[]
                                        )
                                        enhanced_faqs.append(enhanced_faq)
                                except Exception as e:
                                    st.error(f"❌ Error enhancing FAQ {i}: {str(e)}")
                                    # Create basic enhanced FAQ as fallback
                                    enhanced_faq = EnhancedFAQ(
                                        question=faq.question,
                                        answer=faq.answer,
                                        category='general',
                                        tags=[],
                                        alternate_questions=[]
                                    )
                                    enhanced_faqs.append(enhanced_faq)

                        if enhanced_faqs:
                            st.success(f"🎉 Success! Generated {len(enhanced_faqs)} Enhanced FAQs! Review and edit them below before saving.")
                            st.session_state.generated_enhanced_faqs = enhanced_faqs
                            render_enhanced_faqs_editor(enhanced_manager)
                        else:
                            st.error("❌ Failed to create any enhanced FAQs.")
                    else:
                        st.error("❌ Failed to generate basic FAQs. Please try again.")
            except Exception as e:
                st.error(f"❌ Unexpected error during FAQ generation: {str(e)}")
                import traceback
                st.error(f"Traceback: {traceback.format_exc()}")
        else:
            st.warning("Please enter a topic first.")

    # Question-based generation
    st.markdown("---")
    st.markdown("#### Question-Based FAQ Generation")
    
    question = st.text_input(
        "Enter your question:",
        placeholder="How do I track candidate applications?"
    )

    if st.button("Generate Enhanced Answer", type="primary"):
        if question.strip():
            try:
                with st.spinner("Generating enhanced answer..."):
                    # Get existing FAQs for context
                    from models import FAQManager
                    old_faq_manager = FAQManager()
                    existing_faqs = old_faq_manager.get_all_faqs()

                    answer = ai_helper.generate_answer_for_question(question.strip(), existing_faqs)

                    if answer:
                        st.success("✅ Answer generated successfully!")

                        # Enhance the FAQ with AI
                        with st.spinner("Creating enhanced structure..."):
                            try:
                                enhanced_data = ai_helper.enhance_faq_to_structured_format(question.strip(), answer)

                                if enhanced_data:
                                    enhanced_faq = EnhancedFAQ(
                                        question=question.strip(),
                                        answer=answer,
                                        category=enhanced_data.get('category', 'general'),
                                        tags=enhanced_data.get('tags', []),
                                        alternate_questions=enhanced_data.get('alternate_questions', [])
                                    )

                                    st.success("🎉 Perfect Enhanced FAQ Generated! Review and edit below before saving.")
                                    st.session_state.generated_enhanced_faqs = [enhanced_faq]
                                    render_enhanced_faqs_editor(enhanced_manager)
                                else:
                                    st.warning("⚠️ Failed to enhance structure, creating basic enhanced FAQ")
                                    # Create basic enhanced FAQ as fallback
                                    enhanced_faq = EnhancedFAQ(
                                        question=question.strip(),
                                        answer=answer,
                                        category='general',
                                        tags=[],
                                        alternate_questions=[]
                                    )
                                    st.session_state.generated_enhanced_faqs = [enhanced_faq]
                                    render_enhanced_faqs_editor(enhanced_manager)
                            except Exception as e:
                                st.error(f"❌ Error enhancing FAQ structure: {str(e)}")
                                # Create basic enhanced FAQ as fallback
                                enhanced_faq = EnhancedFAQ(
                                    question=question.strip(),
                                    answer=answer,
                                    category='general',
                                    tags=[],
                                    alternate_questions=[]
                                )
                                st.session_state.generated_enhanced_faqs = [enhanced_faq]
                                render_enhanced_faqs_editor(enhanced_manager)
                    else:
                        st.error("❌ Failed to generate answer. Please try again.")
            except Exception as e:
                st.error(f"❌ Unexpected error during answer generation: {str(e)}")
                import traceback
                st.error(f"Traceback: {traceback.format_exc()}")
        else:
            st.warning("Please enter a question first.")

    # Back button
    if st.button("Back to Mode Selection"):
        if 'creation_mode' in st.session_state:
            del st.session_state.creation_mode
        if 'generated_enhanced_faqs' in st.session_state:
            del st.session_state.generated_enhanced_faqs
        if 'generated_faqs' in st.session_state:  # Clean up old key too
            del st.session_state.generated_faqs
        st.rerun()


def render_enhanced_faqs_editor(enhanced_manager: EnhancedFAQManager):
    """Editor for enhanced generated FAQs"""

    st.markdown("---")
    st.markdown("### Review & Perfect Your Enhanced FAQs")
    st.markdown("*Edit the AI-generated enhanced content with categories, tags, and alternate questions*")

    if 'generated_enhanced_faqs' in st.session_state and st.session_state.generated_enhanced_faqs:
        for i, enhanced_faq in enumerate(st.session_state.generated_enhanced_faqs):
            with st.expander(f"Enhanced FAQ {i+1}: {enhanced_faq.question[:50]}...", expanded=True):

                # Show the generated ID
                st.markdown(f"**Generated ID:** `{enhanced_faq.id}`")

                # Editable fields
                col1, col2 = st.columns(2)

                with col1:
                    edited_category = st.selectbox(
                        "Category:",
                        options=["dashboard", "candidate_management", "job_posting", "interview_scheduling",
                                "resume_applications", "analytics_reporting", "team_collaboration",
                                "ai_features", "integrations", "account_settings", "general"],
                        index=0 if enhanced_faq.category == "dashboard" else
                              (["dashboard", "candidate_management", "job_posting", "interview_scheduling",
                                "resume_applications", "analytics_reporting", "team_collaboration",
                                "ai_features", "integrations", "account_settings", "general"].index(enhanced_faq.category)
                               if enhanced_faq.category in ["dashboard", "candidate_management", "job_posting", "interview_scheduling",
                                                           "resume_applications", "analytics_reporting", "team_collaboration",
                                                           "ai_features", "integrations", "account_settings", "general"] else 10),
                        key=f"category_{i}"
                    )

                with col2:
                    edited_tags = st.text_input(
                        "Tags (comma-separated):",
                        value=", ".join(enhanced_faq.tags),
                        key=f"tags_{i}",
                        placeholder="tag1, tag2, tag3"
                    )

                edited_question = st.text_input(
                    "Question:",
                    value=enhanced_faq.question,
                    key=f"enhanced_question_{i}",
                    placeholder="Enter your question here..."
                )

                edited_answer = st.text_area(
                    "Answer:",
                    value=enhanced_faq.answer,
                    key=f"enhanced_answer_{i}",
                    height=150,
                    placeholder="Enter your answer here..."
                )

                # Alternate questions
                st.markdown("**Alternate Questions:**")
                edited_alt_questions = []
                for j, alt_q in enumerate(enhanced_faq.alternate_questions):
                    alt_question = st.text_input(
                        f"Alternate Question {j+1}:",
                        value=alt_q,
                        key=f"alt_q_{i}_{j}",
                        placeholder="Alternative way to ask this question..."
                    )
                    if alt_question.strip():
                        edited_alt_questions.append(alt_question.strip())

                if st.button(f"Save Enhanced FAQ", key=f"save_enhanced_{i}", type="primary", use_container_width=True):
                    if edited_question.strip() and edited_answer.strip():
                        # Parse tags
                        tags_list = [tag.strip() for tag in edited_tags.split(",") if tag.strip()]

                        # Create updated enhanced FAQ
                        updated_enhanced_faq = EnhancedFAQ(
                            question=edited_question.strip(),
                            answer=edited_answer.strip(),
                            category=edited_category,
                            tags=tags_list,
                            alternate_questions=edited_alt_questions
                        )

                        if enhanced_manager.add_enhanced_faq(updated_enhanced_faq):
                            st.success(f"Enhanced FAQ #{i+1} Saved! Added to your enhanced knowledge base.")
                            st.balloons()

                            # Show the saved structure
                            with st.expander("View Saved Structure", expanded=False):
                                st.json(updated_enhanced_faq.to_dict())
                        else:
                            st.error("Enhanced FAQ already exists!")
                    else:
                        st.warning("Please fill in both question and answer.")


def render_manual_creation(enhanced_manager: EnhancedFAQManager, ai_helper: AIHelper):
    """Manual Enhanced FAQ creation"""

    st.markdown("### Manual Enhanced FAQ Creation")
    st.markdown("*Create your own custom enhanced FAQ with categories, tags, and alternate questions*")

    # Basic fields
    question = st.text_input(
        "Question:",
        placeholder="Enter your question here..."
    )

    answer = st.text_area(
        "Answer:",
        height=200,
        placeholder="Enter your answer here..."
    )

    # Enhanced fields
    col1, col2 = st.columns(2)

    with col1:
        category = st.selectbox(
            "Category:",
            options=["dashboard", "candidate_management", "job_posting", "interview_scheduling",
                    "resume_applications", "analytics_reporting", "team_collaboration",
                    "ai_features", "integrations", "account_settings", "general"],
            index=10  # Default to "general"
        )

    with col2:
        tags_input = st.text_input(
            "Tags (comma-separated):",
            placeholder="tag1, tag2, tag3"
        )

    # Alternate questions
    st.markdown("**Alternate Questions** *(Optional - or use AI to generate)*")
    alt_questions = []
    for i in range(5):  # Allow up to 5 alternate questions
        alt_q = st.text_input(
            f"Alternate Question {i+1}:",
            key=f"manual_alt_q_{i}",
            placeholder="Alternative way to ask this question..."
        )
        if alt_q.strip():
            alt_questions.append(alt_q.strip())

    # AI assistance for manual creation
    if ai_helper.is_configured() and question.strip() and answer.strip():
        if st.button("🤖 Auto-Generate Enhanced Fields", use_container_width=True):
            with st.spinner("Generating enhanced fields with AI..."):
                enhanced_data = ai_helper.enhance_faq_to_structured_format(question.strip(), answer.strip())

                if enhanced_data:
                    st.session_state.ai_suggested_category = enhanced_data.get('category', 'general')
                    st.session_state.ai_suggested_tags = ", ".join(enhanced_data.get('tags', []))
                    st.session_state.ai_suggested_alt_questions = enhanced_data.get('alternate_questions', [])
                    st.success("AI suggestions generated! Check the fields above.")
                    st.rerun()

    # Show AI suggestions if available
    if 'ai_suggested_category' in st.session_state:
        st.markdown("**🤖 AI Suggestions:**")
        st.info(f"**Category:** {st.session_state.ai_suggested_category}")
        st.info(f"**Tags:** {st.session_state.ai_suggested_tags}")
        if st.session_state.ai_suggested_alt_questions:
            st.info(f"**Alternate Questions:** {', '.join(st.session_state.ai_suggested_alt_questions[:3])}...")

    col1, col2 = st.columns([3, 1])

    with col1:
        if st.button("Save Enhanced FAQ", type="primary", use_container_width=True):
            if question.strip() and answer.strip():
                # Parse tags
                tags_list = [tag.strip() for tag in tags_input.split(",") if tag.strip()]

                # Create enhanced FAQ
                enhanced_faq = EnhancedFAQ(
                    question=question.strip(),
                    answer=answer.strip(),
                    category=category,
                    tags=tags_list,
                    alternate_questions=alt_questions
                )

                if enhanced_manager.add_enhanced_faq(enhanced_faq):
                    st.success("Enhanced FAQ saved successfully!")
                    st.balloons()

                    # Show the saved structure
                    with st.expander("View Saved Enhanced FAQ", expanded=False):
                        st.json(enhanced_faq.to_dict())

                    # Clear AI suggestions
                    for key in ['ai_suggested_category', 'ai_suggested_tags', 'ai_suggested_alt_questions']:
                        if key in st.session_state:
                            del st.session_state[key]

                    # Clear the form
                    st.rerun()
                else:
                    st.error("This Enhanced FAQ already exists!")
            else:
                st.warning("Please fill in both question and answer.")

    with col2:
        if st.button("Back", use_container_width=True):
            if 'creation_mode' in st.session_state:
                del st.session_state.creation_mode
            # Clear AI suggestions
            for key in ['ai_suggested_category', 'ai_suggested_tags', 'ai_suggested_alt_questions']:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()
