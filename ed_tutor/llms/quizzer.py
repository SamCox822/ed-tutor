
from langchain.chains import LLMChain
from langchain_openai import OpenAI

from .prompts import llm_quizzer_prompt, llm_quizzer_input

class LLMQuizzer:
    def __init__(self, output_dir):
        self.prompt = llm_quizzer_prompt
        self.notes = None
        self.output_dir = output_dir

        self.llm_chain = LLMChain(prompt=self.prompt, llm=OpenAI())

    def read_notes(self, file):
        with open(file, "r") as f:
            self.notes = f.read()

    def _check_answer(self, answer:str, correct_answer:str) -> bool:
        answer = answer.lower().strip()
        correct_answer = correct_answer.lower().strip()
        return answer == correct_answer

    def run_llm(self, wrong, question, correct_answer):
        prompt_with_inputs = llm_quizzer_input.format(notes=self.notes, question=question, wrong=wrong, correct=correct_answer)
        return self.llm_chain.run(prompt_with_inputs)
    
    def run(self, answer:str, question:str, correct_answer:str) -> str:
    
        #write to json file called context.json
        context = {"question": question, "correct_answer": correct_answer, "student answer": answer}
        message = self.run_llm(answer, question, correct_answer)
        context["message"] = message
        #write to json
        with open(f"{self.output_dir}/context.json", "a") as f:
            f.write(str(context))
        return message
