import requests

def test_ollama():
    print("=" * 50)
    print("ПРОВЕРКА OLLAMA")
    print("=" * 50)
    
    # 1. Проверка подключения
    print("\n1. Проверка подключения...")
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            print("   ✅ Ollama доступна!")
        else:
            print("   ❌ Ollama не отвечает")
            return
    except:
        print("   ❌ Ollama не доступна!")
        print("   Запустите: ollama serve")
        return
    
    # 2. Список моделей
    print("\n2. Список моделей:")
    try:
        data = response.json()
        models = data.get('models', [])
        if models:
            for model in models:
                name = model.get('name', 'unknown')
                size = model.get('size', 0) / (1024**3)
                print(f"   ✅ {name} ({size:.1f} GB)")
        else:
            print("   ❌ Модели не найдены!")
            print("   Скачайте: ollama pull llama2")
            return
    except:
        print("   ❌ Ошибка получения списка моделей")
        return
    
    # 3. Тест генерации
    print("\n3. Тест генерации...")
    try:
        payload = {
            "model": "llama2",
            "prompt": "Напиши приветствие для соцсети",
            "stream": False
        }
        response = requests.post(
            "http://localhost:11434/api/generate",
            json=payload,
            timeout=30
        )
        if response.status_code == 200:
            result = response.json()
            text = result.get('response', '')
            print(f"   ✅ Ответ получен!")
            print(f"   📝 {text[:150]}...")
        else:
            print("   ❌ Ошибка генерации")
    except Exception as e:
        print(f"   ❌ Ошибка: {e}")
    
    print("\n" + "=" * 50)
    print("ПРОВЕРКА ЗАВЕРШЕНА")
    print("=" * 50)

if __name__ == "__main__":
    test_ollama()
