import streamlit as st
import pandas as pd
import pymongo
from pymongo import MongoClient
from datetime import datetime, timedelta

st.set_page_config(page_title="DSA Practice", layout="wide")

# MongoDB connection
try:
    client = MongoClient('mongodb://localhost:27017/')
    db = client['DSA_code_app_db']
    collection = db['submissions']
except Exception as e:
    st.error(f"MongoDB connection error: {e}")

# Streamlit UI
st.title("💻 DSA Practice Platform")
st.markdown("---")

# Tabs
tab1, tab2, tab3 = st.tabs(["Practice Problems", "Track Progress", "Leaderboard"])

with tab1:
    st.header("📚 Available DSA Problems")
    
    problems = [
        {
            "title": "Two Sum",
            "difficulty": "Easy",
            "description": "Given an array of integers nums and an integer target, return the indices of the two numbers that add up to target.",
            "examples": "Input: nums = [2,7,11,15], target = 9\nOutput: [0,1]"
        },
        {
            "title": "Reverse Array",
            "difficulty": "Easy",
            "description": "Reverse the given array in-place.",
            "examples": "Input: [1,2,3,4,5]\nOutput: [5,4,3,2,1]"
        },
        {
            "title": "Binary Search",
            "difficulty": "Easy",
            "description": "Search for a target value in a sorted array.",
            "examples": "Input: arr = [1,3,5,7,9], target = 5\nOutput: 2"
        },
        {
            "title": "Merge Sort",
            "difficulty": "Medium",
            "description": "Implement merge sort algorithm.",
            "examples": "Input: [38,27,43,3,9,82,10]\nOutput: [3,9,10,27,38,43,82]"
        },
        {
            "title": "Longest Palindrome",
            "difficulty": "Medium",
            "description": "Find the longest palindromic substring.",
            "examples": 'Input: "babad"\nOutput: "bab" or "aba"'
        }
    ]
    
    for idx, problem in enumerate(problems):
        with st.expander(f"**{idx+1}. {problem['title']}** - {problem['difficulty']}"):
            st.write(problem['description'])
            st.code(problem['examples'])
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"View Solution", key=f"view_{idx}"):
                    st.info("Solution will be shown here after implementation")
            with col2:
                if st.button(f"Submit Code", key=f"submit_{idx}"):
                    st.success("Code submission accepted!")
                    try:
                        submission = {
                            "username": "student",
                            "problem": problem['title'],
                            "timestamp": datetime.now(),
                            "status": "Accepted"
                        }
                        collection.insert_one(submission)
                    except:
                        pass

with tab2:
    st.header("📊 Your Progress")
    
    # User input
    username = st.text_input("Enter your username", "student")
    
    if username:
        try:
            # Fetch user submissions
            submissions = list(collection.find({"username": username}))
            
            if submissions:
                df = pd.DataFrame([
                    {
                        "Problem": s.get('problem', 'Unknown'),
                        "Status": s.get('status', 'Pending'),
                        "Time": s.get('timestamp', 'N/A')
                    }
                    for s in submissions
                ])
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Problems Solved", len([s for s in submissions if s.get('status') == 'Accepted']))
                with col2:
                    st.metric("Total Submissions", len(submissions))
                with col3:
                    st.metric("Success Rate", f"{(len([s for s in submissions if s.get('status') == 'Accepted'])/len(submissions)*100):.1f}%" if submissions else "0%")
                
                st.markdown("---")
                
                st.subheader("Recent Submissions")
                st.dataframe(df.sort_values("Time", ascending=False).head(10), use_container_width=True)
            else:
                st.info("No submissions yet. Start solving problems!")
        except Exception as e:
            st.warning(f"Could not load progress: {e}")

with tab3:
    st.header("🏆 Leaderboard")
    
    try:
        # Get statistics from database
        pipeline = [
            {
                "$group": {
                    "_id": "$username",
                    "solved": {"$sum": {"$cond": [{"$eq": ["$status", "Accepted"]}, 1, 0]}},
                    "total": {"$sum": 1}
                }
            },
            {
                "$sort": {"solved": -1}
            },
            {
                "$limit": 10
            }
        ]
        
        results = list(collection.aggregate(pipeline))
        
        if results:
            leaderboard_data = []
            for idx, user in enumerate(results, 1):
                leaderboard_data.append({
                    "Rank": idx,
                    "Username": user["_id"],
                    "Problems Solved": user["solved"],
                    "Submission Rate": f"{(user['solved']/user['total']*100):.1f}%"
                })
            
            df_leaderboard = pd.DataFrame(leaderboard_data)
            st.dataframe(df_leaderboard, use_container_width=True)
        else:
            st.info("No submissions yet. Be the first to solve a problem!")
    except Exception as e:
        st.info("Leaderboard data unavailable. Start practicing to see results!")

st.markdown("---")
st.markdown("### 🎯 Practice Tips:")
st.markdown("""
- **Consistency**: Practice one problem per day
- **Understand**: Read and understand the problem first
- **Code**: Write clean, optimized code
- **Test**: Test with multiple test cases
- **Review**: Learn from accepted solutions
""")
