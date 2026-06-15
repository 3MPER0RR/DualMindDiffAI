## DualMindDiffAI

git clone https://github.com/3MPER0RR/DualMindDiffAI.git

cd DualMindDiff

python3 -m venv venv
source venv/bin/activate

pip install requests, python-dotenv


## Usage insert a sample.txt in data/

export OLLAMA_API_KEY="api_key"

export OLLAMA_BASE_URL="https://ollama.com"

export GOOGLE_API_KEY="api_key"


python3 main.py
