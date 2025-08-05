"""
Enhanced FAQ Management Page
Comprehensive listing, viewing, editing, and management of enhanced FAQs
"""

import streamlit as st
from models import EnhancedFAQ, EnhancedFAQManager
from ai_helper import AIHelper
import json


def render_enhanced_faqs_page(ai_helper: AIHelper):
    """Enhanced FAQ management page with listing, editing, and advanced features"""
    
    # Initialize enhanced FAQ manager
    enhanced_manager = EnhancedFAQManager()
    
    st.header("🔹 Enhanced FAQ Management")
    st.markdown("*Manage your structured FAQs with categories, tags, and alternate questions*")
    
    # Get all enhanced FAQs
    enhanced_faqs = enhanced_manager.get_all_enhanced_faqs()
    
    # Top controls
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        # Search functionality
        search = st.text_input(
            "🔍 Search Enhanced FAQs", 
            placeholder="Search questions, answers, tags, or alternate questions..."
        )
    
    with col2:
        # Category filter
        categories = ["All"] + list(set([faq.category for faq in enhanced_faqs]))
        selected_category = st.selectbox("📂 Filter by Category", categories)
    
    with col3:
        # Download enhanced FAQs
        if enhanced_faqs:
            enhanced_json = enhanced_manager.export_to_json()
            st.download_button(
                label="📥 Download Enhanced JSON",
                data=enhanced_json,
                file_name="hire_hub_enhanced_faqs.json",
                mime="application/json",
                use_container_width=True
            )
    
    # Filter FAQs
    filtered_faqs = enhanced_faqs
    
    # Apply category filter
    if selected_category != "All":
        filtered_faqs = [faq for faq in filtered_faqs if faq.category == selected_category]
    
    # Apply search filter
    if search:
        search_results = []
        search_lower = search.lower()
        for faq in filtered_faqs:
            if (search_lower in faq.question.lower() or
                search_lower in faq.answer.lower() or
                any(search_lower in tag.lower() for tag in faq.tags) or
                any(search_lower in alt_q.lower() for alt_q in faq.alternate_questions)):
                search_results.append(faq)
        filtered_faqs = search_results
    
    # Display stats and bulk operations
    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        st.markdown(f"**Showing {len(filtered_faqs)} of {len(enhanced_faqs)} Enhanced FAQs**")

    with col2:
        if enhanced_faqs:
            if st.button("📊 View Analytics", use_container_width=True):
                st.session_state.show_analytics = True
                st.rerun()

    with col3:
        if enhanced_faqs:
            if st.button("🔄 Bulk Operations", use_container_width=True):
                st.session_state.show_bulk_ops = True
                st.rerun()

    if not enhanced_faqs:
        st.info("🚀 No enhanced FAQs found. Create your first enhanced FAQ!")
        if st.button("Create First Enhanced FAQ", type="primary"):
            st.session_state.current_page = "Create FAQ"
            st.rerun()
        return

    # Show analytics if requested
    if st.session_state.get('show_analytics', False):
        render_enhanced_analytics(enhanced_faqs)

    # Show bulk operations if requested
    if st.session_state.get('show_bulk_ops', False):
        render_bulk_operations(enhanced_manager, enhanced_faqs)
    
    # Display enhanced FAQs
    for i, faq in enumerate(filtered_faqs):
        with st.expander(f"🔹 {faq.question}", expanded=False):
            # Main content
            col1, col2 = st.columns([3, 1])

            with col1:
                st.markdown(f"**Answer:** {faq.answer}")

                # Enhanced fields
                col1a, col1b = st.columns(2)
                with col1a:
                    st.markdown(f"**Category:** `{faq.category}`")
                    st.markdown(f"**ID:** `{faq.id}`")

                with col1b:
                    if faq.tags:
                        tags_display = ", ".join([f"`{tag}`" for tag in faq.tags])
                        st.markdown(f"**Tags:** {tags_display}")

                # Alternate questions
                if faq.alternate_questions:
                    with st.expander("🔄 Alternate Questions", expanded=False):
                        for j, alt_q in enumerate(faq.alternate_questions, 1):
                            st.write(f"{j}. {alt_q}")

            with col2:
                # Action buttons
                edit_key = f"edit_enhanced_{i}"
                if st.button("✏️ Edit", key=edit_key, use_container_width=True):
                    # Set editing state with unique identifier
                    st.session_state.editing_faq_id = faq.id
                    st.session_state.editing_faq_data = faq
                    st.rerun()

                if st.button("🗑️ Delete", key=f"delete_enhanced_{i}", use_container_width=True):
                    st.session_state.deleting_enhanced_faq = faq
                    st.session_state.show_delete_confirmation = True
                    st.rerun()

                if st.button("📋 Copy JSON", key=f"copy_enhanced_{i}", use_container_width=True):
                    st.session_state.show_json_modal = faq
                    st.rerun()

        # Show editor right after this FAQ if it's being edited
        if (st.session_state.get('editing_faq_id') == faq.id and
            st.session_state.get('editing_faq_data') is not None):
            st.markdown("---")
            st.markdown("### ✏️ Edit Enhanced FAQ")
            st.markdown(f"*Editing: {faq.question[:60]}...*")

            render_inline_enhanced_editor(enhanced_manager, faq, ai_helper, i)
    
    # Editor is now rendered inline after the specific FAQ being edited
    
    # Delete Confirmation Modal
    if st.session_state.get('show_delete_confirmation', False):
        render_delete_confirmation(enhanced_manager)
    
    # JSON Display Modal
    if st.session_state.get('show_json_modal'):
        render_json_modal()


