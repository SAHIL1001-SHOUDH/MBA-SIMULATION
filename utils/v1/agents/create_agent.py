from config.v1.llm_config import llm_config
from langchain.agents import initialize_agent
from langchain.agents import AgentType
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.prompts import HumanMessagePromptTemplate, SystemMessagePromptTemplate

open_ai_llm = ChatOpenAI(
    model=llm_config.MODEL_NAME,
    openai_api_key=llm_config.OPENAI_API_KEY,
)


def create_agent(name, role_description, system_instructions, tools=None):
    system_message = f"""You are {name}, {role_description}.
    {system_instructions}
    - Maintain conversation context
    - Acknowledge when you need to use tools
    - Always stay professional and objective"""

    prompt = ChatPromptTemplate.from_messages(
        [
            SystemMessagePromptTemplate.from_template(system_message),
            MessagesPlaceholder(variable_name="chat_history", optional=True),
            HumanMessagePromptTemplate.from_template("{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ]
    )

    return initialize_agent(
        tools=tools or [],
        llm=open_ai_llm,
        agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
        verbose=True,
        prompt=prompt,
        handle_parsing_errors=True,
        max_iterations=3,
    )
