#!/usr/bin/env python3
"""
DualMindDiff AI - Function Calling Module
Supports: Google Gemini | Groq | OpenRouter
Usage: python3 fc_module.py --provider google --prompt "analyze data/sample.txt"
"""

import os
import json
import sys
import requests
import argparse
import subprocess
import datetime

# =========================
# COLORS
# =========================
class C:
    RESET  = "\033[0m"
    RED    = "\033[91m"
    GREEN  = "\033[92m"
    YELLOW = "\033[93m"
    CYAN   = "\033[96m"
    BOLD   = "\033[1m"

def ok(msg):    print(f"{C.GREEN}[+]{C.RESET} {msg}")
def info(msg):  print(f"{C.CYAN}[*]{C.RESET} {msg}")
def warn(msg):  print(f"{C.YELLOW}[!]{C.RESET} {msg}")
def err(msg):   print(f"{C.RED}[ERROR]{C.RESET} {msg}")
def tool(msg):  print(f"{C.YELLOW}[TOOL]{C.RESET} {msg}")
def result(msg):print(f"{C.GREEN}[RESULT]{C.RESET} {msg}")

# =========================
# MODELS
# =========================
MODELS = {
    "google":     "gemini-2.5-flash",
    "groq":       "llama-3.3-70b-versatile",
    "openrouter": "mistralai/mistral-7b-instruct",
}

# =========================
# TOOL DEFINITIONS - OpenAI style
# =========================
TOOLS_OPENAI = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Reads a text file from disk and returns its content",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Path to the file"}
                },
                "required": ["path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "save_report",
            "description": "Saves analysis output to a file",
            "parameters": {
                "type": "object",
                "properties": {
                    "filename": {"type": "string", "description": "Output file path"},
                    "content":  {"type": "string", "description": "Content to save"}
                },
                "required": ["filename", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_files",
            "description": "Lists all files in a directory",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Directory path"}
                },
                "required": ["path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_cve",
            "description": "Searches NVD for CVE details by CVE ID",
            "parameters": {
                "type": "object",
                "properties": {
                    "cve_id": {"type": "string", "description": "CVE ID e.g. CVE-2021-3156"}
                },
                "required": ["cve_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "run_command",
            "description": "Runs a safe shell command and returns the output. Only allowed: nmap, whois, dig, curl, ping, ls, cat, file, strings",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {"type": "string", "description": "Shell command to execute"}
                },
                "required": ["command"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "fetch_url",
            "description": "Fetches the content of a URL and returns it as text",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "URL to fetch"}
                },
                "required": ["url"]
            }
        }
    }
]

# Google style
TOOLS_GOOGLE = [{
    "function_declarations": [t["function"] for t in TOOLS_OPENAI]
}]

# =========================
# TOOL IMPLEMENTATIONS
# =========================
ALLOWED_COMMANDS = ["nmap", "whois", "dig", "curl", "ping", "ls", "cat", "file", "strings"]

