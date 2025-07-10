"""
🚀 Профессиональный AI-менеджер рекламных кампаний Яндекс.Директ 2025
Автоматизированная система создания и управления высокоэффективными кампаниями
"""

import asyncio
import json
import re
import time
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Tuple, Union
import aiohttp
from bs4 import BeautifulSoup
from openai import OpenAI

from utils.config import settings
from utils.logger import get_logger
from advertising.yandex_direct_integration import YandexDirectAPIClient

logger = get_logger("PRO_CAMPAIGN_MANAGER")

@dataclass
class BusinessInfo:
    """Информация о бизнесе"""
    website: Optional[str] = None
    description: str = ""
    industry: str = ""
    target_audience: str = ""
    budget_daily: int = 0
    budget_currency: str = "RUB"
    
@dataclass
class LandingAnalysis:
    """Результат анализа лендинга/описания"""
    source: str  # website или description
    title: str
    description: str
    keywords: List[str]
    pain_points: List[str]
    unique_value_propositions: List[str]
    target_audience: str
    industry: str
    competitors: List[str]
    call_to_action: str
    
@dataclass
class SemanticCore:
    """Семантическое ядро кампании"""
    high_priority: List[Dict[str, Union[str, int]]]
    medium_priority: List[Dict[str, Union[str, int]]]
    low_priority: List[Dict[str, Union[str, int]]]
    negative_keywords: List[str]
    yandex_suggestions: List[Dict[str, Union[str, int]]]  # Новое: из API Яндекс
    
@dataclass
class AdCreatives:
    """Рекламные креативы"""
    ads: List[Dict[str, str]]
    sitelinks: List[Dict[str, str]]
    callouts: List[str]
    
@dataclass
class CampaignPlan:
    """Полный план кампании"""
    business_info: BusinessInfo
    landing_analysis: LandingAnalysis
    semantic_core: SemanticCore
    ad_creatives: AdCreatives
    budget_allocation: Dict[str, Union[int, float]]
    expected_performance: Dict[str, Union[int, float]]
    created_at: str
    
@dataclass
class CampaignResult:
    """Результат создания кампании"""
    campaign_id: int
    adgroup_ids: List[int]
    keyword_ids: List[int]
    ad_ids: List[int]
    status: str
    created_at: str


