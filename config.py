"""
Configuration management for Autonomous Trading Evolution Platform.
Uses environment variables with Firebase integration as primary state store.
"""
import os
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
from dotenv import load_dotenv

load_dotenv()

class TradingMode(Enum):
    """Trading operation modes"""
    BACKTEST = "backtest"
    PAPER = "paper"
    LIVE = "live"
    EVOLUTION = "evolution"

class RiskProfile(Enum):
    """Risk management profiles"""
    CONSERVATIVE = "conservative"
    MODERATE = "moderate"
    AGGRESSIVE = "aggressive"

@dataclass
class ExchangeConfig:
    """Exchange-specific configuration"""
    name: str
    api_key: Optional[str] = None
    secret: Optional[str] = None
    sandbox: bool = True
    rate_limit: int = 1000
    timeout: int = 30000

@dataclass
class FirebaseConfig:
    """Firebase configuration"""
    project_id: str
    credentials_path: str
    database_url: Optional[str] = None
    enable_realtime: bool = True

@dataclass
class EvolutionConfig:
    """Evolutionary algorithm configuration"""
    population_size: int = 50
    generations: int = 100
    mutation_rate: float = 0.1
    crossover_rate: float = 0.7
    elite_size: int = 5
    fitness_window: int = 30  # days

class Config:
    """Central configuration management"""
    
    def __init__(self):
        self.mode = TradingMode(os.getenv("TRADING_MODE", "paper"))
        self.risk_profile = RiskProfile(os.getenv("RISK_PROFILE", "moderate"))
        
        # Exchange configuration
        self.exchange = ExchangeConfig(
            name=os.getenv("EXCHANGE", "binance"),
            api_key=os.getenv("EXCHANGE_API_KEY"),
            secret=os.getenv("EXCHANGE_API_SECRET"),
            sandbox=os.getenv("EXCHANGE_SANDBOX", "true").lower() == "true"
        )
        
        # Firebase configuration
        self.firebase = FirebaseConfig(
            project_id=os.getenv("FIREBASE_PROJECT_ID", ""),
            credentials_path=os.getenv("FIREBASE_CREDENTIALS_PATH", "firebase-credentials.json"),
            database_url=os.getenv("FIREBASE_DATABASE_URL")
        )
        
        # Evolution configuration
        self.evolution = EvolutionConfig(
            population_size=int(os.getenv("EVOLUTION_POPULATION_SIZE", "50")),
            generations=int(os.getenv("EVOLUTION_GENERATIONS", "100")),
            mutation_rate=float(os.getenv("EVOLUTION_MUTATION_RATE", "0.1"))
        )
        
        # Risk limits
        self.max_position_size = float(os.getenv("MAX_POSITION_SIZE", "0.1"))  # 10% of portfolio
        self.max_daily_loss = float(os.getenv("MAX_DAILY_LOSS", "0.02"))  # 2% max daily loss
        self.stop_loss_pct = float(os.getenv("STOP_LOSS_PCT", "0.05"))  # 5% stop loss
        
        # Logging
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        
        # Validate critical configurations
        self._validate()
    
    def _validate(self):
        """Validate configuration and raise informative errors"""
        if self.mode == TradingMode.LIVE:
            if not self.exchange.api_key or not self.exchange.secret:
                raise ValueError("Live trading requires exchange API credentials")
        
        if not self.firebase.project_id:
            logging.warning("Firebase project ID not set - limited functionality available")
        
        # Validate risk parameters
        if self.max_position_size > 0.5:
            logging.warning("Maximum position size exceeds 50% of portfolio - high risk")
        
        if self.max_daily_loss > 0.1:
            logging.warning("Maximum daily loss exceeds 10% - extremely high risk")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary for serialization"""
        return {
            "mode": self.mode.value,
            "risk_profile": self.risk_profile.value,
            "exchange": {
                "name": self.exchange.name,
                "sandbox": self.exchange.sandbox
            },
            "risk_limits": {
                "max_position_size": self.max_position_size,
                "max_daily_loss": self.max_daily_loss,
                "stop_loss_pct": self.stop_loss_pct
            }
        }

# Global configuration instance
config = Config()