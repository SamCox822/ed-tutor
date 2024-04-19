from langchain.chains import LLMChain
from langchain_openai import OpenAI

from .prompts import llm_chat_prompt, llm_chat_input

class QuizChat:
    def __init__(self, output_dir):
        self.output_dir = output_dir
        self.prompt = llm_chat_prompt

        self.chat_history = None
        self.context = None

        self.llm_chain = LLMChain(prompt=self.prompt, llm=OpenAI())

    def load_data(self, output_dir):
        if self.chat_history and self.context:
            return self.chat_history, self.context
        self.output_dir = output_dir
        with open(f"{self.output_dir}/context.json", "r") as f:
            context = f.read()
        context = str(context)

        with open(f"{self.output_dir}/chat_history.json", "r") as f:
            chat_history = f.read()
        #convert chat history to string
        chat_history = str(chat_history)
        return chat_history, context

    def run(self, question):
        prompt_with_inputs = llm_chat_input.format(chat_history=self.chat_history, context=self.context, question=question)
        output = self.llm_chain.run(prompt_with_inputs)
        qa = {"question": question, "answer": output}
        with open(f"{self.output_dir}/chat_history.json", "a") as f:
            f.write(str(qa))
        return output
    
