from langchain.agents import AgentExecutor
from langchain_openai import ChatOpenAI
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.prompts import PromptTemplate
from langchain.agents import ZeroShotAgent
from langchain.tools import BaseTool
import os

#dummy tool for now
class DummyTool(BaseTool): #in case we want to add tools later
    name = "dummy_tool"
    description = "This is a dummy tool. It does nothing. DO not use this tool."

    def _run(self, input):
        return input


instructions = PromptTemplate(
    input_variables=["rubric", "procedure", "report"],
    template="""You are the Professor of a general chemistry course at a university.
    I will give you the lab procedure and the report rubric. I will also give you a student's lab report. Your task is to guide the student, with the following gudie:
    1. Does the report contain all the required sections?
    2. Does the report contain all the required information and calculations?
    3. What grade would you give the student's report in each section?
    4. How can the student improve the report, based on the rubric?

    Do not use any tools. 

    Here is the rubric: {rubric}
    Here is the lab procedure: {procedure}
    Here is the student's report: {report}
    """)

class LabGuider:
    def __init__(self, temperature=0, llm='gpt4', file=None, rubric=None, procedure=None):
        self.temperature = temperature
        self.llm = llm
        self.prompt = instructions
        self.file = file
        self.rubric = rubric
        self.procedure = procedure

        with open(rubric, "r") as f:
            self.rubric = f.read()
        
        with open(procedure, "r") as f:
            self.procedure = f.read()

        if file != "":
            with open(file, "r") as f:
                self.report = f.read()

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
       
    def run(self):
        output = self.agent_instance.invoke(self.prompt.format(rubric=self.rubric, procedure=self.procedure, report=self.report))
        return output["output"]