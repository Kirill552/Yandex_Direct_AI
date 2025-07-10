# Yandex.Direct AI Campaign Manager

🚀 **Автоматизированный менеджер рекламных кампаний для Яндекс.Директ с использованием ИИ**

## 📋 Описание

Yandex.Direct AI Campaign Manager — это интеллектуальная система для автоматического создания, оптимизации и управления рекламными кампаниями в Яндекс.Директ. Система использует передовые AI-модели для анализа лендингов, создания семантического ядра, написания текстов объявлений и прогнозирования эффективности.

## ✨ Основные возможности

- 🔍 **Анализ лендингов** — автоматическое извлечение ключевых слов и УТП
- 🎯 **Семантическое ядро** — создание целевых ключевых фраз с приоритизацией
- 📝 **Генерация объявлений** — создание эффективных текстов с психологическими триггерами
- 📊 **Прогнозирование** — расчет ожидаемой эффективности кампаний
- 🔄 **Автоматизация** — полный цикл создания и управления кампаниями
- 🎨 **Интерактивный режим** — удобный интерфейс для настройки кампаний

## 🏗️ Архитектура

```
Yandex_Direct_AI/
├── advertising/                    # Основные модули рекламы
│   ├── professional_campaign_manager.py  # Профессиональный менеджер кампаний
│   ├── ai_campaign_manager.py            # AI-менеджер с reasoning моделью
│   └── __init__.py
├── ai_services/                    # AI-сервисы
│   └── __init__.py
├── api/                           # API интеграции
│   └── professional_campaign_api.py      # API для профессиональных кампаний
├── utils/                         # Утилиты
│   ├── config.py                  # Конфигурация
│   ├── logger.py                  # Логирование
│   └── __init__.py
├── logs/                          # Логи системы
├── advertising_campaigns_agent.py  # Главный агент кампаний
└── requirements.txt               # Зависимости
```

## 🚀 Установка и настройка

### 1. Клонирование репозитория

```bash
git clone https://github.com/Kirill552/Yandex_Direct_AI.git
cd Yandex_Direct_AI
```

### 2. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 3. Настройка переменных окружения

Создайте файл `.env` в корне проекта:

```env
# OpenAI API
OPENAI_API_KEY=your_openai_api_key_here

# Yandex.Direct API
YANDEX_DIRECT_TOKEN=your_yandex_direct_token_here
YANDEX_DIRECT_CLIENT_LOGIN=your_client_login_here

# Настройки логирования
LOG_LEVEL=INFO
```

### 4. Получение API ключей

#### OpenAI API Key:
1. Перейдите на [platform.openai.com](https://platform.openai.com)
2. Создайте аккаунт или войдите
3. Перейдите в раздел API Keys
4. Создайте новый ключ

#### Yandex.Direct API Token:
1. Перейдите на [oauth.yandex.ru](https://oauth.yandex.ru)
2. Создайте приложение для Яндекс.Директ API
3. Получите токен доступа

## 🎯 Использование

### Интерактивный режим

```python
import asyncio
from advertising.professional_campaign_manager import ProfessionalCampaignManager

async def main():
    manager = ProfessionalCampaignManager()
    
    # Создание кампании в интерактивном режиме
    campaign_plan = await manager.create_campaign_interactive()
    
    # Автоматическое создание кампании в Яндекс.Директ
    campaign_result = await manager.create_campaign_automatically(campaign_plan)
    
    # Запуск мониторинга и оптимизации
    await manager.monitor_and_optimize(campaign_result.campaign_id)

if __name__ == "__main__":
    asyncio.run(main())
```

### Программный режим

```python
from advertising.professional_campaign_manager import ProfessionalCampaignManager

manager = ProfessionalCampaignManager()

# Анализ лендинга
landing_analysis = manager.analyze_landing_page("https://example.com")

# Создание семантического ядра
semantic_core = manager.create_semantic_core(landing_analysis, "Описание бизнеса")

# Создание объявлений
ad_creatives = manager.create_ad_creatives(landing_analysis, semantic_core)
```

## 📊 Возможности системы

### 🔍 Анализ лендингов
- Извлечение заголовков и описаний
- Определение ключевых слов
- Выявление болевых точек аудитории
- Анализ уникальных торговых предложений

### 🎯 Семантическое ядро
- Приоритизация ключевых фраз
- Интеграция с Яндекс.Директ API для получения статистики
- Автоматическое создание минус-слов
- Группировка по тематикам

### 📝 Создание объявлений
- Генерация заголовков с психологическими триггерами
- Создание продающих текстов
- Оптимизация под требования Яндекс.Директ
- A/B тестирование вариантов

### 📈 Прогнозирование и оптимизация
- Расчет ожидаемой эффективности
- Распределение бюджета
- Мониторинг показателей
- Автоматическая оптимизация ставок

## 🤖 AI-модели

Система использует следующие AI-модели:

- **o4-mini (Reasoning)** — для сложного анализа и стратегического планирования
- **GPT-4** — для создания креативного контента
- **GPT-3.5-turbo** — для быстрых операций и оптимизации

## 📋 Требования

- Python 3.8+
- OpenAI API ключ
- Yandex.Direct API токен
- Интернет-соединение для API вызовов

## 🔧 Конфигурация

Система поддерживает гибкую конфигурацию через файл `utils/config.py`:

```python
# Настройки AI-моделей
OPENAI_MODEL_REASONING = "o4-mini"
OPENAI_MODEL_CREATIVE = "gpt-4"
OPENAI_MODEL_OPTIMIZATION = "gpt-3.5-turbo"

# Настройки кампаний
DEFAULT_DAILY_BUDGET = 1000
DEFAULT_CURRENCY = "RUB"
MAX_KEYWORDS_PER_GROUP = 20
```

## 🤝 Участие в разработке

Мы приветствуем вклад в развитие проекта! Пожалуйста:

1. Fork репозитория
2. Создайте feature branch
3. Внесите изменения
4. Создайте Pull Request

## 📄 Лицензия

MIT License - подробности в файле `LICENSE`

## 📞 Поддержка

Если у вас есть вопросы или предложения:

- 🐛 [Создать Issue](https://github.com/Kirill552/Yandex_Direct_AI/issues)
- 📧 Email: kirill552@example.com
- 💬 Telegram: @kirill552

## 🏆 Автор

Создано с ❤️ командой **Kirill552**

---

⭐ **Поставьте звездочку, если проект был полезен!** 