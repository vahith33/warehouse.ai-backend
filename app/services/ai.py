import os
import re
from typing import Any, Dict, List, Optional

import openai

from app.services import ai_tools as tools

# initialize once at module import
openai.api_key = os.getenv("GROQ_API_KEY")
openai.api_base = "https://api.groq.com/openai/v1"
MODEL = "llama-3.3-70b-versatile"


async def _call_groq(messages: List[Dict[str, str]]) -> str:
    """Helper that invokes the Groq chat endpoint asynchronously."""
    try:
        response = await openai.ChatCompletion.acreate(
            model=MODEL,
            messages=messages,
            temperature=0.3,
        )
        return response.choices[0].message["content"].strip()
    except Exception as e:
        print(f"Groq API error: {e}")
        return "I'm sorry, I'm having trouble connecting to my brain right now."


async def process_message(message: str) -> str:
    """Analyse a user message, run the appropriate tool and return a reply."""
    lc = message.lower().strip()

    # System prompt for data interpretation
    interpret_prompt = (
        "You are a professional warehouse manager assistant. "
        "Your goal is to provide clear, concise, and helpful information in English. "
        "If data is provided from a tool, summarise it clearly. If no products are found, "
        "politely inform the user. Always stay professional."
    )

    try:
        # Greetings and general conversational logic
        greetings = ["hi", "hello", "good morning", "good afternoon", "gm", "hey", "good evening"]
        if any(greet in lc for greet in greetings) or len(lc) < 4:
            if not any(keyword in lc for keyword in ["stock", "product", "movement", "sku"]):
                return await _call_groq([
                    {"role": "system", "content": interpret_prompt + " Reply to the user's greeting or general question warmly and ask how you can help with the warehouse today."},
                    {"role": "user", "content": message},
                ])

        # low‑stock intent
        if "low stock" in lc or "low in stock" in lc or "reorder" in lc:
            data = await tools.get_low_stock_products()
            user_prompt = f"The user asked about low stock. Tool results: {data}. Please summarize this for them in English."
            return await _call_groq([
                {"role": "system", "content": interpret_prompt},
                {"role": "user", "content": user_prompt},
            ])

        # today's movements intent
        if "today" in lc and ("movement" in lc or "stock" in lc or "activity" in lc):
            data = await tools.get_today_stock_movements()
            user_prompt = f"The user asked about today's movements. Tool results: {data}. Please summarize this in English."
            return await _call_groq([
                {"role": "system", "content": interpret_prompt},
                {"role": "user", "content": user_prompt},
            ])

        # product inventory intent
        if any(p in lc for p in ["stock of", "stock for", "how many", "quantity", "inventory of"]):
            # Extract query: look for everything after the indicator
            m = re.search(r"(?:stock (?:of|for)|how many|inventory of|quantity (?:of|for))\s*(.*)", lc)
            query = m.group(1).strip() if m and m.group(1) else message
            data = await tools.get_product_inventory(query)
            user_prompt = f"The user asked about inventory for '{query}'. Tool results: {data}. Please explain the current stock level in English."
            return await _call_groq([
                {"role": "system", "content": interpret_prompt},
                {"role": "user", "content": user_prompt},
            ])

        # product search intent
        if any(s in lc for s in ["find", "search", "sku", "where is", "look for"]):
            m = re.search(r"(?:find|search|sku|look for)\s*(.*)", lc)
            query = m.group(1).strip() if m and m.group(1) else message
            data = await tools.search_products_by_name(query)
            user_prompt = f"The user is searching for '{query}'. Tool results: {data}. Please list the findings clearly in English."
            return await _call_groq([
                {"role": "system", "content": interpret_prompt},
                {"role": "user", "content": user_prompt},
            ])

        # Default fallback - Let the LLM handle it instead of a hardcoded string
        return await _call_groq([
            {"role": "system", "content": interpret_prompt + " If the user is asking a question you don't have a specific tool for, answer to the best of your ability or explain what you can do (check stock, search products, etc.)"},
            {"role": "user", "content": message},
        ])

    except Exception as exc: 
        print(f"AI Processing error: {exc}")
        return "I encountered a minor error while processing your request. Could you please try again?"
