from celery import shared_task
from celery.utils.log import get_task_logger
from django.core.management import call_command 


logger = get_task_logger(__name__)


@shared_task
def sample_task():
    logger.info("The sample task just ran.")
    return "sample_task success"

@shared_task
def update_portfolio_and_send_reports():
    call_command("update_portfolio", )
    logger.info("The update_portfolio_and_send_reports task just ran.")
    return "update_portfolio_and_send_reports task success"