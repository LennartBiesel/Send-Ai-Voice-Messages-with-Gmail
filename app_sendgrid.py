from flask import Flask, request, jsonify
import os
from elevenlabs import set_api_key, generate, save
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from dotenv import load_dotenv
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Attachment, FileContent, FileName, FileType, Disposition
from base64 import b64encode
from io import BytesIO


load_dotenv()


app = Flask(__name__)

# Set the Eleven Labs API key
set_api_key(os.environ.get('ELEVENLABS_API_KEY'))

@app.route('/api/generate_voice_message/', methods=['POST'])
def generate_voice_message_endpoint():
    data = request.get_json()
    name = data['name']
    email = data['email']
    
    file_path = generate_voice_message(name)
    send_audio_email(email, name, file_path)
    
    return jsonify({"status": "success"})

def generate_voice_message(name):
    audio = generate(
        text=f"Hi {name},! Just so you know, this isn't a human speaking, but an AI. As you can tell, I'm aware your name is {name}. But that's just a fraction of what AI can do. I'd love to delve deeper and discuss more with you. Would you like to book a call?",
        voice="Bella",
        model="eleven_monolingual_v1"
    )
    return audio


def send_audio_email(email, name, audio_data):
    subject = "Your AI sonic treat is here"
    
    # Message template
    # Message template
    message = f"""
    Hi {name},<br><br>

    Thank you for taking the time to test the waters with AI!<br><br>

    We hope you enjoy the voice clip attached.<br><br>

    It is just a small glimpse into the possibilities that AI brings. There is so much more to AI than meets the ear!<br><br>

    At Growth Lab, we've got the tools, the talent, and the tech to take you on a deep dive into the universe of AI. Whether you're a newbie or a tech-ninja, we're here to help you find the right AI solution for your business.<br><br>

    Curious?<br><br> 

    Give us a shout, and we'll show you how AI can be the game-changer you've been waiting for.<br><br>

    The Growth Lab Team<br><br>

    P.S. If the voice clip got you excited, just wait until you see the rest! 😉🔥
    """


    email_message = Mail(
        from_email='your email here',
        to_emails=email,
        subject=subject,
        html_content=message
    )
    
    # Convert audio_data to base64
    audio_base64 = b64encode(audio_data).decode()
    
    # Create an attachment using SendGrid's Attachment class
    attachment = Attachment()
    attachment.file_content = FileContent(audio_base64)
    attachment.file_type = FileType('audio/mpeg')
    attachment.file_name = FileName('voice_message.mp3')
    attachment.disposition = Disposition('attachment')
    
    email_message.attachment = attachment
    
    try:
        sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        sg.send(email_message)
    except Exception as e:
        print(e)

if __name__ == '__main__':
    app.run(debug=True)

