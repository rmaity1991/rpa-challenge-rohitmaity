from RPA.Browser.Selenium import Selenium
from RPA.Robocorp.WorkItems  import WorkItems
import logging
from resources.xpaths import CONFIG

class RPAChallenge:

    def __init__(self,url):
        self.dataUrl=url

    def get_input_data(self):
        try:
            library=WorkItems()
            input_work_item=library.get_input_work_item()
            data_payload=library.get_work_item_payload()
            self.dataPayload=data_payload
            logging.log(logging.INFO,"Work Item data has been read succesfully")
        except Exception as e:
            logging.log(logging.ERROR,e)
            self.dataPayload=None

    def mainTask(self):
        browser_object=Selenium(auto_close=False)

        try:
            browser_object.open_available_browser(url=self.dataUrl,maximized=True,browser_selection="Edge")
            
            try:
                browser_object.wait_until_page_contains_element(CONFIG["reuters"]["search_field"],timeout=30)
                browser_object.click_element(CONFIG["reuters"]["search_field"])
                browser_object.wait_until_page_contains_element(CONFIG["reuters"]["search_text_field"],timeout=30)
                logging.log(logging.DEBUG,"The search option for the webpage is loaded")

                if browser_object.does_page_contain_element(CONFIG["reuters"]["search_text_field"]):
                    browser_object.input_text(CONFIG["reuters"]["search_text_field"],self.dataPayload['SEARCH'])
                    browser_object.click_element(CONFIG["reuters"]["search_button"])

            except Exception as e:
                logging.log(logging.ERROR,"The search option for the webpage failed to load")
                return
        except Exception as e:
            logging.log(logging.ERROR,"The search option for the webpage failed to load")
            return
            