def render_inline_enhanced_editor(enhanced_manager: EnhancedFAQManager, faq: EnhancedFAQ, ai_helper: AIHelper, index: int):
    """Inline enhanced FAQ editor that renders immediately"""

    # Create form for editing
    with st.form(f"inline_edit_form_{faq.id}_{index}"):
        # Basic fields
        edited_question = st.text_input(
            "Question:",
            value=faq.question,
            placeholder="Enter your question here..."
        )

        edited_answer = st.text_area(
            "Answer:",
            value=faq.answer,
            height=150,
            placeholder="Enter your answer here..."
        )

        # Enhanced fields
        col1, col2 = st.columns(2)

        with col1:
            categories = ["dashboard", "candidate_management", "job_posting", "interview_scheduling",
                         "resume_applications", "analytics_reporting", "team_collaboration",
                         "ai_features", "integrations", "account_settings", "general"]

            current_category_index = categories.index(faq.category) if faq.category in categories else -1

            edited_category = st.selectbox(
                "Category:",
                options=categories,
                index=current_category_index if current_category_index >= 0 else len(categories) - 1
            )

        with col2:
            edited_tags = st.text_input(
                "Tags (comma-separated):",
                value=", ".join(faq.tags),
                placeholder="tag1, tag2, tag3"
            )

        # Alternate questions
        st.markdown("**Alternate Questions:**")
        edited_alt_questions = []

        # Show existing alternate questions + empty slots
        all_alt_questions = faq.alternate_questions + [""] * (5 - len(faq.alternate_questions))

        for j, alt_q in enumerate(all_alt_questions[:5]):
            alt_question = st.text_input(
                f"Alternate Question {j+1}:",
                value=alt_q,
                key=f"inline_alt_q_{faq.id}_{index}_{j}",
                placeholder="Alternative way to ask this question..."
            )
            if alt_question.strip():
                edited_alt_questions.append(alt_question.strip())

        # Form buttons
        col1, col2 = st.columns(2)

        with col1:
            submitted = st.form_submit_button("💾 Save Changes", type="primary", use_container_width=True)

        with col2:
            cancel = st.form_submit_button("❌ Cancel", use_container_width=True)

        # Handle form submission
        if submitted:
            if edited_question.strip() and edited_answer.strip():
                # Parse tags
                tags_list = [tag.strip() for tag in edited_tags.split(",") if tag.strip()]

                # Create updated enhanced FAQ with same ID
                updated_enhanced_faq = EnhancedFAQ(
                    question=edited_question.strip(),
                    answer=edited_answer.strip(),
                    category=edited_category,
                    tags=tags_list,
                    alternate_questions=edited_alt_questions,
                    id=faq.id  # Keep the same ID
                )

                # Update in manager (remove old, add new)
                enhanced_manager.faqs = [f for f in enhanced_manager.faqs if f.id != faq.id]

                if enhanced_manager.add_enhanced_faq(updated_enhanced_faq):
                    st.success("✅ Enhanced FAQ updated successfully!")
                    st.balloons()
                    # Clear editing state
                    if 'editing_faq_id' in st.session_state:
                        del st.session_state.editing_faq_id
                    if 'editing_faq_data' in st.session_state:
                        del st.session_state.editing_faq_data
                    st.rerun()
                else:
                    st.error("❌ Failed to update enhanced FAQ")
            else:
                st.error("Please fill in both question and answer fields.")

        if cancel:
            # Clear editing state
            if 'editing_faq_id' in st.session_state:
                del st.session_state.editing_faq_id
            if 'editing_faq_data' in st.session_state:
                del st.session_state.editing_faq_data
            st.rerun()


