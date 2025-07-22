import os
from typing import Literal, Optional
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI as Chat
from langchain_groq import ChatGroq
from pydantic_settings import BaseSettings, SettingsConfigDict

# Define LLM choices
LLMChoice = Literal["openai", "anthropic", "pro", "flash", "lite", "image", "groq", "ollama"]

class APISettings(BaseSettings):
    """Holds all API keys, loaded from environment variables."""
    # model_config allows loading from a .env file
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    GOOGLE_API_KEY: Optional[str] = None 
    GROQ_API_KEY: Optional[str] = None
    OLLAMA_BASE_URL: Optional[str] = "http://localhost:11434"

# Instantiate once to load keys from the environment
API_KEYS = APISettings()

class LLMConfig(BaseSettings):
    """Defines the configuration for a specific LLM to be used in a run."""
    llm: LLMChoice = "pro"
    model_name: Optional[str] = None
    temperature: float = 0.65

def get_llm(config: LLMConfig) -> BaseChatModel:
    """
    Factory function to get an LLM instance based on the provided config.
    The supervisor agent will construct and pass the LLMConfig.
    """
    if config.llm == "openai":
        model_name = config.model_name or "gpt-4o"
        return ChatOpenAI(
            model=model_name,
            temperature=config.temperature,
            api_key=API_KEYS.OPENAI_API_KEY
        )
    elif config.llm == "anthropic":
        model_name = config.model_name or "claude-3-5-sonnet-latest"
        return ChatAnthropic(
            model=model_name,
            temperature=config.temperature,
            api_key=API_KEYS.ANTHROPIC_API_KEY
        )
    elif config.llm == "flash":
        model_name = "gemini-2.5-flash"
        return Chat(
            model_name=model_name,
            temperature=config.temperature,
            google_api_key=API_KEYS.GOOGLE_API_KEY
        )
    elif config.llm == "pro":
        model_name = "gemini-2.5-pro"
        return Chat(
            model_name=model_name,
            temperature=config.temperature,
            google_api_key=API_KEYS.GOOGLE_API_KEY
        )
    elif config.llm == "lite":
        model_name = "gemini-2.5-flash-lite-preview-06-17"
        return Chat(
            model_name=model_name,
            temperature=config.temperature,
            google_api_key=API_KEYS.GOOGLE_API_KEY
        )
    elif config.llm == "image":
        model_name = "gemini-2.0-flash-preview-image-generation"
        return Chat(
            model_name=model_name,
            temperature=config.temperature,
            google_api_key=API_KEYS.GOOGLE_API_KEY
        )
    elif config.llm == "groq":
        model_name = config.model_name or "qwen/qwen3-32b"
        return ChatGroq(
            model_name=model_name,
            temperature=config.temperature,
            api_key=API_KEYS.GROQ_API_KEY
        )
    elif config.llm == "ollama":
        if not config.model_name:
            raise ValueError("model_name must be specified for Ollama")
        return ChatOpenAI( # Ollama uses the OpenAI API spec
            model=config.model_name,
            temperature=config.temperature,
            base_url=API_KEYS.OLLAMA_BASE_URL,
            api_key="None"  # Ollama does not require an API key but OpenAI client requires it
        )
    else:
        raise ValueError(f"Unsupported LLM choice: {config.llm}")