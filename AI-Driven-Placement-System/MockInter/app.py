import streamlit as st
import pymongo
from pymongo import MongoClient
from datetime import datetime
import random

st.set_page_config(page_title="Mock Interview", layout="wide")

# MongoDB connection
try:
    client = MongoClient('mongodb://localhost:27017/')
    db = client['mock_interviews']
    feedback_collection = db['feedbacks']
except Exception as e:
    st.error(f"MongoDB connection error: {e}")

st.title("🎤 Mock Interview Practice")
st.markdown("---")

# Sidebar
with st.sidebar:
    st.header("Interview Settings")
    interview_type = st.selectbox(
        "Select Interview Type",
        ["Technical", "HR", "Behavioral"]
    )
    difficulty = st.selectbox(
        "Difficulty Level",
        ["Easy", "Medium", "Hard"]
    )

# Mock Interview Questions
QUESTIONS = {
    "Technical": {
        "Easy": [
            "What is the difference between var and let in JavaScript?",
            "Explain the concept of a database index.",
            "What is RESTful API?"
        ],
        "Medium": [
            "How does garbage collection work in Python?",
            "Explain the concept of polymorphism in OOP.",
            "What is microservices architecture?"
        ],
        "Hard": [
            "Design a system to handle traffic spikes.",
            "Explain distributed transaction handling.",
            "How would you optimize a slow database query?"
        ]
    },
    "HR": {
        "Easy": [
            "Tell me about yourself.",
            "What are your strengths?",
            "Why do you want to work here?"
        ],
        "Medium": [
            "Describe a challenging situation you overcame.",
            "How do you handle conflicts with team members?",
            "What are your career goals?"
        ],
        "Hard": [
            "Tell me about a time you failed and how you recovered.",
            "How do you balance innovation with execution?",
            "Describe your approach to leadership."
        ]
    },
    "Behavioral": {
        "Easy": [
            "Give an example of teamwork.",
            "Describe a time you met a deadline.",
            "When did you take initiative?"
        ],
        "Medium": [
            "Describe a conflict you resolved.",
            "Give an example of your problem-solving skills.",
            "Tell me about a time you learned something new."
        ],
        "Hard": [
            "Describe your most complex project.",
            "How did you handle a high-pressure situation?",
            "Tell me about a decision that had significant impact."
        ]
    }
}

# Main Interview Area
col1, col2 = st.columns([2, 1])

with col1:
    st.header("📝 Interview Session")
    
    if interview_type in QUESTIONS and difficulty in QUESTIONS[interview_type]:
        questions = QUESTIONS[interview_type][difficulty]
        
        # Question selector
        question_idx = st.selectbox(
            "Select Question",
            range(len(questions)),
            format_func=lambda i: f"Q{i+1}: {questions[i]}"
        )
        
        current_question = questions[question_idx]
        st.subheader(f"Question {question_idx + 1}")
        st.write(current_question)
        
        st.markdown("---")
        
        # Response area
        st.subheader("📢 Your Response")
        response = st.text_area(
            "Type your answer here (you can also record using microphone)",
            height=150,
            placeholder="Provide your answer to the question..."
        )
        
        col_submit, col_skip = st.columns(2)
        
        with col_submit:
            if st.button("✅ Submit Answer"):
                if response.strip():
                    st.success("✅ Answer submitted!")
                    try:
                        feedback_doc = {
                            "username": "student",
                            "interview_type": interview_type,
                            "difficulty": difficulty,
                            "question": current_question,
                            "response": response,
                            "timestamp": datetime.now(),
                            "rating": "pending"
                        }
                        feedback_collection.insert_one(feedback_doc)
                    except:
                        pass
                else:
                    st.warning("Please provide an answer before submitting!")
        
        with col_skip:
            if st.button("⏭️ Skip Question"):
                st.info("Question skipped. Moving to next question...")

with col2:
    st.header("⏱️ Interview Info")
    st.metric("Interview Type", interview_type)
    st.metric("Difficulty", difficulty)
    st.metric("Question #", question_idx + 1)
    st.metric("Total Questions", len(questions))
    
    st.markdown("---")
    
    st.subheader("📊 Tips")
    st.markdown("""
    - **Be Clear**: Speak clearly and confidently
    - **Be Concise**: Answer directly without rambling
    - **Use Examples**: Support answers with concrete examples
    - **Ask Questions**: Show interest by asking clarifying questions
    - **Be Professional**: Maintain professional tone
    """)

st.markdown("---")

# Interview History
st.header("📋 Interview History")

tab1, tab2 = st.tabs(["Recent Interviews", "Performance"])

with tab1:
    try:
        interviews = list(feedback_collection.find({"username": "student"}).sort("timestamp", -1).limit(10))
        if interviews:
            for idx, interview in enumerate(interviews, 1):
                with st.expander(f"Interview {idx} - {interview.get('interview_type')} ({interview.get('difficulty')})"):
                    st.write(f"**Question**: {interview.get('question')}")
                    st.write(f"**Your Response**: {interview.get('response')}")
                    st.caption(f"Submitted: {interview.get('timestamp')}")
        else:
            st.info("No interview history yet. Start practicing!")
    except Exception as e:
        st.info("No interview history available yet.")

with tab2:
    st.subheader("Performance Overview")
    try:
        all_interviews = list(feedback_collection.find({"username": "student"}))
        if all_interviews:
            technical_count = len([i for i in all_interviews if i.get('interview_type') == 'Technical'])
            hr_count = len([i for i in all_interviews if i.get('interview_type') == 'HR'])
            behavioral_count = len([i for i in all_interviews if i.get('interview_type') == 'Behavioral'])
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Technical", technical_count)
            with col2:
                st.metric("HR", hr_count)
            with col3:
                st.metric("Behavioral", behavioral_count)
        else:
            st.info("Complete interviews to see performance metrics.")
    except:
        st.info("Performance data unavailable.")

st.markdown("---")
st.markdown("### 💡 Interview Preparation Tips:")
st.markdown("""
1. **Research the company** - Know their mission, products, and recent news
2. **Practice common questions** - Prepare answers for behavioral questions
3. **Technical preparation** - Review data structures, algorithms, and system design
4. **Mock interviews** - Practice with friends and mentors
5. **Dress professionally** - First impressions matter
6. **Be on time** - Arrive 10 minutes early
7. **Ask questions** - Show genuine interest in the role and company
""")
