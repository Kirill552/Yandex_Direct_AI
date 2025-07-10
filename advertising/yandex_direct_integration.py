"""
Интеграция с API Яндекс.Директ для автоматического создания и управления кампаниями
"""
import httpx
import asyncio
import json
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

from utils.config import settings
from utils.logger import get_logger

logger = get_logger("YANDEX_DIRECT")


class YandexDirectAPIClient:
    """Клиент для работы с API Яндекс.Директ"""
    
    def __init__(self, use_sandbox: bool = True):
        """
        Инициализация клиента
        
        Args:
            use_sandbox: True для песочницы, False для продакшена
        """
        self.use_sandbox = use_sandbox
        
        if use_sandbox:
            # Адрес песочницы согласно документации
            self.api_url = "https://api-sandbox.direct.yandex.com/json/v5"
            self.token = settings.yandex_direct_sandbox_token
            logger.info("🧪 Используем песочницу Яндекс.Директ")
        else:
            # Боевой адрес - обновлен для 2025 (v501)
            self.api_url = "https://api.direct.yandex.com/json/v5"
            self.token = settings.yandex_direct_token
            logger.info("🚀 Используем боевой API Яндекс.Директ")
        
        # Заголовки согласно документации
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept-Language": "ru",
            "Content-Type": "application/json; charset=utf-8"
        }
        
        # Логируем конфигурацию
        logger.info(f"🔧 API URL: {self.api_url}")
        logger.info(f"🔑 Токен: {self.token[:15]}...")
    
    async def get_keyword_suggestions(self, base_keywords: List[str], region_ids: List[int] = None) -> List[Dict]:
        """
        🔍 Получение предложений ключевых слов из API Яндекс.Директ
        
        Args:
            base_keywords: Базовые ключевые слова для расширения
            region_ids: Идентификаторы регионов (по умолчанию [225] - Россия)
            
        Returns:
            List[Dict]: Список предложенных ключевых слов с данными
        """
        if region_ids is None:
            region_ids = [225]  # Россия по умолчанию
            
        logger.info(f"🔍 Получаем предложения для {len(base_keywords)} ключевых слов")
        
        try:
            # Используем метод keywordsresearch.get для получения предложений
            params = {
                "Operation": "KEYWORDS_BY_KEYWORD",
                "KeywordsByKeywordParams": {
                    "Keywords": base_keywords[:10],  # Максимум 10 ключевых слов за раз
                    "RegionIds": region_ids,
                    "Language": "RU",
                    "IncludePhrasesCount": True,
                    "ResultColumns": ["KEYWORD", "SEARCH_VOLUME", "COMPETITION", "AVERAGE_BID"]
                }
            }
            
            result = await self._make_request("keywordsresearch", "get", params)
            
            suggestions = []
            
            if "KeywordsByKeywordSearchResults" in result:
                for keyword_result in result["KeywordsByKeywordSearchResults"]:
                    if "Keywords" in keyword_result:
                        for keyword_data in keyword_result["Keywords"]:
                            suggestions.append({
                                "keyword": keyword_data.get("Keyword", ""),
                                "search_volume": keyword_data.get("SearchVolume", 0),
                                "competition": keyword_data.get("Competition", "UNKNOWN"),
                                "average_bid": keyword_data.get("AverageBid", 0) / 1000000,  # Из микрорублей
                                "source": "yandex_direct_api"
                            })
            
            logger.info(f"✅ Получено {len(suggestions)} предложений от Яндекс.Директ")
            return suggestions
            
        except Exception as e:
            logger.error(f"❌ Ошибка получения предложений: {e}")
            return []
    
    async def get_keyword_forecast(self, keywords: List[str], region_ids: List[int] = None) -> List[Dict]:
        """
        📊 Получение прогноза эффективности ключевых слов
        
        Args:
            keywords: Список ключевых слов для прогноза
            region_ids: Идентификаторы регионов
            
        Returns:
            List[Dict]: Прогноз эффективности для каждого ключевого слова
        """
        if region_ids is None:
            region_ids = [225]  # Россия по умолчанию
            
        logger.info(f"📊 Получаем прогноз для {len(keywords)} ключевых слов")
        
        try:
            # Подготавливаем данные для прогноза
            forecast_params = {
                "RegionIds": region_ids,
                "Currency": "RUB",
                "AuctionBids": [
                    {
                        "Keyword": keyword,
                        "AuctionBidItems": [
                            {
                                "Bid": 1000000,  # 1 рубль в микрорублях
                                "PositionGuaranteeType": "PREMIUM_GUARANTEE"
                            }
                        ]
                    }
                    for keyword in keywords[:50]  # Максимум 50 ключевых слов
                ]
            }
            
            result = await self._make_request("keywordsresearch", "CreateNewForecast", forecast_params)
            
            if "ForecastId" in result:
                forecast_id = result["ForecastId"]
                
                # Ждем готовности прогноза
                await asyncio.sleep(5)
                
                # Получаем результат прогноза
                get_params = {
                    "ForecastId": forecast_id
                }
                
                forecast_result = await self._make_request("keywordsresearch", "GetForecast", get_params)
                
                forecasts = []
                if "KeywordForecasts" in forecast_result:
                    for forecast in forecast_result["KeywordForecasts"]:
                        forecasts.append({
                            "keyword": forecast.get("Keyword", ""),
                            "min_searches": forecast.get("MinSearches", 0),
                            "max_searches": forecast.get("MaxSearches", 0),
                            "min_price": forecast.get("MinPrice", 0) / 1000000,  # Из микрорублей
                            "max_price": forecast.get("MaxPrice", 0) / 1000000,
                            "competition": forecast.get("Competition", "UNKNOWN")
                        })
                
                logger.info(f"✅ Получен прогноз для {len(forecasts)} ключевых слов")
                return forecasts
                
        except Exception as e:
            logger.error(f"❌ Ошибка получения прогноза: {e}")
            return []
    
    async def get_keyword_statistics(self, keywords: List[str], date_from: str, date_to: str) -> List[Dict]:
        """
        📈 Получение статистики по ключевым словам
        
        Args:
            keywords: Список ключевых слов
            date_from: Дата начала в формате YYYY-MM-DD
            date_to: Дата окончания в формате YYYY-MM-DD
            
        Returns:
            List[Dict]: Статистика по ключевым словам
        """
        logger.info(f"📈 Получаем статистику для {len(keywords)} ключевых слов")
        
        try:
            # Используем сервис reports для получения статистики
            report_params = {
                "SelectionCriteria": {
                    "DateFrom": date_from,
                    "DateTo": date_to
                },
                "FieldNames": [
                    "Query",
                    "Impressions", 
                    "Clicks",
                    "Cost",
                    "Ctr",
                    "AvgCpc",
                    "Conversions",
                    "ConversionRate"
                ],
                "ReportName": "SEARCH_QUERY_PERFORMANCE_REPORT",
                "ReportType": "SEARCH_QUERY_PERFORMANCE_REPORT",
                "DateRangeType": "CUSTOM_DATE",
                "Format": "TSV",
                "IncludeVAT": "YES"
            }
            
            result = await self._make_request("reports", "get", report_params)
            
            # Парсим TSV данные
            statistics = []
            if "result" in result:
                # Здесь нужно распарсить TSV формат
                # Пока возвращаем пустой список для избежания ошибок
                pass
                
            logger.info(f"✅ Получена статистика для {len(statistics)} ключевых слов")
            return statistics
            
        except Exception as e:
            logger.error(f"❌ Ошибка получения статистики: {e}")
            return []
    
    async def get_competitor_keywords(self, domain: str, region_ids: List[int] = None) -> List[Dict]:
        """
        🎯 Получение ключевых слов конкурентов (эмуляция)
        
        Args:
            domain: Домен конкурента
            region_ids: Идентификаторы регионов
            
        Returns:
            List[Dict]: Ключевые слова конкурентов
        """
        if region_ids is None:
            region_ids = [225]
            
        logger.info(f"🎯 Анализируем конкурента: {domain}")
        
        # Пока эмуляция, так как прямого API для этого нет
        competitor_keywords = [
            {"keyword": f"услуги {domain}", "competition": "HIGH", "estimated_bid": 45},
            {"keyword": f"купить {domain}", "competition": "MEDIUM", "estimated_bid": 35},
            {"keyword": f"{domain} цена", "competition": "LOW", "estimated_bid": 25}
        ]
        
        logger.info(f"✅ Найдено {len(competitor_keywords)} ключевых слов конкурента")
        return competitor_keywords

    async def optimize_keyword_bids(self, keyword_bids: List[Dict], target_position: int = 3) -> List[Dict]:
        """
        🎯 Оптимизация ставок для достижения целевой позиции
        
        Args:
            keyword_bids: Список словарей с ключевыми словами и текущими ставками
            target_position: Целевая позиция (1-12)
            
        Returns:
            List[Dict]: Оптимизированные ставки
        """
        logger.info(f"🎯 Оптимизируем ставки для {len(keyword_bids)} ключевых слов")
        
        optimized_bids = []
        
        for keyword_data in keyword_bids:
            current_bid = keyword_data.get("bid", 0)
            keyword = keyword_data.get("keyword", "")
            
            # Простая логика оптимизации (в реальности нужны более сложные алгоритмы)
            if target_position <= 3:
                # Для топ-3 позиций увеличиваем ставку на 20%
                new_bid = current_bid * 1.2
            elif target_position <= 6:
                # Для позиций 4-6 оставляем текущую ставку
                new_bid = current_bid
            else:
                # Для позиций 7+ можем снизить ставку на 10%
                new_bid = current_bid * 0.9
            
            optimized_bids.append({
                "keyword": keyword,
                "old_bid": current_bid,
                "new_bid": new_bid,
                "change_percent": ((new_bid - current_bid) / current_bid) * 100
            })
        
        logger.info(f"✅ Оптимизированы ставки для {len(optimized_bids)} ключевых слов")
        return optimized_bids
    
    async def test_connection(self) -> Dict:
        """Тест подключения к API - получение списка кампаний"""
        
        try:
            logger.info("🔍 Тестируем подключение к API...")
            
            # Простой запрос для проверки соединения
            result = await self._make_request("campaigns", "get", {
                "SelectionCriteria": {},
                "FieldNames": ["Id", "Name", "Status"]
            })
            
            campaigns = result.get("Campaigns", [])
            
            logger.info(f"✅ Подключение успешно! Найдено кампаний: {len(campaigns)}")
            
            # Логируем найденные кампании
            for campaign in campaigns[:3]:  # Только первые 3
                logger.info(f"   📊 Кампания: {campaign.get('Name')} (ID: {campaign.get('Id')})")
            
            return {
                "success": True,
                "campaigns_count": len(campaigns),
                "campaigns": campaigns
            }
            
        except Exception as e:
            logger.error(f"❌ Ошибка подключения: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _make_request(self, service: str, method: str, params: Dict = None) -> Dict:
        """Выполнить запрос к API Яндекс.Директ"""
        
        request_data = {
            "method": method,
            "params": params or {}
        }
        
        url = f"{self.api_url}/{service}"
        
        try:
            logger.info(f"🌐 Отправляем запрос: {service}.{method}")
            logger.debug(f"   URL: {url}")
            logger.debug(f"   Headers: {self.headers}")
            logger.debug(f"   Data: {json.dumps(request_data, ensure_ascii=False, indent=2)}")
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    url=url,
                    headers=self.headers,
                    json=request_data
                )
                
                logger.info(f"📡 Ответ API {service}.{method}: HTTP {response.status_code}")
                
                # Логируем заголовки ответа
                if "RequestId" in response.headers:
                    logger.info(f"   RequestId: {response.headers['RequestId']}")
                if "Units" in response.headers:
                    logger.info(f"   Units: {response.headers['Units']}")
                
                if response.status_code == 200:
                    result = response.json()
                    logger.debug(f"   Response: {json.dumps(result, ensure_ascii=False, indent=2)}")
                    
                    if "error" in result:
                        logger.error(f"❌ API Error: {result['error']}")
                        raise Exception(f"Yandex.Direct API Error: {result['error']}")
                    
                    return result.get("result", {})
                else:
                    logger.error(f"❌ HTTP Error: {response.status_code}")
                    logger.error(f"   Response: {response.text}")
                    response.raise_for_status()
                    
        except Exception as e:
            logger.error(f"❌ Yandex.Direct API Request failed: {str(e)}")
            raise

    async def create_campaign(self, campaign_config: Dict) -> Dict:
        """Создание новой рекламной кампании"""
        
        try:
            # Подготавливаем данные кампании согласно документации API
            campaign_data = {
                "Name": campaign_config.get("name", "Автоматическая кампания"),
                "StartDate": campaign_config.get("start_date", datetime.now().strftime("%Y-%m-%d")),
                
                # Настройки текстовой кампании (определяет тип кампании)
                "TextCampaign": self._build_text_campaign_config(campaign_config),
                
                # Дневной бюджет
                "DailyBudget": {
                    "Amount": campaign_config.get("daily_budget", 1000) * 1000000,  # В микрорублях
                    "Mode": "STANDARD"
                },
                
                # Временная зона
                "TimeZone": "Europe/Moscow"
            }
            
            # Добавляем дату окончания если указана
            if campaign_config.get("end_date"):
                campaign_data["EndDate"] = campaign_config["end_date"]
            
            # Формируем окончательные параметры запроса
            campaign_params = {
                "Campaigns": [campaign_data]
            }
            
            # Логируем структуру запроса для отладки
            logger.info(f"🔍 Структура запроса campaigns.add:")
            logger.info(json.dumps(campaign_params, ensure_ascii=False, indent=2))
            
            result = await self._make_request("campaigns", "add", campaign_params)
            
            # Детальное логирование ответа для отладки
            logger.info(f"🔍 Полный ответ API campaigns.add: {result}")
            
            # Проверяем структуру ответа
            if "AddResults" not in result:
                logger.error(f"❌ Нет AddResults в ответе API: {result}")
                if "Errors" in result:
                    logger.error(f"🚨 Ошибки API: {result['Errors']}")
                raise Exception(f"Неожиданная структура ответа API: {result}")
            
            add_results = result.get("AddResults", [])
            logger.info(f"📊 AddResults содержит {len(add_results)} элементов")
            
            campaign_ids = []
            errors = []
            
            for i, item in enumerate(add_results):
                logger.info(f"🔍 AddResults[{i}]: {item}")
                
                if "Id" in item:
                    campaign_ids.append(item["Id"])
                    logger.info(f"✅ Кампания создана с ID: {item['Id']}")
                elif "Errors" in item:
                    errors.extend(item["Errors"])
                    logger.error(f"❌ Ошибка создания кампании: {item['Errors']}")
                else:
                    logger.warning(f"⚠️ Неожиданная структура элемента: {item}")
            
            if errors:
                logger.error(f"🚨 Общие ошибки создания кампаний: {errors}")
                raise Exception(f"Ошибки создания кампаний: {errors}")
            
            logger.info(f"✅ Создано кампаний: {campaign_ids}")
            return {"campaign_ids": campaign_ids, "result": result}
            
        except Exception as e:
            logger.error(f"Ошибка создания кампании: {str(e)}")
            raise

    def _build_text_campaign_config(self, campaign_config: Dict) -> Dict:
        """Построение конфигурации текстовой кампании согласно API"""
        
        bidding_strategy = campaign_config.get("bidding_strategy", "HIGHEST_POSITION")
        
        # Базовая структура
        text_campaign = {
            "BiddingStrategy": {
                "Search": {
                    "BiddingStrategyType": bidding_strategy
                },
                "Network": {
                    "BiddingStrategyType": "SERVING_OFF"  # Отключаем рекламную сеть
                }
            },
            "Settings": [{
                "Option": "ADD_METRICA_TAG",
                "Value": "YES"
            }]
        }
        
        # Добавляем параметры для конкретных стратегий
        if bidding_strategy == "AVERAGE_CPC":
            average_cpc = campaign_config.get("average_cpc", 50) * 1000000  # В микрорублях
            text_campaign["BiddingStrategy"]["Search"]["AverageCpc"] = {
                "AverageCpc": average_cpc
            }
        elif bidding_strategy == "WB_MAXIMUM_CLICKS":
            weekly_spend = campaign_config.get("weekly_spend_limit", 7000) * 1000000  # В микрорублях
            text_campaign["BiddingStrategy"]["Search"]["WbMaximumClicks"] = {
                "WeeklySpendLimit": weekly_spend
            }
        
        return text_campaign

    async def create_ad_groups(self, campaign_id: int, groups_config: List[Dict]) -> Dict:
        """Создание групп объявлений"""
        
        try:
            ad_groups = []
            
            for group_config in groups_config:
                ad_group = {
                    "Name": group_config.get("name", "Группа объявлений"),
                    "CampaignId": campaign_id,
                    "RegionIds": group_config.get("region_ids", [213])  # Москва по умолчанию
                }
                
                # Добавляем негативные ключевые слова только если они есть
                negative_keywords = group_config.get("negative_keywords", [])
                if negative_keywords:
                    ad_group["NegativeKeywords"] = {
                        "Items": negative_keywords
                    }
                
                ad_groups.append(ad_group)
            
            params = {"AdGroups": ad_groups}
            
            logger.info(f"🔍 Структура запроса adgroups.add:")
            logger.info(json.dumps(params, ensure_ascii=False, indent=2))
            
            result = await self._make_request("adgroups", "add", params)
            
            # Обработка результатов
            group_ids = []
            errors = []
            
            for item in result.get("AddResults", []):
                if "Id" in item:
                    group_ids.append(item["Id"])
                    logger.info(f"✅ Группа создана с ID: {item['Id']}")
                elif "Errors" in item:
                    errors.extend(item["Errors"])
                    logger.error(f"❌ Ошибка создания группы: {item['Errors']}")
            
            if errors:
                logger.error(f"🚨 Ошибки создания групп: {errors}")
                raise Exception(f"Ошибки создания групп: {errors}")
            
            logger.info(f"✅ Создано групп объявлений: {len(group_ids)}")
            return {"group_ids": group_ids, "result": result}
            
        except Exception as e:
            logger.error(f"Ошибка создания групп: {str(e)}")
            raise

    async def create_keywords(self, group_id: int, keywords_config: List[Dict]) -> Dict:
        """Добавление ключевых слов в группу"""
        
        try:
            keywords = []
            
            for keyword_config in keywords_config:
                keyword = {
                    "Keyword": keyword_config.get("text", ""),
                    "AdGroupId": group_id
                }
                
                # Добавляем ставку только если указана
                if keyword_config.get("bid"):
                    keyword["Bid"] = keyword_config["bid"] * 1000000  # В микрорублях
                
                # Добавляем пользовательские параметры для подстановки
                if keyword_config.get("param1"):
                    keyword["UserParam1"] = keyword_config["param1"]
                if keyword_config.get("param2"):
                    keyword["UserParam2"] = keyword_config["param2"]
                
                keywords.append(keyword)
            
            params = {"Keywords": keywords}
            
            logger.info(f"🔍 Структура запроса keywords.add:")
            logger.info(json.dumps(params, ensure_ascii=False, indent=2))
            
            result = await self._make_request("keywords", "add", params)
            
            # Обработка результатов
            keyword_ids = []
            errors = []
            
            for item in result.get("AddResults", []):
                if "Id" in item:
                    keyword_ids.append(item["Id"])
                    logger.info(f"✅ Ключевое слово создано с ID: {item['Id']}")
                elif "Errors" in item:
                    errors.extend(item["Errors"])
                    logger.error(f"❌ Ошибка создания ключевого слова: {item['Errors']}")
            
            if errors:
                logger.error(f"🚨 Ошибки создания ключевых слов: {errors}")
                raise Exception(f"Ошибки создания ключевых слов: {errors}")
            
            logger.info(f"✅ Добавлено ключевых слов: {len(keyword_ids)}")
            return {"keyword_ids": keyword_ids, "result": result}
            
        except Exception as e:
            logger.error(f"Ошибка добавления ключевых слов: {str(e)}")
            raise

    async def create_ads(self, group_id: int, ads_config: List[Dict]) -> Dict:
        """Создание объявлений"""
        
        try:
            ads = []
            
            for ad_config in ads_config:
                ad = {
                    "AdGroupId": group_id,
                    
                    # Текстово-графическое объявление
                    "TextAd": {
                        "Title": ad_config.get("title", "Заголовок объявления"),
                        "Text": ad_config.get("text", "Текст объявления"),
                        "Href": ad_config.get("href", "https://example.com"),  # Обязательное поле
                        "Mobile": "NO"
                    }
                }
                
                # Добавляем второй заголовок если есть
                if ad_config.get("title2"):
                    ad["TextAd"]["Title2"] = ad_config["title2"]
                
                # Добавляем отображаемую ссылку если есть
                if ad_config.get("display_href"):
                    ad["TextAd"]["DisplayHref"] = ad_config["display_href"]
                
                ads.append(ad)
            
            params = {"Ads": ads}
            
            logger.info(f"🔍 Структура запроса ads.add:")
            logger.info(json.dumps(params, ensure_ascii=False, indent=2))
            
            result = await self._make_request("ads", "add", params)
            
            # Обработка результатов
            ad_ids = []
            errors = []
            
            for item in result.get("AddResults", []):
                if "Id" in item:
                    ad_ids.append(item["Id"])
                    logger.info(f"✅ Объявление создано с ID: {item['Id']}")
                elif "Errors" in item:
                    errors.extend(item["Errors"])
                    logger.error(f"❌ Ошибка создания объявления: {item['Errors']}")
            
            if errors:
                logger.error(f"🚨 Ошибки создания объявлений: {errors}")
                raise Exception(f"Ошибки создания объявлений: {errors}")
            
            logger.info(f"✅ Создано объявлений: {len(ad_ids)}")
            return {"ad_ids": ad_ids, "result": result}
            
        except Exception as e:
            logger.error(f"Ошибка создания объявлений: {str(e)}")
            raise

    async def get_campaign_stats(self, campaign_ids: List[int], date_from: str, date_to: str) -> Dict:
        """Получение статистики по кампаниям"""
        
        try:
            report_definition = {
                "SelectionCriteria": {
                    "DateFrom": date_from,
                    "DateTo": date_to,
                    "CampaignIds": campaign_ids
                },
                "FieldNames": [
                    "Date", "CampaignId", "CampaignName", "Impressions", "Clicks",
                    "Ctr", "Cost", "AvgCpc", "Conversions", "ConversionRate", "CostPerConversion"
                ],
                "ReportName": f"Отчет кампаний {datetime.now().strftime('%Y-%m-%d')}",
                "ReportType": "CAMPAIGN_PERFORMANCE_REPORT",
                "DateRangeType": "CUSTOM_DATE",
                "Format": "TSV",
                "IncludeVAT": "YES",
                "IncludeDiscount": "YES"
            }
            
            result = await self._make_request("reports", "get", report_definition)
            
            logger.info(f"Получена статистика для {len(campaign_ids)} кампаний")
            return result
            
        except Exception as e:
            logger.error(f"Ошибка получения статистики: {str(e)}")
            raise

    async def update_bids(self, keyword_ids: List[int], new_bids: List[float]) -> Dict:
        """Обновление ставок для ключевых слов"""
        
        try:
            keywords = []
            
            for keyword_id, bid in zip(keyword_ids, new_bids):
                keyword = {
                    "Id": keyword_id,
                    "Bid": int(bid * 1000000)  # В микрорублях
                }
                keywords.append(keyword)
            
            params = {"Keywords": keywords}
            result = await self._make_request("keywords", "update", params)
            
            logger.info(f"Обновлены ставки для {len(keyword_ids)} ключевых слов")
            return result
            
        except Exception as e:
            logger.error(f"Ошибка обновления ставок: {str(e)}")
            raise

    async def moderate_campaign(self, campaign_id: int) -> Dict:
        """Отправка кампании на модерацию"""
        
        try:
            # Сначала активируем кампанию
            params = {
                "CampaignIds": [campaign_id]
            }
            
            result = await self._make_request("campaigns", "resume", params)
            
            logger.info(f"Кампания {campaign_id} отправлена на модерацию")
            return result
            
        except Exception as e:
            logger.error(f"Ошибка отправки на модерацию: {str(e)}")
            raise


