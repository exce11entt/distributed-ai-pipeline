from typing import List, Dict

# The tool definitions Vapi will use to "see" our agent capabilities
VAPI_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "check_balance",
            "description": "Check the current balance of a specific account type.",
            "parameters": {
                "type": "object",
                "properties": {
                    "account_type": {
                        "type": "string",
                        "enum": ["checking", "savings", "credit"],
                        "description": "The type of account to check."
                    }
                },
                "required": ["account_type"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "transfer_funds",
            "description": "Transfer money between accounts.",
            "parameters": {
                "type": "object",
                "properties": {
                    "to_account": {"type": "string"},
                    "amount": {"type": "number"},
                    "currency": {"type": "string", "default": "USD"}
                },
                "required": ["to_account", "amount"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "ask_policy_agent",
            "description": "Use this for complex questions about bank policies, fees, or regulations.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The user's full question about policy."
                    }
                },
                "required": ["query"]
            }
        }
    }
]
