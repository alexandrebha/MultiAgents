from langchain_ollama import ChatOllama
from langchain.messages import HumanMessage
from langchain_core.messages import SystemMessage
from langchain.messages import AIMessage
from agents.utils import *

import yfinance as yf



class Agent:
    def __init__(self, name : str, description : str, modelName : str):
        self.name=name
        self.description=description
        self.model=ChatOllama(model=modelName)
        self.conversation_history = load_history_from_file(f"history_{self.name}.json")
       

    
    def add_history(self, role : str, content : str):
        self.conversation_history.append({"role": role, "content": content})

    

    def callLlm(self, systemPromptInput: str, userPromptInput: str, formatJson: bool = False, useHistory: bool = True) -> str:
        systemPrompt = SystemMessage(content=f"Tu es {self.name}. Ton role est {self.description}. {systemPromptInput}")
        userPrompt = HumanMessage(content=userPromptInput)


        if useHistory:
            messages = [systemPrompt] + self.conversation_history + [userPrompt]
        else:
            messages = [systemPrompt, userPrompt]

       
        if formatJson:
            response = self.model.bind(format="json").invoke(messages)
        else:
            response = self.model.invoke(messages)

      
        if useHistory:
            self.add_history("user", userPrompt.content)
            self.add_history("assistant", response.content)
            save_history_to_file(self.conversation_history, f"history_{self.name}.json")

        return response.content
    