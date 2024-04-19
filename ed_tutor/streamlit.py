import os
import streamlit as st
import shutil

from llms.quizzer import LLMQuizzer
from llms.chat import QuizChat


class StreamlitApp:

    def __init__(self):
        self.dir_path = None
        self.questions = []
        self.answers = []
        self.choices = []
        self.quiz_llm = None
        self.chat_llm = None


    def make_llms(self):
        if not self.dir_path:
            return "Please upload a quiz and notes"
        self.chat_llm = QuizChat(self.dir_path)
        self.quiz_llm = LLMQuizzer(self.dir_path)

    def make_files(self, dir_path):
        if not os.path.exists(f"{dir_path}/context.json"):
            with open(f"{dir_path}/context.json", "w") as f:
                f.write("")
        if not os.path.exists(f"{dir_path}/chat_history.json"):
            with open(f"{dir_path}/chat_history.json", "w") as f:
                f.write("")

    def make_student_folder(self, student_id:str):
        if not student_id:
            return "Please enter a student ID"
        student_path = os.path.join(os.getcwd(), "student_data", f"id_{student_id}")
        if not os.path.exists(student_path):
            os.makedirs(student_path)
        self.make_files(student_path)
        self.dir_path = student_path

    def get_all_questions_and_answers(self, quiz:str):
        with open(quiz, "r") as f:
            quiz = f.read()
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
                key = o[:1].strip()
                val = o[2:].strip()
                opts[key] = val
                opts_list.append(val)
            correct = opts[ans]
        
            questions.append(ques)
            answers.append(correct)
            choices.append(opts_list)
        self.questions = questions
        self.answers = answers
        self.choices = choices

    def get_answer_options(self, quiz_path:str) -> list:
        with open(quiz_path, "r") as f:
            quiz_path = f.read()
        #start with "answer options:"
        start = "answer options:"
        end = "correct answer:"
        options_block = quiz_path.split(start)[1].split(end)[0]
        options = [option.strip() for option in options_block.strip().split('\n') if option.strip()]

        #then the line after correct answer is the correct answer
        correct_answer = quiz_path.split(end)[1].split("\n")[1]
        return options, correct_answer

    def get_all_questions(self, selected_question_index, questions, answers, choices_list):
        if questions:  # Ensure there are questions to display
            # Display only the form for the selected question
            question, choice, answer = questions[selected_question_index], choices_list[selected_question_index], answers[selected_question_index]
            return question, choice, answer

    def display_quiz(self, quiz:str) -> str:
        with open(quiz, "r") as f:
            quiz = f.read()
        stop_code = "answer options:"
        question = quiz.split(stop_code)[0]
        return question

    def upload_file(self, content, student_id_path:str):
        if not content:
            return ""
        with open(content.name, "wb") as f:
                f.write(content.getbuffer())
        path_to_file = os.path.join(os.getcwd(), content.name)
        #copy_file_to_student_folder
        shutil.copy(path_to_file, student_id_path)
        new_path = os.path.join(student_id_path, content.name)
        return new_path

    def upload_quiz_and_notes(self):
        note_col, quiz_col = st.columns(2)
        with note_col:
            notes = st.file_uploader(
                "Upload your notes as a txt file", type=["txt"],key=f"notes")
            notes_path = self.upload_file(notes, self.dir_path)
        with quiz_col:
            quiz = st.file_uploader(
                "Upload your quiz as a txt file", type=["txt"], key=f"quiz")
            quiz_path = self.upload_file(quiz, self.dir_path)
        return notes_path, quiz_path

    def get_user_question_selection(self):
        question_indices = list(range(len(self.questions)))
        question_titles = [f"{i+1}. {self.questions[i].split('?')[0]}?" for i in question_indices]
        selected_index = st.selectbox("Select a Question", question_indices, format_func=lambda x: question_titles[x])
        return selected_index
    
    def run_llm_quizzer(self, notes_path, question, choices, answer,correct_answer):
        question=question + "\n" + '\n'.join(choices)
        self.quiz_llm.read_notes(notes_path)
        return self.quiz_llm.run(answer, question, correct_answer)
    
    def get_specific_inputs(self, question_index):
        question = self.questions[question_index]
        choices = self.choices[question_index]
        answer = self.answers[question_index]
        return question, choices, answer, question_index

    def create_question_form(self, scratch, notes_path, question_index):

        question, choices, answer, key = self.get_specific_inputs(question_index)
        with scratch.form(key=f"form_{key}"):
            st.write(question)
            # Create radio buttons for choices
            selected_choice = st.radio("Choices", choices, key=f"radio_{key}")
            
            # Submit button for the form
            submitted = st.form_submit_button("Submit")
            if submitted:
                if selected_choice == answer:
                    st.success("Correct!")
                else:
                    st.write("Incorrect. Let's see why...")
                    help = self.run_llm_quizzer(notes_path, question, choices, selected_choice, answer)
                    st.write(help)


    def run_streamlit(self):
        st.title("Quiz + Tutor")

        student_id = st.text_input("Enter your student ID", key="student_id")
        self.make_student_folder(student_id)
        self.make_llms()

        notes_path, quiz_path = self.upload_quiz_and_notes()
        if not notes_path or not quiz_path:
            return ""
        self.get_all_questions_and_answers(quiz_path)
        selected_question_index = self.get_user_question_selection()

        scratch = st.empty()
        self.create_question_form(scratch, notes_path, selected_question_index)

        scratch = st.empty()
        st.write("How can I help?", allow_unsafe_html=True)

        if question := st.chat_input():
            st.chat_message("user").write(question)
            with st.chat_message("assistant"):
                self.chat_llm.load_data(self.dir_path)
                response = self.chat_llm.run(question)
                st.write(response)

        else:
            quiz_uploaded=""
            print ("No file uploaded")


if __name__ == "__main__":
    streamlit_app = StreamlitApp()
    streamlit_app.run_streamlit()