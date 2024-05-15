from robocorp.tasks import task
from functions import NewsScrapper
from xpaths import CONFIG
import logging


news_data={
    "LATimes":"https://www.latimes.com/",   
}
@task
def minimal_task():
    obj=NewsScrapper(url=news_data["LATimes"],xpaths=CONFIG)
    data=obj.readConfig()
    if obj.dataPayload == None:
        logging.log(logging.DEBUG,"There are no payloads to process the bot..Exiting")
        return
    else:
        logging.log(logging.DEBUG,"Starting Bot Operation...")
        obj.mainTask()
