import streamlit as st
import requests
import json
import os
import time
# Constants
base_path = os.path.dirname(os.path.abspath(__file__))
PRESET_FILE = os.path.join(base_path, 'preset.txt')
STYLE_FILE = os.path.join(base_path, 'styles.txt')
OLLAMA_API_URL = 'http://localhost:11434/api'
INPUT_LENGTH = 8192
# Load items from file
def load_items(file_path):
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r') as file:
                return json.load(file)
        except json.JSONDecodeError:
            st.error(f"Error loading from {file_path}: file might be corrupted. Starting with empty items.")
    return {}
# Save items to file
def save_items(file_path, items):
    try:
        with open(file_path, 'w') as file:
            json.dump(items, file, indent=4)
    except IOError as e:
        st.error(f"Error saving items to {file_path}: {e}")

# Call Ollama API to generate text
def call_ollama_generate_text(model, prompt):
    response = requests.post(
        f'{OLLAMA_API_URL}/generate',
        json={'model': model, 'prompt': prompt, "options": {"num_ctx": INPUT_LENGTH}},
        stream=True
    )
    response.raise_for_status()
    return ''.join(json.loads(line).get('response', '') for line in response.iter_lines())
# Call Ollama API for chat
def call_ollama_chat(model, prompt, preset_choice):
    messages = [{"role": "user", "content": prompt}]
    response = requests.post(
        f'{OLLAMA_API_URL}/chat',
        json={"model": model, "messages": messages, "options": {"num_ctx": INPUT_LENGTH}, "stream": True},
        stream=True
    )
    response.raise_for_status()

    output = ""
    for line in response.iter_lines():
        body = json.loads(line)
        if "error" in body:
            raise Exception(body["error"])
        if not body.get("done", False):
            message = body.get("message", "")
            content = body.get("message", {}).get("content", "")
            if preset_choice == "Chat":
                output += content
        if body.get("done", False):
            message["content"] = output
            return output
# General function to call Ollama based on model type
def call_ollama(model, prompt, preset_choice):
    return call_ollama_generate_text(model, prompt, preset_choice) if "llama" in model.lower() else call_ollama_chat(model, prompt, preset_choice)
# Append preset/system prompt to the input prompt
def append_prompts(preset_prompt, input_prompt):
    return f"{preset_prompt}: {input_prompt}" if preset_prompt else f"{input_prompt}"
# Fetch model names from the Ollama API
def fetch_model_names():
    try:
        response = requests.get(f'{OLLAMA_API_URL}/tags')
        response.raise_for_status()
        data = response.json()
        return [model['name'] for model in data.get('models', [])]
    except requests.RequestException as e:
        st.error(f"Error fetching model names: {e}")
        return []
# Streamlit GUI
st.title("Ollama Interaction GUI")
# Initialize session state for preset and style management
if 'preset_choice' not in st.session_state:
    st.session_state.preset_choice = "Chat"
if 'style_choice' not in st.session_state:
    st.session_state.style_choice = "None"
if 'new_style_active' not in st.session_state:
    st.session_state.new_style_active = False
if 'new_preset_active' not in st.session_state:
    st.session_state.new_preset_active = False
if 'edit_preset_active' not in st.session_state:
    st.session_state.edit_preset_active = False
if 'edit_style_active' not in st.session_state:
    st.session_state.edit_style_active = False

# Monitor preset and style files for changes
def monitor_file(file_path, session_key):
    if os.path.exists(file_path):
        current_modified = os.path.getmtime(file_path)
        if session_key not in st.session_state or current_modified != st.session_state[session_key]:
            st.session_state[f'saved_{session_key}'] = load_items(file_path)
            st.session_state[session_key] = current_modified

monitor_file(PRESET_FILE, 'last_modified_preset')
monitor_file(STYLE_FILE, 'last_modified_style')
# Preset and model selection
preset_options = ["None"] + list(st.session_state.get('saved_last_modified_preset', {}).keys())
preset_choice = st.selectbox("Choose a preset prompt", options=preset_options, index=preset_options.index(st.session_state.preset_choice) if st.session_state.preset_choice in preset_options else 0)

style_options = ["None"] + list(st.session_state.get('saved_last_modified_style', {}).keys())
style_choice = st.selectbox("Choose a writing style", options=style_options, index=style_options.index(st.session_state.style_choice) if st.session_state.style_choice in style_options else 0)

selected_model = st.selectbox("Choose a model", fetch_model_names() or ["No models available"])
# Update session state
st.session_state.preset_choice = preset_choice
st.session_state.style_choice = style_choice
# Show selected preset and style if any
preset_prompt = st.session_state.get('saved_last_modified_preset', {}).get(st.session_state.preset_choice, "")
style_prompt = st.session_state.get('saved_last_modified_style', {}).get(st.session_state.style_choice, "")

input_prompt = st.text_area("Input Prompt", placeholder="Enter your input prompt", height=200)
# Submit button
if st.button("Write Now!"):
    if style_prompt:
        final_style_prompt = f"Use the text between '<' and '>' signs as examples for writing style. Try to imitate the style as much as you can when generating new text. <{style_prompt}.>"
    else :
        final_style_prompt = "Use a neutral Australian tone for writing."

    final_prompt = append_prompts(f"{final_style_prompt} {preset_prompt}", input_prompt)
    result = call_ollama(selected_model, final_prompt, preset_choice)
    st.markdown(f'<div style="height: 400px; overflow-y: auto;background-color:#2e2d2a;">{result}</div>', unsafe_allow_html=True)
