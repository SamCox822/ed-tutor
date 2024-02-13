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

def get_all_questions_and_answers(quiz:str):
    with open(quiz, "r") as f:
        quiz = f.read()
    stop_code = "answer options:"
    full_qs = quiz.split('\n\n')

    questions = []
    answers = []
    choices = []
    for q in full_qs:
        ques = q.split('answer options:')[0].strip()
        ans = q.split('correct answer:')[1].strip()
        opts = {}
        opts_list = []
        opts_str = q.split('correct answer:')[0].split('answer options:')[1].strip().split('\n')
        print(opts_str)
        for o in opts_str:
            # key = o.split(')')[0].strip()
            # val = o.split(')')[1].strip()
            key = o[:1].strip()
            val = o[2:].strip()
            opts[key] = val
            opts_list.append(val)
        correct = opts[ans]
    
        questions.append(ques)
        answers.append(correct)
        choices.append(opts_list)

    return questions, answers, choices

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

    questions, answers, choices_list = get_all_questions_and_answers(quiz_uploaded)
    
    def chat_generate(question:str) -> str:
            result = chat.run(question)
            return result

    scratch = st.empty()
    def create_question_form(question, choices, answer, key):
        with scratch.form(key=f"form_{key}"):
            st.write(question)
            # Create radio buttons for choices
            selected_choice = st.radio("Choices", choices, key=f"radio_{key}")
            
            # Submit button for the form
            submitted = st.form_submit_button("Submit")
            study_buddy = StudyBuddy(question=question + "\n" + '\n'.join(choices), correct_answer=answer, quiz=quiz_uploaded, llm=llm)
            if submitted:
                if selected_choice == answer:
                    st.success("Correct!")
                else:
                    st.write("Incorrect. Let's see why...")
                    help = study_buddy.run(answer)
                    st.write(help)


    # Iterate over each question and create a form
    for i, (question, choice, answer) in enumerate(zip(questions, choices_list, answers)):
        create_question_form(question, choice, answer, i)

    # options, answer = get_answer_options(quiz_uploaded)
    # question = display_quiz(quiz_uploaded)
    # #options is list -> make string
    # question_for_study_buddy = question + ''.join(options)

    # study_buddy = StudyBuddy(question=question_for_study_buddy, correct_answer=answer, quiz=quiz_uploaded, llm=llm)

    # def generate_response(answer:str) -> str:
    #     result = study_buddy.run(answer)
    #     return result

    # scratch = st.empty()
    # question = display_quiz(quiz_uploaded)
    if not resume:
        pass
        # st.write(question, allow_unsafe_html=True)
        # for option in options:
        #     st.write(option)
        # st.write('\n' + "Input the letter of the correct answer.", allow_unsafe_html=True)

        # if answer := st.chat_input():
        #     st.chat_message("user").write(answer)
        #     with st.chat_message("assistant"):
        #         response = generate_response(answer)
        #         st.write(response)
    else:
        # def chat_generate(question:str) -> str:
        #     result = chat.run(question)
        #     return result
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


