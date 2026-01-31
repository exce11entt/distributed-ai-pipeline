from langgraph.graph import StateGraph, END
from src.agents.state import AgentState
from src.data.vector_db import get_vector_store
from src.data.vector_db import get_vector_store
from src.core.reranker import reranker
from src.core.checkpointer import get_checkpointer
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

class EnterpriseAgent:
    def __init__(self, model_name="gpt-4-turbo-preview"):
        self.llm = ChatOpenAI(model=model_name, temperature=0)
        self.graph = self._build_graph()

    def _should_continue(self, state: AgentState):
        """Logic to determine if the agent needs more tools or reasoning."""
        if state.get("is_complete", False):
            return "end"
        return "continue"

    def reasoner(self, state: AgentState):
        """The main thinking node of the agent."""
        # Principal Move: Using a structured prompt for deterministic thinking
        context_block = "\n".join(state.get("context", []))
        system_prompt = SystemMessage(content=(
            "You are a Banking AI Assistant. Analyze the user request. "
            f"CONTEXT FROM DATABASE:\n{context_block}\n\n"
            "If you need context, specify RAG as your next step. "
            "If you have enough info, provide a final answer based ONLY on the context."
        ))
        response = self.llm.invoke([system_prompt] + state["messages"])
        
        # Simple logic to simulate internal state transition
        is_complete = "final answer" in response.content.lower()
        return {
            "messages": [response],
            "is_complete": is_complete,
            "current_step": "reasoning"
        }

    async def rag_retriever(self, state: AgentState):
        """Real RAG node using Vector Store + Re-ranking."""
        query = state["messages"][-1].content
        vector_store = get_vector_store()
        
        # 1. Broad Search (Get top 10 candidates)
        # We fetch more than we need so the re-ranker has options to filter
        broad_results = await vector_store.search(query, k=10)
        
        # 2. Re-ranking (Filter down to top 3 high-quality matches)
        # This fixes specific-question accuracy
        metrics_msg = f"Retrieved {len(broad_results)} documents."
        
        refined_results = reranker.rerank(query, broad_results, top_k=3)
        
        # Format context
        context_str = "\n".join([f"- {doc.page_content}" for doc in refined_results])
        
        return {
            "context": [context_str],
            "current_step": "retrieval"
        }

    def _build_graph(self):
        workflow = StateGraph(AgentState)

        # Define the nodes
        workflow.add_node("reasoner", self.reasoner)
        workflow.add_node("rag_retriever", self.rag_retriever)

        # Set the entry point
        workflow.set_entry_point("reasoner")

        # Define the edges
        workflow.add_conditional_edges(
            "reasoner",
            self._should_continue,
            {
                "continue": "rag_retriever",
                "end": END
            }
        )
        
        # After retrieval, go back to reasoning to process the new info
        workflow.add_edge("rag_retriever", "reasoner")

        # Principal Move: Add Persistence
        checkpointer = get_checkpointer()
        return workflow.compile(checkpointer=checkpointer)

    def run(self, user_input: str, session_id: str = "default"):
        # We need a thread configuration to tell the checkpointer which session this is
        thread_config = {"configurable": {"thread_id": session_id}}
        
        # Check if state exists (resume) or new (start)
        # Note: In a real app, we check specific state. 
        # Here we just pass the new input which appends to history.
        
        inputs = {
            "messages": [HumanMessage(content=user_input)],
            # Logic: If resuming, we keep existing state logic
        }
        
        return self.graph.invoke(inputs, config=thread_config)
