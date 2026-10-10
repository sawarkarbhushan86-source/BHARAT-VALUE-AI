"""Bharat Value AI - Configuration Module."""
import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field

BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    app_name: str = Field(default="Bharat Value AI", env="APP_NAME")
    app_env: str = Field(default="development", env="APP_ENV")
    debug: bool = Field(default=True, env="DEBUG")
    port: int = Field(default=8000, env="PORT")
    host: str = Field(default="127.0.0.1", env="HOST")

    # Database
    database_url: str = Field(
        default=f"sqlite:///{BASE_DIR}/data/bharat_value_ai.db",
        env="DATABASE_URL"
    )

    # Market Data
    market_data_provider: str = Field(default="yfinance", env="MARKET_DATA_PROVIDER")
    default_exchange: str = Field(default="NSE", env="DEFAULT_EXCHANGE")
    cache_ttl_seconds: int = Field(default=300, env="CACHE_TTL_SECONDS")
    candle_cache_days: int = Field(default=30, env="CANDLE_CACHE_DAYS")

    # API Keys
    gemini_api_key: Optional[str] = Field(default=None, env="GEMINI_API_KEY")
    news_api_key: Optional[str] = Field(default=None, env="NEWS_API_KEY")
    alphavantage_api_key: Optional[str] = Field(default=None, env="ALPHAVANTAGE_API_KEY")

    # NLP & RAG
    nlp_model_type: str = Field(default="hybrid", env="NLP_MODEL_TYPE")
    vector_store_path: str = Field(
        default=str(BASE_DIR / "data" / "vector_store"),
        env="VECTOR_STORE_PATH"
    )
    embedding_dimension: int = Field(default=384, env="EMBEDDING_DIMENSION")

    # Risk Thresholds
    promoter_pledge_high_threshold: float = Field(default=25.0, env="PROMOTER_PLEDGE_HIGH_THRESHOLD")
    debt_to_equity_max_threshold: float = Field(default=2.0, env="DEBT_TO_EQUITY_MAX_THRESHOLD")
    interest_coverage_min_threshold: float = Field(default=2.5, env="INTEREST_COVERAGE_MIN_THRESHOLD")
    altman_z_distress_threshold: float = Field(default=1.8, env="ALTMAN_Z_DISTRESS_THRESHOLD")

    # Transaction Costs for Backtesting
    default_brokerage_pct: float = Field(default=0.0005, env="DEFAULT_BROKERAGE_PCT")
    default_stt_pct: float = Field(default=0.001, env="DEFAULT_STT_PCT")
    default_slippage_pct: float = Field(default=0.0005, env="DEFAULT_SLIPPAGE_PCT")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

settings = Settings()
