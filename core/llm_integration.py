from typing import Optional, Dict, Any, List
from openai import OpenAI
from core.config import Config
from utils.helpers import log_execution, get_logger

class LLMIntegration:
    
    def __init__(self):
        """
        Инициализация клиента OpenAI с настройками для OpenRouter
        """
        self.logger = get_logger("llm_integration")
        self.client = self._initialize_client()
        self.logger.info("Инициализирован клиент LLM")
    
    @log_execution()
    def _initialize_client(self) -> OpenAI:
        return OpenAI(
            base_url=Config.OPENAI_API_BASE,
            api_key=Config.OPENAI_API_KEY
        )
    
    @log_execution()
    def call_model(
        self,
        messages: List[Dict[str, str]],
        model: str = Config.DEFAULT_MODEL,
        temperature: float = Config.DEFAULT_TEMPERATURE,
        max_tokens: int = Config.DEFAULT_MAX_TOKENS,
        stream: bool = False
    ) -> Optional[Dict[str, Any]]:
        try:
            response = self.client.chat.completions.create(
                model=Config.MODELS.get(model, Config.MODELS[Config.DEFAULT_MODEL]),
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                extra_body={}
            )
            return response
        except Exception as e:
            print(f"Ошибка при вызове модели {model}: {str(e)}")
            return None


    @log_execution()
    def call_llama(self, prompt: str, **kwargs) -> Optional[str]:
        messages = [{"role": "user", "content": prompt}]
        response = self.call_model(messages, model="llama_3.1_nemotron", **kwargs)
        return self._extract_response_text(response, "llama_3.1_nemotron")
    

    @log_execution()
    def call_qwen(self, prompt: str, **kwargs) -> Optional[str]:
        messages = [{"role": "user", "content": prompt}]
        response = self.call_model(messages, model="qwen3_325b", **kwargs)
        return self._extract_response_text(response, "qwen3_325b")
    

    @log_execution()
    def call_deepseek_v3(self, prompt: str, **kwargs) -> Optional[str]:
        messages = [{"role": "user", "content": prompt}]
        response = self.call_model(messages, model="deepseek_v3", **kwargs)
        return self._extract_response_text(response, "deepseek_v3")
    

    @log_execution()
    def call_deepseek_r1(self, prompt: str, **kwargs) -> Optional[str]:
        messages = [{"role": "user", "content": prompt}]
        response = self.call_model(messages, model="deepseek_r1", **kwargs)
        return self._extract_response_text(response, "deepseek_r1")
    

    @log_execution()
    def call_gemini_flash(self, prompt: str, **kwargs) -> Optional[str]:
        messages = [{"role": "user", "content": prompt}]
        response = self.call_model(messages, model="gemini_2.5_flash", **kwargs)
        return self._extract_response_text(response, "gemini_2.5_flash")
    

    @log_execution()
    def call_grok_mini(self, prompt: str, **kwargs) -> Optional[str]:
        messages = [{"role": "user", "content": prompt}]
        response = self.call_model(messages, model="grok3_mini", **kwargs)
        return self._extract_response_text(response, "grok3_mini")
    

    @log_execution()
    def call_gpt_mini(self, prompt: str, **kwargs) -> Optional[str]:
        messages = [{"role": "user", "content": prompt}]
        response = self.call_model(messages, model="gpt4o_mini", **kwargs)
        return self._extract_response_text(response, "gpt4o_mini")


    @log_execution()
    def _extract_response_text(self, response, model_name: str) -> Optional[str]:
        if response and hasattr(response, 'choices'):
            content = response.choices[0].message.content
            self.logger.debug(f"Ответ от {model_name}: {content[:200]}...")
            return content
        return None