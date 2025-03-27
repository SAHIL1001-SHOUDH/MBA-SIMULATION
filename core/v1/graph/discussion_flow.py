from langgraph.graph import StateGraph, END
from models.v1.validations.conversation_state import ConversationState
from core.v1.nodes.moderator_node import Moderator_Node
from core.v1.nodes.ceo_node import Ceo_Node
from core.v1.nodes.hr_node import Hr_Node
from core.v1.nodes.product_manager_node import Product_Manager_Node
from core.v1.nodes.user_node import User_Node   
from utils.v1.workflow.decide_turn import decide_next_speaker


def build_conversation_graph():
    graph = StateGraph(ConversationState)

    graph.add_node("moderator", Moderator_Node)
    graph.add_node("ceo", Ceo_Node)
    graph.add_node("product_manager", Product_Manager_Node)
    graph.add_node("hr", Hr_Node)
    graph.add_node("user", User_Node)

    graph.add_conditional_edges(
        "moderator",
        lambda state: decide_next_speaker(state),
        {
            "ceo": "ceo",
            "product_manager": "product_manager",
            "hr": "hr",
            "user": "user",
            "end_discussion": END,
        },
    )

    graph.add_edge("ceo", "moderator")
    graph.add_edge("product_manager", "moderator")
    graph.add_edge("hr", "moderator")
    graph.add_edge("user", "moderator")

    graph.set_entry_point("moderator")

    return graph.compile()
