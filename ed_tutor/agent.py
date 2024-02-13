from langchain.agents import AgentExecutor
from langchain_openai import ChatOpenAI
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.prompts import PromptTemplate
from langchain.agents import ZeroShotAgent
from langchain.tools import BaseTool
from langchain_openai import ChatOpenAI

#dummy tool for now
class DummyTool(BaseTool): #in case we want to add tools later
    name = "dummy_tool"
    description = "This is a dummy tool. It does nothing. DO not use this tool."

    def _run(self, input):
        return input


instructions = PromptTemplate(
        input_variables=["notes", "question", "wrong", "correct"],
        template="""You are an helpful assistant tasked with helping students understand why their answer on a quiz question is incorrect. You will have access to the question that student was asked,
        the answer they provided, and the correct answer. Based on the class notes I will give you, explain to the student why their answer is incorrect.  

        Please contain your explanation to the text contained in the class notes. Please keep the discussion focused on the concepts relating to the question.
        Do not ask questions.

        Here are the class notes: {notes}
        Here is the question student was asked: {question}
        Here is what they answered (incorrect): {wrong}
        Here is the correct answer: {correct}
        """
        )

class LLMQuizer:
    def __init__(self, temperature=0, llm='gpt4', file=""):
        self.temperature = temperature
        self.llm = llm
        self.prompt = instructions
        self.file = file

        if file != "":
            with open(file, "r") as f:
                self.notes = f.read()

        self.model = ChatOpenAI(
            temperature=self.temperature,
            model="gpt-4",
            client=None,
            streaming=True,
            verbose=True,
            callbacks=[StreamingStdOutCallbackHandler()],
        )
        self.tools = [DummyTool()]
        
        self.agent_instance = AgentExecutor.from_agent_and_tools(
            tools=self.tools,
            agent=ZeroShotAgent.from_llm_and_tools(
                llm=self.model, tools=self.tools
            ),
            handle_parsing_errors=True,
            return_intermediate_steps=False,
            verbose=False
        )

       
    def run(self, wrong, question, correct):
        output = self.agent_instance.invoke(self.prompt.format(notes=self.notes, question=question, wrong=wrong, correct=correct))
        return output["output"]

class StudyBuddy():
    #input a quiz and display one question to student
    #take in a student answer
    #if wrong, call the lab guider to help student
    LLMQuizer = LLMQuizer
    #create blank file context.json
    with open("context.json", "w") as f:
        f.write("")

    def __init__(self, question:str = None, correct_answer:str = None, quiz:str=None, llm=None):
        self.llm = llm
        self.correct_answer = correct_answer
        self.quiz = quiz
        self.question=question
    
    def _check_answer(self, answer:str, correct_answer:str) -> bool:
        answer = answer.lower().strip()
        correct_answer = correct_answer.lower().strip()
        return answer == correct_answer
    
    def _if_wrong(self, wrong:str):
        return self.llm.run(wrong, question=self.question, correct=self.correct_answer)
    
    def run(self, answer:str) -> str:
        #write to json file called context.json
        context = {"question": self.question, "correct_answer": self.correct_answer, "student answer": answer}
        message = self._if_wrong(answer)
        context["message"] = message
        #write to json
        with open("context.json", "a") as f:
            f.write(str(context))
        return message
