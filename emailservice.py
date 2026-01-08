# emailservice.py (Modern Friendly Agent HTML Email with PDF Attachment)
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import logging
from GoogleSheet import map_value, INCOME_MAP, INSURANCE_MAP, TIMING_MAP
import os

# -----------------------------
# Configuration
# -----------------------------
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USERNAME = "kkmjpaibot@gmail.com"
SMTP_PASSWORD = "wkmi vjtc qtfg geph"   # App password
FROM_EMAIL = SMTP_USERNAME
SUBJECT = "😊 Your Insurance Chat Summary – KKMJP Superagent"
WHATSAPP_NUMBER = "60123456789"  # Agent WhatsApp (no +)
ATTACHMENT_PATH = "Benefits.pdf"  # Path to your PDF file

# -----------------------------
# Send email function
# -----------------------------
def send_summary_email(to_email, session_data):
    """
    Sends a modern, friendly, human-like insurance summary email
    with a WhatsApp CTA button and PDF attachment.
    """
    try:
        # Map the session data to friendly labels
        insurance = map_value(session_data.get('insurance', ''), INSURANCE_MAP)
        timing = map_value(session_data.get('timing', ''), TIMING_MAP)
        income = map_value(session_data.get('income', ''), INCOME_MAP)

        # Plan premium details (if available)
        plan_info = session_data.get('plan_info', {})
        premium_html = ""
        if plan_info:
            premium_html = (
                f"<div style='margin:20px 0; padding:20px; background:#f1f5f9; "
                f"border-radius:10px; font-size:16px;'>"
                f"<b>Your estimated monthly premium is RM {plan_info.get('premium', '')}</b><br><br>"
                f"• Life: RM {plan_info.get('life', '')}<br>"
                f"• Critical Illness: RM {plan_info.get('critical', '')}<br>"
                f"• Medical Card: RM {plan_info.get('medical', '')}"
                f"</div>"
            )

        # WhatsApp link
        whatsapp_link = (
            f"https://wa.me/{WHATSAPP_NUMBER}"
            "?text=Hi%20KKMJP%20Superagent,%20I%20just%20received%20my%20summary%20email%20and%20would%20like%20to%20know%20more."
        )

        # HTML email body
        body = f"""
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>KKMJP Insurance Summary</title>
</head>
<body style="margin:0; padding:0; background:#f2f4f8; font-family: 'Segoe UI', Arial, sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="padding:24px 0;">
    <tr>
      <td align="center">
        <table width="600" cellpadding="0" cellspacing="0"
               style="background:#ffffff; border-radius:14px; overflow:hidden;
                      box-shadow:0 8px 24px rgba(0,0,0,0.08);">

          <!-- Header -->
          <tr>
            <td style="background:linear-gradient(135deg,#0d47a1,#1976d2);
                       padding:28px; text-align:center;">
              <h1 style="margin:0; color:#ffffff; font-size:24px;">
                KKMJP Superagent
              </h1>
              <p style="margin:8px 0 0; color:#e3f2fd; font-size:15px;">
                Your Personal Insurance Assistant
              </p>
            </td>
          </tr>

          <!-- Content -->
          <tr>
            <td style="padding:32px; color:#333333;">

              <p style="font-size:16px; margin-top:0;">
                Hi <strong>{session_data.get('name', '')}</strong> 👋,
              </p>

              <p style="font-size:16px; line-height:1.6;">
                Thank you for chatting with <strong>KKMJP Superagent</strong>!  
                I’ve put together a quick summary of what you shared, so you can
                review it anytime 😊
              </p>

              <!-- Premium Details -->
              {premium_html}

              <!-- Summary Table -->
              <table width="100%" cellpadding="0" cellspacing="0"
                     style="margin-top:20px; border-collapse:collapse; font-size:15px;">
                <tr>
                  <td style="padding:10px; color:#666;">🎂 Date of Birth</td>
                  <td style="padding:10px; font-weight:600;">
                    {session_data.get('dob', '')} (Age: {session_data.get('age', '')})
                  </td>
                </tr>
                <tr style="background:#f9fafb;">
                  <td style="padding:10px; color:#666;">🛡️ Coverage Interest</td>
                  <td style="padding:10px; font-weight:600;">{insurance}</td>
                </tr>
                <tr>
                  <td style="padding:10px; color:#666;">⏰ Preferred Timing</td>
                  <td style="padding:10px; font-weight:600;">{timing}</td>
                </tr>
                <tr style="background:#f9fafb;">
                  <td style="padding:10px; color:#666;">💰 Income Range</td>
                  <td style="padding:10px; font-weight:600;">{income}</td>
                </tr>
                <tr>
                  <td style="padding:10px; color:#666;">📞 Phone</td>
                  <td style="padding:10px; font-weight:600;">
                    {session_data.get('phone', '')}
                  </td>
                </tr>
                <tr style="background:#f9fafb;">
                  <td style="padding:10px; color:#666;">📧 Email</td>
                  <td style="padding:10px; font-weight:600;">
                    {session_data.get('email', '')}
                  </td>
                </tr>
                <tr>
                  <td style="padding:10px; color:#666;">📋 Selected Plan</td>
                  <td style="padding:10px; font-weight:600;">
                    {session_data.get('plan', '')}
                  </td>
                </tr>
              </table>

              <!-- WhatsApp Button -->
              <div style="text-align:center; margin-top:32px;">
                <a href="{whatsapp_link}" target="_blank"
                   style="background:#25D366; color:#ffffff; text-decoration:none;
                          padding:14px 30px; border-radius:30px;
                          font-size:16px; font-weight:600; display:inline-block;">
                  💬 Chat with a Real Agent on WhatsApp
                </a>
              </div>

              <!-- Footer -->
              <p style="margin-top:32px; font-size:15px; line-height:1.6;">
                If you have any questions at all, just reply on WhatsApp — 
                we’re always happy to help 😊
              </p>

              <p style="margin-bottom:0; font-size:15px;">
                Warm regards,<br>
                <strong>KKMJP Superagent Team</strong>
              </p>

            </td>
          </tr>
        </table>

        <p style="font-size:12px; color:#888; margin-top:14px;">
          © 2026 KKMJP Superagent. All rights reserved.
        </p>

      </td>
    </tr>
  </table>
</body>
</html>
"""

        # -----------------------------
        # Create email
        # -----------------------------
        msg = MIMEMultipart()
        msg["From"] = FROM_EMAIL
        msg["To"] = to_email
        msg["Subject"] = SUBJECT

        # Attach HTML body
        msg.attach(MIMEText(body, "html"))

        # Attach PDF
        if os.path.isfile(ATTACHMENT_PATH):
            with open(ATTACHMENT_PATH, "rb") as f:
                pdf = MIMEApplication(f.read(), _subtype="pdf")
                pdf.add_header('Content-Disposition', 'attachment', filename=os.path.basename(ATTACHMENT_PATH))
                msg.attach(pdf)
        else:
            logging.warning(f"Attachment {ATTACHMENT_PATH} not found, skipping.")

        # -----------------------------
        # Send email
        # -----------------------------
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.send_message(msg)
        server.quit()

        logging.info(f"Email sent successfully to {to_email}")
        return True

    except Exception as e:
        logging.exception(f"Failed to send email to {to_email}")
        return False