def render_enhanced_faq_editor(enhanced_manager: EnhancedFAQManager, ai_helper: AIHelper):
    """Enhanced FAQ editor modal"""

    if 'editing_enhanced_faq' not in st.session_state:
        st.error("No FAQ selected for editing")
        return

    faq = st.session_state.editing_enhanced_faq

    st.markdown("---")
    st.markdown("### ✏️ Edit Enhanced FAQ")
    st.markdown(f"*Editing: {faq.question[:60]}...*")
    
    # Create form for editing
    with st.form(f"enhanced_faq_edit_form_{faq.id}"):
        # Basic fields
        edited_question = st.text_input(
            "Question:",
            value=faq.question,
            placeholder="Enter your question here..."
        )
        
        edited_answer = st.text_area(
            "Answer:",
            value=faq.answer,
            height=150,
            placeholder="Enter your answer here..."
        )
        
        # Enhanced fields
        col1, col2 = st.columns(2)
        
        with col1:
            categories = ["dashboard", "candidate_management", "job_posting", "interview_scheduling", 
                         "resume_applications", "analytics_reporting", "team_collaboration", 
                         "ai_features", "integrations", "account_settings", "general"]
            
            current_category_index = categories.index(faq.category) if faq.category in categories else -1
            
            edited_category = st.selectbox(
                "Category:",
                options=categories,
                index=current_category_index if current_category_index >= 0 else len(categories) - 1
            )
        
        with col2:
            edited_tags = st.text_input(
                "Tags (comma-separated):",
                value=", ".join(faq.tags),
                placeholder="tag1, tag2, tag3"
            )
        
        # Alternate questions
        st.markdown("**Alternate Questions:**")
        edited_alt_questions = []
        
        # Show existing alternate questions + empty slots
        all_alt_questions = faq.alternate_questions + [""] * (5 - len(faq.alternate_questions))
        
        for j, alt_q in enumerate(all_alt_questions[:5]):
            alt_question = st.text_input(
                f"Alternate Question {j+1}:",
                value=alt_q,
                key=f"edit_alt_q_{faq.id}_{j}",
                placeholder="Alternative way to ask this question..."
            )
            if alt_question.strip():
                edited_alt_questions.append(alt_question.strip())
        
        # Form buttons
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            submitted = st.form_submit_button("💾 Save Changes", type="primary", use_container_width=True)
        
        with col2:
            if st.form_submit_button("🤖 AI Enhance", use_container_width=True):
                if ai_helper.is_configured() and edited_question.strip() and edited_answer.strip():
                    with st.spinner("Getting AI suggestions..."):
                        enhanced_data = ai_helper.enhance_faq_to_structured_format(
                            edited_question.strip(), 
                            edited_answer.strip()
                        )
                        
                        if enhanced_data:
                            st.session_state.ai_suggestions = enhanced_data
                            st.success("🤖 AI suggestions generated! Check the fields above.")
                            st.rerun()
        
        with col3:
            cancel = st.form_submit_button("❌ Cancel", use_container_width=True)
        
        # Handle form submission
        if submitted:
            if edited_question.strip() and edited_answer.strip():
                # Parse tags
                tags_list = [tag.strip() for tag in edited_tags.split(",") if tag.strip()]
                
                # Create updated enhanced FAQ with same ID
                updated_enhanced_faq = EnhancedFAQ(
                    question=edited_question.strip(),
                    answer=edited_answer.strip(),
                    category=edited_category,
                    tags=tags_list,
                    alternate_questions=edited_alt_questions,
                    id=faq.id  # Keep the same ID
                )
                
                # Update in manager (remove old, add new)
                enhanced_manager.faqs = [f for f in enhanced_manager.faqs if f.id != faq.id]
                
                if enhanced_manager.add_enhanced_faq(updated_enhanced_faq):
                    st.success("✅ Enhanced FAQ updated successfully!")
                    st.balloons()
                    
                    # Clear editor state
                    del st.session_state.editing_enhanced_faq
                    del st.session_state.show_enhanced_editor
                    st.rerun()
                else:
                    st.error("❌ Failed to update enhanced FAQ")
            else:
                st.error("Please fill in both question and answer fields.")
        
        if cancel:
            # Clear editor state
            del st.session_state.editing_enhanced_faq
            del st.session_state.show_enhanced_editor
            st.rerun()
    
    # Show AI suggestions if available
    if st.session_state.get('ai_suggestions'):
        suggestions = st.session_state.ai_suggestions
        st.markdown("### 🤖 AI Suggestions")
        st.info(f"**Suggested Category:** {suggestions.get('category', 'N/A')}")
        st.info(f"**Suggested Tags:** {', '.join(suggestions.get('tags', []))}")
        if suggestions.get('alternate_questions'):
            st.info(f"**Suggested Alternates:** {', '.join(suggestions.get('alternate_questions', [])[:3])}...")


