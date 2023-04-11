import streamlit as st
from collections import defaultdict
import time
import json
import db_connection_functions as dbf
def footer():
    footer_col1, footer_col2, footer_col3 = st.columns([1, 4, 1])

    with footer_col2:
        st.markdown(
            """
            <div style="text-align: center; margin-top: 30px; font-size: 12px;">
                &copy; 2023 HomeworkBuddies Project Inc.
            </div>
            """,
            unsafe_allow_html=True,
        )

def main():
    st.title("MatchingNeeds Projects")
    st.sidebar.title("MatchingNeeds Projects")
    st.sidebar.info("An app to help college students connect with each other based on their current and past classes.")
    
    page = st.sidebar.selectbox("Choose a page", ["Register", "Look Up","Suggestions"])
    engine = dbf.start_engine()

    if page == "Register":
        register_page(engine)
    elif page == "Look Up":
        look_up_page(engine)
    elif page == "Suggestions":
        suggestion_page(engine)
    
    footer()
# def save_feedback(feedback):
#     # Save the feedback to a database or a file
#     with open('feedback.txt', 'a') as f:
#         f.write(f"{feedback}\n")
#         f.write("---\n")

def suggestion_page(engine):
    st.header("Suggestions and Feedback")
    feedback = st.text_area("Please leave your suggestion or feedback:")

    if st.button("Submit"):
        # Save feedback to the database
        dbf.add_feedback(feedback,engine)

        st.success("Your feedback has been submitted. Thank you!")    
def register_page(engine):
    st.header("Register")

    net_id = st.text_input("Net ID (3 letters and 4 numbers):")
    
    existing_user=dbf.check_user(engine,net_id)

    if existing_user:
        st.warning("Net ID already registered. Please choose a different one.")
        return
    
    security_questions = [
        "What is your favorite professor at NYU?",
        "What is the name of your first pet?",
        "What is the name of your favorite coffee shop?"
    ]
    chosen_questions = st.multiselect("Choose 2 security questions:", security_questions)

    if len(chosen_questions) != 2:
        st.warning("Please select exactly 2 security questions.")
        return

    security_answers = [st.text_input(f"Answer: {question}") for question in chosen_questions]

    current_classes = st.text_area("Current classes (comma-separated):")
    past_classes = st.text_area("Past classes with grade B or better (comma-separated):")

    if st.button("Register"):
        dbf.add_user_to_database(
            engine,
            net_id,
            chosen_questions,
            security_answers,
            list(set(current_classes.split(','))),
            list(set(past_classes.split(',')))
        )

            
        st.success("User registered!")

def look_up_page(engine):
    st.header("Look Up")

    if "step" not in st.session_state:
        st.session_state["step"] = 0
        st.session_state["input_answers"] = []
        st.session_state["net_id"] = ""
    # user = ""
    if st.session_state["step"] == 0:
        st.session_state["net_id"] = st.text_input("Net ID:")
        user = dbf.get_user_by_net_id(engine, st.session_state["net_id"])

        if st.button("Look Up"):
            if user is None:
                st.warning("Net ID not found. Please go to the Register page.")
                return
            st.session_state["step"] = 1
            
    try:
        if st.session_state["step"] == 1 and user['questions'] is not None:
            for idx, question in enumerate(user['questions'][:st.session_state["step"]]):
                st.markdown(f"**Security Question {idx + 1}:**")
                st.write(question)
                input_answer = st.text_input(f"Answer {idx + 1}:", value=st.session_state["input_answers"][idx] if st.session_state["input_answers"] else '')

                if st.button(f"Submit Answer {idx + 1}"):
                    if input_answer.lower() != user["answers"][idx].lower():
                        st.warning("Incorrect security answer.")
                    else:
                        st.session_state["input_answers"].append(input_answer)
                        st.session_state["step"] += 1
    except:
        st.warning("Please, reload the page.")
    if st.session_state["step"] == 2 and user['questions'] is not None:
        question = user['questions'][1]
        st.markdown("**Security Question 2:**")
        st.write(question)
        input_answer = st.text_input("Answer 2:")

        if st.button("Submit Answer 2"):
            if input_answer.lower() != user["answers"][1].lower():
                st.warning("Incorrect security answer.")
            else:
                st.session_state["input_answers"].append(input_answer)
                st.session_state["step"] += 1

    if st.session_state["step"] == 3:
        if st.button("Find Matches"):
            with st.spinner("Looking for matches..."):
                progress = st.progress(0)

                for i in range(100):
                    time.sleep(0.01)
                    progress.progress(i + 1)

            st.success("Logged in successfully!")

            st.header("Your Classes:")
            st.write(f"Current Classes: {', '.join(user['current_classes'])}")
            st.write(f"Past Classes: {', '.join(user['past_classes'])}")

            st.header("Matches:")

            matches = dbf.get_matches(engine, st.session_state["net_id"])

            for match in matches:
                st.write(f"Match found: {match['net_id']}")
                st.write(f"Current Classes: {', '.join(match['current_classes'])}")
                st.write(f"Past Classes: {', '.join(match['past_classes'])}")
                st.write("---")

            # Reset session state variables only after showing the matches
            st.session_state["step"] = 0
            st.session_state["input_answers"] = []


if __name__ == "__main__":
    main()
