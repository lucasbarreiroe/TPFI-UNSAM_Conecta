# import smtplib
import aiosmtplib
from email.message import EmailMessage
from app.core.config import settings

async def send_verification_email(user_email: str, token: str):
    #verification_url = f"http://127.0.0.1:8000/api/v1/auth/verify?token={token}"
    verification_url = f"{settings.BASE_URL}/api/v1/auth/verify?token={token}"

    if not settings.SMTP_EMAIL or not settings.SMTP_PASSWORD:
        print(f"\n⚠️ MODO PRUEBA: No hay credenciales SMTP en el .env")
        print(f"👉 Simulación de correo enviado a {user_email}")
        print(f"🔗 HAZ CLIC AQUÍ PARA VERIFICAR: {verification_url}\n")
        return

    msg = EmailMessage()
    msg['Subject'] = "UNSAM Conecta - Confirma tu correo electrónico"
    msg['From'] = f"UNSAM Conecta <{settings.SMTP_EMAIL}>"
    msg['To'] = user_email
    
    msg.set_content(f"""\
    <html>
      <body style="font-family: Arial, sans-serif; padding: 20px;">
        <h2 style="color: #0d6efd;">¡Bienvenido a UNSAM Conecta!</h2>
        <p>Gracias por registrarte en nuestra plataforma. Para poder iniciar sesión y anotarte a los eventos, necesitamos validar tu correo electrónico.</p>
        <a href="{verification_url}" style="background-color: #0d6efd; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block; margin-top: 10px;">
            Verificar mi cuenta
        </a>
        <p style="margin-top: 20px; font-size: 12px; color: #666;">Si no creaste esta cuenta, puedes ignorar este correo.</p>
      </body>
    </html>
    """, subtype='html')

    # try:
    #     with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
    #         smtp.login(settings.SMTP_EMAIL, settings.SMTP_PASSWORD)
    #         smtp.send_message(msg)
    #         print(f"✅ Correo enviado con éxito a {user_email}")
    # except Exception as e:
    #     print(f"❌ Error enviando correo: {e}")
    try:
        # Usamos la conexión asíncrona y el puerto seguro 587 con STARTTLS para Render
        await aiosmtplib.send(
            msg,
            hostname="smtp.gmail.com",
            port=587,
            username=settings.SMTP_EMAIL,
            password=settings.SMTP_PASSWORD,
            start_tls=True
        )
        print(f"✅ Correo enviado con éxito a {user_email}")
    except Exception as e:
        print(f"❌ Error enviando correo: {e}")