# AI Customer Issue Troubleshooter

An LLM-powered, agentic troubleshooting assistant built with Python, LangGraph, LangChain, Pydantic, and Streamlit.

## Overview

The application investigates simulated engineering issues using diagnostic tools and generates structured root-cause recommendations supported by collected evidence.

## Features

- LLM-powered issue classification and diagnostic selection
- Stateful LangGraph workflow with conditional routing
- Simulated API health and authentication diagnostics
- Log analysis and local troubleshooting knowledge base
- Evidence evaluation and bounded investigation loops
- Structured diagnosis validated with Pydantic
- Streamlit interface for issue submission and report visualization
- Automated tests for diagnostic tools and workflow routing
- Error handling and inconclusive diagnosis support

## Architecture

Customer Issue → Issue Analysis → Diagnostic Tools → Evidence Evaluation → Structured Report

The investigation can repeat diagnostic checks when more evidence is needed, subject to a maximum of four tool executions.

## Technology Stack

- Python
- LangGraph
- LangChain
- OpenAI-compatible model integration
- Pydantic
- Streamlit
- pytest
- JSON

## Setup

1. Create and activate a Python virtual environment.
2. Install dependencies using `pip install -r requirements.txt`.
3. Create a `.env` file with your API credentials and model configuration.
4. Run tests using `python -m pytest -v`.
5. Launch the application using `streamlit run app.py`.

## Limitations

The initial implementation uses simulated diagnostic data and is intended for demonstration and experimentation. It is not connected to production monitoring systems and should not be used as an autonomous production remediation system.

## Future Improvements

- Integrate read-only monitoring APIs
- Add semantic retrieval over technical documentation
- Store investigation history
- Add human-in-the-loop escalation
- Improve evaluation with a larger set of labelled scenarios
- Add structured logging and latency tracking