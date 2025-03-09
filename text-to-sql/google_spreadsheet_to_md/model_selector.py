from enum import Enum
from dataclasses import dataclass
import os
from typing import Optional, Any
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_core.language_models import BaseChatModel
from dotenv import load_dotenv
from pydantic import SecretStr

load_dotenv()

class OpenAIModels:
    GPT_3_5 = "gpt-3.5-turbo"
    GPT_4 = "gpt-4"
    GPT_4_TURBO = "gpt-4-turbo-preview"
    GPT_4O_MINI = "gpt-4o-mini"

class DeepseekModels:
    CHAT = "deepseek-chat"
    CODER = "deepseek-coder"

class AnthropicModels:
    CLAUDE_3 = "claude-3"
    CLAUDE_2 = "claude-2"
    CLAUDE_INSTANT = "claude-instant-1.2"

class ModelType(Enum):
    OPENAI = "openai"
    DEEPSEEK = "deepseek"
    ANTHROPIC = "anthropic"

@dataclass
class ModelConfig:
    model_name: str
    base_url: Optional[str] = None
    temperature: float = 0
    streaming: bool = False

DEFAULT_CONFIGS = {
    ModelType.OPENAI: ModelConfig(
        model_name=OpenAIModels.GPT_3_5
    ),
    ModelType.DEEPSEEK: ModelConfig(
        model_name=DeepseekModels.CHAT,
        base_url=os.getenv("DEEPSEEK_BASE_URL")
    ),
    ModelType.ANTHROPIC: ModelConfig(
        model_name=AnthropicModels.CLAUDE_3
    )
}

def _get_secret_key(key: Optional[str]) -> Optional[SecretStr]:
    """Convert environment variable to SecretStr if it exists."""
    return SecretStr(key) if key else None

def use_model(
    model_type: ModelType, 
    model_name: Optional[str] = None,
    temperature: Optional[float] = None,
    streaming: Optional[bool] = None
) -> BaseChatModel:
    """
    Factory function to create a chat model instance based on the provider.
    
    Args:
        model_type: The type of model to use (OPENAI, DEEPSEEK, etc.)
        model_name: Optional model name to override the default
        temperature: Optional temperature value to override the default
        streaming: Optional streaming flag to override the default
    
    Returns:
        A configured chat model instance
    
    Example:
        >>> from model_selector import ModelType, OpenAIModels, use_model
        >>> # Use default GPT-3.5
        >>> model = use_model(ModelType.OPENAI)
        >>> # Override with GPT-4
        >>> model = use_model(ModelType.OPENAI, model_name=OpenAIModels.GPT_4)
        >>> # Use GPT-4O-Mini
        >>> model = use_model(ModelType.OPENAI, model_name=OpenAIModels.GPT_4O_MINI)
    """
    config = DEFAULT_CONFIGS[model_type]
    
    if model_name is not None:
        config.model_name = model_name
    if temperature is not None:
        config.temperature = temperature
    if streaming is not None:
        config.streaming = streaming
    
    try:
        if model_type == ModelType.OPENAI:
            return ChatOpenAI(
                model=config.model_name,
                api_key=_get_secret_key(os.getenv("OPENAI_API_KEY")),
                temperature=config.temperature,
                streaming=config.streaming
            )
        
        elif model_type == ModelType.DEEPSEEK:
            return ChatOpenAI(
                model=config.model_name,
                api_key=_get_secret_key(os.getenv("DEEPSEEK_API_KEY")),
                base_url=config.base_url,
                temperature=config.temperature,
                streaming=config.streaming
            )
        
        elif model_type == ModelType.ANTHROPIC:
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                raise ValueError("ANTHROPIC_API_KEY environment variable is not set")
            
            return ChatAnthropic(
                model_name=config.model_name,
                api_key=SecretStr(api_key),
                temperature=config.temperature,
                streaming=config.streaming,
                timeout=60,
                stop=None
            )
        
    except Exception as e:
        raise RuntimeError(f"Failed to initialize {model_type.value} model: {str(e)}")
    
    raise ValueError(f"Unsupported model type: {model_type}")
