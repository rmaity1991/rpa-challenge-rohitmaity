from RPA.Browser.Selenium import Selenium
from RPA.Robocorp.WorkItems  import WorkItems
from RPA.HTTP import HTTP
import logging
from time import sleep
import time
import datetime
from RPA.Excel.Files import Files

logging.basicConfig(filename='./output/botLogging.log', encoding='utf-8', level=logging.INFO)
class NewsScrapper:

    def __init__(self,url,xpaths):
        # Create the data url and get the current system date
        self.dataUrl=url
        self.current_date=datetime.datetime.fromtimestamp(time.time())
        self.browser_object=Selenium(auto_close=False)
        self.excel_obj=Files()
        self.xpaths=xpaths

    def readConfig(self):
        try:
            library=WorkItems()
            input_work_item=library.get_input_work_item()
            data_payload=library.get_work_item_payload()
            self.dataPayload=data_payload
            logging.log(logging.INFO,"Work Item data has been read succesfully")
        except Exception as e:
            logging.log(logging.ERROR,f"The following error has occured whuile reading WorkItems : {e}")
            self.dataPayload=None

    def cleanUpTask(self):
        self.browser_object.close_browser()

    def mainTask(self):
        try:
            self.browser_object.open_available_browser(url=self.dataUrl,maximized=True)
            try:
                self.browser_object.wait_until_page_contains_element(self.xpaths["LATimes"]["search_button"],timeout=120)
                self.browser_object.click_element(self.xpaths["LATimes"]["search_button"])
            except Exception as e:
                logging.log(logging.ERROR,f'Page does contain element for {self.xpaths["LATimes"]["search_button"]}, Try chercking the xpaths')
                return
                    
            logging.log(logging.DEBUG,"The search button for the webpage is clicked")

            try:
                self.browser_object.wait_until_page_contains_element(self.xpaths["LATimes"]["search_text_field"],timeout=120)
                self.browser_object.input_text(self.xpaths["LATimes"]["search_text_field"],self.dataPayload['SEARCH'])
            except Exception as e:
                logging.log(logging.ERROR,f'Page does contain element for {self.xpaths["LATimes"]["search_text_field"]}, Try checking the xpaths')
                return
            
            logging.log(logging.DEBUG,"The search input for the webpage is written")
        
            self.browser_object.click_element_when_clickable(self.xpaths["LATimes"]["search_submit_button"])
            logging.log(logging.DEBUG,"The search button for the webpage is clicked")

            try:
                self.browser_object.wait_until_page_contains_element(self.xpaths["LATimes"]["category_selection"],timeout=120)
            except Exception as e:
                logging.log(logging.ERROR,f'Page does contain element for {self.xpaths["LATimes"]["category_selection"]}, Try chercking the xpaths')
                return

            if self.browser_object.does_page_contain_element(self.xpaths["LATimes"]["category_selection"]):
                self.browser_object.select_from_list_by_label(self.xpaths["LATimes"]["category_selection"],self.dataPayload['CATEGORY'])
                self.browser_object.wait_until_page_contains_element(self.xpaths["LATimes"]["news_results_open_status"],120)
                sleep(20)             
                                                
            data=[]
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
                            logging.log(logging.DEBUG,f"The date difference is greter than the specified in the work Items CONFIG MONTH")
                            stop_page_scroll=True
                            break

                        data_dict={"TITLE":self.browser_object.get_text(x),"DESC":self.browser_object.get_text(y),"DATE":f"{news_timeStamp.month}/{news_timeStamp.day}/{news_timeStamp.year}","LINK":news_link_address}
                        data.append(data_dict)  

                    self.browser_object.scroll_element_into_view(self.xpaths["LATimes"]["news_next_page"])
                    self.browser_object.click_element(self.xpaths["LATimes"]["news_next_page"])
                    self.browser_object.wait_until_page_contains_element(self.xpaths["LATimes"]["news_results_open_status"],120)
                    sleep(15)
            print(data)
            workbook=self.excel_obj.create_workbook(path='./output/results.xlsx',sheet_name="Sheet1")
            self.excel_obj.set_active_worksheet("Sheet1")
            self.excel_obj.append_rows_to_worksheet(data,header=True)
            self.excel_obj.save_workbook()
        except Exception as e:
            logging.log(logging.ERROR,f"The following error has occured whiole processing the bot : {e}")
            return
            
