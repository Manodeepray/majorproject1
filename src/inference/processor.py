import os
import json

from llama_cpp import Llama
from groq import Groq

class Colors:
    RESET = '\033[0m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    
    

    


class LLMEngine:
    def __init__(self):
        self.local_dir = os.path.join(os.path.expanduser("~"), ".cache", "qwen")
        pass
    
    def respond(self , query:str , context:str , suffix:str=None, max_tokens:int=16):
        pass
 
 
 
 
 
class FastProcessor(LLMEngine):
    """
    smaller llm used for entity  recognition from chunk / batche of chunks

    """
    
    def __init__(self):
        super().__init__()
        
        self.repo_id = "Qwen/Qwen2.5-1.5B-Instruct-GGUF"
        self.filename="qwen2.5-1.5b-instruct-q4_k_m.gguf"
        
        
        
        print(f"[ENGINE | PROCESSOR] {Colors.YELLOW} LOADING FAST_PROCESSOR {self.repo_id} FROM {self.filename} {Colors.RESET}")


        try : 
            self.llm = Llama.from_pretrained(
                                repo_id=self.repo_id,
                                filename=self.filename,
                                local_dir = self.local_dir
                            )
            print(f"[ENGINE | PROCESSOR]{Colors.GREEN} LOADED {Colors.RESET}")
        
        except:
            
            
            raise FileNotFoundError(f"{Colors.RED}[ERROR] couldn't load llm from {self.filename} or {self.repo_id} {Colors.RESET}")
        


    def respond(self , query:str =None, context:str=None , suffix:str=None, max_tokens:int=1024, schema:dict=None):
        
        user_prompt = context
        if suffix:
            user_prompt += f"\n\n{suffix}"
        try:
            completion = self.llm.create_chat_completion(
                messages=[
                    {
                        "role": "system",
                        "content": query,
                    },
                    {"role": "user", "content": user_prompt},
                ],
                response_format={
                        "type": "json_object",
                        "schema": schema,
                    },
                    temperature=0.7,
                    max_tokens=max_tokens,
            )
            return completion["choices"][0]["message"]['content']
        except Exception as e:
            print(f"{Colors.RED}[ERROR] Fast Processor : {self.repo_id} call failed: {e}{Colors.RESET}")
            return None
 
    
    
    
    
class LargeProcessor(LLMEngine):
    """
    Larger llm used for
    -> KNOWLEDGE GRAPH creation.
    -> agentic calls
    -> prompt cycling/ de construction
    Uses Groq API.
    """

    def __init__(self):
        super().__init__()
        print(f"[ENGINE | PROCESSOR] {Colors.YELLOW} INITIALIZING LARGE_PROCESSOR with Groq API {Colors.RESET}")
        try:
            self.client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
            print(f"[ENGINE | PROCESSOR]{Colors.GREEN} Groq Client Initialized {Colors.RESET}")
        except Exception as e:
            raise ConnectionError(f"{Colors.RED}[ERROR] couldn't initialize Groq client: {e} {Colors.RESET}")

    def respond(self, query: str = None, context: str = None, suffix: str = None, max_tokens: int = 1024, schema: dict = None):
        """
        Generates a response using the Groq API.
        """
        user_prompt = context
        if suffix:
            user_prompt += f"\n\n{suffix}"

        system_prompt = query

        params = {
            "messages": [
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": user_prompt,
                }
            ],
            "model": "llama-3.1-8b-instant",
            "max_tokens": max_tokens,
            "temperature": 0.5,
            "top_p": 1,
            "stop": None,
            "stream": False,
        }

        if schema:
            params["response_format"] = {"type": "json_object", "schema": schema}
            # Groq API requires 'json' in the prompt when using json_object response_format
            if "json" not in params["messages"][0]["content"].lower():
                params["messages"][0]["content"] += "\n\nProvide the output in JSON format."

        try:
            chat_completion = self.client.chat.completions.create(**params)
            response = chat_completion.choices[0].message.content
            return response
        except Exception as e:
            print(f"{Colors.RED}[ERROR] Groq API call failed: {e}{Colors.RESET}")
            return None
            




if __name__ == "__main__":
    processor = FastProcessor()
    # processor = LargeProcessor()
    
    schema = {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "age": {"type": "number"}
        },
        "required": ["name", "age"]
    }

    print(processor.respond(query="Extract user details from context", context="My name is John and I am 25 years old.", schema=schema))
    
