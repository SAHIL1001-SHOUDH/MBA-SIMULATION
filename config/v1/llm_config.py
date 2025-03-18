from typing import Optional

from MBA_SIMULATION.config.v1 import BaseSettingsWrapper

from MBA_SIMULATION.utils.v1.enums import LLMEnums, OpenAIEnums


class LLMConfig(BaseSettingsWrapper):
    """
    Configuration class for the LLM model

    """

    OPENAI_API_KEY: Optional[str] = None
    MODEL_NAME: Optional[str] = OpenAIEnums.gpt_4.value


llm_config = LLMConfig()
