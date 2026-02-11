# AI-Powered Course Tutor

An intelligent tutoring system that answers course questions using lecture notes and exercises.

## Features
- Question classification (relevant/irrelevant/redirect)
- Semantic similarity matching
- Context-aware responses using local LLM
- Streamlit web interface

## Quick Start

### 1. Clone the Repository
\`\`\`bash
git clone https://github.com/notlonelee/AI-Powered-Course-Tutor.git
cd AI-Powered-Course-Tutor
\`\`\`

### 2. Install Dependencies
\`\`\`bash
pip install -r requirements.txt
\`\`\`

### 3. Run the App
\`\`\`bash
streamlit run src/app.py
\`\`\`

## Requirements
- Python 3.9+
- Ollama running locally
  - Install from [ollama.ai](https://ollama.ai)
  - Run: `ollama serve`
  - Pull model: `ollama pull qwen2-math:1.5b`

## Project Structure
ai-course-tutor/
├── src/            
├── data/
│   ├── lectures/    
│   └── exercises/  
├── requirements.txt
└── README.md