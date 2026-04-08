import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from google import genai
from google.genai import types


client = genai.Client(api_key="")

async def run():
    server_params = StdioServerParameters(
        command="python",
        args=["mcpserver2.py"]
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools_result = await session.list_tools()
            tools = [
                types.Tool(function_declarations=[
                    types.FunctionDeclaration(
                        name = t.name,
                        description=t.description,
                        parameters = t.inputSchema,
                    )
                ])
                for t in tools_result.tools
            ]
            history = []
            while True:
                user_input = input("You: ")
                if user_input == "quit":
                    break
                if not user_input:
                    continue
                history.append({
                    "role": "User",
                    "parts": [{"text": user_input}]
                })
                while True:
                    response = client.models.generate_content(
                        model= "gemini-2.5-flash-lite",
                        contents = history,
                        config = types.GenerateContentConfig(
                            system_instruction="""
                            You are a strict assistant for managing a todo database.

                            RULES:
                            - You MUST use the provided tools for ALL operations (insert, update, fetch, delete).
                            - NEVER answer from your own knowledge or memory.
                            - NEVER generate fake or assumed data.
                            - ALWAYS call the appropriate tool when the user asks about todos.
                            - If a tool is available, you MUST use it.

                            OUTPUT RULES:
                            - Return tool results exactly as received.
                            - Do NOT summarize or omit records.
                            - Show ALL records when fetching data.

                            If you do not use a tool when required, the response is invalid.
                            """,
                            tools = tools
                        )
                    )

                    if not response.candidates or not response.candidates[0].content:
                        continue

                    content = response.candidates[0].content

                    if not content.parts:
                        continue

                    part = content.parts[0]

                    if hasattr(part, "function_call") and part.function_call:
                        fn = part.function_call
                        result = await session.call_tool(fn.name, dict(fn.args))
                        print(f"SERVER RESPONSE: {result.content[0].text}")  # Add this!
                        tool_result = result.content[0].text
                        history.append({
                            "role": "model",
                            "parts": [types.Part(function_call=fn)],

                        })
                        history.append({
                            "role": "User",
                            "parts": [types.Part(function_response=types.FunctionResponse(
                                name = fn.name,
                                response = { "result": tool_result}
                            ))]
                        })

                    else:
                        history.append({
                            "role": "model",
                            "parts": [{"text": part.text}]
                        })
                        print(f"Gemini: {part.text}\n")
                        break

asyncio.run(run())

