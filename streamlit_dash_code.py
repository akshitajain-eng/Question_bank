import streamlit as st
import pandas as pd
import json

st.set_page_config(page_title="Question Bank Auditor", layout="wide")

# Custom CSS for better readability
st.markdown("""
    <style>
    .stCode { white-space: pre-wrap !important; }
    .reportview-container .main .block-container{ max-width: 95%; }
    </style>
    """, unsafe_allow_html=True)

st.title("🔍 Question Quality Auditor")

@st.cache_data
def load_data():
    # Ensure this matches your latest filename
    df = pd.read_csv('questions_evaluated_v6_6.csv')
    return df

try:
    df = load_data()
    
    # Sidebar Filters
    st.sidebar.header("Filters")
    verdict_filter = st.sidebar.multiselect("Status", options=df['final_verdict'].unique(), default=df['final_verdict'].unique())
    filtered_df = df[df['final_verdict'].isin(verdict_filter)]

    # Main Selection
    selected_id = st.selectbox("Select Question ID to Review", filtered_df['question_id'])
    q = filtered_df[filtered_df['question_id'] == selected_id].iloc[0]

    # --- Layout ---
    col1, col2 = st.columns([1, 1])


    def format_newlines(text):
        if not isinstance(text, str): return text
        return text.replace('\\\\n', '\n').replace('\\n', '\n')
    with col1:
        st.subheader("📝 Question Content")
        st.info(f"**Role:** {q['role']} | **Skill:** {q['skill']} | **Difficulty:** {q['difficulty']}")
        
        # 1. Question Text - Cleaned
        st.markdown("**Question Text:**")
        st.write(q['question_text'].replace('\\n', '\n'))
        
        # 2. Options Display - Cleaned
        st.markdown("**Options:**")
        try:
            options = json.loads(q['options_json_cleaned'])
            correct_id = str(q['correct_option_id'])
            for opt in options:
                # Replace literal \n with actual line break for each option
                # Inside your loop:
                clean_opt_text = format_newlines(opt['text'])
                label = f"{opt['option_id']}: {clean_opt_text}"
                
                if str(opt['option_id']) == correct_id:
                    st.success(f"✅ **{label} (Correct Answer)**")
                else:
                    st.write(f"⚪ {label}")
        except:
            st.error("Could not parse options_json_cleaned")

        # 3. Sample Data
        st.markdown("**Sample Data:**")
        try:
            sample_data = json.loads(q['sample_data_json'])
            # Fixed width parameter
            st.dataframe(pd.DataFrame(sample_data), width='stretch')
        except:
            st.warning("Sample data is empty or malformed.")

        # 4. Solution - Cleaned
        st.markdown("**Solution / Explanation:**")
        # Replace literal \n with actual line break for the solution code block
        # For your Solution display:
        formatted_solution = format_newlines(q['solution'])
        st.code(formatted_solution, language='python')

    with col2:
        st.subheader("⚖️ Chairman Verdict")
        color = "green" if q['final_verdict'] == "accept" else "red"
        st.markdown(f"Status: **:{color}[{q['final_verdict'].upper()}]**")
        
        st.write(f"**True Difficulty:** {q['true_difficulty']}")
        st.write(f"**Interview Ready:** {q['interview_ready']}")
        
        st.markdown("**Chairman Notes:**")
        # Cleaned \n here as well just in case
        st.warning(str(q['chairman_notes']).replace('\\n', '\n'))

        st.markdown("**Detailed Council Feedback (JSON):**")
        try:
            council_data = json.loads(q['council_json'])
            st.json(council_data)
        except:
            st.error("Could not parse Council JSON")

except FileNotFoundError:
    st.error("CSV file not found. Check the filename in the load_data() function.")