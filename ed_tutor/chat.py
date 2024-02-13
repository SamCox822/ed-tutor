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
        input_variables=["chat_history", "context", "question"],
        template="""You are a helpful assistant that continues a chat with a student. Before the chat, the student will have answered a question incorrectly, and they will be shown why they were wrong. Now, they will ask you questions about the topic. You have access to the history of the chat, including their answer, the correct answer, the question, and the context they were given, as well as any questions that were previously asked and answered. 

        Here is the chat history: {chat_history}
        Here is the context: {context}
        Here is the student's question: {question}

        Answer the students question clearly, given the context and the chat history as context.
        """
        )

class ChatBuddy:
    def __init__(self, temperature=0, llm='gpt4'):
        self.temperature = temperature
        self.llm = llm
        self.prompt = instructions

        #get context from context.json
        with open("context.json", "r") as f:
            self.context = f.read()
        #convert context to string
        self.context = str(self.context)

        #get chat history from chat_history.json
        with open("chat_history.json", "r") as f:
            self.chat_history = f.read()
        #convert chat history to string
        self.chat_history = str(self.chat_history)

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

    def run(self, question):
        #write to chat_history.json
        output = self.agent_instance.invoke(self.prompt.format(chat_history=self.chat_history, context=self.context, question=question))
        output = output["output"]
        qa = {"question": question, "answer": output}
        with open("chat_history.json", "a") as f:
            f.write(str(qa))
        return output
    
