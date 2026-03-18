import streamlit as st
import pymongo
from pymongo import MongoClient
from datetime import datetime
import random

st.set_page_config(page_title="Aptitude Practice", layout="wide")

# MongoDB connection
try:
    client = MongoClient('mongodb://localhost:27017/')
    db = client['aptitude_db']
    collection = db['attempts']
except Exception as e:
    st.error(f"MongoDB connection error: {e}")

# Aptitude Questions Database
QUESTIONS = {
    "C++": [
        {
            "id": 1,
            "question": "What is the output of: int x = 5; cout << x++ << ++x;",
            "options": ["5 7", "6 7", "5 6", "6 8"],
            "correct": 0,
            "explanation": "x++ returns 5 then increments to 6, ++x increments 6 to 7 then returns 7"
        },
        {
            "id": 2,
            "question": "Which of the following is NOT a valid C++ data type?",
            "options": ["int", "float", "string", "word"],
            "correct": 3,
            "explanation": "'word' is not a built-in C++ data type"
        }
    ],
    "Java": [
        {
            "id": 1,
            "question": "What is the default value of a local variable in Java?",
            "options": ["0", "null", "None", "Not initialized"],
            "correct": 3,
            "explanation": "Local variables must be explicitly initialized before use"
        }
    ],
    "Data Structures": [
        {
            "id": 1,
            "question": "Time complexity of Binary Search is:",
            "options": ["O(n)", "O(log n)", "O(n log n)", "O(n²)"],
            "correct": 1,
            "explanation": "Binary Search divides the search space in half each time: O(log n)"
        }
    ],
    "Logical Reasoning": [
        {
            "id": 1,
            "question": "If all roses are flowers and some flowers are red, then:",
            "options": [
                "All roses are red",
                "Some roses are red",
                "No conclusion can be drawn",
                "No roses are red"
            ],
            "correct": 2,
            "explanation": "We cannot conclude anything about roses being red from the given statements"
        }
    ]
}

# Streamlit UI
st.title("🧠 Aptitude Practice Platform")
st.markdown("---")

# Sidebar
with st.sidebar:
    st.header("Practice Options")
    category = st.selectbox(
        "Select Category",
        list(QUESTIONS.keys())
    )
    
    mode = st.radio(
        "Select Mode",
        ["Practice", "View Results"]
    )

# Main Content
if mode == "Practice":
    st.header(f"📚 {category} Questions")
    
    if category in QUESTIONS:
        questions = QUESTIONS[category]
        
        # Question selection
        question_num = st.selectbox(
            "Select Question",
            range(1, len(questions) + 1)
        ) - 1
        
        q = questions[question_num]
        
        st.subheader(f"Question {q['id']}: {q['question']}")
        
        # Display options
        answer = st.radio(
            "Select your answer:",
            q['options'],
            key=f"q_{q['id']}"
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Submit Answer", key=f"submit_{q['id']}"):
                selected_idx = q['options'].index(answer)
                if selected_idx == q['correct']:
                    st.success("✅ Correct!")
                    # Store in MongoDB
                    try:
                        collection.insert_one({
                            "user": "student",
                            "category": category,
                            "question_id": q['id'],
                            "result": "correct",
                            "timestamp": datetime.now()
                        })
                    except:
                        pass
                else:
                    st.error(f"❌ Incorrect! Correct answer: {q['options'][q['correct']]}")
                    try:
                        collection.insert_one({
                            "user": "student",
                            "category": category,
                            "question_id": q['id'],
                            "result": "incorrect",
                            "timestamp": datetime.now()
                        })
                    except:
                        pass
                
                st.info(f"📝 **Explanation**: {q['explanation']}")
        
        with col2:
            st.info(f"**Progress**: Question {question_num + 1} of {len(questions)}")

else:  # View Results
    st.header("📊 Your Results")
    
    try:
        # Fetch user results
        results = list(collection.find({"user": "student"}))
        
        if results:
            correct = len([r for r in results if r['result'] == 'correct'])
            total = len(results)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Correct Answers", correct)
            with col2:
                st.metric("Total Attempts", total)
            with col3:
                st.metric("Accuracy", f"{(correct/total*100):.1f}%")
            
            st.markdown("---")
            
            # Results by category
            st.subheader("Performance by Category")
            category_results = {}
            for r in results:
                cat = r.get('category', 'Unknown')
                if cat not in category_results:
                    category_results[cat] = {"correct": 0, "total": 0}
                category_results[cat]["total"] += 1
                if r['result'] == 'correct':
                    category_results[cat]["correct"] += 1
            
            for cat, stats in category_results.items():
                st.write(f"**{cat}**: {stats['correct']}/{stats['total']} ({stats['correct']/stats['total']*100:.1f}%)")
        else:
            st.info("No results yet. Start practicing!")
    except Exception as e:
        st.warning(f"Could not load results: {e}")

st.markdown("---")
st.markdown("### 💡 Tips:")
st.markdown("""
- Practice regularly to improve your aptitude scores
- Review explanations to understand concepts better
- Track your progress to identify weak areas
- Focus on categories with lower accuracy
""")
