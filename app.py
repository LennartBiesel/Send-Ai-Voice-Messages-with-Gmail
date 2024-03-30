from flask import Flask, request, jsonify, render_template
import os
from dotenv import load_dotenv
from elevenlabs import set_api_key, generate, save
# Import the necessary functions and modules for Gmail API
from googleapiclient.discovery import build
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.audio import MIMEAudio
from base64 import urlsafe_b64encode

from auth import load_credentials 

load_dotenv()

app = Flask(__name__)

# Set the Eleven Labs API key
set_api_key(os.environ.get('ELEVENLABS_API_KEY'))

@app.route('/form', methods=['GET'])
def form():
    return render_template('form.html')

@app.route('/api/generate_voice_message/', methods=['GET', 'POST'])
def generate_voice_message_endpoint():
    if request.method == 'POST':
        if request.is_json:
            # Handle JSON request
            data = request.get_json()
        else:
            # Handle form submission
            data = request.form
    
        name = data['name']
        email = data['email']
        
        file_path = generate_voice_message(name)
        send_audio_email(email, name, file_path)
        
        return jsonify({"status": "success"})
    return render_template('form.html')

def generate_voice_message(name):
    audio = generate(
        text=f"Hi {name},! Just so you know, this isn't a human speaking, but an AI. As you can tell, I'm aware your name is {name}. But that's just a fraction of what AI can do. I'd love to delve deeper and discuss more with you. Would you like to book a call?",
        voice="Bella",
        model="eleven_monolingual_v1"
    )
    return audio

def send_audio_email(email, name, audio_data):
    subject = "Your AI sonic treat is here"
    
    message_html = f"""
    Hi {name},<br><br>

    Thank you for taking the time to test the waters with AI!<br><br>

    We hope you enjoy the voice clip attached.<br><br>

    It is just a small glimpse into the possibilities that AI brings. There is so much more to AI than meets the ear!<br><br>

    AI organization, we've got the tools, the talent, and the tech to take you on a deep dive into the universe of AI. Whether you're a newbie or a tech-ninja, we're here to help you find the right AI solution for your business.<br><br>

    Curious?<br><br> 

    Give us a shout, and we'll show you how AI can be the game-changer you've been waiting for.<br><br>

    The AI Team<br><br>

    P.S. If the voice clip got you excited, just wait until you see the rest! 😉🔥
    """

    message = MIMEMultipart()
    message['to'] = email
    message['subject'] = subject

    # Attach the HTML content
    msg_html = MIMEText(message_html, 'html')
    message.attach(msg_html)

    # Attach the audio file
    msg_audio = MIMEAudio(audio_data, 'mpeg')
    msg_audio.add_header('Content-Disposition', 'attachment', filename="voice_message.mp3")
    message.attach(msg_audio)

    # Encode the entire message
    raw_message = {'raw': urlsafe_b64encode(message.as_bytes()).decode()}

    try:
        creds = load_credentials()
        service = build('gmail', 'v1', credentials=creds)
        message = (service.users().messages().send(userId="me", body=raw_message)
                   .execute())
        print(f"Message sent: {message['id']}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == '__main__':
    app.run(debug=True)
