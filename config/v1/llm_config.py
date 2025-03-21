from typing import Optional

from config.v1 import BaseSettingsWrapper

from utils.v1.enums import OpenAIEnums


class LLMConfig(BaseSettingsWrapper):
    """
    Configuration class for the LLM model

    """

    OPENAI_API_KEY: Optional[str] = None
    MODEL_NAME: Optional[str] = OpenAIEnums.gpt_o3_mini.value


llm_config = LLMConfig()
