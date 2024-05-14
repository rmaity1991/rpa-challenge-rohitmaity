from robocorp.tasks import task
from resources.functions import RPAChallenge
import logging


news_data={
    "LATimes":"https://www.latimes.com/",   
}
@task
def minimal_task():
    obj=RPAChallenge(url=news_data["LATimes"])
    data=obj.readConfig()

    if obj.dataPayload == None:
        logging.log(logging.DEBUG,"There are no payloads to process the bot..Exiting")
        return
    else:
        obj.mainTask()