# New and Edit preset and style buttons
col1, col2, col3, col4 = st.columns(4)
with col1:
    if st.button("New preset prompt"):
        st.session_state.new_preset_active = True
with col2:
    edit_preset_button = st.button("Edit preset prompt")
    if edit_preset_button:
        st.session_state.edit_preset_active = True
with col3:
    if st.button("New writing style"):
        st.session_state.new_style_active = True
with col4:
    if st.button("Edit writing style"):
        st.session_state.edit_style_active = True
# New preset prompt
if st.session_state.new_preset_active:
    new_preset_name = st.text_input("Preset Name", key="new_preset_name")
    new_preset_prompt = st.text_area("Preset Prompt", placeholder="Enter a preset prompt", key="new_preset_prompt")
    if st.button("Save Preset"):
        if new_preset_name and new_preset_prompt:
            saved_presets = st.session_state.get('saved_last_modified_preset', {})
            saved_presets[new_preset_name] = new_preset_prompt
            save_items(PRESET_FILE, saved_presets)
            st.session_state.saved_last_modified_preset = saved_presets
            st.session_state.preset_choice = new_preset_name

            st.success(f"Preset '{new_preset_name}' saved successfully.")
            time.sleep(1)
            st.session_state.new_preset_active = False
            st.experimental_rerun()
        else:
            st.error("Preset name and prompt cannot be empty.")

    if st.button("Cancel", key="cancel_new_preset"):
        st.session_state.new_preset_active = False
        st.experimental_rerun()
# Edit preset prompt
if st.session_state.edit_preset_active and st.session_state.preset_choice != "None":
    st.write(f"Current preset: {st.session_state.preset_choice}")
    edited_preset_prompt = st.text_area("Edit Preset Prompt", preset_prompt)
    col1, col2 = st.columns(2)
    with col1:
        save_change_preset_active = st.button("Save Changes")
    with col2:
        delete_preset_active = st.button("Delete Preset")
    if save_change_preset_active:
        saved_presets = st.session_state.get('saved_last_modified_preset', {})
        # st.write(f"SAve preset: {saved_presets}")
        saved_presets[st.session_state.preset_choice] = edited_preset_prompt
        save_items(PRESET_FILE, saved_presets)
        st.session_state.saved_last_modified_preset = saved_presets
        st.success(f"Preset '{st.session_state.preset_choice}' updated successfully.")
        time.sleep(1)
        st.session_state.edit_preset_active = False
        st.experimental_rerun()

    if delete_preset_active:
        st.write("Delete button is clicked")
        saved_presets = st.session_state.get('saved_last_modified_preset', {})
        if st.session_state.preset_choice in saved_presets:
            del saved_presets[st.session_state.preset_choice]
            save_items(PRESET_FILE, saved_presets)
            st.session_state.saved_last_modified_preset = saved_presets
            st.session_state.preset_choice = "None"
            st.success("Preset deleted successfully.")
            time.sleep(1)
            st.session_state.edit_preset_active = False
            # Reset session states as needed
            st.experimental_rerun()

# New writing style
if st.session_state.new_style_active:
    new_style_name = st.text_input("Style Name", key="new_style_name")
    new_style_prompt = st.text_area("Style Prompt", placeholder="Enter a style prompt", key="new_style_prompt")

    if st.button("Save Style"):
        if new_style_name and new_style_prompt:
            saved_styles = st.session_state.get('saved_last_modified_style', {})
            saved_styles[new_style_name] = new_style_prompt
            save_items(STYLE_FILE, saved_styles)
            st.session_state.saved_last_modified_style = saved_styles
            st.session_state.style_choice = new_style_name
            st.success(f"Style '{new_style_name}' saved successfully.")
            time.sleep(1)
            st.session_state.new_style_active = False
            st.experimental_rerun()
        else:
            st.error("Style name and prompt cannot be empty.")

    if st.button("Cancel", key="cancel_new_style"):
        st.session_state.new_style_active = False
        st.experimental_rerun()

# Edit writing style
if st.session_state.edit_style_active and st.session_state.style_choice != "None":
    st.write(f"Current style: {st.session_state.style_choice}")
    edited_style_prompt = st.text_area("Edit Style Prompt", style_prompt)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Save Style Changes"):
            saved_styles = st.session_state.get('saved_last_modified_style', {})
            saved_styles[st.session_state.style_choice] = edited_style_prompt
            save_items(STYLE_FILE, saved_styles)
            st.session_state.saved_last_modified_style = saved_styles
            st.success(f"Style '{st.session_state.style_choice}' updated successfully.")
            time.sleep(1)
            st.session_state.edit_style_active = False
            st.experimental_rerun()
    with col2:
        if st.button("Delete Style"):
            saved_styles = st.session_state.get('saved_last_modified_style', {})
            if st.session_state.style_choice in saved_styles:
                del saved_styles[st.session_state.style_choice]
                save_items(STYLE_FILE, saved_styles)
                st.session_state.saved_last_modified_style = saved_styles
                st.session_state.style_choice = "None"
                st.success("Style deleted successfully.")
                time.sleep(1)
                st.session_state.edit_style_active = False
                # Reset session states as needed
                st.experimental_rerun()
