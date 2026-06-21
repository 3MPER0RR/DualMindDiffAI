## DualMindDiffAI

git clone https://github.com/3MPER0RR/DualMindDiffAI.git

cd DualMindDiff

python3 -m venv venv
source venv/bin/activate

pip install requests python-dotenv


## Usage e configure

insert a sample.txt in data/

export OLLAMA_API_KEY="api_key"

export OLLAMA_BASE_URL="https://ollama.com"

export GOOGLE_API_KEY="api_key"

## Edit model e prompt in main.py



run(
    prompt="Analyze the content in the document.",
    file_path="data/sample.txt",
    safe_llm_mode="ollama-cloud",
    safe_model="gemma4:31b-cloud",
    raw_llm_mode="google",
    raw_model="gemini-2.5-flash"
)



python3 main.py

## output 

=== SAFE ===
[filtered analysis from the first model]

=== RAW ===
[raw analysis from the second model]

=== DIFF ===
[reasoning differences between the two models]


es CVE-2024-21413

<img src="screen.png" width="400"/>

https://github.com/user-attachments/assets/7a17081f-04e8-4fa1-87e5-2f8f15f48d1f


## Fuction Call Module Usage

```bash
python3 fc_module.py --provider <provider> --prompt "<prompt>"
```

### Providers

| Provider | Value | Model default |
|----------|-------|---------------|
| Google Gemini | `google` | `gemini-2.5-flash` |
| Groq | `groq` | `llama-3.3-70b-versatile` |
| OpenRouter | `openrouter` | `mistralai/mistral-7b-instruct` |

---

## Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `--provider` | yes | Provider to use: `google`, `groq`, `openrouter` |
| `--prompt` | yes | Prompt in natural language |
| `--model` | no | Override default model |
| `--no-log` | no | Disable session logging |

---

## Available Tools

| Tool | Description |
|------|-------------|
| `read_file` | Reads a text file from disk |
| `save_report` | Saves output to a file |
| `list_files` | Lists files in a directory |
| `search_cve` | Searches NVD for CVE details |
| `run_command` | Runs safe shell commands |
| `fetch_url` | Fetches content from a URL |

### Allowed commands for `run_command`
```
nmap, whois, dig, curl, ping, ls, cat, file, strings
```

---

## Examples

### Read and analyze a file
```bash
python3 fc_module.py --provider google \
  --prompt "Read data/sample.txt and analyze it from a security perspective"
```

### Search a CVE
```bash
python3 fc_module.py --provider google \
  --prompt "Search CVE-2021-3156 and give me a detailed analysis"
```

### Search a CVE with Groq
```bash
python3 fc_module.py --provider groq \
  --prompt "Search CVE-2017-0144 and give me a detailed analysis"
```

### Compare two CVEs and save report
```bash
python3 fc_module.py --provider google \
  --prompt "Search CVE-2017-0144 and CVE-2021-3156, compare them and save a report to output/comparison.txt"
```

### Read file and save report
```bash
python3 fc_module.py --provider google \
  --prompt "Read data/sample.txt, analyze it from a security perspective, then save the report to output/report.txt"
```

### List files in a directory
```bash
python3 fc_module.py --provider google \
  --prompt "List files in data/ and tell me what you find"
```

### Fetch a URL and analyze content
```bash
python3 fc_module.py --provider groq \
  --prompt "Fetch https://example.com and analyze the content"
```

### Override model
```bash
python3 fc_module.py --provider groq \
  --model "mixtral-8x7b-32768" \
  --prompt "Search CVE-2021-3156 and analyze it"
```

### Disable logging
```bash
python3 fc_module.py --provider google \
  --no-log \
  --prompt "Read data/sample.txt and analyze it"
```

---

## Multi-tool chains

The model automatically calls multiple tools in sequence based on the prompt.

### Read + analyze + save
```bash
python3 fc_module.py --provider google \
  --prompt "Read data/sample.txt, analyze it and save the report to output/report.txt"
```

### Search multiple CVEs + compare + save
```bash
python3 fc_module.py --provider google \
  --prompt "Search CVE-2017-0144 and CVE-2021-3156, compare them and save a report to output/comparison.txt"
```

### List + read + analyze
```bash
python3 fc_module.py --provider google \
  --prompt "List files in data/, read sample.txt and analyze it from a security perspective"
```

---

## Output

### Terminal output
```
=== DualMindDiff AI - Function Calling ===
[*] Provider : GOOGLE
[*] Model    : gemini-2.5-flash
[*] Prompt   : ...

[TOOL] Calling search_cve with args: {'cve_id': 'CVE-2021-3156'}
[RESULT] CVE: CVE-2021-3156 ...

=== FINAL RESPONSE ===
[model analysis]

[+] Session logged to logs/session_TIMESTAMP.json
