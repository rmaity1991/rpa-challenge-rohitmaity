from RPA.Browser.Selenium import Selenium
from RPA.Robocorp.WorkItems  import WorkItems
import logging
from time import sleep
import datetime
from RPA.Excel.Files import Files

months={
    "January":1,
    "February":2,
    "March":3,
    "April":4,
    "May":5,
    "June":6,
    "July":7,
    "August":8,
    "September":9,
    "October":10,
    "November":11,
    "December":12
}
class NewsScrapper:

    current_date=datetime.datetime.now()

    def __init__(self,url,xpaths):
        # Create the data url and get the current system date
        self.dataUrl=url
        self.current_date=datetime.datetime.now()
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
                logging.log(logging.ERROR,f'Page does contain element for {self.xpaths["LATimes"]["search_text_field"]}, Try chercking the xpaths')
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
                    
                    for x,y,z in zip(news_title,news_desc,news_date):
                        news_timeStamp=int(z.get_attribute("data-timestamp"))
                        news_timeStamp=datetime.datetime.fromtimestamp(timestamp=int(news_timeStamp))
                        data_dict={"title":self.browser_object.get_text(x),"desc":self.browser_object.get_text(y),"date_stamp":news_timeStamp}
                        data.append(data_dict)

                    stop_page_scroll=True                    
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
            
