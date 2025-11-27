"""
Example Celery tasks for Wedding Management project.

Tasks for background processing and scheduled jobs.
"""

from celery import shared_task
from django.core.mail import send_mail
from django.utils import timezone


@shared_task
def send_welcome_email(user_email):
    """
    Send a welcome email to a new user.

    Args:
        user_email (str): Email address of the user

    Returns:
        bool: True if email was sent successfully
    """
    subject = "Bem-vindo ao SIM, Aceito!"
    message = (
        "Obrigado por se cadastrar no nosso sistema de gerenciamento "
        "de casamentos. Estamos felizes em ter você conosco!"
    )
    from_email = "contato@simaceito.com.br"

    send_mail(
        subject,
        message,
        from_email,
        [user_email],
        fail_silently=False,
    )
    return True


@shared_task
def send_reminder_emails():
    """
    Send reminder emails for upcoming events.

    This task can be scheduled with Celery Beat to run periodically.
    """
    from datetime import timedelta

    from apps.scheduler.models import Event

    # Get events happening in the next 24 hours
    tomorrow = timezone.now() + timedelta(days=1)
    upcoming_events = Event.objects.filter(
        date__date=tomorrow.date(),
        reminder_sent=False
    )

    for event in upcoming_events:
        # Send reminder email
        send_mail(
            subject=f"Lembrete: {event.title}",
            message=f"Seu evento '{event.title}' está agendado para amanhã às {event.date.time()}",  # noqa: E501
            from_email="contato@simaceito.com.br",
            recipient_list=[event.wedding.user.email],
            fail_silently=False,
        )

        # Mark as sent
        event.reminder_sent = True
        event.save()

    return len(upcoming_events)


@shared_task
def cleanup_old_sessions():
    """
    Clean up expired sessions from the database.

    This task should be scheduled to run daily.
    """
    from django.core.management import call_command

    call_command('clearsessions')
    return True


@shared_task
def generate_wedding_report(wedding_id):
    """
    Generate a detailed report for a wedding.

    Args:
        wedding_id (int): ID of the wedding

    Returns:
        str: Path to the generated report
    """
    from apps.weddings.models import Wedding

    wedding = Wedding.objects.get(id=wedding_id)

    # Generate report logic here
    # This is just a placeholder
    report_data = {
        "wedding": wedding.title,
        "date": wedding.date,
        "budget": wedding.budget_set.first(),
        "contracts": wedding.contract_set.count(),
        "items": wedding.item_set.count(),
        "events": wedding.event_set.count(),
    }

    return f"Report generated for {wedding.title}: {report_data}"


@shared_task(bind=True, max_retries=3)
def process_contract_document(self, contract_id):
    """
    Process a contract document (e.g., generate PDF, send for signing).

    Args:
        contract_id (int): ID of the contract

    Returns:
        bool: True if processing was successful
    """
    try:
        from apps.contracts.models import Contract

        contract = Contract.objects.get(id=contract_id)

        # Processing logic here
        # This is just a placeholder
        contract.status = "processed"
        contract.save()

        return True

    except Exception as exc:
        # Retry the task if it fails
        raise self.retry(exc=exc, countdown=60)


# Example of periodic task configuration
# Add this to your settings or celery.py:
"""
from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    'send-reminder-emails-every-day': {
        'task': 'apps.core.tasks.send_reminder_emails',
        'schedule': crontab(hour=9, minute=0),  # Run at 9 AM daily
    },
    'cleanup-sessions-weekly': {
        'task': 'apps.core.tasks.cleanup_old_sessions',
        'schedule': crontab(hour=0, minute=0, day_of_week=0),  # Sunday midnight
    },
}
"""
