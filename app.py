from flask import Flask, request
from flask_mail import Mail, Message
import os

app = Flask(__name__)

# Configuratie Flask-Mail
app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER')
app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT'))
app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS', 'True') == 'True'
app.config['MAIL_USE_SSL'] = os.environ.get('MAIL_USE_SSL', 'False') == 'True'
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER', app.config['MAIL_USERNAME'])

mail = Mail(app)

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    print("Ontvangen data:", data)  # voor debuggen

    if not data:
        return "No JSON received", 400

    # We proberen uit 'segments' de transcriptie te halen
    segments = data.get('segments', [])
    if not segments:
        return "No transcript segments found.", 400

    # HTML-opbouw
    html_content = "<h2>Nieuwe AI gesprek binnengekomen</h2>"
    html_content += "<table border='1' cellpadding='5' cellspacing='0' style='border-collapse: collapse;'>"
    html_content += "<tr><th>Tijd</th><th>Tekst</th></tr>"

    for segment in segments:
        timestamp = segment.get('timestamp', 'Onbekend tijdstip')
        text = segment.get('text', '')
        html_content += f"<tr><td>{timestamp}</td><td>{text}</td></tr>"

    html_content += "</table>"

    # Opbouwen en verzenden van e-mail
    sender = os.environ.get('MAIL_DEFAULT_SENDER') or os.environ.get('MAIL_USERNAME')
    recipient = os.environ.get('MAIL_RECIPIENT')

    msg = Message(subject='Nieuwe AI gesprek binnengekomen',
                  sender=sender,
                  recipients=[recipient])

    msg.html = html_content  # ← we gebruiken HTML nu!

    try:
        mail.send(msg)
        return "Transcriptie ontvangen en e-mail verzonden.", 200
    except Exception as e:
        print("Error sending email:", e)
        return f"Fout bij verzenden van e-mail: {str(e)}", 500

# Extra route /transcript blijft ook beschikbaar
@app.route('/transcript', methods=['POST'])
def transcript():
    return webhook()

# Health check
@app.route('/', methods=['GET'])
def health():
    return "Server is running!", 200

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
