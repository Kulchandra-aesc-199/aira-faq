"""
AI Helper module for FAQ Manager
Handles OpenAI integration and AI-powered features
"""

import os
import streamlit as st
from dotenv import load_dotenv
import openai
from typing import List, Optional, Dict
import json

# Load environment variables
load_dotenv()


class AIHelper:
    """AI Helper class for FAQ management"""
    
    def __init__(self):
        self.client = None
        self.model = os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize OpenAI client"""
        api_key = os.getenv('OPENAI_API_KEY')
        if api_key and api_key != 'your_openai_api_key_here':
            try:
                self.client = openai.OpenAI(api_key=api_key)
            except Exception as e:
                st.error(f"Error initializing OpenAI client: {str(e)}")
                self.client = None
    
    def is_configured(self) -> bool:
        """Check if AI is properly configured"""
        return self.client is not None
    
    def test_connection(self) -> bool:
        """Test OpenAI API connection"""
        if not self.is_configured():
            return False
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=5
            )
            return True
        except Exception as e:
            st.error(f"OpenAI API test failed: {str(e)}")
            return False
    
    def enhance_question(self, question: str) -> Optional[str]:
        """Enhance a question for The Hire Hub ATS system"""
        if not self.is_configured():
            return None

        try:
            prompt = f"""
            Improve this FAQ question for The Hire Hub ATS system to make it clearer and more professional for recruiters and HR professionals:

            Original: {question}

            Requirements:
            - Keep the same core meaning and intent
            - Make it more specific to ATS/recruitment context when applicable
            - Use professional recruitment terminology
            - Make it concise and clear for busy recruiters
            - Ensure it sounds like a question a recruiter would actually ask
            - Return only the improved question, no explanations or quotes
            """

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=100,
                temperature=0.3
            )

            return response.choices[0].message.content.strip()
        except Exception as e:
            st.error(f"Error enhancing question: {str(e)}")
            return None
    
    def enhance_answer(self, question: str, answer: str) -> Optional[str]:
        """Enhance an answer for The Hire Hub ATS system"""
        if not self.is_configured():
            return None

        try:
            prompt = f"""
            Improve this FAQ answer for The Hire Hub ATS system to make it more helpful and comprehensive for recruiters and HR professionals:

            Question: {question}
            Original Answer: {answer}

            Enhancement Guidelines:
            - Keep the same core information and accuracy
            - Add step-by-step instructions where applicable
            - Include specific UI references (buttons, tabs, menus) when relevant
            - Mention related features that might be helpful
            - Use professional but friendly tone suitable for busy recruiters
            - Add practical tips or best practices if appropriate
            - Ensure the answer is actionable and specific to The Hire Hub platform
            - Return only the improved answer, no explanations or meta-text
            """

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=400,
                temperature=0.3
            )

            return response.choices[0].message.content.strip()
        except Exception as e:
            st.error(f"Error enhancing answer: {str(e)}")
            return None
    
    def generate_answer_for_question(self, question: str, existing_faqs: List = None) -> Optional[str]:
        """Generate an answer for a given question about The Hire Hub ATS system"""
        if not self.is_configured():
            return None

        try:
            context = ""
            if existing_faqs:
                # Use existing FAQs as context
                context_faqs = existing_faqs[:5]  # Use first 5 FAQs as context
                context = "\n".join([f"Q: {faq.question}\nA: {faq.answer}" for faq in context_faqs])
                context = f"\nContext from existing FAQs:\n{context}\n"

            prompt = f"""
            You are a knowledgeable support specialist for "The Hire Hub" - a comprehensive AI-powered ATS (Applicant Tracking System) designed for modern recruitment teams.

            Question: {question}
            {context}

            About The Hire Hub ATS Platform:
            - Complete recruitment management solution with AI-powered features
            - Core modules: Candidate Management, Job Posting, Interview Scheduling, Resume Parsing, Analytics
            - AI Features: Smart candidate matching, automated screening, predictive analytics, resume insights
            - User Types: Recruiters, Hiring Managers, HR Administrators, Team Leads
            - Integrations: Job boards, email systems, calendar apps, HRIS platforms
            - Key Workflows: Job creation → Candidate sourcing → Screening → Interview scheduling → Decision tracking → Onboarding

            Answer Guidelines:
            - Provide step-by-step instructions when applicable (e.g., "1. Navigate to... 2. Click on... 3. Select...")
            - Reference specific UI elements (buttons, tabs, menus) that users would see
            - Include relevant permissions or role-based access information
            - Mention related features that might be helpful
            - Use professional, helpful tone suitable for busy recruiters
            - Keep answers practical and actionable
            - Assume users have basic ATS knowledge but may need guidance on specific features

            Return only the comprehensive answer, no explanations or meta-text.
            """

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=400,
                temperature=0.3
            )

            return response.choices[0].message.content.strip()
        except Exception as e:
            st.error(f"Error generating answer: {str(e)}")
            return None
    
    def generate_faq_from_topic(self, topic: str, existing_faqs: List = None) -> List:
        """Generate complete FAQ (question + answer) from topic for The Hire Hub ATS system"""
        if not self.is_configured():
            return []

        try:
            context = ""
            if existing_faqs:
                context_faqs = existing_faqs[:5]
                context = "\n".join([f"Q: {faq.question}\nA: {faq.answer}" for faq in context_faqs])
                context = f"\nExisting FAQs for reference (avoid duplicating):\n{context}\n"

            prompt = f"""
            You are creating comprehensive FAQ content for "The Hire Hub" - a professional AI-powered ATS (Applicant Tracking System) used by recruitment teams.

            Topic: {topic}
            {context}

            The Hire Hub Platform Details:
            - Complete ATS solution with AI-enhanced recruitment features
            - User Roles: Recruiters, Hiring Managers, HR Admins, Team Leads
            - Core Features: Job posting, candidate sourcing, resume parsing, interview scheduling, collaboration tools
            - AI Capabilities: Smart matching, automated screening, predictive analytics, candidate insights
            - Integrations: Major job boards, email platforms, calendar systems, HRIS tools
            - Reporting: Analytics dashboard, hiring metrics, team performance, compliance tracking

            Generate 3 high-quality FAQ pairs that:
            1. Address real challenges recruiters face with this topic
            2. Provide step-by-step guidance where applicable
            3. Reference specific platform features and UI elements
            4. Include practical tips and best practices
            5. Consider different user roles and permissions
            6. Avoid generic answers - be specific to The Hire Hub

            Question Types to Consider:
            - "How do I..." (procedural questions)
            - "What is the best way to..." (best practice questions)
            - "Can I..." (capability/permission questions)
            - "Why is..." (troubleshooting/explanation questions)

            Return as JSON array with this exact format:
            [
                {{"question": "How do I...", "answer": "To accomplish this in The Hire Hub: 1. Navigate to... 2. Click on... 3. Select..."}},
                {{"question": "What is...", "answer": "This feature allows you to... You can access it by..."}}
            ]

            Return only the JSON array, no explanations or additional text.
            """

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1000,
                temperature=0.3
            )

            content = response.choices[0].message.content.strip()
            try:
                faqs_data = json.loads(content)
                if isinstance(faqs_data, list):
                    # Import FAQ class here to avoid circular imports
                    from models import FAQ
                    return [FAQ(faq_dict["question"], faq_dict["answer"]) for faq_dict in faqs_data]
                else:
                    return []
            except json.JSONDecodeError:
                st.error("Failed to parse AI response")
                return []

        except Exception as e:
            st.error(f"Error generating FAQs: {str(e)}")
            return []
    
    def categorize_faq(self, question: str, answer: str) -> Optional[str]:
        """Categorize an FAQ for The Hire Hub ATS system"""
        if not self.is_configured():
            return None

        try:
            prompt = f"""
            Categorize this FAQ for The Hire Hub ATS system into one of these recruitment-specific categories:
            - Candidate Management (tracking, profiles, communication)
            - Job Posting (creating jobs, publishing, requirements)
            - Interview Scheduling (calendar, coordination, logistics)
            - Resume & Applications (parsing, screening, evaluation)
            - Analytics & Reporting (metrics, dashboards, insights)
            - Team Collaboration (sharing, permissions, workflows)
            - AI Features (matching, automation, predictions)
            - Integrations (job boards, email, calendar, HRIS)
            - Account & Settings (user management, configuration)
            - General (basic usage, navigation, getting started)

            Question: {question}
            Answer: {answer}

            Return only the category name, no explanations.
            """

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=30,
                temperature=0.1
            )

            return response.choices[0].message.content.strip()
        except Exception as e:
            st.error(f"Error categorizing FAQ: {str(e)}")
            return None

    def enhance_faq_to_structured_format(self, question: str, answer: str) -> Optional[dict]:
        """Convert a simple FAQ to the enhanced structured format"""
        if not self.is_configured():
            return None

        try:
            prompt = f"""
            Convert this FAQ into a structured format for The Hire Hub ATS system.

            Question: {question}
            Answer: {answer}

            Generate the following components:
            1. Category: Choose from these ATS-specific categories:
               - dashboard, candidate_management, job_posting, interview_scheduling,
               - resume_applications, analytics_reporting, team_collaboration,
               - ai_features, integrations, account_settings, general

            2. Tags: Generate 3-5 relevant tags (lowercase, underscore-separated)

            3. Alternate Questions: Generate 4-5 different ways users might ask the same question
               - Use different phrasings and terminology
               - Include common variations recruiters might use
               - Make them natural and conversational

            Return as JSON with this exact format:
            {{
                "category": "category_name",
                "tags": ["tag1", "tag2", "tag3"],
                "alternate_questions": [
                    "How do I...",
                    "Where can I find...",
                    "What is the best way to...",
                    "I need to..."
                ]
            }}

            Return only the JSON, no explanations.
            """

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=400,
                temperature=0.4
            )

            content = response.choices[0].message.content.strip()
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                st.error("Failed to parse AI response for structured format")
                return None

        except Exception as e:
            st.error(f"Error enhancing FAQ to structured format: {str(e)}")
            return None
