import streamlit as st
import os
from dotenv import load_dotenv
import transformers
from transformers import pipeline

load_dotenv()

def get_api_token():
    """Get API token from various sources"""
    # Try Streamlit secrets first
    try:
        return st.secrets["HUGGINGFACEHUB_API_TOKEN"]
    except:
        pass
    
    # Try environment variable
    token = os.getenv("HUGGINGFACEHUB_API_TOKEN")
    if token:
        return token
    
    # Ask user for input
    return st.sidebar.text_input(
        "🔑 HuggingFace API Token:",
        type="password",
        placeholder="hf_...",
        help="Get from: https://huggingface.co/settings/tokens"
    )

def img2txt(image_path):
    """Convert image to text description"""
    try:
        pipe = pipeline("image-to-text", model="Salesforce/blip-image-captioning-base")
        text = pipe(image_path)[0]['generated_text']
        return text
    except Exception as e:
        st.error(f"Error analyzing image: {str(e)}")
        return None

def generate_story(scenario):
    """Generate story from image description"""
    try:
        prompt = f"Write a short story about {scenario}."
        pipe = transformers.pipeline("text-generation", model="gpt2")
        output = pipe(prompt, max_length=150, num_return_sequences=1, truncation=True)
        story = output[0]['generated_text']
        return story
    except Exception as e:
        st.error(f"Error generating story: {str(e)}")
        return None

def create_browser_tts(text):
    """Create HTML with browser's built-in speech synthesis"""
    # Escape quotes in text for JavaScript
    escaped_text = text.replace('"', '\\"').replace("'", "\\'").replace('\n', ' ')
    
    html_code = f"""
    <div style="padding: 20px; border: 1px solid #ddd; border-radius: 10px; background: #f9f9f9;">
        <h4>🎵 Audio Player</h4>
        <p>Click the button below to hear your story:</p>
        
        <button onclick="playStory()" style="
            background: #ff4b4b;
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 16px;
            margin-right: 10px;
        ">🔊 Play Story</button>
        
        <button onclick="stopStory()" style="
            background: #666;
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 16px;
        ">⏹️ Stop</button>
        
        <div id="status" style="margin-top: 10px; font-style: italic;"></div>
    </div>
    
    <script>
        let currentUtterance = null;
        
        function playStory() {{
            // Stop any current speech
            speechSynthesis.cancel();
            
            const text = `{escaped_text}`;
            currentUtterance = new SpeechSynthesisUtterance(text);
            
            // Set voice properties
            currentUtterance.rate = 0.9;
            currentUtterance.pitch = 1.0;
            currentUtterance.volume = 1.0;
            
            // Event listeners
            currentUtterance.onstart = function() {{
                document.getElementById('status').innerHTML = '🎵 Playing...';
            }};
            
            currentUtterance.onend = function() {{
                document.getElementById('status').innerHTML = '✅ Finished playing';
            }};
            
            currentUtterance.onerror = function() {{
                document.getElementById('status').innerHTML = '❌ Error playing audio';
            }};
            
            // Start speaking
            speechSynthesis.speak(currentUtterance);
        }}
        
        function stopStory() {{
            speechSynthesis.cancel();
            document.getElementById('status').innerHTML = '⏹️ Stopped';
        }}
    </script>
    """
    return html_code

def main():
    # Page setup
    st.set_page_config(
        page_title="Image to Audio Story",
        page_icon="🎵",
        layout="wide"
    )
    
    st.title("🎵 Image to Audio Story Generator")
    st.markdown("Upload an image and get an AI-generated story with audio!")
    
    # Get API token
    token = get_api_token()
    
    if not token:
        st.warning("⚠️ Please provide your HuggingFace API token to continue")
        st.info("Get your free token from: https://huggingface.co/settings/tokens")
        st.stop()
    
    # File uploader
    uploaded_file = st.file_uploader(
        "📁 Choose an image file",
        type=['jpg', 'jpeg', 'png'],
        help="Upload a JPG, JPEG, or PNG image"
    )
    
    if uploaded_file is not None:
        # Create two columns
        col1, col2 = st.columns([1, 1])
        
        with col1:
            # Display the uploaded image
            st.image(uploaded_file, caption="Your Uploaded Image", use_column_width=True)
        
        with col2:
            # Save the uploaded file temporarily
            temp_filename = f"temp_{uploaded_file.name}"
            with open(temp_filename, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            # Step 1: Analyze the image
            with st.spinner("🔍 Analyzing your image..."):
                scenario = img2txt(temp_filename)
            
            if scenario:
                st.success("✅ Image analyzed successfully!")
                
                # Show the description
                st.subheader("🖼️ Image Description")
                st.write(f"*{scenario}*")
                
                # Step 2: Generate story
                with st.spinner("📝 Writing your story..."):
                    story = generate_story(scenario)
                
                if story:
                    st.success("✅ Story generated!")
                    
                    # Show the story
                    st.subheader("📖 Your Generated Story")
                    st.write(story)
                    
                    # Step 3: Audio player
                    st.subheader("🎵 Listen to Your Story")
                    
                    # Create browser-based TTS
                    tts_html = create_browser_tts(story)
                    st.components.v1.html(tts_html, height=200)
                    
                    # Additional options
                    with st.expander("📋 More Options"):
                        st.markdown("**Copy story text for other TTS services:**")
                        st.text_area("Story Text:", story, height=100)
                        
                        st.markdown("**External TTS Services:**")
                        st.markdown("""
                        - [NaturalReaders](https://www.naturalreaders.com/online/) - Free online TTS
                        - [TTSMaker](https://ttsmaker.com/) - Multiple voices available
                        - [ResponsiveVoice](https://responsivevoice.org/) - High quality voices
                        """)
            
            # Clean up temporary file
            try:
                os.remove(temp_filename)
            except:
                pass
    
    # Sidebar information
    with st.sidebar:
        st.markdown("### 📋 How it works")
        st.markdown("""
        1. **Upload** an image (JPG, PNG)
        2. **AI analyzes** the image content
        3. **Story generated** based on the image
        4. **Listen** using browser's built-in TTS
        """)
        
        st.markdown("### ℹ️ About")
        st.markdown("""
        - **Image Analysis**: Salesforce BLIP model
        - **Story Generation**: GPT-2 model  
        - **Text-to-Speech**: Browser's built-in voice
        - **No additional installs** required!
        """)
        
        if token:
            masked_token = f"hf_...{token[-6:]}"
            st.success(f"🔑 Token: {masked_token}")

if __name__ == '__main__':
    main()