def render_delete_confirmation(enhanced_manager: EnhancedFAQManager):
    """Delete confirmation modal for enhanced FAQs"""
    
    faq = st.session_state.deleting_enhanced_faq
    
    st.markdown("---")
    st.markdown("### 🗑️ Delete Enhanced FAQ")
    st.warning(f"Are you sure you want to delete this enhanced FAQ?")
    
    # Show FAQ details
    with st.expander("FAQ to Delete", expanded=True):
        st.markdown(f"**Question:** {faq.question}")
        st.markdown(f"**Category:** {faq.category}")
        st.markdown(f"**ID:** `{faq.id}`")
        if faq.tags:
            st.markdown(f"**Tags:** {', '.join(faq.tags)}")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🗑️ Yes, Delete", type="primary", use_container_width=True):
            # Remove from manager
            enhanced_manager.faqs = [f for f in enhanced_manager.faqs if f.id != faq.id]
            
            if enhanced_manager.save_faqs():
                st.success("✅ Enhanced FAQ deleted successfully!")
                
                # Clear delete state
                del st.session_state.deleting_enhanced_faq
                del st.session_state.show_delete_confirmation
                st.rerun()
            else:
                st.error("❌ Failed to delete enhanced FAQ")
    
    with col2:
        if st.button("❌ Cancel", use_container_width=True):
            # Clear delete state
            del st.session_state.deleting_enhanced_faq
            del st.session_state.show_delete_confirmation
            st.rerun()


def render_json_modal():
    """JSON display modal for enhanced FAQs"""
    
    faq = st.session_state.show_json_modal
    
    st.markdown("---")
    st.markdown("### 📋 Enhanced FAQ JSON Structure")
    st.markdown(f"*JSON structure for: {faq.question[:60]}...*")
    
    # Display JSON
    st.json(faq.to_dict())
    
    # Copy to clipboard (show the JSON as text for easy copying)
    st.markdown("**Copy this JSON:**")
    st.code(json.dumps(faq.to_dict(), indent=2), language="json")
    
    if st.button("❌ Close", use_container_width=True):
        del st.session_state.show_json_modal
        st.rerun()


def render_enhanced_analytics(enhanced_faqs):
    """Analytics dashboard for enhanced FAQs"""

    st.markdown("---")
    st.markdown("### 📊 Enhanced FAQ Analytics")

    # Category distribution
    categories = {}
    tags = {}
    total_alt_questions = 0

    for faq in enhanced_faqs:
        # Count categories
        categories[faq.category] = categories.get(faq.category, 0) + 1

        # Count tags
        for tag in faq.tags:
            tags[tag] = tags.get(tag, 0) + 1

        # Count alternate questions
        total_alt_questions += len(faq.alternate_questions)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total Enhanced FAQs", len(enhanced_faqs))
        st.metric("Total Categories", len(categories))

    with col2:
        st.metric("Total Tags", len(tags))
        st.metric("Avg Alt Questions", round(total_alt_questions / len(enhanced_faqs), 1) if enhanced_faqs else 0)

    with col3:
        most_common_category = max(categories.items(), key=lambda x: x[1]) if categories else ("N/A", 0)
        st.metric("Top Category", f"{most_common_category[0]} ({most_common_category[1]})")

    # Category breakdown
    st.markdown("#### 📂 Category Distribution")
    for category, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / len(enhanced_faqs)) * 100
        st.write(f"**{category}**: {count} FAQs ({percentage:.1f}%)")

    # Top tags
    if tags:
        st.markdown("#### 🏷️ Most Used Tags")
        top_tags = sorted(tags.items(), key=lambda x: x[1], reverse=True)[:10]
        for tag, count in top_tags:
            st.write(f"**{tag}**: {count} uses")

    if st.button("❌ Close Analytics"):
        del st.session_state.show_analytics
        st.rerun()


