import smtplib
import asyncio
from email.message import EmailMessage
from datetime import datetime, timezone, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.models.domain import Event, Registration, RegistrationStatusEnum, EventStatusEnum

async def send_email(to_email: str, subject: str, html_content: str):
    """Motor asíncrono para enviar el correo."""
    if not settings.SMTP_EMAIL or not settings.SMTP_PASSWORD:
        print(f"⚠️ MODO PRUEBA: Correo omitido hacia {to_email} | Asunto: {subject}")
        return

    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = f"UNSAM Conecta <{settings.SMTP_EMAIL}>"
    msg['To'] = to_email
    msg.set_content(html_content, subtype='html')

    try:
        def _send():
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                smtp.login(settings.SMTP_EMAIL, settings.SMTP_PASSWORD)
                smtp.send_message(msg)
        
        await asyncio.to_thread(_send)
        print(f"✅ Recordatorio enviado a {to_email} ({subject})")
    except Exception as e:
        print(f"❌ Error enviando correo: {e}")

async def process_event_reminders():
    """Busca eventos próximos y envía recordatorios 24hs o 1hs antes."""
    async with AsyncSessionLocal() as db:
        now = datetime.now(timezone.utc)
        
        query = select(Event).options(
            selectinload(Event.registrations).selectinload(Registration.user)
        ).where(
            Event.status == EventStatusEnum.PUBLISHED,
            Event.start_time > now
        )
        
        result = await db.execute(query)
        events = result.scalars().all()

        for event in events:
            time_until_start = event.start_time - now
            hours_until_start = time_until_start.total_seconds() / 3600.0

            if 23.5 <= hours_until_start <= 24.5 and not event.reminder_24h_sent:
                await _notify_attendees(event, "24 horas")
                event.reminder_24h_sent = True
                db.add(event)

            elif 0.5 <= hours_until_start <= 1.5 and not event.reminder_1h_sent:
                await _notify_attendees(event, "1 hora")
                event.reminder_1h_sent = True
                db.add(event)
        
        await db.commit()

async def _notify_attendees(event: Event, time_label: str):
    """Construye y envía el correo HTML a los inscriptos confirmados."""
    confirmed_regs = [r for r in event.registrations if r.status == RegistrationStatusEnum.CONFIRMED]
    if not confirmed_regs:
        return

    # CAMBIO CLAVE: Localizar el objeto datetime UTC nativo de la BD a la zona horaria de Argentina (UTC-3)
    arg_tz = timezone(timedelta(hours=-3))
    start_time_local = event.start_time.astimezone(arg_tz)
    fecha = start_time_local.strftime("%d/%m/%Y a las %H:%M hs")
    
    subject = f"Recordatorio: Faltan {time_label} para {event.title}"
    
    for reg in confirmed_regs:
        user = reg.user
        html = f"""
        <html>
          <body style="font-family: Arial, sans-serif; padding: 20px;">
            <h2 style="color: #0d6efd;">¡Hola {user.full_name}!</h2>
            <p>Te recordamos que faltan exactamente <strong>{time_label}</strong> para el evento en la universidad.</p>
            <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0;">
                <h3 style="margin-top: 0; color: #198754;">{event.title}</h3>
                <p><strong>📅 Cuándo:</strong> {fecha}</p>
                <p><strong>📍 Dónde:</strong> {event.location}</p>
            </div>
            <p>¡Te esperamos!</p>
            <p style="font-size: 12px; color: #666;">El equipo de UNSAM Conecta</p>
          </body>
        </html>
        """
        await send_email(user.email, subject, html)