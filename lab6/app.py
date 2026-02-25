import streamlit as st
import requests
import pandas as pd
import json
from datetime import datetime
import os
import random

# Page configuration
st.set_page_config(
    page_title="Human Preference Data Collection",
    page_icon="🤖",
    layout="wide"
)

# Initialize session state
if 'preference_data' not in st.session_state:
    st.session_state.preference_data = []
if 'current_responses' not in st.session_state:
    st.session_state.current_responses = None
if 'current_prompt' not in st.session_state:
    st.session_state.current_prompt = None
if 'seed_a' not in st.session_state:
    st.session_state.seed_a = 1
if 'seed_b' not in st.session_state:
    st.session_state.seed_b = 2
if 'prompts_dataset' not in st.session_state:
    st.session_state.prompts_dataset = None
if 'selected_prompt' not in st.session_state:
    st.session_state.selected_prompt = ""

# Title
st.title("🤖 Human Preference Data Collection")
st.markdown("Enter a prompt and compare two AI responses to record your preference.")

# Sidebar configuration
st.sidebar.header("Configuration")

# Ollama configuration (runs locally, no API key needed)
ollama_url = st.sidebar.text_input(
    "Ollama URL",
    value="http://localhost:11434",
    help="Ollama server URL (default: http://localhost:11434)"
)

# Check if Ollama is running
try:
    response = requests.get(f"{ollama_url}/api/tags", timeout=2)
    if response.status_code != 200:
        st.sidebar.warning("⚠️ Could not connect to Ollama. Make sure Ollama is running.")
except:
    st.sidebar.warning("⚠️ Could not connect to Ollama. Make sure Ollama is installed and running.")

# Model selection
model = st.sidebar.selectbox(
    "Model",
    [
        "llama2",
        "llama3",
        "mistral",
        "phi",
        "gemma",
        "qwen"
    ],
    index=0,
    help="Select an Ollama model (make sure you've pulled it with 'ollama pull <model>')"
)

# Generation Settings (collapsible)
with st.sidebar.expander("⚙️ Generation Settings", expanded=True):
    # Common settings
    st.markdown("**Common Settings**")
    max_new_tokens = st.slider("max_new_tokens", 10, 500, 90, 10)
    top_p = st.slider("top_p", 0.0, 1.0, 0.95, 0.05)
    
    st.divider()
    
    # Response A settings
    st.markdown("**Response A**")
    col_a1, col_a2 = st.columns([3, 1])
    with col_a1:
        seed_a = st.number_input("seed_A", min_value=0, max_value=1000000, value=st.session_state.seed_a, step=1, key="seed_a_input")
        st.session_state.seed_a = seed_a
    with col_a2:
        st.write("")  # Spacing
        if st.button("−", key="dec_a"):
            st.session_state.seed_a = max(0, st.session_state.seed_a - 1)
            st.rerun()
        if st.button("+", key="inc_a"):
            st.session_state.seed_a = min(1000000, st.session_state.seed_a + 1)
            st.rerun()
    
    temperature_a = st.slider("temperature_A", 0.0, 2.0, 0.70, 0.01)
    
    st.divider()
    
    # Response B settings
    st.markdown("**Response B**")
    col_b1, col_b2 = st.columns([3, 1])
    with col_b1:
        seed_b = st.number_input("seed_B", min_value=0, max_value=1000000, value=st.session_state.seed_b, step=1, key="seed_b_input")
        st.session_state.seed_b = seed_b
    with col_b2:
        st.write("")  # Spacing
        if st.button("−", key="dec_b"):
            st.session_state.seed_b = max(0, st.session_state.seed_b - 1)
            st.rerun()
        if st.button("+", key="inc_b"):
            st.session_state.seed_b = min(1000000, st.session_state.seed_b + 1)
            st.rerun()
    
    temperature_b = st.slider("temperature_B", 0.0, 2.0, 1.00, 0.01)
    
    st.caption("Keep seeds fixed for reproducibility; vary temperature for diversity.")

# Load prompts dataset
@st.cache_data
def load_prompts_dataset():
    """Load prompts from the dataset file."""
    try:
        with open("prompts_dataset.json", "r") as f:
            data = json.load(f)
            return data.get("prompts", [])
    except FileNotFoundError:
        return []
    except Exception as e:
        st.error(f"Error loading prompts dataset: {str(e)}")
        return []

# Load prompts
if st.session_state.prompts_dataset is None:
    st.session_state.prompts_dataset = load_prompts_dataset()

# Prompt input section
st.subheader("Prompt")
prompt_col1, prompt_col2 = st.columns([4, 1])

