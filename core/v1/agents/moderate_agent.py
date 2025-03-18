from MBA_SIMULATION.utils.v1.agents.create_agent import create_agent
from MBA_SIMULATION.config.v1.llm_config import LLMConfig

moderator_agent = create_agent(
    name="Discussion Moderator",
    role_description="responsible for keeping discussions on topic, summarizing key points, and guiding the conversation forward",
    system_instructions="""You are the Discussion Moderator. Your responsibilities include:
1. Ensuring the conversation stays on topic.
2. Identifying pending questions and suggesting which agent should answer them.
3. Summarizing key points and decisions.
4. Guiding the conversation forward to ensure progress.""",
    llm=LLMConfig.MODEL_NAME,
)
