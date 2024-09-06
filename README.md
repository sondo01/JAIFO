# JAIFO
Just another Interface for Ollama

## Overview:
Simple tasks such as writing emails, translation, or generating documents (like this one) do not require commercial Large Language Models (LLMs) like ChatGPT or Gemini. Small and Open Source LLMs, such as Llama3.1:7B or Gemma2:2B, can be run locally with Ollama to achieve the same results while maintaining user privacy. However, there is currently no simple User Interface (UI) for running Ollama, prompting the creation of this script.

JAIFO is an open-source, locally-run interface for using small-scale Large Language Models (LLMs) like Llama3.1 and Gemma2 with Ollama. This script provides a simple web interface for such tasks.

## Key Features
- Simple and lightweight web interface
- Ability to create, edit, and delete prompts as presets for easy reuse
- Ability to create, edit, and delete writing styles for reuse
### Use Cases
- Quickly generate a follow-up email by copying the original into the input prompt text area, selecting a preset prompt ("Write follow-up email"), choosing an LLM model (default: Llama3.1), and clicking "Write Now"
- Improve a text by typing a few ideas and selecting the "Improve the text" preset, then clicking "Write Now" to get a corrected version

## Installation
### Requirements
- A PC or laptop with at least 16GB RAM
- MacBook Pro M1 or later for optimal performance
### Dependencies
- Install Ollama from http://ollama.com/ and follow the instructions
- Download models using Ollama. Open Terminal (on Mac or Linux) or Command prompt on Windows:
```
$ ollama pull llama3.1
$ ollama pull gemma2:2B
```
- Install Streamlit: 
```
pip install streamlit
```
- Download and save this JAIFO project to a local folder
### Running JAIFO
To start JAIFO, navigate to the project folder and run:
```
$ streamlit run main.py
```
This will open a new tab in your default browser with the JAIFO interface.

Enjoy using JAIFO for your writing needs!

























