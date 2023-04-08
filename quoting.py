import streamlit as st
from collections import defaultdict
import time
import json



def main():
    st.title("Quoting App")

    page = st.sidebar.selectbox("Choose a page", ["Register", "Look Up"])

    if page == "Register":
        register_page()
    elif page == "Look Up":
        look_up_page()

def register_page():
    st.header("Register")
    
    with open('user_data.json', 'r') as f:
        user_data = json.load(f)

    net_id = st.text_input("Net ID (3 letters and 4 numbers):")
    
    if net_id in user_data:
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
        user_data[net_id] = {
            "questions": chosen_questions,
            "answers": security_answers,
            "current_classes": list(set(current_classes.split(','))),
            "past_classes": list(set(past_classes.split(',')))
        }
        
        with open('user_data.json', 'w') as f:
            json.dump(user_data, f)
            
        st.success("User registered!")

def look_up_page():
    st.header("Look Up")
    
    with open('user_data.json', 'r') as f:
        user_data = json.load(f)

    if "step" not in st.session_state:
        st.session_state["step"] = 0
        st.session_state["input_answers"] = []
        st.session_state["net_id"] = ""

    user = None
    chosen_questions = None

    if st.session_state["net_id"] in user_data:
        user = user_data[st.session_state["net_id"]]
        chosen_questions = user["questions"]

    if st.session_state["step"] == 0:
        st.session_state["net_id"] = st.text_input("Net ID:")

        if st.button("Look Up"):
            if st.session_state["net_id"] not in user_data:
                st.warning("Net ID not found. Please go to the Register page.")
                return
            st.session_state["step"] = 1

    if st.session_state["step"] == 1 and chosen_questions is not None:
        for idx, question in enumerate(chosen_questions[:st.session_state["step"]]):
            st.markdown(f"**Security Question {idx + 1}:**")
            st.write(question)
            input_answer = st.text_input(f"Answer {idx + 1}:", value=st.session_state["input_answers"][idx] if st.session_state["input_answers"] else '')

            if st.button(f"Submit Answer {idx + 1}"):
                if input_answer.lower() != user["answers"][idx].lower():
                    st.warning("Incorrect security answer.")
                else:
                    st.session_state["input_answers"].append(input_answer)
                    st.session_state["step"] += 1

    if st.session_state["step"] == 2 and chosen_questions is not None:
        question = chosen_questions[1]
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

            for other_net_id, other_user in user_data.items():
                if other_net_id == st.session_state["net_id"]:
                    continue

                if (
                    len(set(user["current_classes"]) & set(other_user["past_classes"])) > 0
                    and len(set(user["past_classes"]) & set(other_user["current_classes"])) > 0
                ):
                    st.write(f"Match found: {other_net_id}")
                    st.write(f"Current Classes: {', '.join(other_user['current_classes'])}")
                    st.write(f"Past Classes: {', '.join(other_user['past_classes'])}")
                    st.write("---")

            # Reset session state variables only after showing the matches
            st.session_state["step"] = 0
            st.session_state["input_answers"] = []


if __name__ == "__main__":
    main()
