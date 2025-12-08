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
        print(self.conversation_history)

    
    def add_history(self, role : str, content : str):
        self.conversation_history.append({"role": role, "content": content})

    

    def callLlm(self,systemPromptInput : str, userPromptInput : str, formatJson : bool = False) -> str : 
        systemPrompt = SystemMessage(content = f"Tu es {self.name}. Ton rôle est {self.description}. {systemPromptInput}")
        userPrompt =  HumanMessage({userPromptInput})
        
        messages = [systemPrompt] + self.conversation_history+ [userPrompt] 

        print(messages)

        response = self.model.bind(format="json").invoke(messages)

        print("--------------------------------------")
        print(response)

        self.add_history("user", userPrompt.content)
        self.add_history("assistant", response.content)

        save_history_to_file(self.conversation_history, f"history_{self.name}.json")

        return response.content
    