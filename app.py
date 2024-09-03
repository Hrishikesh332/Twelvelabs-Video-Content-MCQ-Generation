# Import the necessary libraries and functions
import streamlit as st
from utils import create_task, wait_for_task, generate_mcq, parse_json_with_regex, save_uploaded_file, calculate_score

def upload_and_index():

    # Minimal custom HTML and CSS
    st.markdown("""
        <h1 style='text-align: center; color: #2c3e50; font-size: 36px; font-weight: bold; margin-bottom: 30px;'>
            📹 Video Content Quiz Generator
        </h1>
    """, unsafe_allow_html=True)

    st.write("Upload a video to start the quiz generation process and test yourself!")

    # # Check if a video has already been indexed
    if 'video_id' in st.session_state and st.session_state.video_id:
        st.info("Video already indexed. Next, Proceeding to quiz generation.")
        return generate_quiz()


    # File uploader for video files
    uploaded_file = st.file_uploader("Choose a video file", type=['mp4'])

    if uploaded_file is not None:

        # Save the uploaded file
        file_path = save_uploaded_file(uploaded_file)
        st.success("File uploaded successfully!")

        # To proceed witht the indexing of the video
        with st.spinner("Indexing video... Please wait"):
            task = create_task(file_path)
            video_id = wait_for_task(task)

        st.success("Video indexed successfully!")
        st.session_state.video_id = video_id
        
        return generate_quiz()

# Utility function to generate the quiz questions based on the indexed video
def generate_quiz():

    with st.spinner("Generating quiz questions..."):
        raw_response = generate_mcq(st.session_state.video_id)
        questions = parse_json_with_regex(raw_response)

    if questions:
        st.session_state.questions = questions
        st.session_state.page = "quiz"
        st.experimental_rerun()
    else:
        st.error("Failed to generate quiz questions. Please try again.")

def quiz():
    st.title("🎓 Video Content Quiz")
    st.write("Answer the following questions based on the video content -")

    questions = st.session_state.questions
    

    # # Initialize user answers if not already done
    if 'user_answers' not in st.session_state:
        st.session_state.user_answers = {q_num: None for q_num in questions}
    if 'submitted' not in st.session_state:
        st.session_state.submitted = False


    # Display the questions and answer options
    for q_num, q_data in questions.items():
        with st.container():
            st.subheader(f"Question {q_num[-1]}")
            st.write(q_data["question"])
            
            answer = st.radio(
                f"Select your answer for Question {q_num[-1]}:",
                options=q_data["options"],
                key=f"select_{q_num}",
                index=q_data["options"].index(st.session_state.user_answers[q_num]) if st.session_state.user_answers[q_num] else 0,
                on_change=update_answer,
                args=(q_num,)
            )
        st.markdown("---")

    # Submit quiz button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        submit_button = st.button("Submit Quiz 📝", key="submit_quiz", use_container_width=True)
        if submit_button:
            submit_quiz()
            st.balloons()

    # Display results if quiz is submitted
    if st.session_state.submitted:
        display_results()

    start_over_button = st.button("Start Over 🔄", key="start_over", use_container_width=True)
    if start_over_button:
        reset_state()

def update_answer(q_num):
    # Session state, to update the user's answer
    st.session_state.user_answers[q_num] = st.session_state[f"select_{q_num}"]

def submit_quiz():
    # On the submission button, mark quiz as submitted and calculate score
    st.session_state.submitted = True
    st.session_state.score = calculate_score(st.session_state.user_answers, st.session_state.questions)

def display_results():
    # To display the user's score
    st.success(f"🏆 Your score: {st.session_state.score} out of {len(st.session_state.questions)}")

    # Display the correct results for each question
    for q_num, q_data in st.session_state.questions.items():
        with st.expander(f"Question {q_num[-1]} Details"):
            st.write(f"**Your answer:** {st.session_state.user_answers[q_num]}")
            st.write(f"**Correct answer:** {q_data['correct_answer']}")
            if st.session_state.user_answers[q_num] == q_data['correct_answer']:
                st.success("Correct! 🎉")
            else:
                st.error("Incorrect ❌")

def reset_state():
    # Clear all session state variables
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.experimental_rerun()

def main():
    # Set up the Streamlit page configuration
    st.set_page_config(page_title="QnA Generator", page_icon="🎥", layout="wide")
    
    # Custom CSS
    st.markdown("""
        <style>
        .stApp {
            background-color: #f0f2f6;
        }
        .stButton > button {
            background-color: #4CAF50;
            color: white;
            font-weight: bold;
            border-radius: 30px;
            padding: 15px 30px;
            font-size: 18px;
            transition: all 0.3s ease 0s;
            border: none;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        .stButton > button:hover {
            background-color: #45a049;
            box-shadow: 0 6px 8px rgba(0, 0, 0, 0.15);
            transform: translateY(-2px);
        }
        .stButton > button:active {
            transform: translateY(0px);
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }
        .stRadio > label {
            background-color: #e1e5eb;
            padding: 12px;
            border-radius: 8px;
            margin-bottom: 12px;
            transition: all 0.2s ease 0s;
            cursor: pointer;
        }
        .stRadio > label:hover {
            background-color: #d0d4d9;
            transform: translateY(-2px);
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        .stExpander {
            background-color: #ffffff;
            border-radius: 15px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            margin-bottom: 20px;
        }
        h1 {
            color: #2c3e50;
            font-size: 36px;
            font-weight: bold;
            margin-bottom: 20px;
        }
        h2, h3 {
            color: #34495e;
        }
        .stAlert {
            border-radius: 10px;
            font-weight: bold;
        }
        .stSpinner > div {
            border-color: #4CAF50 !important;
        }
        [data-testid="stAppViewContainer"] {
            background-image: url("https://img.freepik.com/free-photo/vivid-blurred-colorful-wallpaper-background_58702-3508.jpg?size=626&ext=jpg");
            background-size: cover;
        }
        [data-testid="stHeader"] {
            background-color: rgba(0,0,0,0);
        }
        [data-testid="stToolbar"] {
            right: 2rem;
            background-image: url("");
            background-size: cover;
        }
        </style>
    """, unsafe_allow_html=True)


    # Initialize the page state if not already set
    if 'page' not in st.session_state:
        st.session_state.page = "upload"


    # To show the appropriate page based on the current state
    if st.session_state.page == "upload":
        upload_and_index()
    elif st.session_state.page == "quiz":
        quiz()

if __name__ == "__main__":
    main()