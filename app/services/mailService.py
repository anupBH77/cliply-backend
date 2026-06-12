import asyncio
import base64
import logging
import re
import smtplib
import sys
from asyncio import to_thread
from datetime import datetime, timedelta
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
import httpx
from jinja2 import Environment, FileSystemLoader, select_autoescape

from app.config.env_config import (
    GMAIL_SMTP_CLIENTID,
    GMAIL_SMTP_CLIENT_SECRET,
    GMAIL_SMTP_REFRESH_TOKEN,
    GMAIL_SMTP_SENDER,
    GMAIL_SMTP_USERNAME,
)

logger = logging.getLogger(__name__)


class GMailService:

    def __init__(self):

        self.access_token_expiresin = datetime.now()
        self.access_token = self.get_access_token(force_refresh=True)
        self.smtp_server = None

    @staticmethod
    def generate_oauth2_string(access_token: str, as_base64: bool = False) -> str:

        username = GMAIL_SMTP_USERNAME
        auth_string = f"user={username}\1auth=Bearer {access_token}\1\1"
        if as_base64:
            return base64.b64encode(auth_string.encode("ascii")).decode("ascii")
        return auth_string

    @staticmethod
    def extract_plaintext(html: str):
        return re.sub(r"<[^>]+>", "", html)

    def get_access_token(self, force_refresh: bool = False) -> str:

        now = datetime.now()
        if not force_refresh and self.access_token_expiresin < now:
            return self.access_token

        # Get access token from refresh token
        access_resp = httpx.post(
            "https://oauth2.googleapis.com/token",
            data={
                "client_id": GMAIL_SMTP_CLIENTID,
                "client_secret": GMAIL_SMTP_CLIENT_SECRET,
                "refresh_token": GMAIL_SMTP_REFRESH_TOKEN,
                "grant_type": "refresh_token",
            },
        ).raise_for_status()

        resp: dict[str, str] = access_resp.json()

        self.access_token_expiresin = datetime.now() + timedelta(
            seconds=int(resp["expires_in"])
        )

        return resp["access_token"]

    async def __smtp_server(self):
          # Creating a new smtp server each time to avoid threading issues
          self.smtp_server = await to_thread(smtplib.SMTP_SSL, "smtp.gmail.com", 465)
          await self.__smtp_connect()
          return self.smtp_server


    async def __smtp_connect(self):
        
        _ = await to_thread(self.smtp_server.connect, "smtp.gmail.com", 465)

        await to_thread(self.smtp_server.ehlo)
        auth_string = self.generate_oauth2_string(
            self.get_access_token(),
            as_base64=False,
        )

        def authobject(challenge: bytes | None = None):
            if challenge:
                raise NotImplementedError(
                    "Response to SMTP challenge is not implemented"
                )
            return auth_string

        _ = await to_thread(
            self.smtp_server.auth, mechanism="XOAUTH2", authobject=authobject
        )
    @staticmethod
    def render_email(template_name: str, context: dict) -> str:
      env = Environment(
          loader=FileSystemLoader("src/templates"),
          autoescape=select_autoescape(["html", "xml"])
      )
      template = env.get_template(template_name)
      return template.render(**context)
    
    async def send_emails(
        self,
        subject: str,
        body_html: str,
        recipients: list[str],
        sender: str = GMAIL_SMTP_SENDER,
        debug: bool = False,
        Bcc:str = None
    ):
        html, plaintext = self.generate_body(body_html)
        # Connect to Gmail's SMTP server using SSL
        # with smtplib.SMTP("smtp.gmail.com", 587) as smtp_server:

        
        try:

            tasks = []

            for recipient in recipients:
                msg = MIMEMultipart("alternative")

                # Record the MIME types of both parts - text/plain and text/html.
                part1 = MIMEText(plaintext, "plain")
                part2 = MIMEText(html, "html")

                # Attach parts into message container.
                # According to RFC 2046, the last part of a multipart message,
                # in this case the HTML message, is best and preferred.

                msg.attach(part1)  # Attach plaintext email
                msg.attach(part2)  # Attach html email

                msg["Subject"] = subject
                msg["From"] = sender
                msg["To"] = recipient
                if Bcc:
                    msg["Bcc"] = Bcc

                # smtp_server.sendmail(sender, recipient, msg.as_string())
                # Create a new smtp_server for each email to avoid threading issues
                smtp_server = await self.__smtp_server()
                smtp_server.set_debuglevel(debug)

                tasks.append(
                    asyncio.to_thread(smtp_server.sendmail, sender, recipient, msg.as_string())
                )

                logger.info("Message sent to %s!", recipient)

            await asyncio.gather(*tasks)

        except smtplib.SMTPServerDisconnected:
            # if server has disconnected, reconnect and try again
            await self.__smtp_connect()
            await self.send_emails(
                subject=subject,
                body_html=body_html,
                recipients=recipients,
                sender=sender,
                debug=debug,
                Bcc=Bcc
            )

    async def __send_msg(
        self,
        sender: str,
        recipient: list[str] | str,
        msg: MIMEBase,
    ):
        smtp_server = await self.__smtp_server()
        try:
            await to_thread(
                smtp_server.sendmail,
                from_addr=sender,
                to_addrs=recipient,
                msg=msg.as_string(),
            )
        except smtplib.SMTPServerDisconnected:
            await self.__smtp_connect()
            await to_thread(
                smtp_server.sendmail,
                from_addr=sender,
                to_addrs=recipient,
                msg=msg.as_string(),
            )

    @staticmethod
    def generate_body(body_html: str) -> tuple[str, str]:
        """
        Takes input the HTML body of the email and returns
        a tuple of str (HTML, text)
        """
        html_template = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600&display=swap" rel="stylesheet">
      <style>
        body {{
          font-family: 'Montserrat', sans-serif;
          margin: 0;
          padding: 0;
          background-color: #F9FAFB;
        }}
        .email-container {{
          max-width: 600px;
          margin: 0 auto;
          background-color: #FCFCFD;
        }}
        .header {{
          background-color: #5DC7E2;
          text-align: center;
          padding: 20px 0;
        }}
        .header img {{
          max-width: 150px;
          height: auto;
        }}
        a:hover {{
          cursor: pointer;
        }}
        .footer {{
          background-color: #f4f4f4;
          text-align: center;
          padding: 20px;
          font-size: 12px;
          color: #888888;
        }}
        .footer a {{
          color: #006097;
          text-decoration: none;
          margin: 0 10px;
        }}
        .footer a:hover {{
          text-decoration: underline;
        }}
        .social-icon {{
          width: 24px;
          vertical-align: middle;
          margin-top: 10px;
        }}
        .footer-links {{
          margin: 10px 0;
        }}
        

      </style>
    </head>
    <body>
      <div class="email-container">
        <!-- Header Section -->
        <div style="background-color:transparent;">
        <div class="header">
        
          <img src="cid:mindologo.png" alt="mindO Logo">
        </div>
        </div>

        <!-- Main Content Section -->
        <div class="content">
          {body_html}
        </div>

       <div class="footer" style="font-size:13px; color:#555; text-align:center;">

  <!-- Help / Support -->
  <p>
    Need help? Contact us at 
    <a href="mailto:support@mindo.tech">support@mindo.tech</a>
  </p>

  <!-- Why receiving -->
  <p style="font-size:12px; color:#777;">
    You are receiving this email because you installed mindO extension on Zoho CRM.
  </p>

  <!-- Links -->
  <p>
    <a href="https://mindo.tech" target="_blank">mindo.tech</a> |
    <a href="https://mindo.tech/about-us" target="_blank">About Us</a> |
    <a href="https://mindo.tech/faqs" target="_blank">FAQ</a>
  </p>

  <!-- Social -->
  <p>
    <a href="https://linkedin.com/company/mindotech" target="_blank">
      <img src="https://cdn-icons-png.flaticon.com/512/174/174857.png"
           alt="LinkedIn"
           width="20"
           style="vertical-align :middle;">
    </a>
  </p>

  <!-- Legal -->
  <p style="font-size:12px; color:#777;">
    © 2026 mindO. All rights reserved.
  </p>


</div>
      </div>
    </body>
    </html>
        """
        return html_template, GMailService.extract_plaintext(body_html)
       