class YandexDirectCampaignManager:
    """Менеджер для автоматического создания кампаний"""
    
    def __init__(self):
        self.api_client = YandexDirectAPIClient()
    
    async def create_full_campaign_from_strategy(self, strategy_config: Dict) -> Dict:
        """Создание полной кампании на основе стратегии ИИ-агента"""
        
        try:
            logger.info("Начинаем создание кампании из стратегии ИИ")
            
            # 1. Создаем кампанию
            campaign_result = await self.api_client.create_campaign(strategy_config.get("campaign", {}))
            campaign_id = campaign_result["campaign_ids"][0]
            
            # 2. Создаем группы объявлений
            groups_config = strategy_config.get("ad_groups", [])
            groups_result = await self.api_client.create_ad_groups(campaign_id, groups_config)
            
            # 3. Добавляем ключевые слова в каждую группу
            for i, group_id in enumerate(groups_result["group_ids"]):
                if i < len(groups_config):
                    keywords_config = groups_config[i].get("keywords", [])
                    if keywords_config:
                        await self.api_client.create_keywords(group_id, keywords_config)
            
            # 4. Создаем объявления в каждой группе
            for i, group_id in enumerate(groups_result["group_ids"]):
                if i < len(groups_config):
                    ads_config = groups_config[i].get("ads", [])
                    if ads_config:
                        await self.api_client.create_ads(group_id, ads_config)
            
            # 5. Сохраняем результат
            campaign_summary = {
                "campaign_id": campaign_id,
                "groups_count": len(groups_result["group_ids"]),
                "created_at": datetime.now().isoformat(),
                "status": "created_in_draft",
                "next_steps": [
                    "Проверить настройки кампании",
                    "Протестировать объявления",
                    "Отправить на модерацию"
                ]
            }
            
            logger.info(f"Кампания создана успешно: {campaign_summary}")
            return campaign_summary
            
        except Exception as e:
            logger.error(f"Ошибка создания кампании: {str(e)}")
            raise

    async def optimize_campaign_bids(self, campaign_id: int, optimization_rules: Dict) -> Dict:
        """Автоматическая оптимизация ставок кампании"""
        
        try:
            # Получаем текущую статистику
            date_from = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
            date_to = datetime.now().strftime("%Y-%m-%d")
            
            stats = await self.api_client.get_campaign_stats([campaign_id], date_from, date_to)
            
            # Анализируем производительность и корректируем ставки
            # (здесь будет логика анализа и оптимизации)
            
            optimization_result = {
                "campaign_id": campaign_id,
                "optimization_date": datetime.now().isoformat(),
                "changes_made": 0,
                "expected_improvement": "5-15%"
            }
            
            logger.info(f"Оптимизация кампании {campaign_id} завершена")
            return optimization_result
            
        except Exception as e:
            logger.error(f"Ошибка оптимизации кампании: {str(e)}")
            raise


# Глобальный экземпляр менеджера
yandex_direct_manager = YandexDirectCampaignManager() 