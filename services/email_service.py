# Server/services/email_service.py
import smtplib
from email.message import EmailMessage

def send_styled_email(to_email: str, code: str):
    msg = EmailMessage()
    msg.set_content(f"Your password reset code is: {code}")  # Fallback plain text
    msg['Subject'] = 'Reset your password'
    msg['From'] = 'dentai.dentalcare.eg@gmail.com'
    msg['To'] = to_email

    # Add HTML styling
    msg.add_alternative(f"""
    <!DOCTYPE html>
    <html>
      <head>
        <style>
          body {{
            font-family: 'Segoe UI', sans-serif;
            background-color: #0A2542;
            color: #ffffff;
            padding: 20px;
            margin: 0;
          }}
          .container {{
            background-color: #ffffff;
            color: #0A2542;
            border-radius: 8px;
            padding: 24px;
            max-width: 500px;
            margin: auto;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
          }}
          h2 {{
            color: #0A2542;
          }}
          .code {{
            font-size: 24px;
            font-weight: bold;
            background-color: #f2f6fc;
            padding: 10px 20px;
            border-radius: 6px;
            display: inline-block;
            margin: 20px 0;
            letter-spacing: 4px;
          }}
          .footer {{
            margin-top: 20px;
            font-size: 12px;
            color: #777;
          }}
        </style>
      </head>
      <body>
        <div class="container">
          <h2>Password Reset Code</h2>
          <p>Hi there,</p>
          <p>You recently requested to reset your password. Use the code below to proceed:</p>
          <div class="code">{code}</div>
          <p>If you didn't request this, you can safely ignore this email.</p>
          <div class="footer">
            &copy; 2025 DentAI Dental Care • This is an automated message, please do not reply.
          </div>
        </div>
      </body>
    </html>
    """, subtype='html')

    # Send the email
    with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
        smtp.starttls()
        smtp.login('dentai.dentalcare.eg@gmail.com', 'mdehhkcrnuylccqp')  # 🔐 Replace with secure method!
        smtp.send_message(msg)
