import requests

class OllamaClient:
    """
    Клиент для работы с Ollama API
    """
    def __init__(self, base_url="http://localhost:11434", model="llama2"):
        self.base_url = base_url
        self.model = model
    
    def test_connection(self):
        """Проверка подключения к Ollama"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def list_models(self):
        """Список доступных моделей"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                return response.json().get('models', [])
            return []
        except:
            return []
    
    def generate(self, prompt, system_prompt=None):
        """Генерация текста"""
        url = f"{self.base_url}/api/generate"
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False
        }
        if system_prompt:
            payload["system"] = system_prompt
        
        try:
            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()
            return response.json().get('response', '')
        except Exception as e:
            print(f"Ошибка: {e}")
            return None
    
    def chat(self, messages):
        """Чат с моделью"""
        url = f"{self.base_url}/api/chat"
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False
        }
        
        try:
            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()
            return response.json().get('message', {}).get('content', '')
        except Exception as e:
            print(f"Ошибка: {e}")
            return None

# Создаём экземпляр клиента
ollama_client = OllamaClient()
