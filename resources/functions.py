from RPA.Browser.Selenium import Selenium
from RPA.Robocorp.WorkItems  import WorkItems


class RPAChallenge:

    def __init__(self,url):
        self.dataUrl=url

    def get_input_data(self):
        try:
            library=WorkItems()
            input_work_item=library.get_input_work_item()
            data_payload=library.get_work_item_payload()
            
