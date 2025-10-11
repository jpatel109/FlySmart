import speech_recognition as sr
import pyttsx3
from flask import Flask, jsonify

# Initialize Flask app
app = Flask(__name__)

# Initialize recognizer and text-to-speech engine
recognizer = sr.Recognizer()
engine = pyttsx3.init()

def speak(text):
    """Convert text to speech."""
    engine.say(text)
    engine.runAndWait()

def recognize_speech():
    """Capture audio and convert to text."""
    with sr.Microphone() as source:
        print("Adjusting for ambient noise...")
        recognizer.adjust_for_ambient_noise(source, duration=1)  # Reduce background noise
        print("Listening... Speak now!")
        try:
            audio = recognizer.listen(source, timeout=5)  # Capture audio
            print("Processing speech...")
            text = recognizer.recognize_google(audio)
            print(f"Recognized text: {text}")
            return text.lower()
        except sr.UnknownValueError:
            print("Speech recognition could not understand audio")
            return "Sorry, I couldn't understand that."
        except sr.RequestError as e:
            print(f"Speech recognition request failed: {e}")
            return "Sorry, there was an issue with the recognition service."

@app.route("/run-assistant", methods=["GET"])
def run_assistant():
    """Handle voice input and respond accordingly."""
    command = recognize_speech()
    print(f"You said: {command}")

    if "search flight" in command or "find flight" in command:
        response = "Searching for flights based on your preferences."
    
    elif "hello" in command or "hi" in command:
        response = "Hello! How can I assist you today?"
    
    elif "exit" in command or "stop" in command:
        response = "Goodbye! Have a great day."
    
    else:
        response = f"I heard: {command}. How can I assist you?"
    
    speak(response)
    return jsonify({"response": response})

if __name__ == "__main__":
    app.run(port=5000, debug=True)
