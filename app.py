from flask import Flask, request
import smtplib
from email.mime.text import MIMEText
import ssl

app = Flask(__name__)

@app.route('/transcript', methods=['POST'])
def send_transcript():
    data = request.json
    transcript = data.get('transcript', 'Geen transcript ontvangen.')

    # Maak de e-mail
    msg = MIMEText(transcript)
    msg['Subject'] = 'Nieuwe transcriptie van AI gesprek'
    msg['From'] = 'support@contactons.nl'
    msg['To'] = 'support@contactons.nl'

    # Verstuur de e-mail via je eigen SMTP server met SSL
    context = ssl.create_default_context()
    try:
        with smtplib.SMTP_SSL('mail.contactons.nl', 465, context=context) as server:
            server.login('support@contactons.nl', 'SuPP#2123(CO')
            server.send_message(msg)
        return 'Transcript verstuurd', 200
    except Exception as e:
        print(f"Fout bij verzenden: {e}")
        return f"Fout: {e}", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
