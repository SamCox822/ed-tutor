import os
import streamlit as st

#import RubricGuide
from ed_tutor.agent import StudyBuddy, LLMQuizer
from ed_tutor.chat import ChatBuddy

chat = ChatBuddy()

#make sure files exist
if not os.path.exists("context.json"):
    with open("context.json", "w") as f:
        f.write("")
if not os.path.exists("chat_history.json"):
    with open("chat_history.json", "w") as f:
        f.write("")

resume_op = st.selectbox("Mode:", ["Take Quiz", "Chat about Quiz"])
if resume_op == "Take Quiz":
    resume = False
else:
    resume = True

# Streamlit app
st.title("Quiz")

def display_quiz(quiz:str) -> str:
    with open(quiz, "r") as f:
        quiz = f.read()
    stop_code = "answer options:"
    question = quiz.split(stop_code)[0]
    return question

def get_answer_options(quiz:str) -> list:
    with open(quiz, "r") as f:
        quiz = f.read()
    #start with "answer options:"
    start = "answer options:"
    end = "correct answer:"
    options_block = quiz.split(start)[1].split(end)[0]
    options = [option.strip() for option in options_block.strip().split('\n') if option.strip()]

    #then the line after correct answer is the correct answer
    correct_answer = quiz.split(end)[1].split("\n")[1]
    return options, correct_answer

notes = st.file_uploader(
    "Upload your notes as a txt file", type=["txt"],)
# write file to disk
if notes:
    with open(notes.name, "wb") as f:
        f.write(notes.getbuffer())

    st.write("Files successfully uploaded!")
    notes_uploaded = os.path.join(os.getcwd(), notes.name)
else:
    notes_uploaded=""
    print ("No file uploaded")

llm = LLMQuizer(temperature=0, llm='gpt4', file=notes_uploaded)

#just txt for now - pdf maybe later
quiz = st.file_uploader(
    "Upload your quiz as a txt file", type=["txt"],)
# write file to disk
if quiz and notes_uploaded:
    with open(quiz.name, "wb") as f:
        f.write(quiz.getbuffer())

    st.write("Files successfully uploaded!")
    quiz_uploaded = os.path.join(os.getcwd(), quiz.name)
    options, answer = get_answer_options(quiz_uploaded)
    question = display_quiz(quiz_uploaded)
    #options is list -> make string
    question_for_study_buddy = question + ''.join(options)

    study_buddy = StudyBuddy(question=question_for_study_buddy, correct_answer=answer, quiz=quiz_uploaded, llm=llm)

    def generate_response(answer:str) -> str:
        result = study_buddy.run(answer)
        return result

    scratch = st.empty()
    question = display_quiz(quiz_uploaded)
    if not resume:
        st.write(question, allow_unsafe_html=True)
        for option in options:
            st.write(option)
        st.write('\n' + "Input the letter of the correct answer.", allow_unsafe_html=True)

        if answer := st.chat_input():
            st.chat_message("user").write(answer)
            with st.chat_message("assistant"):
                response = generate_response(answer)
                st.write(response)
    else:
        def chat_generate(question:str) -> str:
            result = chat.run(question)
            return result
        scratch = st.empty()
        st.write("How can I help?", allow_unsafe_html=True)

        if question := st.chat_input():
            st.chat_message("user").write(question)
            with st.chat_message("assistant"):
                response = chat_generate(question)
                st.write(response)

else:
    quiz_uploaded=""
    print ("No file uploaded")


