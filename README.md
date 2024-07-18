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
   git clone https://github.com/your_username/image-to-audio-story.git
   cd image-to-audio-story
   ```

2. **Run the Application**: Start the Streamlit application to use the image-to-audio story converter.

   ```bash
   streamlit run app.py
   ```

3. **Upload an Image**: Use the provided interface to upload an image. The application will generate a short description (caption) based on the image.

4. **Generate Story**: Click on the generated caption to expand it into a full narrative story using the GPT-2 text generation model.

5. **Convert to Audio**: Finally, listen to the generated story by clicking on the provided audio start option.

## Future Enhancements

- Enhance image captioning accuracy using advanced computer vision techniques.
- Integrate additional language models for generating diverse and engaging narrative stories.
- Implement support for multiple languages and dialects in text-to-speech conversion.

## Contributors

- GitHub: Fahad10inb
- Email: fahadrahiman10@gmail.com

---


