from langchain.agents import AgentExecutor
from langchain_openai import ChatOpenAI


def create_agent(name, role_description, system_instructions, llm, tools=None):
    system_message = f"""{system_instructions}

    You are {name}, {role_description}. 
    Stay within your domain of expertise, provide structured responses, 
    and ensure clarity in decision-making. 
    Your responses should be insightful, concise, and aligned with business objectives."""

    return AgentExecutor.from_agent_and_tools(
        agent=llm, tools=tools or [], system_message=system_message, verbose=True
    )
