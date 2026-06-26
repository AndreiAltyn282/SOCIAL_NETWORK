#!/usr/bin/env python
"""
Скрипт проверки структуры проекта ProSocial
Запуск: python check_project.py
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

# Цвета для вывода
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(text):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.END}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(60)}{Colors.END}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.END}\n")

def print_success(text):
    print(f"{Colors.GREEN}✅ {text}{Colors.END}")

def print_error(text):
    print(f"{Colors.RED}❌ {text}{Colors.END}")

def print_warning(text):
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.END}")

def print_info(text):
    print(f"{Colors.BLUE}ℹ️  {text}{Colors.END}")

def print_file_status(filename, exists, required=True):
    if exists:
        print_success(f"Найден: {filename}")
        return True
    else:
        if required:
            print_error(f"ОТСУТСТВУЕТ: {filename} (обязательный файл)")
        else:
            print_warning(f"ОТСУТСТВУЕТ: {filename} (рекомендуемый файл)")
        return False

class ProjectChecker:
    def __init__(self, root_dir):
        self.root_dir = Path(root_dir)
        self.results = {
            'required_files': [],
            'optional_files': [],
            'apps': {},
            'models': [],
            'views': [],
            'serializers': [],
            'urls_config': False,
            'settings_config': False,
            'issues': [],
            'warnings': []
        }
        
    def check_root_files(self):
        """Проверяет файлы в корне проекта"""
        print_header("ПРОВЕРКА ФАЙЛОВ В КОРНЕ ПРОЕКТА")
        
        required_files = [
            'manage.py',
            'requirements.txt',
            '.env',
            'check_project.py'
        ]
        
        optional_files = [
            'README.md',
            '.gitignore',
            'docker-compose.yml',
            'Dockerfile'
        ]
        
        for file in required_files:
            exists = (self.root_dir / file).exists()
            print_file_status(file, exists, required=True)
            if not exists:
                self.results['issues'].append(f"Отсутствует обязательный файл: {file}")
        
        for file in optional_files:
            exists = (self.root_dir / file).exists()
            print_file_status(file, exists, required=False)
            if not exists:
                self.results['warnings'].append(f"Отсутствует рекомендуемый файл: {file}")
    
    def check_settings(self):
        """Проверяет настройки Django"""
        print_header("ПРОВЕРКА НАСТРОЕК DJANGO")
        
        settings_file = self.root_dir / 'social_network' / 'settings.py'
        
        if not settings_file.exists():
            print_error("Файл settings.py не найден!")
            self.results['issues'].append("Отсутствует settings.py")
            return
            
        print_success("Файл settings.py найден")
        
        # Читаем содержимое
        with open(settings_file, 'r') as f:
            content = f.read()
        
        # Проверяем основные настройки
        checks = {
            'INSTALLED_APPS': 'INSTALLED_APPS' in content,
            'MIDDLEWARE': 'MIDDLEWARE' in content,
            'DATABASES': 'DATABASES' in content,
            'REST_FRAMEWORK': 'REST_FRAMEWORK' in content,
            'CHANNEL_LAYERS': 'CHANNEL_LAYERS' in content,
            'CORS_ALLOWED_ORIGINS': 'CORS_ALLOWED_ORIGINS' in content,
            'ASGI_APPLICATION': 'ASGI_APPLICATION' in content,
        }
        
        for key, exists in checks.items():
            if exists:
                print_success(f"{key} настроен")
            else:
                print_warning(f"{key} не найден в настройках")
                self.results['warnings'].append(f"Возможно отсутствует {key} в настройках")
        
        self.results['settings_config'] = True
        
        # Проверяем установленные приложения
        if 'INSTALLED_APPS' in content:
            import re
            apps = re.findall(r"['\"](\w+)['\"]", content.split('INSTALLED_APPS = [')[1].split(']')[0])
            print_info(f"Найдены приложения: {', '.join(apps)}")
            self.results['installed_apps'] = apps
    
    def check_urls(self):
        """Проверяет URL конфигурацию"""
        print_header("ПРОВЕРКА URL КОНФИГУРАЦИИ")
        
        urls_file = self.root_dir / 'social_network' / 'urls.py'
        
        if not urls_file.exists():
            print_error("Файл urls.py не найден!")
            self.results['issues'].append("Отсутствует urls.py")
            return
            
        print_success("Файл urls.py найден")
        
        with open(urls_file, 'r') as f:
            content = f.read()
        
        checks = {
            'admin/': "path('admin/" in content or "path('admin/" in content,
            'api/': "path('api/" in content,
            'api/token/': "api/token" in content,
        }
        
        for key, exists in checks.items():
            if exists:
                print_success(f"URL {key} настроен")
            else:
                print_warning(f"URL {key} не найден")
                self.results['warnings'].append(f"Отсутствует URL: {key}")
        
        self.results['urls_config'] = True
    
    def check_apps(self):
        """Проверяет все приложения"""
        print_header("ПРОВЕРКА ПРИЛОЖЕНИЙ")
        
        # Ищем все папки с __init__.py
        app_dirs = []
        for item in self.root_dir.iterdir():
            if item.is_dir() and (item / '__init__.py').exists():
                # Исключаем системные папки
                if item.name not in ['venv', 'env', 'social_network', '__pycache__', 'static', 'media', 'migrations']:
                    app_dirs.append(item.name)
        
        if not app_dirs:
            print_warning("Приложения не найдены!")
            return
        
        print_info(f"Найдено приложений: {len(app_dirs)}")
        print_info(f"Список: {', '.join(app_dirs)}")
        
        required_apps = ['users', 'posts']
        recommended_apps = ['comments', 'messages_app', 'subscriptions', 'startup_packs', 'notifications', 'core', 'ai']
        
        print("\nПроверка обязательных приложений:")
        for app in required_apps:
            exists = app in app_dirs
            print_file_status(f"Приложение {app}", exists, required=True)
            if exists:
                self.check_app_structure(app)
        
        print("\nПроверка рекомендуемых приложений:")
        for app in recommended_apps:
            exists = app in app_dirs
            print_file_status(f"Приложение {app}", exists, required=False)
            if exists:
                self.check_app_structure(app)
            else:
                self.results['warnings'].append(f"Рекомендуется создать приложение: {app}")
        
        self.results['apps'] = {app: True for app in app_dirs}
    
    def check_app_structure(self, app_name):
        """Проверяет структуру конкретного приложения"""
        app_path = self.root_dir / app_name
        
        required_files = ['__init__.py', 'models.py', 'views.py']
        optional_files = ['serializers.py', 'admin.py', 'urls.py', 'tests.py']
        
        # Проверяем обязательные файлы
        for file in required_files:
            exists = (app_path / file).exists()
            if not exists:
                print_warning(f"  {app_name}/{file} отсутствует")
                self.results['warnings'].append(f"В приложении {app_name} отсутствует {file}")
        
        # Проверяем наличие моделей
        models_file = app_path / 'models.py'
        if models_file.exists():
            with open(models_file, 'r') as f:
                content = f.read()
                if 'class' in content and 'models.Model' in content:
                    print_success(f"  {app_name}: модели найдены")
                else:
                    print_warning(f"  {app_name}: модели не найдены")
    
    def check_models(self):
        """Проверяет все модели в проекте"""
        print_header("ПРОВЕРКА МОДЕЛЕЙ")
        
        # Ищем все файлы models.py
        models_files = list(self.root_dir.glob('*/models.py'))
        models_files = [f for f in models_files if 'venv' not in str(f)]
        
        if not models_files:
            print_warning("Файлы models.py не найдены")
            return
        
        print_info(f"Найдено файлов models.py: {len(models_files)}")
        
        for models_file in models_files:
            app_name = models_file.parent.name
            print(f"\n{Colors.BLUE}📄 {app_name}/models.py{Colors.END}")
            
            with open(models_file, 'r') as f:
                content = f.read()
                import re
                # Ищем классы моделей
                models = re.findall(r'class\s+(\w+)\(.*models\.Model.*\):', content)
                
                if models:
                    for model in models:
                        print_success(f"  Найдена модель: {model}")
                    self.results['models'].extend([(app_name, model) for model in models])
                else:
                    print_warning(f"  Модели не найдены")
    
    def check_ws_files(self):
        """Проверяет наличие WebSocket файлов"""
        print_header("ПРОВЕРКА WEBSOCKET")
        
        # Проверяем наличие channels в настройках
        settings_file = self.root_dir / 'social_network' / 'settings.py'
        if settings_file.exists():
            with open(settings_file, 'r') as f:
                content = f.read()
                if 'channels' in content and 'CHANNEL_LAYERS' in content:
                    print_success("Channels настроен")
                else:
                    print_warning("Channels не настроен")
                    self.results['warnings'].append("Channels не настроен для WebSocket")
        
        # Проверяем consumers
        consumers_files = list(self.root_dir.glob('**/consumers.py'))
        consumers_files = [f for f in consumers_files if 'venv' not in str(f)]
        
        if consumers_files:
            print_success(f"Найдены consumers.py: {', '.join([str(f.parent.name) for f in consumers_files])}")
        else:
            print_warning("Файлы consumers.py не найдены")
            self.results['warnings'].append("Нет файлов consumers.py для WebSocket")
        
        # Проверяем asgi.py
        asgi_file = self.root_dir / 'social_network' / 'asgi.py'
        if asgi_file.exists():
            print_success("asgi.py найден")
        else:
            print_warning("asgi.py не найден")
            self.results['warnings'].append("asgi.py не найден для WebSocket")
    
    def check_env(self):
        """Проверяет переменные окружения"""
        print_header("ПРОВЕРКА ПЕРЕМЕННЫХ ОКРУЖЕНИЯ")
        
        env_file = self.root_dir / '.env'
        if not env_file.exists():
            print_error(".env файл не найден!")
            self.results['issues'].append("Отсутствует .env файл")
            return
        
        print_success(".env файл найден")
        
        with open(env_file, 'r') as f:
            content = f.read()
        
        required_vars = ['SECRET_KEY', 'DB_NAME', 'DB_USER', 'DB_PASSWORD', 'DB_HOST', 'DB_PORT']
        optional_vars = ['REDIS_URL', 'DEBUG']
        
        for var in required_vars:
            if var in content:
                print_success(f"Переменная {var} установлена")
            else:
                print_error(f"Переменная {var} отсутствует")
                self.results['issues'].append(f"В .env отсутствует {var}")
        
        for var in optional_vars:
            if var in content:
                print_success(f"Переменная {var} установлена")
            else:
                print_warning(f"Переменная {var} отсутствует (необязательно)")
                self.results['warnings'].append(f"В .env отсутствует {var}")
    
    def check_frontend(self):
        """Проверяет наличие фронтенда"""
        print_header("ПРОВЕРКА ФРОНТЕНДА")
        
        # Проверяем наличие React приложения
        react_paths = [
            self.root_dir / 'frontend',
            self.root_dir / 'client',
            self.root_dir / 'react-app'
        ]
        
        found = False
        for path in react_paths:
            if path.exists() and (path / 'package.json').exists():
                print_success(f"Найдено React приложение: {path.name}")
                found = True
                # Проверяем основные файлы
                if (path / 'src' / 'App.js').exists():
                    print_success("  App.js найден")
                if (path / 'src' / 'index.js').exists():
                    print_success("  index.js найден")
                break
        
        if not found:
            print_warning("React приложение не найдено")
            print_info("Создать React приложение можно командой: npx create-react-app frontend")
    
    def check_migrations(self):
        """Проверяет состояние миграций"""
        print_header("ПРОВЕРКА МИГРАЦИЙ")
        
        migrations_dirs = list(self.root_dir.glob('*/migrations'))
        migrations_dirs = [d for d in migrations_dirs if 'venv' not in str(d) and d.name != '__pycache__']
        
        if migrations_dirs:
            print_success(f"Найдены папки миграций: {len(migrations_dirs)}")
            for dir_path in migrations_dirs:
                app_name = dir_path.parent.name
                mig_files = list(dir_path.glob('*.py'))
                mig_files = [f for f in mig_files if f.name != '__init__.py']
                if mig_files:
                    print_success(f"  {app_name}: {len(mig_files)} миграций")
                else:
                    print_warning(f"  {app_name}: миграции не созданы (запусти makemigrations)")
        else:
            print_warning("Папки миграций не найдены")
            print_info("Запусти: python manage.py makemigrations")
    
    def generate_report(self):
        """Генерирует итоговый отчет"""
        print_header("ИТОГОВЫЙ ОТЧЕТ")
        
        print(f"{Colors.BOLD}📊 Статистика:{Colors.END}")
        print(f"  - Найдено приложений: {len(self.results['apps'])}")
        print(f"  - Найдено моделей: {len(self.results['models'])}")
        print(f"  - Найдено issues: {len(self.results['issues'])}")
        print(f"  - Найдено warnings: {len(self.results['warnings'])}")
        
        if self.results['issues']:
            print(f"\n{Colors.RED}{Colors.BOLD}❌ КРИТИЧЕСКИЕ ПРОБЛЕМЫ:{Colors.END}")
            for issue in self.results['issues']:
                print(f"  {Colors.RED}•{Colors.END} {issue}")
        
        if self.results['warnings']:
            print(f"\n{Colors.YELLOW}{Colors.BOLD}⚠️  ПРЕДУПРЕЖДЕНИЯ:{Colors.END}")
            for warning in self.results['warnings']:
                print(f"  {Colors.YELLOW}•{Colors.END} {warning}")
        
        if not self.results['issues'] and not self.results['warnings']:
            print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 ВСЕ ОТЛИЧНО! Проект готов к работе!{Colors.END}")
        elif not self.results['issues']:
            print(f"\n{Colors.YELLOW}{Colors.BOLD}⚠️  Проект работает, но есть рекомендации по улучшению{Colors.END}")
        else:
            print(f"\n{Colors.RED}{Colors.BOLD}❌ Требуется исправить критические ошибки перед запуском{Colors.END}")
        
        # Сохраняем отчет в файл
        report_file = self.root_dir / 'project_report.txt'
        with open(report_file, 'w') as f:
            f.write("="*60 + "\n")
            f.write("ОТЧЕТ О ПРОВЕРКЕ ПРОЕКТА ProSocial\n")
            f.write(f"Дата: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("="*60 + "\n\n")
            
            f.write("СТРУКТУРА ПРОЕКТА:\n")
            for app in self.results['apps']:
                f.write(f"  - {app}\n")
            
            f.write(f"\nМОДЕЛИ ({len(self.results['models'])}):\n")
            for app, model in self.results['models']:
                f.write(f"  - {app}.{model}\n")
            
            if self.results['issues']:
                f.write(f"\nКРИТИЧЕСКИЕ ПРОБЛЕМЫ ({len(self.results['issues'])}):\n")
                for issue in self.results['issues']:
                    f.write(f"  - {issue}\n")
            
            if self.results['warnings']:
                f.write(f"\nПРЕДУПРЕЖДЕНИЯ ({len(self.results['warnings'])}):\n")
                for warning in self.results['warnings']:
                    f.write(f"  - {warning}\n")
        
        print(f"\n{Colors.GREEN}📄 Отчет сохранен в файл: project_report.txt{Colors.END}")
    
    def run(self):
        """Запускает все проверки"""
        print_header("🚀 ЗАПУСК ПРОВЕРКИ ПРОЕКТА ProSocial")
        print(f"📁 Корневая папка: {self.root_dir}")
        print(f"🕐 Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        self.check_root_files()
        self.check_env()
        self.check_settings()
        self.check_urls()
        self.check_apps()
        self.check_models()
        self.check_ws_files()
        self.check_migrations()
        self.check_frontend()
        self.generate_report()

def main():
    # Определяем корневую директорию
    root_dir = Path.cwd()
    
    # Проверяем, что мы в правильной папке
    if not (root_dir / 'manage.py').exists():
        print_error("Файл manage.py не найден! Убедитесь, что вы находитесь в корневой папке проекта.")
        sys.exit(1)
    
    checker = ProjectChecker(root_dir)
    checker.run()

if __name__ == '__main__':
    main()