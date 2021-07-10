import os
import time
from pprint import pprint
from celery import Celery
from celery.utils.log import get_task_logger
from celery.signals import task_postrun

# from celery.contrib import rdb
from celery.schedules import crontab
import root_app.tasks
 
# https://soshace.com/dockerizing-django-with-postgres-redis-and-celery/ 
 
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'root_app.settings')
 
app = Celery('root_app', broker='redis://redis:6379/0', backend='redis://redis:6379/0')
app.config_from_object('django.conf:settings', namespace='CELERY')
logger = get_task_logger(__name__)

@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    print('Inside setup_periodic_tasks')
    results = []
    for i in range(3):
        async_result = test_task.delay(i)
        results.append(async_result)
        print('Execute task', i, '-', async_result.status)
    
    # time.sleep(4)
    
    # print('Workers', app.control.inspect())
    # print('Queyes', app.control.inspect().active_queyes())
    
    # print('After sleep...', len(results))
    # print(app.control.ping(timeout=2.5))
    
    # pprint(vars(app.control.inspect()))
    # object_methods = [method_name for method_name in dir(object)
                  # if callable(getattr(app.control.inspect(), method_name))]
    # print()
    # for method in object_methods:
        # print(method)
    # print()
    # print('Workers', app.control.inspect())
    # for elem in app.control.inspect():
        # print(elem)
    for elem in results:
        print(elem.status)
        # print(elem.get())
        
    # Calls test('hello') every 10 seconds.
    # sender.add_periodic_task(1.0, test.s('hello'), name='hello', expires=5)

    # Calls test('world') every 30 seconds
    # sender.add_periodic_task(3.0, test.s('world'), name='world', expires=10)

@app.task(track_started=True)
def test_task(arg):
    logger.info('Inside task function with argument {0}'.format(arg))
    # print('Inside task function')
    # print(arg)
    with open("celery_test.txt", "a+") as myfile:
        myfile.write(str(arg)+"\n")
    # rdb.set_trace()
    logger.info('Finishing task with argument {0}'.format(arg))
    return "Success-zzz"


# print('Before autodiscover_tasks')
app.autodiscover_tasks()
# print('After autodiscover_tasks')

@task_postrun.connect
def after_task(**kwargs):
    # print('BEGIN after_task')
    # print('task_id -', kwargs.get('task_id'))
    # print('args -', kwargs.get('args'))
    # print('state -', kwargs.get('state'))
    # print('retval -', kwargs.get('retval'))
    # print('END after_task')
    
    logger.info('BEGIN after_task')
    logger.info('task_id -' + kwargs.get('task_id'))
    logger.info('args - ' + str(kwargs.get('args')))
    logger.info('state - ' + kwargs.get('state'))
    logger.info('retval - ' + kwargs.get('retval'))
    logger.info('END after_task')