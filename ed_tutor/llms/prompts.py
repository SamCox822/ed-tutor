from langchain.prompts import PromptTemplate

llm_quizzer_prompt = PromptTemplate(
    input_variables=["inputs"],
    template="""You are an helpful assistant tasked with helping students understand why their answer on a quiz question is incorrect. You will have access to the question that student was asked,
    the answer they provided, and the correct answer. Based on the class notes I will give you, explain to the student why their answer is incorrect.  

    Please contain your explanation to the text contained in the class notes. Please keep the discussion focused on the concepts relating to the question.
    Do not ask questions.

    {inputs}
    """)

llm_quizzer_input = """
Here are the class notes: {notes}
Here is the question student was asked: {question}
Here is what they answered (incorrect): {wrong}
Here is the correct answer: {correct}"""


llm_chat_prompt = PromptTemplate(
    input_variables=["inputs"],
    template="""You are a helpful assistant that continues a chat with a student. Before the chat, the student will have answered a question incorrectly, and they will be shown why they were wrong. Now, they will ask you questions about the topic. You have access to the history of the chat, including their answer, the correct answer, the question, and the context they were given, as well as any questions that were previously asked and answered. 

    {inputs}

    Answer the students question clearly, given the context and the chat history as context.
    """
    )

llm_chat_input = """
    Here is the chat history: {chat_history}
    Here is the context: {context}
    Here is the student's question: {question}"""