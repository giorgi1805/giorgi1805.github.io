import json

def run(object, script):
    try:
        data = json.loads(script)
    except Exception as e:
        return f"Error parsing JSON: {e}"

    results = []

    if isinstance(data, dict):
        data = [data]

    for call in data:
        if not isinstance(call, dict):
            results.append("Invalid command format.")
            continue

        tool = call.get("tool")

        if not tool:
            results.append("Missing tool name.")
            continue

        args = call.get("args", [])
        kwargs = call.get("kwargs", {})

        if hasattr(object, tool):
            try:
                func = getattr(object, tool)
                result = func(*args, **kwargs)
                results.append(result)
            except Exception as e:
                results.append(f"Error executing {tool}: {e}")
        else:
            results.append(f"Function {tool} not found.")

    return results if results else None

if __name__ == "__main__": 
    from tool_call.classic import Classic 

    print(run(Classic, "[{\"tool\": \"open_website\", \"args\": [\"https://youtube.com\"], \"kwargs\": {}}, {\"tool\": \"open_website\",\"args\": [\"https://youtube.com\"], \"kwargs\": {}}]"))