import smtplib

from celery import Celery

celery = Celery('notifications', broker="redis://localhost:6379/0")

@celery.task
def send_to_email(user_email: str, event_id: int, topic: str = "Регистрация", body: str = "Благодарим за регистрацию на мероприятие:"):
    server = smtplib.SMTP('smtp.example.com', 587)
    server.starttls()
    server.login("your_email@example.com", "your_password")
    message = f"Subject: {topic}\n\n{body} {event_id}"
    server.sendmail("your_email@example.com", user_email, message)
    server.quit()