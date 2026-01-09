"""
LLM Summarization Module

This module makes a SINGLE Gemini API call to summarize pre-computed
analytical agent results into natural language. Temperature is set low
(≤ 0.3) for consistent, deterministic-like outputs.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional
import os

# Try to load .env or !.env file if python-dotenv is available
try:
    from dotenv import load_dotenv
    from pathlib import Path
    # Try to load !.env first, then fall back to .env
    env_file = Path('!.env')
    if env_file.exists():
        load_dotenv('!.env')
    else:
        load_dotenv()  # Load .env file if it exists
except ImportError:
    # python-dotenv not installed, will use environment variables only
    pass


def load_prompt_template() -> str:
    """
    Load the fixed, versioned prompt template from prompt.txt.
    
    Returns:
        Prompt template string
    
    Raises:
        FileNotFoundError: If prompt.txt is not found
    """
    prompt_path = Path(__file__).parent / "prompt.txt"
    
    if not prompt_path.exists():
        raise FileNotFoundError(f"Prompt template not found: {prompt_path}")
    
    with open(prompt_path, 'r', encoding='utf-8') as f:
        return f.read()


def format_agent_results(agent_outputs: List[Dict]) -> str:
    """
    Format agent outputs into a readable string for the LLM prompt.
    
    Args:
        agent_outputs: List of agent output dictionaries
    
    Returns:
        Formatted string representation of agent results
    """
    formatted_results = []
    
    for agent_output in agent_outputs:
        agent_name = agent_output.get('agent_name', 'unknown')
        results = agent_output.get('results', {})
        confidence = agent_output.get('confidence', 0.0)
        
        formatted_results.append(f"\n[{agent_name.upper()}]")
        formatted_results.append(f"Confidence: {confidence:.4f}")
        formatted_results.append(f"Results: {json.dumps(results, indent=2)}")
    
    return "\n".join(formatted_results)


def summarize_with_gemini(agent_outputs: List[Dict], 
                          api_key: Optional[str] = None,
                          temperature: float = 0.3) -> Dict:
    """
    Summarize agent outputs using Gemini API (single call).
    
    Args:
        agent_outputs: List of agent output dictionaries
        api_key: Gemini API key (if None, reads from GEMINI_API_KEY env var)
        temperature: Temperature setting (default 0.3, max 0.3 as per constraints)
    
    Returns:
        Dictionary with summary text and metadata
    
    Raises:
        ImportError: If google-generativeai is not installed
        ValueError: If API key is missing
        Exception: For API errors
    """
    # Import check
    try:
        import google.generativeai as genai
    except ImportError:
        raise ImportError(
            "google-generativeai package not found. "
            "Install with: pip install google-generativeai"
        )
    
    # Get API key
    if api_key is None:
        api_key = os.getenv('GEMINI_API_KEY')
    
    if not api_key:
        raise ValueError(
            "Gemini API key required. Set GEMINI_API_KEY environment variable "
            "or pass api_key parameter."
        )
    
    # Validate temperature constraint
    if temperature > 0.3:
        temperature = 0.3
    
    # Configure Gemini
    genai.configure(api_key=api_key)
    
    # Select model - list available models and pick best one
    models = genai.list_models()
    available = [m.name for m in models if 'generateContent' in m.supported_generation_methods]
    
    if not available:
        raise ValueError("No available Gemini models found")
    
    # Try to find preferred model (flash or pro variants)
    model_name = None
    for preferred in ['gemini-1.5-flash', 'gemini-pro', 'gemini-1.5-pro']:
        for m in available:
            if preferred in m.lower():
                model_name = m
                break
        if model_name:
            break
    
    # Fallback to first available
    if not model_name:
        model_name = available[0]
    
    model = genai.GenerativeModel(model_name)
    
    # Load and format prompt
    prompt_template = load_prompt_template()
    agent_results_str = format_agent_results(agent_outputs)
    full_prompt = prompt_template.format(agent_results=agent_results_str)
    
    # Generate summary (SINGLE CALL)
    # Create generation configuration
    try:
        # Use GenerationConfig from genai.types
        generation_config = genai.types.GenerationConfig(
            temperature=temperature,
            top_p=0.95,
            top_k=40,
            max_output_tokens=1024,
        )
        
        response = model.generate_content(
            full_prompt,
            generation_config=generation_config
        )
        
        summary_text = response.text.strip()
        
        return {
            "summary": summary_text,
            "model": "gemini-1.5-flash",
            "temperature": temperature,
            "num_agents_summarized": len(agent_outputs),
            "status": "success"
        }
    
    except Exception as e:
        return {
            "summary": None,
            "error": str(e),
            "model": "gemini-1.5-flash",
            "temperature": temperature,
            "num_agents_summarized": len(agent_outputs),
            "status": "error"
        }


def summarize_agent_results(agent_outputs: List[Dict],
                           api_key: Optional[str] = None) -> Dict:
    """
    Main function to summarize agent results.
    This is the primary interface for the summarizer.
    
    Args:
        agent_outputs: List of agent output dictionaries
        api_key: Gemini API key (optional, uses env var if not provided)
    
    Returns:
        Dictionary containing summary and metadata
    """
    return summarize_with_gemini(
        agent_outputs,
        api_key=api_key,
        temperature=0.3
    )

