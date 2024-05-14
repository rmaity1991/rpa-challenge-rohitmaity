from robocorp.tasks import task
from resources.functions import RPAChallenge


news_data={
    "yahoo":"https://news.yahoo.com/",   
}
@task
def minimal_task():
    obj=RPAChallenge(url=news_data["yahoo"])
    obj.get_input_data()
