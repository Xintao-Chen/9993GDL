# GDL2NL Project

This project is designed to run and evaluate multiple prompting strategies for automatically generating GDL (Game Description Language) code from natural language using Large Language Models (LLMs).

## 1. Environment Setup

### 1.1 Install Eclipse
Download and install Eclipse from the [official website](https://www.eclipse.org/downloads/).  
If your workflow requires GDL parsing, you will also need Eclipse Prolog support.

### 1.2 Create and Configure a Python Virtual Environment
```bash
python -m venv myeny
source myeny/bin/activate    # Linux / macOS
# myeny\Scripts\activate     # Windows
pip install -r requirements.txt
Remember to set OpenAi key
```bash
export OPENAI_API_KEY="your key"
