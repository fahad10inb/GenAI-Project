Certainly! Here's the revised README with improved grammar and alignment:

---

# Image-to-Audio Story Converter

This project facilitates the conversion of images into narrative audio stories using image captioning, text generation, and text-to-speech technologies.

## Overview

The project encompasses three core functionalities:

1. **Image-to-Text Conversion**: Utilizes the Salesforce/blip-image-captioning-base model to generate descriptive text from uploaded images.

2. **Text-to-Story Generation**: Employs the GPT-2 text generation model from Hugging Face Transformers to expand short descriptions into complete narrative stories.

3. **Text-to-Speech Conversion**: Integrates with the ESPnet-based Kan-Bayashi LJSpeech VITS model via the Hugging Face API to convert generated stories into audio files.

## Technologies Used

- **Python**: Programming language for backend processing.
- **Streamlit**: Web application framework for the user interface.
- **Hugging Face Transformers**: Library for accessing pre-trained language models like GPT-2.
- **Hugging Face API**: Provides access to the ESPnet-based text-to-speech model.
- **Salesforce/blip-image-captioning-base**: Model for generating image captions.
- **ESPnet Kan-Bayashi LJSpeech VITS**: Model for converting text to speech.

## Setup and Usage

1. **Clone the Repository**: Clone this repository to your local machine.
   
   ```bash
   git clone https://github.com/fahad10inb/GenAI-Project.git
   ```

2. **Run the Application**: Start the Streamlit application to use the image-to-audio story converter.

   ```bash
   streamlit run app.py
   ```

3. **Upload an Image**: Use the provided interface to upload an image. The application will generate a short description (caption) based on the image.

4. **Generate Story**: Click on the generated caption to expand it into a full narrative story using the GPT-2 text generation model.

5. **Convert to Audio**: Finally, listen to the generated story by clicking on the provided audio start option.

## Integration with ESPnet for Text-to-Speech

To integrate ESPnet for text-to-speech conversion, follow these steps:

- **Install ESPnet**: Ensure ESPnet is installed in your environment. You can install it using pip:
  
  ```bash
  pip install espnet
  ```

- **Initialize ESPnet TTS Model**: Load the ESPnet model for text-to-speech conversion.

  ```python
  from espnet2.bin.tts_inference import Text2Speech

  # Load the ESPnet model
  model = Text2Speech.from_pretrained("espnet/kan-bayashi_ljspeech_vits")
  ```

- **Generate Speech**: Use the initialized model to generate speech from text. Here’s a basic example:

  ```python
  # Generate speech from text
  text_to_generate = "Text to convert into speech"
  speech, *_ = model(text_to_generate)

  # Save speech to a file (example)
  with open("output.wav", "wb") as f:
      f.write(speech.numpy())
  ```

- **Handle Audio Output**: Implement logic in your application to manage the audio output from ESPnet and provide options for users to download the generated audio file.

## Future Enhancements

- Enhance image captioning accuracy using advanced computer vision techniques.
- Integrate additional language models for generating diverse and engaging narrative stories.
- Implement support for multiple languages and dialects in text-to-speech conversion.

## Contributors

- GitHub: [Fahad10inb](https://github.com/fahad10inb)
- Email: [fahadrahiman10@gmail.com](mailto:fahadrahiman10@gmail.com)

---
