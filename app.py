from flask import Flask, request
from flask_mail import Mail, Message
import os

app = Flask(__name__)

# Configuratie voor Flask-Mail
app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'mail.jouwdomein.nl')
app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS', 'True') == 'True'
app.config['MAIL_USE_SSL'] = os.environ.get('MAIL_USE_SSL', 'False') == 'True'
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER', app.config['MAIL_USERNAME'])

mail = Mail(app)

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    if not data:
        return "No JSON received", 400

    transcription = data.get('text', '')
    phone_number = data.get('phone_number', 'Onbekend nummer')

    sender = os.environ.get('MAIL_DEFAULT_SENDER') or os.environ.get('MAIL_USERNAME')
    recipient = os.environ.get('MAIL_RECIPIENT')

    if not sender or not recipient:
        return "Server configuration error: sender or recipient missing.", 500

    msg = Message('Nieuwe Transcriptie Ontvangen',
                  sender=sender,
                  recipients=[recipient])
    msg.body = f'Transcriptie:\n{transcription}\n\nBeller: {phone_number}'
    
    try:
        mail.send(msg)
        return "Transcriptie ontvangen en e-mail verzonden.", 200
    except Exception as e:
        return f"Email verzenden mislukt: {str(e)}", 500

# Extra endpoint om ook /transcript te ondersteunen
@app.route('/transcript', methods=['POST'])
def transcript():
    return webhook()

# Health check route
@app.route('/', methods=['GET'])
def health():
    return "Server is running!", 200

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)