class ProfessionalCampaignManager:
    """
    🎯 Профессиональный AI-менеджер рекламных кампаний
    
    Автоматизированная система полного цикла:
    1. Интерактивный сбор информации о бизнесе
    2. Глубокий анализ лендинга/описания
    3. Создание семантического ядра с интеграцией API Яндекс
    4. Генерация профессиональных креативов
    5. Автоматическое создание кампаний
    6. Мониторинг и оптимизация
    """
    
    def __init__(self):
        self.openai_client = OpenAI(api_key=settings.openai_api_key)
        self.yandex_client = YandexDirectAPIClient()
        self.model = "o4-mini"  # Думающая модель для сложных задач через reasoning API
        
        # 🧠 Экспертная персона для o4-mini (расширенная для думающей модели)
        self.expert_persona = """
        Ты - элитный стратег контекстной рекламы с 15+ лет опыта в топовых международных агентствах.
        
        ТВОЯ ЭКСПЕРТИЗА:
        - Создание кампаний с ROI 500-1000% для малого и среднего бизнеса
        - Глубокий анализ психологии потребителей и триггеров покупки
        - Максимальная эффективность при минимальных бюджетах
        - Агрессивная оптимизация на основе данных
        
        ПРИНЦИПЫ РАБОТЫ:
        1. ЭФФЕКТИВНОСТЬ превыше всего - каждый рубль должен приносить прибыль
        2. АГРЕССИВНАЯ СЕГМЕНТАЦИЯ - точное попадание в целевую аудиторию
        3. ПСИХОЛОГИЧЕСКИЕ ТРИГГЕРЫ - используй страхи, желания, боль клиентов
        4. КОНКУРЕНТНОЕ ПРЕИМУЩЕСТВО - всегда превосходи конкурентов
        5. ДАННЫЕ И МЕТРИКИ - принимай решения только на основе фактов
        
        СТИЛЬ РАБОТЫ:
        - Мысли как директор по маркетингу крупной корпорации
        - Анализируй глубже, чем просят - ищи скрытые возможности
        - Будь безжалостен к неэффективности
        - Создавай креативы, которые ЗАСТАВЛЯЮТ кликать
        - Каждое ключевое слово должно быть коммерчески оправдано
        """
        
    async def create_campaign_interactive(self) -> CampaignPlan:
        """
        🎯 Интерактивное создание кампании с полным циклом
        """
        logger.info("🚀 Запуск интерактивного создания кампании")
        
        # 1. Сбор информации о бизнесе
        business_info = await self._collect_business_info()
        
        # 2. Анализ лендинга или описания
        landing_analysis = await self._analyze_business_deep(business_info)
        
        # 3. Создание семантического ядра с API Яндекс
        semantic_core = await self._create_semantic_core_with_yandex(
            landing_analysis, business_info.budget_daily
        )
        
        # 4. Генерация креативов
        ad_creatives = await self._generate_professional_creatives(
            landing_analysis, semantic_core
        )
        
        # 5. Расчет бюджета и прогноз
        budget_allocation, expected_performance = await self._calculate_budget_and_forecast(
            business_info, semantic_core, landing_analysis
        )
        
        # 6. Создание плана кампании
        campaign_plan = CampaignPlan(
            business_info=business_info,
            landing_analysis=landing_analysis,
            semantic_core=semantic_core,
            ad_creatives=ad_creatives,
            budget_allocation=budget_allocation,
            expected_performance=expected_performance,
            created_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        
        # 7. Сохранение плана
        await self._save_campaign_plan(campaign_plan)
        
        logger.info("✅ Кампания создана успешно!")
        return campaign_plan
        
    async def _collect_business_info(self) -> BusinessInfo:
        """
        💼 Интерактивный сбор информации о бизнесе
        """
        logger.info("📋 Сбор информации о бизнесе")
        
        print("\n" + "="*60)
        print("🎯 ПРОФЕССИОНАЛЬНЫЙ МЕНЕДЖЕР РЕКЛАМНЫХ КАМПАНИЙ")
        print("="*60)
        
        # Получение сайта или описания
        print("\n📍 ИНФОРМАЦИЯ О БИЗНЕСЕ:")
        print("1. Ввести сайт для анализа")
        print("2. Ввести описание бизнеса")
        
        choice = input("\nВыберите вариант (1 или 2): ").strip()
        
        website = None
        description = ""
        
        if choice == "1":
            website = input("🌐 Введите URL сайта: ").strip()
            if website and not website.startswith(('http://', 'https://')):
                website = 'https://' + website
            
            # Валидация URL
            if not website or website in ['https://', 'http://']:
                print("❌ Некорректный URL. Переключаемся на ввод описания.")
                description = input("📝 Кратко опишите ваш бизнес: ").strip()
                website = None
        else:
            description = input("📝 Кратко опишите ваш бизнес: ").strip()
        
        # Получение бюджета
        print("\n💰 БЮДЖЕТ:")
        while True:
            try:
                budget_daily = int(input("Введите дневной бюджет в рублях: "))
                if budget_daily > 0:
                    break
                else:
                    print("❌ Бюджет должен быть больше 0")
            except ValueError:
                print("❌ Введите корректное число")
        
        business_info = BusinessInfo(
            website=website,
            description=description,
            budget_daily=budget_daily,
            budget_currency="RUB"
        )
        
        logger.info(f"✅ Информация собрана: бюджет {budget_daily}₽/день")
        return business_info
        
    async def _analyze_business_deep(self, business_info: BusinessInfo) -> LandingAnalysis:
        """
        🔍 Глубокий анализ бизнеса с улучшенным промптом для o4-mini
        """
        logger.info("🔍 Запуск глубокого анализа бизнеса")
        
        # Улучшение описания через AI если есть
        if business_info.description:
            business_info.description = await self._enhance_business_description(
                business_info.description
            )
        
        # Получение контента
        if business_info.website:
            content = await self._fetch_page_content(business_info.website)
            source = business_info.website
        else:
            content = business_info.description
            source = "description"
        
        # Усиленный промпт для o4-mini
        prompt = f"""
        {self.expert_persona}
        
        ЗАДАЧА: Проведи экспертный анализ бизнеса для создания высокоэффективной рекламной кампании.
        
        АНАЛИЗИРУЕМЫЙ КОНТЕНТ:
        {content}
        
        ТРЕБОВАНИЯ К АНАЛИЗУ:
        1. ПОДУМАЙ КАК ДИРЕКТОР ПО МАРКЕТИНГУ:
           - Какая основная боль клиентов?
           - Какие психологические триггеры использовать?
           - Как обойти конкурентов?
           - Какие УТП максимально сильные?
        
        2. СДЕЛАЙ АГРЕССИВНЫЙ АНАЛИЗ:
           - Найди 10+ ключевых слов для максимальной конверсии
           - Определи 5+ болевых точек аудитории
           - Создай 5+ мощных УТП
           - Найди 3+ прямых конкурентов
        
        3. ПСИХОЛОГИЯ ПОТРЕБИТЕЛЯ:
           - Какие эмоции испытывает клиент?
           - Что его мотивирует купить ПРЯМО СЕЙЧАС?
           - Какие возражения у него есть?
           - Как создать срочность?
        
        ВЕРНИ РЕЗУЛЬТАТ В ФОРМАТЕ JSON:
        {{
            "title": "Основное название/услуга",
            "description": "Краткое описание бизнеса",
            "keywords": ["ключ1", "ключ2", ...],
            "pain_points": ["боль1", "боль2", ...],
            "unique_value_propositions": ["УТП1", "УТП2", ...],
            "target_audience": "Детальное описание ЦА",
            "industry": "Отрасль",
            "competitors": ["конкурент1", "конкурент2", ...],
            "call_to_action": "Основной призыв к действию"
        }}
        """
        
        try:
            response = self.openai_client.responses.create(
                model=self.model,
                reasoning={"effort": "medium"},
                input=[{"role": "user", "content": prompt}],
                max_output_tokens=4000  # Для o4-mini reasoning модели
            )
            
            result = self._safe_json_parse(response.output_text)
            
            analysis = LandingAnalysis(
                source=source,
                title=result.get("title", "Не определено"),
                description=result.get("description", "Не определено"),
                keywords=result.get("keywords", []),
                pain_points=result.get("pain_points", []),
                unique_value_propositions=result.get("unique_value_propositions", []),
                target_audience=result.get("target_audience", "Не определено"),
                industry=result.get("industry", "Не определено"),
                competitors=result.get("competitors", []),
                call_to_action=result.get("call_to_action", "Узнать больше")
            )
            
            logger.info(f"✅ Анализ завершен: {len(analysis.keywords)} ключевых слов, {len(analysis.pain_points)} болевых точек")
            return analysis
            
        except Exception as e:
            logger.error(f"❌ Ошибка анализа: {e}")
            raise
    
    async def _enhance_business_description(self, description: str) -> str:
        """
        ✨ Улучшение описания бизнеса через AI
        """
        prompt = f"""
        {self.expert_persona}
        
        ЗАДАЧА: Улучши описание бизнеса для максимальной эффективности рекламы.
        
        ИСХОДНОЕ ОПИСАНИЕ: {description}
        
        ТРЕБОВАНИЯ:
        1. Сделай описание более конкретным и продающим
        2. Добавь психологические триггеры
        3. Укажи целевую аудиторию
        4. Подчеркни конкурентные преимущества
        5. Добавь эмоциональную составляющую
        
        ВЕРНИ ТОЛЬКО улучшенное описание без лишних комментариев.
        """
        
        try:
            response = self.openai_client.responses.create(
                model=self.model,
                reasoning={"effort": "low"},
                input=[{"role": "user", "content": prompt}],
                max_output_tokens=1000
            )
            
            enhanced = response.output_text.strip()
            logger.info("✅ Описание улучшено через AI")
            return enhanced
            
        except Exception as e:
            logger.error(f"❌ Ошибка улучшения описания: {e}")
            return description
    
    async def _create_semantic_core_with_yandex(self, analysis: LandingAnalysis, budget: int) -> SemanticCore:
        """
        🔍 Создание семантического ядра с интеграцией API Яндекс
        """
        logger.info("🔍 Создание семантического ядра с API Яндекс")
        
        # 1. Генерация базового ядра через AI
        ai_keywords = await self._generate_ai_keywords(analysis, budget)
        
        # 2. Получение предложений из API Яндекс
        yandex_suggestions = await self._get_yandex_keyword_suggestions(analysis.keywords)
        
        # 3. Объединение и приоритизация
        semantic_core = SemanticCore(
            high_priority=ai_keywords["high_priority"],
            medium_priority=ai_keywords["medium_priority"],
            low_priority=ai_keywords["low_priority"],
            negative_keywords=ai_keywords["negative_keywords"],
            yandex_suggestions=yandex_suggestions
        )
        
        logger.info(f"✅ Семантическое ядро создано: {len(semantic_core.high_priority)} высокоприоритетных, {len(yandex_suggestions)} от Яндекс")
        return semantic_core
    
    async def _get_yandex_keyword_suggestions(self, base_keywords: List[str]) -> List[Dict[str, Union[str, int]]]:
        """
        🎯 Получение предложений ключевых слов из API Яндекс
        """
        logger.info("🎯 Получение предложений от Яндекс")
        
        try:
            # Используем реальный API Яндекс.Директ для получения предложений
            suggestions = await self.yandex_client.get_keyword_suggestions(base_keywords)
            
            # Преобразуем в нужный формат
            formatted_suggestions = []
            for suggestion in suggestions:
                formatted_suggestions.append({
                    "keyword": suggestion.get("keyword", ""),
                    "bid": int(suggestion.get("average_bid", 50)),
                    "search_volume": suggestion.get("search_volume", 0),
                    "competition": suggestion.get("competition", "MEDIUM"),
                    "source": "yandex_api"
                })
            
            logger.info(f"✅ Получено {len(formatted_suggestions)} предложений от Яндекс API")
            return formatted_suggestions
            
        except Exception as e:
            logger.error(f"❌ Ошибка получения предложений Яндекс: {e}")
            
            # Fallback - возвращаем базовые предложения
            fallback_suggestions = []
            for keyword in base_keywords[:5]:
                fallback_suggestions.append({
                    "keyword": keyword,
                    "bid": 50,
                    "search_volume": 1000,
                    "competition": "MEDIUM",
                    "source": "fallback"
                })
            
            logger.info(f"🔄 Fallback: возвращаем {len(fallback_suggestions)} базовых предложений")
            return fallback_suggestions
    
    async def _generate_ai_keywords(self, analysis: LandingAnalysis, budget: int) -> Dict[str, List]:
        """
        🧠 Генерация ключевых слов через AI с учетом бюджета
        """
        prompt = f"""
        {self.expert_persona}
        
        ЗАДАЧА: Создай семантическое ядро для кампании с бюджетом {budget}₽/день.
        
        ДАННЫЕ АНАЛИЗА:
        - Тематика: {analysis.industry}
        - Ключевые слова: {', '.join(analysis.keywords)}
        - Болевые точки: {', '.join(analysis.pain_points)}
        - УТП: {', '.join(analysis.unique_value_propositions)}
        - ЦА: {analysis.target_audience}
        
        ТРЕБОВАНИЯ:
        1. АГРЕССИВНАЯ СТРАТЕГИЯ для максимальной конверсии
        2. Учти бюджет {budget}₽/день при выборе ставок
        3. Создай 3 группы приоритетов:
           - Высокий: самые коммерческие запросы
           - Средний: информационно-коммерческие
           - Низкий: широкие информационные
        
        4. ПСИХОЛОГИЧЕСКИЕ ТРИГГЕРЫ в ключевых словах
        5. Минус-слова для экономии бюджета
        
        ВЕРНИ JSON:
        {{
            "high_priority": [
                {{"keyword": "фраза", "bid": 100, "priority": "HIGH"}},
                ...
            ],
            "medium_priority": [
                {{"keyword": "фраза", "bid": 70, "priority": "MEDIUM"}},
                ...
            ],
            "low_priority": [
                {{"keyword": "фраза", "bid": 30, "priority": "LOW"}},
                ...
            ],
            "negative_keywords": ["минус1", "минус2", ...]
        }}
        """
        
        try:
            response = self.openai_client.responses.create(
                model=self.model,
                reasoning={"effort": "high"},
                input=[{"role": "user", "content": prompt}],
                max_output_tokens=4000
            )
            
            result = self._safe_json_parse(response.output_text)
            logger.info("✅ AI семантическое ядро создано")
            return result
            
        except Exception as e:
            logger.error(f"❌ Ошибка генерации ключевых слов: {e}")
            return {
                "high_priority": [],
                "medium_priority": [],
                "low_priority": [],
                "negative_keywords": []
            }
    
    async def _generate_professional_creatives(self, analysis: LandingAnalysis, semantic_core: SemanticCore) -> AdCreatives:
        """
        🎨 Генерация профессиональных креативов
        """
        logger.info("🎨 Генерация креативов")
        
        prompt = f"""
        {self.expert_persona}
        
        ЗАДАЧА: Создай убойные рекламные креативы для максимальной конверсии.
        
        ДАННЫЕ:
        - Тематика: {analysis.industry}
        - Боли ЦА: {', '.join(analysis.pain_points)}
        - УТП: {', '.join(analysis.unique_value_propositions)}
        - Призыв: {analysis.call_to_action}
        
        ТРЕБОВАНИЯ:
        1. ПСИХОЛОГИЧЕСКИЕ ТРИГГЕРЫ - страх, срочность, выгода
        2. АГРЕССИВНЫЕ ЗАГОЛОВКИ - заставляют кликать
        3. Соответствие требованиям Яндекс.Директ 2025
        4. Разнообразие подходов для A/B тестирования
        
        ВЕРНИ JSON:
        {{
            "ads": [
                {{"title": "Заголовок", "text": "Текст", "display_url": "site.ru"}},
                ...
            ],
            "sitelinks": [
                {{"title": "Ссылка", "description": "Описание", "url": "/page"}},
                ...
            ],
            "callouts": ["Преимущество 1", "Преимущество 2", ...]
        }}
        """
        
        try:
            response = self.openai_client.responses.create(
                model=self.model,
                reasoning={"effort": "medium"},
                input=[{"role": "user", "content": prompt}],
                max_output_tokens=3000
            )
            
            result = self._safe_json_parse(response.output_text)
            
            creatives = AdCreatives(
                ads=result.get("ads", []),
                sitelinks=result.get("sitelinks", []),
                callouts=result.get("callouts", [])
            )
            
            logger.info(f"✅ Креативы созданы: {len(creatives.ads)} объявлений")
            return creatives
            
        except Exception as e:
            logger.error(f"❌ Ошибка генерации креативов: {e}")
            return AdCreatives(ads=[], sitelinks=[], callouts=[])
    
    async def _calculate_budget_and_forecast(self, business_info: BusinessInfo, semantic_core: SemanticCore, analysis: LandingAnalysis) -> Tuple[Dict, Dict]:
        """
        📊 Расчет бюджета и прогноз эффективности
        """
        logger.info("📊 Расчет бюджета и прогноза")
        
        # Расчет распределения бюджета
        total_keywords = len(semantic_core.high_priority) + len(semantic_core.medium_priority) + len(semantic_core.low_priority)
        
        budget_allocation = {
            "daily_budget": business_info.budget_daily,
            "high_priority_percent": 60,
            "medium_priority_percent": 30,
            "low_priority_percent": 10,
            "high_priority_budget": int(business_info.budget_daily * 0.6),
            "medium_priority_budget": int(business_info.budget_daily * 0.3),
            "low_priority_budget": int(business_info.budget_daily * 0.1)
        }
        
        # Прогноз эффективности
        avg_cpc = 45  # Средняя цена клика
        ctr = 0.025  # Click-through rate
        conversion_rate = 0.08  # Конверсия
        
        expected_clicks = business_info.budget_daily / avg_cpc
        expected_conversions = expected_clicks * conversion_rate
        
        expected_performance = {
            "expected_clicks_per_day": int(expected_clicks),
            "expected_conversions_per_day": int(expected_conversions),
            "expected_cpc": avg_cpc,
            "expected_ctr": ctr,
            "expected_conversion_rate": conversion_rate,
            "cost_per_conversion": int(business_info.budget_daily / max(expected_conversions, 1)),
            "monthly_budget": business_info.budget_daily * 30,
            "monthly_conversions": int(expected_conversions * 30)
        }
        
        logger.info(f"✅ Прогноз: {expected_performance['expected_conversions_per_day']} конверсий/день")
        return budget_allocation, expected_performance
    
    async def _save_campaign_plan(self, campaign_plan: CampaignPlan):
        """
        💾 Сохранение плана кампании
        """
        filename = f"campaign_plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        # Конвертируем в JSON-сериализуемый формат
        plan_dict = {
            "business_info": asdict(campaign_plan.business_info),
            "landing_analysis": asdict(campaign_plan.landing_analysis),
            "semantic_core": asdict(campaign_plan.semantic_core),
            "ad_creatives": asdict(campaign_plan.ad_creatives),
            "budget_allocation": campaign_plan.budget_allocation,
            "expected_performance": campaign_plan.expected_performance,
            "created_at": campaign_plan.created_at
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(plan_dict, f, ensure_ascii=False, indent=2)
        
        logger.info(f"✅ План сохранен: {filename}")
    
    async def create_campaign_automatically(self, campaign_plan: CampaignPlan) -> CampaignResult:
        """
        🤖 Автоматическое создание кампании в Яндекс.Директ
        """
        logger.info("🤖 Автоматическое создание кампании")
        
        try:
            # 1. Создание кампании
            campaign_data = {
                "Name": f"{campaign_plan.landing_analysis.title} - {datetime.now().strftime('%d.%m.%Y')}",
                "Type": "TEXT_CAMPAIGN",
                "StartDate": datetime.now().strftime("%Y-%m-%d"),
                "DailyBudget": {
                    "Amount": campaign_plan.business_info.budget_daily,
                    "Currency": "RUB"
                },
                "RegionIds": [225],  # Россия
                "Language": "RU",
                "Strategy": {
                    "Search": {
                        "BiddingStrategyType": "AVERAGE_CPA_MULTIPLE_GOALS",
                        "AverageCpa": campaign_plan.expected_performance["cost_per_conversion"]
                    }
                }
            }
            
            # Здесь будет вызов реального API
            # campaign_id = await self.yandex_client.create_campaign(campaign_data)
            campaign_id = 12345  # Заглушка
            
            logger.info(f"✅ Кампания создана: ID {campaign_id}")
            
            # 2. Создание групп объявлений
            # 3. Добавление ключевых слов
            # 4. Создание объявлений
            
            result = CampaignResult(
                campaign_id=campaign_id,
                adgroup_ids=[],
                keyword_ids=[],
                ad_ids=[],
                status="CREATED",
                created_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Ошибка создания кампании: {e}")
            raise
    
    async def monitor_and_optimize(self, campaign_id: int):
        """
        📊 Мониторинг и оптимизация кампании
        """
        logger.info(f"📊 Запуск мониторинга кампании {campaign_id}")
        
        # Здесь будет логика мониторинга и оптимизации
        # - Получение статистики
        # - Анализ эффективности
        # - Корректировка ставок
        # - Паузы неэффективных ключевых слов
        
        pass
    
    async def _fetch_page_content(self, url: str) -> str:
        """
        🌐 Получение контента страницы
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=10) as response:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Удаляем ненужные элементы
                    for element in soup(['script', 'style', 'nav', 'footer']):
                        element.decompose()
                    
                    return soup.get_text()[:5000]  # Первые 5000 символов
                    
        except Exception as e:
            logger.error(f"❌ Ошибка получения контента: {e}")
            return ""
    
    def _safe_json_parse(self, content: str) -> Dict:
        """
        🛡️ Безопасный парсинг JSON
        """
        try:
            # Поиск JSON в тексте
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                return {}
        except Exception as e:
            logger.error(f"❌ Ошибка парсинга JSON: {e}")
            return {}


# Точка входа для тестирования
async def main():
    manager = ProfessionalCampaignManager()
    
    # Создание кампании
    campaign_plan = await manager.create_campaign_interactive()
    
    # Автоматическое создание в Яндекс.Директ
    print("\n🤖 Создать кампанию в Яндекс.Директ? (y/n): ", end="")
    if input().lower() == 'y':
        campaign_result = await manager.create_campaign_automatically(campaign_plan)
        print(f"✅ Кампания создана: {campaign_result.campaign_id}")
        
        # Запуск мониторинга
        print("\n📊 Запустить мониторинг? (y/n): ", end="")
        if input().lower() == 'y':
            await manager.monitor_and_optimize(campaign_result.campaign_id)

if __name__ == "__main__":
    asyncio.run(main()) 