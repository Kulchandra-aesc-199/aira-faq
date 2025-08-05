import streamlit as st
import json
import pandas as pd
from datetime import datetime
import os
import openai
from typing import List, Dict, Optional
import time

# Page configuration
st.set_page_config(
    page_title="AIRA FAQ Manager Pro",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Constants
FAQ_FILE = "faq.json"
OPENAI_API_KEY_FILE = "openai_key.txt"

# Custom CSS for better styling
st.markdown("""
<style>
    .stButton > button {
        border-radius: 10px;
        border: 2px solid #ff6b6b;
        background-color: transparent;
        color: #ff6b6b;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        background-color: #ff6b6b;
        color: white;
        transform: translateY(-2px);
    }
    .success-box {
        padding: 1rem;
        border-radius: 10px;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        margin: 1rem 0;
    }
    .warning-box {
        padding: 1rem;
        border-radius: 10px;
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        color: #856404;
        margin: 1rem 0;
    }
    .info-box {
        padding: 1rem;
        border-radius: 10px;
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        color: #0c5460;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

class OpenAIHelper:
    def __init__(self):
        self.client = None
        self.api_key = self.load_api_key()
        if self.api_key:
            self.client = openai.OpenAI(api_key=self.api_key)
    
    def load_api_key(self) -> Optional[str]:
        """Load OpenAI API key from file or session state"""
        if 'openai_api_key' in st.session_state:
            return st.session_state.openai_api_key
        
        try:
            if os.path.exists(OPENAI_API_KEY_FILE):
                with open(OPENAI_API_KEY_FILE, 'r') as f:
                    key = f.read().strip()
                    st.session_state.openai_api_key = key
                    return key
        except Exception:
            pass
        return None
    
    def save_api_key(self, api_key: str):
        """Save API key to file and session state"""
        try:
            with open(OPENAI_API_KEY_FILE, 'w') as f:
                f.write(api_key)
            st.session_state.openai_api_key = api_key
            self.api_key = api_key
            self.client = openai.OpenAI(api_key=api_key)
            return True
        except Exception as e:
            st.error(f"Error saving API key: {str(e)}")
            return False
    
    def is_configured(self) -> bool:
        """Check if OpenAI is properly configured"""
        return self.client is not None and self.api_key is not None
    
    def enhance_question(self, question: str) -> str:
        """Enhance a question to make it clearer and more comprehensive"""
        if not self.is_configured():
            return question
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert at improving FAQ questions. Make them clearer, more specific, and comprehensive while maintaining the original intent. Return only the improved question."},
                    {"role": "user", "content": f"Improve this FAQ question: {question}"}
                ],
                max_tokens=150,
                temperature=0.7
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            st.error(f"Error enhancing question: {str(e)}")
            return question
    
    def enhance_answer(self, question: str, answer: str) -> str:
        """Enhance an answer to make it more detailed and helpful"""
        if not self.is_configured():
            return answer
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert at writing comprehensive FAQ answers. Improve the given answer to be more detailed, helpful, and professional while maintaining accuracy. Format with clear structure and bullet points where appropriate."},
                    {"role": "user", "content": f"Question: {question}\n\nImprove this answer: {answer}"}
                ],
                max_tokens=300,
                temperature=0.7
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            st.error(f"Error enhancing answer: {str(e)}")
            return answer
    
    def generate_related_questions(self, faq_data: List[Dict], count: int = 5) -> List[str]:
        """Generate related questions based on existing FAQ data"""
        if not self.is_configured() or not faq_data:
            return []
        
        try:
            # Sample some questions to provide context
            sample_questions = [item['question'] for item in faq_data[:10]]
            context = "\n".join(sample_questions)
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": f"Based on these existing FAQ questions, generate {count} new, related questions that users might ask. Make them specific and relevant. Return only the questions, one per line."},
                    {"role": "user", "content": f"Existing questions:\n{context}"}
                ],
                max_tokens=200,
                temperature=0.8
            )
            
            questions = response.choices[0].message.content.strip().split('\n')
            return [q.strip('- ').strip() for q in questions if q.strip()][:count]
        except Exception as e:
            st.error(f"Error generating questions: {str(e)}")
            return []
    
    def generate_answer_for_question(self, question: str, context_faqs: List[Dict] = None) -> str:
        """Generate an answer for a given question"""
        if not self.is_configured():
            return ""
        
        try:
            context = ""
            if context_faqs:
                sample_faqs = context_faqs[:5]
                context = "\n".join([f"Q: {faq['question']}\nA: {faq['answer']}" for faq in sample_faqs])
                context = f"\n\nContext from existing FAQs:\n{context}"
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": f"You are an expert at writing comprehensive FAQ answers. Provide a detailed, helpful answer to the question. Use clear structure and bullet points where appropriate.{context}"},
                    {"role": "user", "content": question}
                ],
                max_tokens=300,
                temperature=0.7
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            st.error(f"Error generating answer: {str(e)}")
            return ""

def load_faq_data():
    """Load FAQ data from JSON file"""
    try:
        with open(FAQ_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        st.warning(f"FAQ file '{FAQ_FILE}' not found! Creating a new one...")
        return []
    except json.JSONDecodeError:
        st.error("Error reading FAQ file. Invalid JSON format!")
        return []

def save_faq_data(data):
    """Save FAQ data to JSON file"""
    try:
        # Create backup
        if os.path.exists(FAQ_FILE):
            backup_name = f"faq_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(FAQ_FILE, 'r', encoding='utf-8') as f:
                backup_data = f.read()
            with open(backup_name, 'w', encoding='utf-8') as f:
                f.write(backup_data)
        
        # Save new data
        with open(FAQ_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        st.error(f"Error saving FAQ data: {str(e)}")
        return False

def setup_openai_config():
    """Setup OpenAI configuration in sidebar"""
    st.sidebar.markdown("---")
    st.sidebar.subheader("🤖 AI Enhancement")
    
    ai_helper = OpenAIHelper()
    
    if not ai_helper.is_configured():
        st.sidebar.warning("OpenAI not configured")
        api_key = st.sidebar.text_input("OpenAI API Key:", type="password", help="Enter your OpenAI API key to enable AI features")
        if st.sidebar.button("Save API Key"):
            if api_key:
                if ai_helper.save_api_key(api_key):
                    st.sidebar.success("API Key saved!")
                    st.rerun()
            else:
                st.sidebar.error("Please enter a valid API key")
    else:
        st.sidebar.success("✅ AI features enabled")
        if st.sidebar.button("Remove API Key"):
            if os.path.exists(OPENAI_API_KEY_FILE):
                os.remove(OPENAI_API_KEY_FILE)
            if 'openai_api_key' in st.session_state:
                del st.session_state.openai_api_key
            st.rerun()
    
    return ai_helper

def main():
    st.title("🤖 AIRA FAQ Manager Pro")
    st.markdown("*Enhanced with AI-powered question and answer improvements*")
    st.markdown("---")
    
    # Setup OpenAI
    ai_helper = setup_openai_config()
    
    # Load FAQ data
    faq_data = load_faq_data()
    
    # Sidebar navigation
    st.sidebar.title("📋 Navigation")
    page = st.sidebar.radio(
        "Choose a page:",
        ["🏠 Home", "📖 View All FAQs", "➕ Add New FAQ", "✏️ Edit FAQ", "🗑️ Delete FAQ", "📊 FAQ Statistics", "🎯 AI Suggestions"]
    )
    
    if page == "🏠 Home":
        show_home(faq_data, ai_helper)
    elif page == "📖 View All FAQs":
        view_all_faqs(faq_data)
    elif page == "➕ Add New FAQ":
        add_new_faq(faq_data, ai_helper)
    elif page == "✏️ Edit FAQ":
        edit_faq(faq_data, ai_helper)
    elif page == "🗑️ Delete FAQ":
        delete_faq(faq_data)
    elif page == "📊 FAQ Statistics":
        show_statistics(faq_data)
    elif page == "🎯 AI Suggestions":
        ai_suggestions(faq_data, ai_helper)

def show_home(faq_data, ai_helper):
    """Enhanced home page with overview and quick actions"""
    st.header("🏠 Welcome to AIRA FAQ Manager Pro")
    
    # Quick stats
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📚 Total FAQs", len(faq_data))
    with col2:
        ai_status = "✅ Enabled" if ai_helper.is_configured() else "❌ Disabled"
        st.metric("🤖 AI Features", ai_status)
    with col3:
        if faq_data:
            avg_length = sum(len(item['question']) + len(item['answer']) for item in faq_data) / len(faq_data)
            st.metric("📏 Avg FAQ Length", f"{avg_length:.0f} chars")
        else:
            st.metric("📏 Avg FAQ Length", "0 chars")
    with col4:
        if faq_data:
            recent_count = min(5, len(faq_data))
            st.metric("🆕 Recent FAQs", f"Last {recent_count}")
        else:
            st.metric("🆕 Recent FAQs", "0")
    
    st.markdown("---")
    
    # Recent FAQs preview
    if faq_data:
        st.subheader("🆕 Recent FAQs")
        recent_faqs = faq_data[-5:]  # Show last 5 FAQs
        for i, faq in enumerate(reversed(recent_faqs)):
            with st.expander(f"❓ {faq['question'][:80]}{'...' if len(faq['question']) > 80 else ''}"):
                st.write("**Question:**", faq['question'])
                st.write("**Answer:**", faq['answer'][:200] + "..." if len(faq['answer']) > 200 else faq['answer'])
    
    # Quick actions
    st.subheader("🚀 Quick Actions")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("➕ Add New FAQ", help="Create a new FAQ entry"):
            st.session_state.current_page = "➕ Add New FAQ"
            st.rerun()
    with col2:
        if st.button("🎯 AI Suggestions", help="Get AI-generated FAQ suggestions", disabled=not ai_helper.is_configured()):
            st.session_state.current_page = "🎯 AI Suggestions"
            st.rerun()
    with col3:
        if st.button("📊 View Statistics", help="View detailed FAQ analytics"):
            st.session_state.current_page = "📊 FAQ Statistics"
            st.rerun()

def view_all_faqs(faq_data):
    """Enhanced FAQ viewing with better search and filters"""
    st.header("📖 View All FAQs")
    
    if not faq_data:
        st.info("No FAQs available. Add some FAQs to get started!")
        return
    
    # Enhanced search and filters
    col1, col2 = st.columns([3, 1])
    with col1:
        search_term = st.text_input("🔍 Search FAQs:", placeholder="Enter keywords to search questions and answers...")
    with col2:
        search_in = st.selectbox("Search in:", ["Both", "Questions only", "Answers only"])
    
    col1, col2, col3 = st.columns(3)
    with col1:
        show_questions_only = st.checkbox("Show questions only")
    with col2:
        items_per_page = st.selectbox("Items per page:", [5, 10, 25, 50], index=1)
    with col3:
        sort_by = st.selectbox("Sort by:", ["Original order", "Question length", "Answer length"])
    
    # Filter and sort data
    filtered_data = faq_data.copy()
    
    if search_term:
        if search_in == "Questions only":
            filtered_data = [item for item in faq_data if search_term.lower() in item['question'].lower()]
        elif search_in == "Answers only":
            filtered_data = [item for item in faq_data if search_term.lower() in item['answer'].lower()]
        else:  # Both
            filtered_data = [
                item for item in faq_data 
                if search_term.lower() in item['question'].lower() or search_term.lower() in item['answer'].lower()
            ]
    
    # Sort data
    if sort_by == "Question length":
        filtered_data.sort(key=lambda x: len(x['question']), reverse=True)
    elif sort_by == "Answer length":
        filtered_data.sort(key=lambda x: len(x['answer']), reverse=True)
    
    st.markdown(f"**📊 Results:** {len(filtered_data)} of {len(faq_data)} FAQs")
    
    # Pagination
    if filtered_data:
        total_items = len(filtered_data)
        total_pages = (total_items - 1) // items_per_page + 1 if total_items > 0 else 1
        
        if total_pages > 1:
            page_num = st.selectbox("📄 Page:", range(1, total_pages + 1))
            start_idx = (page_num - 1) * items_per_page
            end_idx = min(start_idx + items_per_page, total_items)
            display_data = filtered_data[start_idx:end_idx]
            st.caption(f"Showing {start_idx + 1}-{end_idx} of {total_items} FAQs")
        else:
            display_data = filtered_data
        
        # Display FAQs
        for i, item in enumerate(display_data):
            original_index = faq_data.index(item)
            with st.expander(f"❓ {item['question'][:100]}{'...' if len(item['question']) > 100 else ''}"):
                st.markdown(f"**🔍 Question:**")
                st.write(item['question'])
                
                if not show_questions_only:
                    st.markdown(f"**💡 Answer:**")
                    st.write(item['answer'])
                
                st.caption(f"FAQ ID: {original_index + 1} | Q: {len(item['question'])} chars | A: {len(item['answer'])} chars")

def add_new_faq(faq_data, ai_helper):
    """Enhanced FAQ addition with AI assistance"""
    st.header("➕ Add New FAQ")
    
    # Tabs for different input methods
    tab1, tab2 = st.tabs(["✍️ Manual Entry", "🤖 AI Assisted"])
    
    with tab1:
        manual_add_faq(faq_data, ai_helper)
    
    with tab2:
        if ai_helper.is_configured():
            ai_assisted_add_faq(faq_data, ai_helper)
        else:
            st.warning("⚠️ OpenAI API key required for AI assistance. Please configure it in the sidebar.")

def manual_add_faq(faq_data, ai_helper):
    """Manual FAQ entry with optional AI enhancement"""
    with st.form("add_faq_form"):
        st.subheader("📝 Enter FAQ Details")
        
        question = st.text_area("❓ Question:", placeholder="Enter the question here...", height=100)
        answer = st.text_area("💡 Answer:", placeholder="Enter the answer here...", height=150)
        
        # AI enhancement options
        col1, col2 = st.columns(2)
        with col1:
            enhance_question = st.checkbox("🤖 Enhance question with AI", disabled=not ai_helper.is_configured())
        with col2:
            enhance_answer = st.checkbox("🤖 Enhance answer with AI", disabled=not ai_helper.is_configured())
        
        col1, col2 = st.columns(2)
        with col1:
            submitted = st.form_submit_button("➕ Add FAQ", type="primary")
        with col2:
            preview = st.form_submit_button("👁️ Preview", type="secondary")
        
        if preview and question.strip() and answer.strip():
            st.subheader("👁️ Preview")
            preview_question = question.strip()
            preview_answer = answer.strip()
            
            if enhance_question and ai_helper.is_configured():
                with st.spinner("Enhancing question..."):
                    preview_question = ai_helper.enhance_question(question.strip())
            
            if enhance_answer and ai_helper.is_configured():
                with st.spinner("Enhancing answer..."):
                    preview_answer = ai_helper.enhance_answer(preview_question, answer.strip())
            
            st.markdown("**Enhanced Question:**")
            st.info(preview_question)
            st.markdown("**Enhanced Answer:**")
            st.info(preview_answer)
        
        if submitted:
            if question.strip() and answer.strip():
                final_question = question.strip()
                final_answer = answer.strip()
                
                # Apply AI enhancements if requested
                if enhance_question and ai_helper.is_configured():
                    with st.spinner("Enhancing question..."):
                        final_question = ai_helper.enhance_question(question.strip())
                
                if enhance_answer and ai_helper.is_configured():
                    with st.spinner("Enhancing answer..."):
                        final_answer = ai_helper.enhance_answer(final_question, answer.strip())
                
                new_faq = {
                    "question": final_question,
                    "answer": final_answer,
                    "created_at": datetime.now().isoformat(),
                    "enhanced": enhance_question or enhance_answer
                }
                faq_data.append(new_faq)
                
                if save_faq_data(faq_data):
                    st.success("✅ FAQ added successfully!")
                    if enhance_question or enhance_answer:
                        st.info("🤖 FAQ was enhanced using AI")
                    st.balloons()
                    time.sleep(2)
                    st.rerun()
            else:
                st.error("❌ Please fill in both question and answer fields.")

def ai_assisted_add_faq(faq_data, ai_helper):
    """AI-assisted FAQ creation"""
    st.subheader("🤖 AI-Assisted FAQ Creation")
    
    # Generate questions based on existing FAQs
    if st.button("🎯 Generate Question Suggestions"):
        if faq_data:
            with st.spinner("Generating question suggestions..."):
                suggestions = ai_helper.generate_related_questions(faq_data, 5)
                if suggestions:
                    st.session_state.question_suggestions = suggestions
                else:
                    st.error("Failed to generate suggestions. Please try again.")
        else:
            st.warning("Add some FAQs first to generate related suggestions.")
    
    # Display suggestions
    if 'question_suggestions' in st.session_state:
        st.markdown("**💡 Suggested Questions:**")
        selected_question = st.selectbox("Choose a suggested question:", 
                                       [""] + st.session_state.question_suggestions)
        
        if selected_question:
            with st.form("ai_assisted_form"):
                question = st.text_area("❓ Question:", value=selected_question, height=100)
                
                if st.form_submit_button("🤖 Generate Answer"):
                    if question.strip():
                        with st.spinner("Generating answer..."):
                            generated_answer = ai_helper.generate_answer_for_question(question.strip(), faq_data)
                            if generated_answer:
                                st.session_state.generated_answer = generated_answer
                                st.session_state.current_question = question.strip()
                                st.rerun()
    
    # Show generated answer and allow editing
    if 'generated_answer' in st.session_state and 'current_question' in st.session_state:
        with st.form("finalize_ai_faq"):
            st.markdown("**🤖 Generated FAQ:**")
            final_question = st.text_area("❓ Question:", value=st.session_state.current_question, height=100)
            final_answer = st.text_area("💡 Answer:", value=st.session_state.generated_answer, height=150)
            
            if st.form_submit_button("✅ Add This FAQ"):
                if final_question.strip() and final_answer.strip():
                    new_faq = {
                        "question": final_question.strip(),
                        "answer": final_answer.strip(),
                        "created_at": datetime.now().isoformat(),
                        "ai_generated": True
                    }
                    faq_data.append(new_faq)
                    
                    if save_faq_data(faq_data):
                        st.success("✅ AI-generated FAQ added successfully!")
                        # Clear session state
                        if 'generated_answer' in st.session_state:
                            del st.session_state.generated_answer
                        if 'current_question' in st.session_state:
                            del st.session_state.current_question
                        st.balloons()
                        time.sleep(2)
                        st.rerun()

def edit_faq(faq_data, ai_helper):
    """Enhanced FAQ editing with AI assistance"""
    st.header("✏️ Edit FAQ")
    
    if not faq_data:
        st.warning("No FAQs available to edit.")
        return
    
    # Select FAQ to edit
    faq_options = [f"{i+1}. {item['question'][:80]}{'...' if len(item['question']) > 80 else ''}" 
                   for i, item in enumerate(faq_data)]
    
    selected_index = st.selectbox("Select FAQ to edit:", range(len(faq_options)), 
                                  format_func=lambda x: faq_options[x])
    
    if selected_index is not None:
        selected_faq = faq_data[selected_index]
        
        # Show current FAQ
        st.subheader("📄 Current FAQ")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Current Question:**")
            st.info(selected_faq['question'])
        with col2:
            st.markdown("**Current Answer:**")
            st.info(selected_faq['answer'])
        
        with st.form("edit_faq_form"):
            st.subheader("✏️ Edit FAQ")
            
            new_question = st.text_area("❓ Question:", value=selected_faq['question'], height=100)
            new_answer = st.text_area("💡 Answer:", value=selected_faq['answer'], height=150)
            
            # AI enhancement options
            col1, col2, col3 = st.columns(3)
            with col1:
                enhance_question = st.checkbox("🤖 Enhance question", disabled=not ai_helper.is_configured())
            with col2:
                enhance_answer = st.checkbox("🤖 Enhance answer", disabled=not ai_helper.is_configured())
            with col3:
                keep_original = st.checkbox("Keep original as backup", value=True)
            
            col1, col2 = st.columns(2)
            with col1:
                submitted = st.form_submit_button("✅ Update FAQ", type="primary")
            with col2:
                preview = st.form_submit_button("👁️ Preview Changes", type="secondary")
            
            if preview and new_question.strip() and new_answer.strip():
                st.subheader("👁️ Preview")
                preview_question = new_question.strip()
                preview_answer = new_answer.strip()
                
                if enhance_question and ai_helper.is_configured():
                    with st.spinner("Enhancing question..."):
                        preview_question = ai_helper.enhance_question(new_question.strip())
                
                if enhance_answer and ai_helper.is_configured():
                    with st.spinner("Enhancing answer..."):
                        preview_answer = ai_helper.enhance_answer(preview_question, new_answer.strip())
                
                st.markdown("**Enhanced Question:**")
                st.success(preview_question)
                st.markdown("**Enhanced Answer:**")
                st.success(preview_answer)
            
            if submitted:
                if new_question.strip() and new_answer.strip():
                    final_question = new_question.strip()
                    final_answer = new_answer.strip()
                    
                    # Apply AI enhancements if requested
                    if enhance_question and ai_helper.is_configured():
                        with st.spinner("Enhancing question..."):
                            final_question = ai_helper.enhance_question(new_question.strip())
                    
                    if enhance_answer and ai_helper.is_configured():
                        with st.spinner("Enhancing answer..."):
                            final_answer = ai_helper.enhance_answer(final_question, new_answer.strip())
                    
                    # Keep original as backup if requested
                    if keep_original and (final_question != selected_faq['question'] or final_answer != selected_faq['answer']):
                        backup_faq = {
                            "question": f"[BACKUP] {selected_faq['question']}",
                            "answer": selected_faq['answer'],
                            "created_at": datetime.now().isoformat(),
                            "is_backup": True,
                            "original_index": selected_index
                        }
                        faq_data.append(backup_faq)
                    
                    # Update the FAQ
                    faq_data[selected_index] = {
                        "question": final_question,
                        "answer": final_answer,
                        "updated_at": datetime.now().isoformat(),
                        "enhanced": enhance_question or enhance_answer
                    }
                    
                    if save_faq_data(faq_data):
                        st.success("✅ FAQ updated successfully!")
                        if enhance_question or enhance_answer:
                            st.info("🤖 FAQ was enhanced using AI")
                        if keep_original:
                            st.info("📋 Original FAQ saved as backup")
                        time.sleep(2)
                        st.rerun()
                else:
                    st.error("❌ Please fill in both question and answer fields.")

def delete_faq(faq_data):
    """Enhanced FAQ deletion with confirmation"""
    st.header("🗑️ Delete FAQ")
    
    if not faq_data:
        st.warning("No FAQs available to delete.")
        return
    
    # Select FAQ to delete
    faq_options = [f"{i+1}. {item['question'][:80]}{'...' if len(item['question']) > 80 else ''}" 
                   for i, item in enumerate(faq_data)]
    
    selected_index = st.selectbox("Select FAQ to delete:", range(len(faq_options)), 
                                  format_func=lambda x: faq_options[x])
    
    if selected_index is not None:
        selected_faq = faq_data[selected_index]
        
        # Show FAQ to be deleted
        st.subheader("📄 FAQ to be deleted:")
        with st.container():
            st.markdown("**❓ Question:**")
            st.error(selected_faq['question'])
            st.markdown("**💡 Answer:**")
            st.error(selected_faq['answer'])
        
        # Confirmation process
        st.warning("⚠️ This action cannot be undone!")
        
        # Two-step confirmation
        confirm_step1 = st.checkbox("I understand this action is permanent")
        
        if confirm_step1:
            confirm_text = st.text_input("Type 'DELETE' to confirm:", placeholder="Type DELETE to confirm deletion")
            
            if confirm_text == "DELETE":
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("🗑️ Confirm Delete", type="primary"):
                        # Create backup before deletion
                        backup_name = f"deleted_faq_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                        backup_data = {"deleted_faq": selected_faq, "deleted_at": datetime.now().isoformat()}
                        try:
                            with open(backup_name, 'w', encoding='utf-8') as f:
                                json.dump(backup_data, f, indent=4, ensure_ascii=False)
                        except:
                            pass
                        
                        faq_data.pop(selected_index)
                        
                        if save_faq_data(faq_data):
                            st.success("✅ FAQ deleted successfully!")
                            st.info(f"💾 Backup saved as: {backup_name}")
                            time.sleep(2)
                            st.rerun()
                with col2:
                    if st.button("❌ Cancel"):
                        st.rerun()

def ai_suggestions(faq_data, ai_helper):
    """AI-powered suggestions and insights"""
    st.header("🎯 AI Suggestions & Insights")
    
    if not ai_helper.is_configured():
        st.warning("⚠️ OpenAI API key required for AI suggestions. Please configure it in the sidebar.")
        return
    
    if not faq_data:
        st.info("Add some FAQs first to get AI suggestions.")
        return
    
    tab1, tab2, tab3 = st.tabs(["💡 Question Suggestions", "🔍 Content Analysis", "📈 Improvement Tips"])
    
    with tab1:
        st.subheader("💡 Generate New Question Suggestions")
        
        col1, col2 = st.columns(2)
        with col1:
            suggestion_count = st.slider("Number of suggestions:", 3, 10, 5)
        with col2:
            if st.button("🎯 Generate Suggestions"):
                with st.spinner("Analyzing existing FAQs and generating suggestions..."):
                    suggestions = ai_helper.generate_related_questions(faq_data, suggestion_count)
                    if suggestions:
                        st.session_state.ai_suggestions = suggestions
                        st.success(f"✅ Generated {len(suggestions)} suggestions!")
                    else:
                        st.error("Failed to generate suggestions. Please try again.")
        
        if 'ai_suggestions' in st.session_state:
            st.markdown("**🎯 Suggested Questions:**")
            for i, suggestion in enumerate(st.session_state.ai_suggestions, 1):
                with st.expander(f"💡 Suggestion {i}: {suggestion[:60]}..."):
                    st.write(suggestion)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button(f"🤖 Generate Answer", key=f"gen_ans_{i}"):
                            with st.spinner("Generating answer..."):
                                answer = ai_helper.generate_answer_for_question(suggestion, faq_data)
                                if answer:
                                    st.session_state[f"generated_answer_{i}"] = answer
                                    st.rerun()
                    
                    with col2:
                        if st.button(f"➕ Add to FAQs", key=f"add_faq_{i}"):
                            if f"generated_answer_{i}" in st.session_state:
                                new_faq = {
                                    "question": suggestion,
                                    "answer": st.session_state[f"generated_answer_{i}"],
                                    "created_at": datetime.now().isoformat(),
                                    "ai_generated": True
                                }
                                faq_data.append(new_faq)
                                if save_faq_data(faq_data):
                                    st.success("✅ FAQ added!")
                                    del st.session_state[f"generated_answer_{i}"]
                            else:
                                st.warning("Generate answer first!")
                    
                    # Show generated answer if available
                    if f"generated_answer_{i}" in st.session_state:
                        st.markdown("**🤖 Generated Answer:**")
                        st.info(st.session_state[f"generated_answer_{i}"])
    
    with tab2:
        st.subheader("🔍 Content Analysis")
        
        if st.button("📊 Analyze FAQ Content"):
            with st.spinner("Analyzing FAQ content..."):
                # Basic analysis
                questions = [faq['question'] for faq in faq_data]
                answers = [faq['answer'] for faq in faq_data]
                
                avg_q_length = sum(len(q) for q in questions) / len(questions)
                avg_a_length = sum(len(a) for a in answers) / len(answers)
                
                # Find short answers that might need enhancement
                short_answers = [(i, faq) for i, faq in enumerate(faq_data) if len(faq['answer']) < avg_a_length * 0.7]
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("📏 Avg Question Length", f"{avg_q_length:.0f} chars")
                    st.metric("📏 Avg Answer Length", f"{avg_a_length:.0f} chars")
                
                with col2:
                    st.metric("⚠️ Short Answers", len(short_answers))
                    st.metric("📚 Total FAQs", len(faq_data))
                
                if short_answers:
                    st.markdown("**⚠️ FAQs with potentially short answers:**")
                    for idx, faq in short_answers[:5]:  # Show first 5
                        with st.expander(f"FAQ {idx+1}: {faq['question'][:50]}..."):
                            st.write("**Question:**", faq['question'])
                            st.write("**Answer:**", faq['answer'])
                            st.caption(f"Answer length: {len(faq['answer'])} characters")
                            
                            if st.button(f"🤖 Enhance Answer", key=f"enhance_{idx}"):
                                with st.spinner("Enhancing answer..."):
                                    enhanced = ai_helper.enhance_answer(faq['question'], faq['answer'])
                                    st.markdown("**✨ Enhanced Answer:**")
                                    st.success(enhanced)
    
    with tab3:
        st.subheader("📈 AI-Powered Improvement Tips")
        
        if st.button("💡 Get Improvement Suggestions"):
            with st.spinner("Analyzing FAQs for improvement opportunities..."):
                # Sample analysis - in a real implementation, you'd use AI to analyze patterns
                tips = [
                    "🎯 Consider adding more specific examples to your answers",
                    "📋 Break down long answers into bullet points for better readability",
                    "🔗 Add related questions at the end of complex answers",
                    "📱 Ensure answers are mobile-friendly with shorter paragraphs",
                    "🎨 Use formatting (bold, italics) to highlight key information",
                    "❓ Consider adding FAQ categories for better organization",
                    "🔄 Regular review and update of outdated information",
                    "📊 Add metrics or statistics to support your answers where relevant"
                ]
                
                st.markdown("**💡 Improvement Suggestions:**")
                for tip in tips:
                    st.markdown(f"• {tip}")
                
                # FAQ quality score (mock implementation)
                quality_score = min(100, (len(faq_data) * 10) + (avg_a_length / 10))
                st.metric("📊 FAQ Quality Score", f"{quality_score:.0f}/100")
                
                if quality_score < 70:
                    st.warning("🔄 Consider enhancing your FAQs for better user experience")
                elif quality_score < 90:
                    st.info("👍 Good FAQ quality! Room for minor improvements")
                else:
                    st.success("🌟 Excellent FAQ quality!")

def show_statistics(faq_data):
    """Enhanced FAQ statistics and analytics"""
    st.header("📊 FAQ Statistics & Analytics")
    
    if not faq_data:
        st.warning("No FAQ data available for statistics.")
        return
    
    # Enhanced basic statistics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📚 Total FAQs", len(faq_data))
    
    with col2:
        avg_question_length = sum(len(item['question']) for item in faq_data) / len(faq_data)
        st.metric("❓ Avg Question Length", f"{avg_question_length:.0f} chars")
    
    with col3:
        avg_answer_length = sum(len(item['answer']) for item in faq_data) / len(faq_data)
        st.metric("💡 Avg Answer Length", f"{avg_answer_length:.0f} chars")
    
    with col4:
        ai_enhanced = sum(1 for item in faq_data if item.get('enhanced') or item.get('ai_generated'))
        st.metric("🤖 AI Enhanced", ai_enhanced)
    
    # Additional metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        longest_question = max(len(item['question']) for item in faq_data)
        st.metric("📏 Longest Question", f"{longest_question} chars")
    
    with col2:
        shortest_question = min(len(item['question']) for item in faq_data)
        st.metric("📏 Shortest Question", f"{shortest_question} chars")
    
    with col3:
        longest_answer = max(len(item['answer']) for item in faq_data)
        st.metric("📏 Longest Answer", f"{longest_answer} chars")
    
    with col4:
        shortest_answer = min(len(item['answer']) for item in faq_data)
        st.metric("📏 Shortest Answer", f"{shortest_answer} chars")
    
    # Create DataFrame for analysis
    df = pd.DataFrame(faq_data)
    df['question_length'] = df['question'].str.len()
    df['answer_length'] = df['answer'].str.len()
    df['total_length'] = df['question_length'] + df['answer_length']
    df['word_count_question'] = df['question'].str.split().str.len()
    df['word_count_answer'] = df['answer'].str.split().str.len()
    
    # Charts and visualizations
    st.subheader("📈 Length Distribution Analysis")
    
    tab1, tab2, tab3 = st.tabs(["📊 Character Length", "📝 Word Count", "🎯 Quality Metrics"])
    
    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**❓ Question Length Distribution**")
            st.bar_chart(df['question_length'])
        
        with col2:
            st.markdown("**💡 Answer Length Distribution**")
            st.bar_chart(df['answer_length'])
    
    with tab2:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**📝 Question Word Count**")
            st.bar_chart(df['word_count_question'])
            st.metric("Avg Words per Question", f"{df['word_count_question'].mean():.1f}")
        
        with col2:
            st.markdown("**📝 Answer Word Count**")
            st.bar_chart(df['word_count_answer'])
            st.metric("Avg Words per Answer", f"{df['word_count_answer'].mean():.1f}")
    
    with tab3:
        # Quality insights
        st.markdown("**🎯 FAQ Quality Insights**")
        
        # Identify potentially problematic FAQs
        very_short_answers = df[df['answer_length'] < 50]
        very_long_answers = df[df['answer_length'] > 500]
        very_short_questions = df[df['question_length'] < 20]
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("⚠️ Very Short Answers", len(very_short_answers), help="Answers under 50 characters")
        with col2:
            st.metric("📖 Very Long Answers", len(very_long_answers), help="Answers over 500 characters")
        with col3:
            st.metric("❓ Very Short Questions", len(very_short_questions), help="Questions under 20 characters")
    
    # Top/Bottom FAQs analysis
    st.subheader("🔍 FAQ Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**📏 Longest FAQs (by total length):**")
        longest_faqs = df.nlargest(5, 'total_length')[['question', 'total_length']]
        for idx, row in longest_faqs.iterrows():
            st.write(f"• {row['question'][:80]}... ({row['total_length']} chars)")
    
    with col2:
        st.markdown("**📏 Shortest FAQs (by total length):**")
        shortest_faqs = df.nsmallest(5, 'total_length')[['question', 'total_length']]
        for idx, row in shortest_faqs.iterrows():
            st.write(f"• {row['question'][:80]}... ({row['total_length']} chars)")
    
    # Export options
    st.subheader("📤 Export Options")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 Export Statistics"):
            stats_data = {
                "total_faqs": len(faq_data),
                "avg_question_length": avg_question_length,
                "avg_answer_length": avg_answer_length,
                "ai_enhanced_count": ai_enhanced,
                "generated_at": datetime.now().isoformat()
            }
            
            filename = f"faq_statistics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(stats_data, f, indent=4, ensure_ascii=False)
            st.success(f"✅ Statistics exported to {filename}")
    
    with col2:
        if st.button("📋 Export FAQ Data"):
            filename = f"faq_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(faq_data, f, indent=4, ensure_ascii=False)
            st.success(f"✅ FAQ data exported to {filename}")
    
    with col3:
        if st.button("📊 Export as CSV"):
            csv_filename = f"faq_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            df[['question', 'answer', 'question_length', 'answer_length']].to_csv(csv_filename, index=False)
            st.success(f"✅ CSV exported to {csv_filename}")

if __name__ == "__main__":
    main()