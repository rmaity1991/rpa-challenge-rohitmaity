from RPA.Browser.Selenium import Selenium
from PIL import ImageGrab
from RPA.Robocorp.WorkItems  import WorkItems
from RPA.HTTP import HTTP
import logging
from time import sleep
import time
import datetime
from RPA.Excel.Files import Files
current_date=f"{datetime.datetime.fromtimestamp(time.time()).day}_{datetime.datetime.fromtimestamp(time.time()).month}_{datetime.datetime.fromtimestamp(time.time()).year}"
task_name="NewsScrapper"
logging.basicConfig(filename=f'./output/botLogging_{current_date}.log', encoding='utf-8', level=logging.DEBUG)
logging.log(logging.INFO,f"*******************************************************************")
class NewsScrapper:

    def __init__(self,url,xpaths):
        # Create the data url and get the current system date
        self.dataUrl=url
        self.current_date=datetime.datetime.fromtimestamp(time.time())
        self.browser_object=Selenium(auto_close=False,page_load_timeout=120)
        self.browser_object.set_browser_implicit_wait(120)
        self.excel_obj=Files()
        self.xpaths=xpaths
        logging.log(logging.INFO,f"{task_name}:Finished Initialization")

    def readConfig(self):
        try:
            library=WorkItems()
            input_work_item=library.get_input_work_item()
            data_payload=library.get_work_item_payload()
            self.dataPayload=data_payload
            logging.log(logging.INFO,f"{task_name}:Work Item data has been read successfully")
        except Exception as e:
            logging.log(logging.ERROR,f"{task_name}:The following error has occured while reading WorkItems : {e}")
            self.dataPayload=None

    def cleanUpTask(self):
        self.browser_object.close_browser()
        logging.log(logging.INFO,"Browser Closed")

    def mainTask(self):
        try:
            logging.log(logging.INFO,f"{task_name}:Opening Available Browser")
            self.browser_object.open_available_browser(url=self.dataUrl,maximized=True,headless=True)
            
            try:
                self.browser_object.wait_until_page_contains_element(self.xpaths["LATimes"]["search_button"],timeout=120)
                self.browser_object.click_element(self.xpaths["LATimes"]["search_button"])
                sleep(15)
                logging.log(logging.INFO,f"{task_name}:Entering in the search field")
            except Exception as e:
                screenshot=ImageGrab.grab()
                screenshot.save(f"./output/Error_{current_date}.png")
                logging.log(logging.ERROR,f'Page does contain element for {self.xpaths["LATimes"]["search_button"]}, Try checking the xpaths : {e}')
                return
                    
            logging.log(logging.INFO,f"{task_name}:The search button for the webpage is clicked")

            try:
                self.browser_object.wait_until_page_contains_element(self.xpaths["LATimes"]["search_text_field"],timeout=120)
                self.browser_object.input_text(self.xpaths["LATimes"]["search_text_field"],self.dataPayload['SEARCH'])
                logging.log(logging.INFO,f"{task_name}:Entering {self.dataPayload['SEARCH']} in the serach field")
            except Exception as e:
                screenshot=ImageGrab.grab()
                screenshot.save(f"./output/Error_{current_date}.png")
                logging.log(logging.ERROR,f'{task_name}:Page does contain element for {self.xpaths["LATimes"]["search_text_field"]}, Try checking the xpaths : {e}')
                return
            
            logging.log(logging.DEBUG,f"{task_name}:The search input for the webpage is written")
        
            self.browser_object.click_element_when_clickable(self.xpaths["LATimes"]["search_submit_button"])
            logging.log(logging.DEBUG,f"{task_name}:The search button for the webpage is clicked")

            try:
                self.browser_object.wait_until_page_contains_element(self.xpaths["LATimes"]["category_selection"],timeout=120)
            except Exception as e:
                screenshot=ImageGrab.grab()
                screenshot.save(f"./output/Error_{current_date}.png")
                logging.log(logging.ERROR,f'{task_name}:Page does contain element for {self.xpaths["LATimes"]["category_selection"]}, Try chercking the xpaths : {e}')
                return

            if self.browser_object.does_page_contain_element(self.xpaths["LATimes"]["category_selection"]):
                self.browser_object.select_from_list_by_label(self.xpaths["LATimes"]["category_selection"],self.dataPayload['CATEGORY'])
                
                sleep(15)
                self.browser_object.wait_until_page_contains_element(self.xpaths["LATimes"]["news_results_open_status"],30)
                             
                                                
            data=[]
            count=0
            if self.browser_object.is_list_selection(self.xpaths["LATimes"]["category_selection"],self.dataPayload['CATEGORY']):
                stop_page_scroll=False
                while self.browser_object.does_page_contain_element(self.xpaths["LATimes"]["news_next_page"]) and stop_page_scroll==False:
                    news_title=self.browser_object.get_webelements(self.xpaths["LATimes"]["news_title"])
                    news_desc=self.browser_object.get_webelements(self.xpaths["LATimes"]["news_data"])
                    news_date=self.browser_object.get_webelements(self.xpaths["LATimes"]["news_date"])
                    news_link=self.browser_object.get_webelements(self.xpaths["LATimes"]["news_link"])
                    
                    for x,y,z,a in zip(news_title,news_desc,news_date,news_link):
                        news_timeStamp=z.get_attribute("data-timestamp")
                        news_link_address=a.get_attribute("href")
                        converted_timestamp=news_timeStamp[0:10]+'.'+news_timeStamp[10:]
                        news_timeStamp=datetime.datetime.fromtimestamp(float(converted_timestamp))

                        if (self.current_date.month - news_timeStamp.month) > self.dataPayload['MONTH']:
                            logging.log(logging.DEBUG,f"{task_name}:The date difference is greter than the specified in the work Items CONFIG MONTH")
                            stop_page_scroll=True
                            break

                        data_dict={"TITLE":self.browser_object.get_text(x),"DESC":self.browser_object.get_text(y),"DATE":f"{news_timeStamp.month}/{news_timeStamp.day}/{news_timeStamp.year}","LINK":news_link_address}
                        data.append(data_dict)  

                    if self.browser_object.does_page_contain_element(self.xpaths["LATimes"]["news_next_page"]):
                        self.browser_object.scroll_element_into_view(self.xpaths["LATimes"]["news_next_page"])
                        self.browser_object.click_element(self.xpaths["LATimes"]["news_next_page"])

                        sleep(15)
                        self.browser_object.wait_until_page_contains_element(self.xpaths["LATimes"]["news_results_open_status"],30)
                    else:
                        stop_page_scroll=True
                        
            print(data)
            workbook=self.excel_obj.create_workbook(path='./output/results.xlsx',sheet_name="Sheet1")
            self.excel_obj.set_active_worksheet("Sheet1")
            self.excel_obj.append_rows_to_worksheet(data,header=True)
            self.excel_obj.save_workbook()
        except Exception as e:
            logging.log(logging.ERROR,f"{task_name}:The following error has occured whole processing the bot : {e}")
            screenshot=ImageGrab.grab()
            screenshot.save(f"./output/Error_{current_date}.png")
            return
            
