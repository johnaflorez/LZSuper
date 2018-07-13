from __future__ import absolute_import

import os

from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait

import time

from django.core.exceptions import ObjectDoesNotExist
from django.db.utils import IntegrityError

from celery.worker.request import Request
from celery import current_app
from celery import Task

from robots.models import TaskRun

BASE_DIR = os.path.dirname(__file__)
app = current_app


class CustomRequest(Request):

    def on_accepted(self, pid, time_accepted):
        super(CustomRequest, self).on_accepted(pid, time_accepted)
        # Task accept going to save on database
        self.task.update_state(task_id=self.task_id, state='PENDING', meta={'info': 'waiting a free worker'})


class CustomTask(Task):
    Request = CustomRequest

    def update_state(self, task_id=None, state=None, meta=None):
        if task_id is None:
            task_id = self.request.id

        if state == 'STARTED' or state == 'PENDING':
            # print(f"Change state to => {state}")
            try:
                task_db = TaskRun.objects.get(task_id=task_id)
                task_db.status = state
                task_db.save()
            except ObjectDoesNotExist:
                # If task don't exist on db will be create
                try:
                    TaskRun.objects.create(task_id=task_id, status=state).save()
                except IntegrityError:
                    # Unique Constraint Error
                    pass
        else:
            # print(task_id)
            self.backend.store_result(task_id, meta, state)

    def after_return(self, status, retval, task_id, args, kwargs, einfo):
        if status == 'PAUSED':
            pass  # Save robot serialized when is PAUSED
        else:  # Clean on TaskRun database task totally executed
            try:
                TaskRun.objects.get(task_id=task_id).delete()
                # print(f"Task {task_id} deleted")
            except ObjectDoesNotExist:
                # print(f"Task {task_id} isn't enable to delete (Object Doesn't Exist)")
                pass

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        # Delete task from task running table
        try:
            TaskRun.objects.get(task_id=task_id).delete()
            # print(f"Task {task_id} deleted")
        except ObjectDoesNotExist:
            # print(f"Task {task_id} isn't enable to delete (Object Doesn't Exist)")
            pass


# Tasks
@app.task(name='google', base=CustomTask, bind=True)
def google(self, **kwargs):
    url = "http://www.google.com"
    keywords = kwargs.pop('keyword', None)

    driver = WebDriver(executable_path=os.path.join(BASE_DIR, 'driver', 'chromedriver'))
    wait_driver = WebDriverWait(driver=driver, timeout=30)
    try:
        print("Start SeoRobot Google")
        driver.get(url)  # Url de la pagina a Buscar
        driver.find_element_by_name('q').send_keys(keywords, Keys.ENTER)
        time.sleep(10)
        links = driver.find_elements_by_css_selector('.rc > .r a')
        print("end")

    finally:
        print("Finished SeoRobot Google")
        result = {"result": dict([(i, _.get_attribute('href')) for i, _ in enumerate(links, 1)])}
        driver.quit()

    return result


@app.task(name='yahoo', base=CustomTask, bind=True)
def yahoo(self, **kwargs):
    url = "https://www.yahoo.com"
    keywords = kwargs.pop('keyword', None)

    driver = WebDriver(executable_path=os.path.join(BASE_DIR, 'driver', 'chromedriver.exe'))
    wait_driver = WebDriverWait(driver=driver, timeout=30)

    try:
        print("Start SeoRobot Yahoo")
        driver.get(url)  # Url de la pagina a Buscar
        driver.find_element_by_name('p').send_keys(keywords, Keys.ENTER)
        time.sleep(10)
        links = driver.find_elements_by_css_selector('h3.title a')
        print("Geting Links...")


    finally:
        print("Finished SeoRobot Yahoo")
        result = {"result": dict([(i, _.get_attribute('href')) for i, _ in enumerate(links, 1)])}
        driver.quit()

    return result


@app.task(name='bing', base=CustomTask, bind=True)
def bing(self, **kwargs):
    url = "http://www.bing.com"
    keywords = kwargs.pop('keyword', None)

    driver = WebDriver(executable_path=os.path.join(BASE_DIR, 'driver', 'chromedriver.exe'))
    wait_driver = WebDriverWait(driver=driver, timeout=30)
    try:
        print("Start SeoRobot Bing")
        driver.get(url)  # Url de la pagina a Buscar
        driver.find_element_by_name('q').send_keys(keywords, Keys.ENTER)
        time.sleep(10)
        links = driver.find_elements_by_css_selector('.b_algo a')

    finally:

        print("Finished SeoRobot Bing")
        result = {"result": dict([(i, _.get_attribute('href')) for i, _ in enumerate(links, 1)])}

        driver.quit()

    return result


@app.task(name='duckduck', base=CustomTask, bind=True)
def duck(self, **kwargs):
    url = "https://www.duckduckgo.com"
    keywords = kwargs.pop('keyword', None)

    driver = WebDriver(executable_path=os.path.join(BASE_DIR, 'driver', 'chromedriver.exe'))
    wait_driver = WebDriverWait(driver=driver, timeout=30)

    try:
        print("Start SeoRobot DuckDuck")
        driver.get(url)  # Url de la pagina a Buscar
        driver.find_element_by_name('q').send_keys(keywords, Keys.ENTER)
        time.sleep(10)
        links = driver.find_elements_by_css_selector('.result__title a')

    finally:
        print("Finished SeoRobot DuckDuck")
        result = {"result": dict([(i, _.get_attribute('href')) for i, _ in enumerate(links, 1)])}

        driver.quit()

    return result


@app.task(serializer='json', base=CustomTask, bind=True)
def sendmail(self, data):
    print(data)

    print("returned", data)

    #send_data = '[{}] {} {}'.format(data['type'], data['code'], data['body'])
    # server = smtplib.SMTP('smtp.gmail.com', 587)
    # server.starttls()
    # server.login('ivanspoof@gmail.com', 'ghdqzh30db2')
    # server.sendmail('ivanspoo@gmail.com', 'ivanspoof@gmail.com', send_data)
    # server.quit()
    return data