with prompt_col2:
    st.write("")  # Spacing
    st.write("")  # Spacing
    random_button = st.button("🎲 Random Prompt", use_container_width=True, help="Select a random prompt from the dataset")
    
    # Show dataset info
    if st.session_state.prompts_dataset:
        st.caption(f"📚 {len(st.session_state.prompts_dataset)} prompts available")

# Handle random prompt selection
if random_button:
    if st.session_state.prompts_dataset and len(st.session_state.prompts_dataset) > 0:
        random_prompt = random.choice(st.session_state.prompts_dataset)
        st.session_state.selected_prompt = random_prompt
        # Update the widget state directly
        if "prompt_input" not in st.session_state:
            st.session_state.prompt_input = ""
        st.session_state.prompt_input = random_prompt
        st.rerun()
    else:
        st.warning("No prompts available in dataset. Make sure prompts_dataset.json exists.")

with prompt_col1:
    # Initialize prompt_input if not exists
    if "prompt_input" not in st.session_state:
        st.session_state.prompt_input = ""
    
    # If selected_prompt is set, use it; otherwise use current input
    if st.session_state.selected_prompt and st.session_state.selected_prompt != st.session_state.prompt_input:
        st.session_state.prompt_input = st.session_state.selected_prompt
        st.session_state.selected_prompt = ""  # Clear after using
    
    prompt = st.text_area(
        "Enter your prompt:",
        height=100,
        placeholder="Type your prompt here...",
        value=st.session_state.prompt_input,
        key="prompt_input"
    )

# Generate responses button
col1, col2, col3 = st.columns([1, 1, 2])
with col1:
    generate_button = st.button("🔄 Generate A/B", type="primary", disabled=not prompt)

def generate_response_ollama(prompt_text: str, model_name: str, ollama_url: str, temperature: float, seed: int, max_tokens: int, top_p_val: float):
    """Generate a response using Ollama API."""
    try:
        # Ollama API endpoint
        api_url = f"{ollama_url}/api/generate"
        
        # Prepare payload
        payload = {
            "model": model_name,
            "prompt": prompt_text,
            "stream": False,
            "options": {
                "temperature": temperature,
                "top_p": top_p_val,
                "num_predict": max_tokens,
            }
        }
        
        # Add seed if provided
        if seed > 0:
            payload["options"]["seed"] = seed
        
        # Generate response
        response = requests.post(api_url, json=payload, timeout=120)
        response.raise_for_status()
        
        result = response.json()
        generated_text = result.get("response", "")
        
        metadata = {
            "model": model_name,
            "temperature": temperature,
            "seed": seed if seed > 0 else None,
            "max_tokens": max_tokens,
            "top_p": top_p_val,
            "timestamp": datetime.now().isoformat(),
            "total_duration": result.get("total_duration", None),
            "load_duration": result.get("load_duration", None)
        }
        
        return generated_text, metadata
        
    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to Ollama. Make sure Ollama is running:\n  ollama serve")
        return None, None
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            st.error(f"❌ Model '{model_name}' not found. Pull it first:\n  ollama pull {model_name}")
        else:
            st.error(f"Error: {str(e)}")
        return None, None
    except Exception as e:
        st.error(f"Error generating response: {str(e)}")
        return None, None

def record_preference(preference: str, responses: dict, reason: str, model_name: str):
    """Record the user's preference and add to the dataset in professor's format."""
    # Generate example_id (timestamp-based unique ID)
    example_id = str(int(datetime.now().timestamp() * 1000))
    
    # Get responses and metadata
    response_A = responses["response1"]
    response_B = responses["response2"]
    metadata_A = responses["metadata1"]
    metadata_B = responses["metadata2"]
    
    # Create data entry matching professor's format
    entry = {
        "example_id": example_id,
        "timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "prompt": st.session_state.current_prompt,
        "response_A": response_A,
        "response_B": response_B,
        "preference": preference.upper() if preference != "tie" else preference,
        "reason": reason if reason else "",
        "gen": {
            "model": model_name,
            "A": {
                "seed": metadata_A.get("seed", None),
                "temperature": metadata_A.get("temperature", None),
                "top_p": metadata_A.get("top_p", None),
                "max_new_tokens": metadata_A.get("max_tokens", None)
            },
            "B": {
                "seed": metadata_B.get("seed", None),
                "temperature": metadata_B.get("temperature", None),
                "top_p": metadata_B.get("top_p", None),
                "max_new_tokens": metadata_B.get("max_tokens", None)
            }
        }
    }
    
    # Add to session state
    st.session_state.preference_data.append(entry)
    
    # Clear current responses to allow new generation
    st.session_state.current_responses = None
    st.session_state.current_prompt = None
    
    st.success(f"✅ Preference recorded! ({preference.upper() if preference != 'tie' else 'TIE'})")
    st.rerun()