def read_file(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"[read_file ERROR] {e}"

def save_report(filename, content):
    try:
        os.makedirs(os.path.dirname(filename) if os.path.dirname(filename) else ".", exist_ok=True)
        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Report saved to {filename}"
    except Exception as e:
        return f"[save_report ERROR] {e}"

def list_files(path):
    try:
        return "\n".join(os.listdir(path))
    except Exception as e:
        return f"[list_files ERROR] {e}"

def search_cve(cve_id):
    try:
        url = f"https://services.nvd.nist.gov/rest/json/cves/2.0?cveId={cve_id}"
        r = requests.get(url, timeout=300)
        data = r.json()
        vuln = data["vulnerabilities"][0]["cve"]
        desc = vuln["descriptions"][0]["value"]
        score = vuln.get("metrics", {})
        cvss = ""
        if "cvssMetricV31" in score:
            cvss = score["cvssMetricV31"][0]["cvssData"]["baseScore"]
        elif "cvssMetricV2" in score:
            cvss = score["cvssMetricV2"][0]["cvssData"]["baseScore"]
        return f"CVE: {cve_id}\nDescription: {desc}\nCVSS Score: {cvss}"
    except Exception as e:
        return f"[search_cve ERROR] {e}"

def run_command(command):
    try:
        cmd_base = command.strip().split()[0]
        if cmd_base not in ALLOWED_COMMANDS:
            return f"[run_command BLOCKED] Command '{cmd_base}' not allowed. Allowed: {', '.join(ALLOWED_COMMANDS)}"
        output = subprocess.check_output(
            command, shell=True, stderr=subprocess.STDOUT, timeout=30
        )
        return output.decode("utf-8", errors="replace")
    except subprocess.TimeoutExpired:
        return "[run_command ERROR] Command timed out"
    except Exception as e:
        return f"[run_command ERROR] {e}"

def fetch_url(url):
    try:
        r = requests.get(url, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
        return r.text[:5000]
    except Exception as e:
        return f"[fetch_url ERROR] {e}"

TOOL_MAP = {
    "read_file":   read_file,
    "save_report": save_report,
    "list_files":  list_files,
    "search_cve":  search_cve,
    "run_command": run_command,
    "fetch_url":   fetch_url,
}

# =========================
# LOGGING
# =========================
def save_log(provider, prompt, tool_calls_log, final_response):
    os.makedirs("logs", exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    log_path = f"logs/session_{timestamp}.json"
    log = {
        "timestamp": timestamp,
        "provider": provider,
        "prompt": prompt,
        "tool_calls": tool_calls_log,
        "response": final_response
    }
    with open(log_path, "w", encoding="utf-8") as f:
        json.dump(log, f, indent=2, ensure_ascii=False)
    ok(f"Session logged to {log_path}")

# =========================
# PROVIDER CALLS
# =========================
def call_google(messages, api_key, model):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    r = requests.post(
        url,
        params={"key": api_key},
        headers={"Content-Type": "application/json"},
        json={"contents": messages, "tools": TOOLS_GOOGLE},
        timeout=340
    )
    r.raise_for_status()
    return r.json()

def call_openai_style(endpoint, api_key, model, messages):
    r = requests.post(
        endpoint,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        },
        json={
            "model": model,
            "messages": messages,
            "tools": TOOLS_OPENAI,
            "tool_choice": "auto"
        },
        timeout=340
    )
    r.raise_for_status()
    return r.json()

# =========================
# TOOL LOOPS
# =========================
def tool_loop_google(messages, api_key, model, tool_calls_log):
    while True:
        response = call_google(messages, api_key, model)
        part = response["candidates"][0]["content"]["parts"][0]

        if "functionCall" in part:
            fn_name = part["functionCall"]["name"]
            fn_args = part["functionCall"]["args"]
            tool(f"Calling {C.BOLD}{fn_name}{C.RESET} with args: {fn_args}")

            res = TOOL_MAP[fn_name](**fn_args)
            result(str(res)[:300])

            tool_calls_log.append({"tool": fn_name, "args": fn_args, "result": str(res)[:500]})

            messages.append({"role": "model", "parts": [{"functionCall": part["functionCall"]}]})
            messages.append({
                "role": "user",
                "parts": [{"functionResponse": {
                    "name": fn_name,
                    "response": {"content": res}
                }}]
            })
        else:
            return part["text"]

def tool_loop_openai_style(endpoint, api_key, model, messages, tool_calls_log):
    while True:
        response = call_openai_style(endpoint, api_key, model, messages)
        message = response["choices"][0]["message"]
        finish_reason = response["choices"][0]["finish_reason"]

        messages.append(message)

        if finish_reason == "tool_calls":
            for tc in message["tool_calls"]:
                fn_name = tc["function"]["name"]
                fn_args = json.loads(tc["function"]["arguments"])
                tool(f"Calling {C.BOLD}{fn_name}{C.RESET} with args: {fn_args}")

                res = TOOL_MAP[fn_name](**fn_args)
                result(str(res)[:300])

                tool_calls_log.append({"tool": fn_name, "args": fn_args, "result": str(res)[:500]})

                messages.append({
                    "role": "tool",
                    "tool_call_id": tc["id"],
                    "content": str(res)
                })
        else:
            return message["content"]

# =========================
# MAIN
# =========================
def main():
    parser = argparse.ArgumentParser(description="DualMindDiff AI - Function Calling Module")
    parser.add_argument("--provider", choices=["google", "groq", "openrouter"], default="google",
                        help="LLM provider to use (default: google)")
    parser.add_argument("--model", default=None,
                        help="Override default model for the provider")
    parser.add_argument("--prompt", default="Read the file data/sample.txt, analyze it from a security perspective, then save the report to output/report.txt",
                        help="Prompt to send to the model")
    parser.add_argument("--no-log", action="store_true",
                        help="Disable session logging")
    args = parser.parse_args()

    provider = args.provider
    model = args.model or MODELS[provider]
    prompt = args.prompt

    # API key check
    key_map = {
        "google":     "GOOGLE_API_KEY",
        "groq":       "GROQ_API_KEY",
        "openrouter": "OPENROUTER_API_KEY",
    }
    api_key = os.getenv(key_map[provider])
    if not api_key:
        err(f"Missing API key - run: export {key_map[provider]}=your_key")
        sys.exit(1)

    endpoint_map = {
        "groq":       "https://api.groq.com/openai/v1/chat/completions",
        "openrouter": "https://openrouter.ai/api/v1/chat/completions",
    }

    print(f"\n{C.BOLD}=== DualMindDiff AI - Function Calling ==={C.RESET}")
    info(f"Provider : {C.CYAN}{provider.upper()}{C.RESET}")
    info(f"Model    : {C.CYAN}{model}{C.RESET}")
    info(f"Prompt   : {prompt}\n")

    tool_calls_log = []

    try:
        if provider == "google":
            messages = [{"role": "user", "parts": [{"text": prompt}]}]
            final = tool_loop_google(messages, api_key, model, tool_calls_log)
        else:
            messages = [
                {"role": "system", "content": "You are a senior security researcher. Use the available tools when needed."},
                {"role": "user", "content": prompt}
            ]
            final = tool_loop_openai_style(endpoint_map[provider], api_key, model, messages, tool_calls_log)

        print(f"\n{C.BOLD}=== FINAL RESPONSE ==={C.RESET}\n")
        print(final)

        if not args.no_log:
            save_log(provider, prompt, tool_calls_log, final)

    except requests.exceptions.HTTPError as e:
        err(f"HTTP error: {e}")
        sys.exit(1)
    except Exception as e:
        err(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
