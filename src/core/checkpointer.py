import os
from langgraph.checkpoint.memory import MemorySaver
# from langgraph.checkpoint.postgres import PostgresSaver # Uncomment for Prod
# import psycopg2

def get_checkpointer():
    """
    Returns a persistence layer for the agent state.
    
    PRINCIPAL TIP: In production, using PostgresSaver allows you to 
    query the conversation history with SQL for analytics.
    
    For this 'Showcase Portfolio', we default to MemorySaver 
    so the code runs out-of-the-box without Docker.
    """
    
    # Simulating Production Switch
    use_postgres = os.getenv("USE_POSTGRES_PERSISTENCE", "false").lower() == "true"
    
    if use_postgres:
        # DB_URI = os.getenv("DATABASE_URL")
        # conn = psycopg2.connect(DB_URI)
        # return PostgresSaver(conn)
        pass

    return MemorySaver()
