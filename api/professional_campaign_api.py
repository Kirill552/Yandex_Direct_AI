"""
🎯 API для профессионального менеджера рекламных кампаний
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, HttpUrl
from typing import Dict, List, Optional

from advertising.professional_campaign_manager import professional_campaign_manager
from utils.logger import get_logger

logger = get_logger("PROFESSIONAL_CAMPAIGN_API")

router = APIRouter()


class CampaignRequest(BaseModel):
    landing_url: HttpUrl
    business_description: str
    selected_tier: Optional[str] = "STANDARD"  # ECONOMY, STANDARD, PREMIUM


class LaunchRequest(BaseModel):
    campaign_plan: Dict


@router.post("/analyze-landing")
async def analyze_landing(landing_url: str):
    """Анализ лендинга для получения основной информации"""
    try:
        analysis = await professional_campaign_manager.analyze_landing_page(landing_url)
        
        return {
            "success": True,
            "analysis": {
                "url": analysis.url,
                "title": analysis.title,
                "main_offer": analysis.main_offer,
                "target_audience": analysis.target_audience,
                "pain_points": analysis.pain_points,
                "unique_value_propositions": analysis.unique_value_propositions,
                "keywords": analysis.keywords
            }
        }
    except Exception as e:
        logger.error(f"❌ Ошибка анализа лендинга: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Ошибка анализа лендинга: {str(e)}")


@router.post("/create-campaign-plan")
async def create_campaign_plan(request: CampaignRequest):
    """Создание профессионального плана кампании"""
    try:
        logger.info(f"🚀 Создание плана кампании для {request.landing_url}")
        
        campaign_plan = await professional_campaign_manager.create_professional_campaign_plan(
            landing_url=str(request.landing_url),
            business_description=request.business_description,
            selected_tier=request.selected_tier
        )
        
        if campaign_plan.get("success"):
            logger.info("✅ План кампании создан успешно")
            return campaign_plan
        else:
            raise HTTPException(status_code=400, detail=campaign_plan.get("error", "Ошибка создания плана"))
            
    except Exception as e:
        logger.error(f"❌ Ошибка создания плана кампании: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Ошибка создания плана: {str(e)}")


@router.post("/launch-campaign")
async def launch_campaign(request: LaunchRequest):
    """Запуск кампании в Яндекс.Директ"""
    try:
        logger.info("🚀 Запуск кампании в Яндекс.Директ")
        
        result = await professional_campaign_manager.launch_campaign(request.campaign_plan)
        
        if result.get("success"):
            logger.info(f"✅ Кампания запущена: ID {result.get('campaign_id')}")
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("error", "Ошибка запуска кампании"))
            
    except Exception as e:
        logger.error(f"❌ Ошибка запуска кампании: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Ошибка запуска: {str(e)}")


@router.get("/campaign-tiers-info")
async def get_campaign_tiers_info():
    """Получение информации о доступных уровнях кампаний"""
    return {
        "tiers": [
            {
                "name": "ECONOMY",
                "title": "Эконом",
                "description": "Базовый уровень для тестирования",
                "daily_budget": 1500,
                "features": [
                    "30 высокоприоритетных ключевых слов",
                    "3 группы объявлений",
                    "Широкое соответствие",
                    "~1 лид в день",
                    "ROI 2.5:1"
                ],
                "best_for": "Тестирование новых ниш, ограниченный бюджет"
            },
            {
                "name": "STANDARD", 
                "title": "Стандарт",
                "description": "Оптимальный баланс цена/качество",
                "daily_budget": 3500,
                "features": [
                    "80 ключевых слов",
                    "7 групп объявлений", 
                    "Фразовое и точное соответствие",
                    "~2 лида в день",
                    "ROI 3.5:1"
                ],
                "best_for": "Стабильный рост, проверенные ниши"
            },
            {
                "name": "PREMIUM",
                "title": "Премиум", 
                "description": "Максимальный охват и результат",
                "daily_budget": 7000,
                "features": [
                    "Все ключевые слова",
                    "12 групп объявлений",
                    "Точное соответствие + ретаргетинг",
                    "~5 лидов в день", 
                    "ROI 4.5:1"
                ],
                "best_for": "Масштабирование, высококонкурентные ниши"
            }
        ]
    }


@router.get("/health")
async def health_check():
    """Проверка работоспособности API"""
    return {
        "status": "healthy",
        "service": "Professional Campaign Manager",
        "version": "1.0.0"
    } 