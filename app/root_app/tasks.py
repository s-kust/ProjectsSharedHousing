from celery import shared_task
from celery.utils.log import get_task_logger
from django.core.management import call_command 


logger = get_task_logger(__name__)


@shared_task
def update_portfolio_and_send_reports():
    call_command("update_portfolio", )
    logger.info("The update_portfolio_and_send_reports task just ran.")
    return "update_portfolio_and_send_reports task success"

@shared_task
def restore_db_state_schemas():
    call_command("restore_crispy_forms_db", )
    logger.info("The restore_db_state_schemas task just ran.")
    return "restore_db_state_schemas task success"