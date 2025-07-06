from typing import List
from sqlalchemy.orm import Session
from app import SessionLocal
from app.models import PortfolioRecommendation
from sqlalchemy import text
import logging

logger = logging.getLogger(__name__)

class PortfolioOptimizerRepo:
    def __init__(self):
        self.db: Session = SessionLocal()

    def get_portfolio_recommendations(self, user_id: int) -> List[PortfolioRecommendation]:
        return self.db.query(PortfolioRecommendation).filter(PortfolioRecommendation.user_id == user_id).all()

    def save_portfolio_recommendation(self, recommendation: PortfolioRecommendation) -> None:
        self.db.add(recommendation)
        self.db.commit()
        self.db.refresh(recommendation)
    def get_all_symbols(self) -> List[str]:
        """
        Obtiene todos los símbolos únicos de criptomonedas en la base de datos.
        
        Args:

        Returns:
            List[str]: Lista de símbolos únicos.
        """
        try:
            querytext = "SELECT DISTINCT symbol FROM cryptocurrencies"
            symbols = self.db.execute(text(querytext)).scalars().all()
            return [symbol.upper() for symbol in symbols]
        except Exception as e:
            logger.error(f"Error obteniendo símbolos de la base de datos: {e}")
            return []
        
    def rollback(self):
        self.db.rollback()
    def close(self):
        self.db.close()