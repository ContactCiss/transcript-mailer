from flask import Flask, request
import smtplib
from email.mime.text import MIMEText
import ssl

app = Flask(__name__)

@app.route('/transcript', methods=['POST'])
def send_transcript():
    print("\n🛬 Webhook POST ontvangen!")

    body = request.get_data()
    print(f"📩 Raw body (decoded): {body.decode('utf-8', errors='replace')}")

    try:
        data = request.get_json()
        print(f"📦 JSON payload: {data}")
    except Exception as e:
        print(f"🚫 Fout bij JSON parsing: {e}")
        return "Invalid JSON", 400

    # Extract all messages (user + agent)
    conversation_lines = []
    try:
        transcript_entries = data["data"]["transcript"]
        for entry in transcript_entries:
            role = entry.get("role", "")
            message = entry.get("message", "")
            if message:
                if role == "user":
                    conversation_lines.append(f"Gebruiker: {message}")
                elif role == "agent":
                    conversation_lines.append(f"Agent: {message}")
    except Exception as e:
        print(f"🚫 Fout bij uitlezen transcript: {e}")
        return "Invalid transcript data", 400

    if not conversation_lines:
        email_content = "Geen berichten gevonden in deze call."
    else:
        email_content = "<br>".join(conversation_lines)

    html_content = f"""
    <html>
        <body>
            <h2>Nieuwe AI-gesprek binnengekomen!</h2>
            <p>{email_content}</p>
        </body>
    </html>
    """

    msg = MIMEText(html_content, 'html')
    msg['Subject'] = 'Nieuwe transcriptie van AI gesprek'
    msg['From'] = 'support@contactons.nl'
    msg['To'] = 'support@contactons.nl'

    context = ssl.create_default_context()
    try:
        with smtplib.SMTP_SSL('mail.contactons.nl', 465, context=context) as server:
            server.login('support@contactons.nl', 'SuPP#2123(CO')
            server.send_message(msg)
        print("✅ E-mail succesvol verzonden.")
        return 'Transcript verstuurd', 200
    except Exception as e:
        print(f"🚫 Fout bij verzenden: {e}")
        return f"Fout: {e}", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
