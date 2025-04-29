from flask import Flask, request
from flask_mail import Mail, Message
import os

app = Flask(__name__)

# Configuratie voor Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER')

mail = Mail(app)

@app.route('/transcript', methods=['POST'])
def webhook():
    data = request.get_json()
    if not data:
        return "No JSON received", 400

    # Extract relevant information
    transcription = data.get('text', '')
    phone_number = data.get('phone_number', 'Onbekend nummer')
    
    # E-mail verzenden
    msg = Message('Nieuwe Transcriptie Ontvangen',
                  recipients=[os.environ.get('MAIL_RECIPIENT')])
    msg.body = f'Transcriptie:\n{transcription}\n\nBeller: {phone_number}'
    mail.send(msg)

    return "Transcriptie ontvangen en e-mail verzonden.", 200

# Health check route
@app.route('/', methods=['GET'])
def health():
    return "Server is running!", 200

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