if generate_button and prompt:
    with st.spinner("Generating responses..."):
        # Generate two responses with different seeds/temperatures
        response1, metadata1 = generate_response_ollama(
            prompt, model, ollama_url, temperature_a, st.session_state.seed_a, max_new_tokens, top_p
        )
        response2, metadata2 = generate_response_ollama(
            prompt, model, ollama_url, temperature_b, st.session_state.seed_b, max_new_tokens, top_p
        )
        
        if response1 and response2:
            # Store in session state (keeps responses fixed)
            st.session_state.current_prompt = prompt
            st.session_state.selected_prompt = ""  # Clear selected prompt after generation
            st.session_state.current_responses = {
                "response1": response1,
                "response2": response2,
                "metadata1": metadata1,
                "metadata2": metadata2
            }
            st.success("✅ Two responses generated! Review them below and select your preference.")
        else:
            st.error("Failed to generate responses. Please try again.")

# Display responses if they exist
if st.session_state.current_responses:
    st.divider()
    st.subheader("Compare Responses")
    
    # Display both responses side by side
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Response A")
        st.info(st.session_state.current_responses["response1"])
        with st.expander("View Metadata"):
            st.json(st.session_state.current_responses["metadata1"])
    
    with col2:
        st.markdown("### Response B")
        st.info(st.session_state.current_responses["response2"])
        with st.expander("View Metadata"):
            st.json(st.session_state.current_responses["metadata2"])
    
    # Preference selection
    st.divider()
    st.subheader("Select Your Preference")
    
    # Reason field (optional)
    reason = st.text_input(
        "Reason (optional)",
        placeholder="Why do you prefer this response?",
        key="preference_reason"
    )
    
    pref_col1, pref_col2, pref_col3 = st.columns([1, 1, 1])
    
    with pref_col1:
        prefer_a = st.button("✅ Prefer Response A", use_container_width=True, type="primary")
    with pref_col2:
        prefer_b = st.button("✅ Prefer Response B", use_container_width=True, type="primary")
    with pref_col3:
        tie = st.button("🤝 Tie / Both Equal", use_container_width=True)
    
    # Handle preference selection
    if prefer_a:
        record_preference("A", st.session_state.current_responses, reason, model)
    elif prefer_b:
        record_preference("B", st.session_state.current_responses, reason, model)
    elif tie:
        record_preference("tie", st.session_state.current_responses, reason, model)

# Data export section
st.divider()
st.subheader("📊 Collected Data")

if st.session_state.preference_data:
    st.metric("Total Preferences Recorded", len(st.session_state.preference_data))
    
    # Display data table
    df = pd.DataFrame([
        {
            "ID": entry["example_id"],
            "Prompt": entry["prompt"][:50] + "..." if len(entry["prompt"]) > 50 else entry["prompt"],
            "Preference": entry["preference"],
            "Timestamp": entry["timestamp"]
        }
        for entry in st.session_state.preference_data
    ])
    st.dataframe(df, use_container_width=True)
    
    # Export options
    st.subheader("📥 Export Data")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Export as JSON (for training format - chosen/rejected pairs)
        training_data = []
        for entry in st.session_state.preference_data:
            if entry["preference"] != "tie":
                if entry["preference"] == "A":
                    chosen = entry["response_A"]
                    rejected = entry["response_B"]
                else:  # preference == "B"
                    chosen = entry["response_B"]
                    rejected = entry["response_A"]
                
                training_data.append({
                    "prompt": entry["prompt"],
                    "chosen": chosen,
                    "rejected": rejected
                })
        
        json_str = json.dumps(training_data, indent=2)
        st.download_button(
            label="📄 Download JSON (Training Format)",
            data=json_str,
            file_name=f"preference_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )
    
    with col2:
        # Export full data in professor's format
        full_data = st.session_state.preference_data
        json_str_full = json.dumps(full_data, indent=2)
        st.download_button(
            label="📊 Download JSON (Full Data)",
            data=json_str_full,
            file_name=f"preference_data_full_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )
    
    # Clear data button
    if st.button("🗑️ Clear All Data", type="secondary"):
        st.session_state.preference_data = []
        st.rerun()
else:
    st.info("No preferences recorded yet. Generate responses and select your preferences to start collecting data.")