def render_bulk_operations(enhanced_manager: EnhancedFAQManager, enhanced_faqs):
    """Bulk operations for enhanced FAQs"""

    st.markdown("---")
    st.markdown("### 🔄 Bulk Operations")

    # Bulk category update
    st.markdown("#### 📂 Bulk Category Update")
    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        new_category = st.selectbox(
            "New Category:",
            ["dashboard", "candidate_management", "job_posting", "interview_scheduling",
             "resume_applications", "analytics_reporting", "team_collaboration",
             "ai_features", "integrations", "account_settings", "general"]
        )

    with col2:
        old_category = st.selectbox(
            "From Category:",
            ["All"] + list(set([faq.category for faq in enhanced_faqs]))
        )

    with col3:
        if st.button("🔄 Update Categories"):
            count = 0
            for faq in enhanced_faqs:
                if old_category == "All" or faq.category == old_category:
                    faq.category = new_category
                    count += 1

            if enhanced_manager.save_faqs():
                st.success(f"✅ Updated {count} FAQs to category '{new_category}'")
            else:
                st.error("❌ Failed to update categories")

    # Bulk tag operations
    st.markdown("#### 🏷️ Bulk Tag Operations")
    col1, col2 = st.columns(2)

    with col1:
        add_tags = st.text_input("Add Tags (comma-separated):", placeholder="new_tag1, new_tag2")
        if st.button("➕ Add Tags to All"):
            if add_tags.strip():
                new_tags = [tag.strip() for tag in add_tags.split(",") if tag.strip()]
                for faq in enhanced_faqs:
                    for tag in new_tags:
                        if tag not in faq.tags:
                            faq.tags.append(tag)

                if enhanced_manager.save_faqs():
                    st.success(f"✅ Added tags {new_tags} to all FAQs")
                else:
                    st.error("❌ Failed to add tags")

    with col2:
        remove_tag = st.text_input("Remove Tag:", placeholder="tag_to_remove")
        if st.button("➖ Remove Tag from All"):
            if remove_tag.strip():
                count = 0
                for faq in enhanced_faqs:
                    if remove_tag.strip() in faq.tags:
                        faq.tags.remove(remove_tag.strip())
                        count += 1

                if enhanced_manager.save_faqs():
                    st.success(f"✅ Removed tag '{remove_tag}' from {count} FAQs")
                else:
                    st.error("❌ Failed to remove tag")

    # Export options
    st.markdown("#### 📤 Export Options")
    col1, col2 = st.columns(2)

    with col1:
        # Export by category
        export_category = st.selectbox(
            "Export Category:",
            ["All"] + list(set([faq.category for faq in enhanced_faqs])),
            key="export_category"
        )

        if st.button("📥 Export Category"):
            if export_category == "All":
                export_faqs = enhanced_faqs
            else:
                export_faqs = [faq for faq in enhanced_faqs if faq.category == export_category]

            export_data = json.dumps([faq.to_dict() for faq in export_faqs], indent=2)
            st.download_button(
                label=f"Download {export_category} FAQs",
                data=export_data,
                file_name=f"hire_hub_{export_category}_faqs.json",
                mime="application/json"
            )

    with col2:
        # Export with specific tags
        export_tags = st.text_input("Export FAQs with Tags:", placeholder="tag1, tag2")

        if st.button("📥 Export by Tags"):
            if export_tags.strip():
                tag_list = [tag.strip().lower() for tag in export_tags.split(",")]
                export_faqs = []
                for faq in enhanced_faqs:
                    if any(tag.lower() in [t.lower() for t in faq.tags] for tag in tag_list):
                        export_faqs.append(faq)

                if export_faqs:
                    export_data = json.dumps([faq.to_dict() for faq in export_faqs], indent=2)
                    st.download_button(
                        label=f"Download Tagged FAQs",
                        data=export_data,
                        file_name=f"hire_hub_tagged_faqs.json",
                        mime="application/json"
                    )
                else:
                    st.warning("No FAQs found with those tags")

    if st.button("❌ Close Bulk Operations"):
        del st.session_state.show_bulk_ops
        st.rerun()
