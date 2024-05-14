from robocorp.tasks import task
from resources.functions import RPAChallenge
import logging


news_data={
    "reuters":"https://timesofindia.indiatimes.com/",   
}
@task
def minimal_task():
    obj=RPAChallenge(url=news_data["reuters"])
    data=obj.get_input_data()

    if obj.dataPayload == None:
        logging.log(logging.DEBUG,"There are no payloads to process the bot..Exiting")
        return
    else:
        obj.mainTask()
