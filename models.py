"""
Data models and utilities for FAQ Manager
"""

import json
import os
import re
from datetime import datetime
from typing import List, Dict, Optional
import streamlit as st


class FAQ:
    """FAQ data model"""
    
    def __init__(self, question: str, answer: str, id: Optional[int] = None):
        self.question = question.strip()
        self.answer = answer.strip()
        self.id = id
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
    
    def to_dict(self) -> Dict:
        """Convert FAQ to dictionary"""
        return {
            "question": self.question,
            "answer": self.answer
        }
    
    @classmethod
    def from_dict(cls, data: Dict, id: Optional[int] = None):
        """Create FAQ from dictionary"""
        return cls(data["question"], data["answer"], id)
    
    def validate(self) -> tuple[bool, str]:
        """Validate FAQ data"""
        if not self.question:
            return False, "Question cannot be empty"
        if not self.answer:
            return False, "Answer cannot be empty"
        if len(self.question) < 5:
            return False, "Question must be at least 5 characters long"
        if len(self.answer) < 10:
            return False, "Answer must be at least 10 characters long"
        return True, ""


class EnhancedFAQ:
    """Enhanced FAQ model with structured format"""

    def __init__(self, question: str, answer: str, category: str = None,
                 tags: List[str] = None, alternate_questions: List[str] = None, id: str = None):
        self.id = id or self._generate_id(question, category)
        self.category = category or "general"
        self.tags = tags or []
        self.question = question.strip()
        self.alternate_questions = alternate_questions or []
        self.answer = answer.strip()
        self.created_at = datetime.now().isoformat()

    def _generate_id(self, question: str, category: str = None) -> str:
        """Generate a structured ID based on question and category"""
        # Clean the question for ID generation
        clean_question = re.sub(r'[^a-zA-Z0-9\s]', '', question.lower())
        words = clean_question.split()[:4]  # Take first 4 words
        question_part = '-'.join(words)

        category_part = category.lower().replace(' ', '_') if category else 'general'

        base_id = f"faq-{category_part}-{question_part}"

        # Add timestamp suffix to ensure uniqueness
        import time
        timestamp = str(int(time.time()))[-6:]  # Last 6 digits of timestamp

        return f"{base_id}-{timestamp}"

    def to_dict(self) -> Dict:
        """Convert Enhanced FAQ to dictionary"""
        return {
            "id": self.id,
            "category": self.category,
            "tags": self.tags,
            "question": self.question,
            "alternate_questions": self.alternate_questions,
            "answer": self.answer
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'EnhancedFAQ':
        """Create Enhanced FAQ from dictionary"""
        return cls(
            question=data["question"],
            answer=data["answer"],
            category=data.get("category", "general"),
            tags=data.get("tags", []),
            alternate_questions=data.get("alternate_questions", []),
            id=data.get("id")
        )


class FAQManager:
    """FAQ data management class"""
    
    def __init__(self, file_path: str = "faq.json"):
        self.file_path = file_path
        self._faqs = []
        self.load_data()
    
    def load_data(self) -> bool:
        """Load FAQ data from JSON file"""
        try:
            if os.path.exists(self.file_path):
                with open(self.file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self._faqs = [FAQ.from_dict(item, i) for i, item in enumerate(data)]
                return True
            else:
                self._faqs = []
                return True
        except (FileNotFoundError, json.JSONDecodeError) as e:
            st.error(f"Error loading FAQ data: {str(e)}")
            self._faqs = []
            return False
    
    def save_data(self) -> bool:
        """Save FAQ data to JSON file with backup"""
        try:
            # Create backup if file exists
            if os.path.exists(self.file_path):
                backup_name = f"faq_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                with open(self.file_path, 'r', encoding='utf-8') as f:
                    backup_data = f.read()
                with open(backup_name, 'w', encoding='utf-8') as f:
                    f.write(backup_data)
            
            # Save new data
            data = [faq.to_dict() for faq in self._faqs]
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            st.error(f"Error saving FAQ data: {str(e)}")
            return False

    def get_all_faqs(self) -> List[FAQ]:
        """Get all FAQs"""
        return self._faqs.copy()

    def get_faq_by_id(self, faq_id: int) -> Optional[FAQ]:
        """Get FAQ by ID"""
        if 0 <= faq_id < len(self._faqs):
            return self._faqs[faq_id]
        return None

    def add_faq(self, faq: FAQ) -> bool:
        """Add new FAQ"""
        is_valid, error_msg = faq.validate()
        if not is_valid:
            st.error(f"Validation error: {error_msg}")
            return False

        faq.id = len(self._faqs)
        self._faqs.append(faq)
        return self.save_data()

    def update_faq(self, faq_id: int, updated_faq: FAQ) -> bool:
        """Update existing FAQ"""
        if not (0 <= faq_id < len(self._faqs)):
            st.error("Invalid FAQ ID")
            return False

        is_valid, error_msg = updated_faq.validate()
        if not is_valid:
            st.error(f"Validation error: {error_msg}")
            return False

        updated_faq.id = faq_id
        updated_faq.updated_at = datetime.now()
        self._faqs[faq_id] = updated_faq
        return self.save_data()

    def delete_faq(self, faq_id: int) -> bool:
        """Delete FAQ by ID"""
        if not (0 <= faq_id < len(self._faqs)):
            st.error("Invalid FAQ ID")
            return False

        self._faqs.pop(faq_id)
        # Update IDs for remaining FAQs
        for i, faq in enumerate(self._faqs):
            faq.id = i

        return self.save_data()

    def search_faqs(self, query: str) -> List[FAQ]:
        """Search FAQs by query"""
        if not query:
            return self._faqs.copy()

        query_lower = query.lower()
        results = []
        for faq in self._faqs:
            if (query_lower in faq.question.lower() or
                query_lower in faq.answer.lower()):
                results.append(faq)
        return results

    def get_count(self) -> int:
        """Get total number of FAQs"""
        return len(self._faqs)


class EnhancedFAQManager:
    """Enhanced FAQ data management class for structured format"""

    def __init__(self, file_path: str = "enhanced_faqs.json"):
        self.file_path = file_path
        self.faqs = []
        self.load_faqs()

    def load_faqs(self) -> bool:
        """Load enhanced FAQs from JSON file"""
        try:
            if os.path.exists(self.file_path):
                with open(self.file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.faqs = [EnhancedFAQ.from_dict(item) for item in data]
                return True
            else:
                self.faqs = []
                return True
        except Exception as e:
            st.error(f"Error loading enhanced FAQ data: {str(e)}")
            self.faqs = []
            return False

    def save_faqs(self) -> bool:
        """Save enhanced FAQs to JSON file"""
        try:
            data = [faq.to_dict() for faq in self.faqs]
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            st.error(f"Error saving enhanced FAQ data: {str(e)}")
            return False

    def add_enhanced_faq(self, enhanced_faq: EnhancedFAQ) -> bool:
        """Add a new enhanced FAQ"""
        try:
            # Check for duplicate questions and IDs
            for existing_faq in self.faqs:
                if existing_faq.question.lower() == enhanced_faq.question.lower():
                    st.warning(f"⚠️ This question already exists: {existing_faq.question}")
                    return False
                if existing_faq.id == enhanced_faq.id:
                    st.warning(f"⚠️ FAQ with this ID already exists: {existing_faq.id}")
                    return False

            self.faqs.append(enhanced_faq)
            return self.save_faqs()
        except Exception as e:
            st.error(f"Error adding enhanced FAQ: {str(e)}")
            return False

    def get_all_enhanced_faqs(self) -> List[EnhancedFAQ]:
        """Get all enhanced FAQs"""
        return self.faqs.copy()

    def get_enhanced_faqs_by_category(self, category: str) -> List[EnhancedFAQ]:
        """Get enhanced FAQs by category"""
        return [faq for faq in self.faqs if faq.category == category]

    def search_enhanced_faqs(self, query: str) -> List[EnhancedFAQ]:
        """Search enhanced FAQs"""
        query = query.lower()
        results = []

        for faq in self.faqs:
            # Search in question, answer, tags, and alternate questions
            if (query in faq.question.lower() or
                query in faq.answer.lower() or
                any(query in tag.lower() for tag in faq.tags) or
                any(query in alt_q.lower() for alt_q in faq.alternate_questions)):
                results.append(faq)

        return results

    def export_to_json(self) -> str:
        """Export all enhanced FAQs to JSON string"""
        data = [faq.to_dict() for faq in self.faqs]
        return json.dumps(data, indent=2, ensure_ascii=False)
