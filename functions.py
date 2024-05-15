from RPA.Browser.Selenium import Selenium
from RPA.Robocorp.WorkItems  import WorkItems
import logging
from xpaths import CONFIG
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
class RPAChallenge:

    current_date=datetime.datetime.now()

    def __init__(self,url):
        self.dataUrl=url
        self.current_date=datetime.datetime.now()
        print(int(self.current_date.month))

    def readConfig(self):
        try:
            library=WorkItems()
            input_work_item=library.get_input_work_item()
            data_payload=library.get_work_item_payload()
            self.dataPayload=data_payload
            logging.log(logging.INFO,"Work Item data has been read succesfully")
        except Exception as e:
            logging.log(logging.ERROR,e)
            self.dataPayload=None

    def getDateFormat(self,date):
        dateFormat=datetime.datetime.fromtimestamp(float(date))
        return dateFormat

    def cleanUpTask(self):
        self.browser_object.close_browser()

    def mainTask(self):
        self.browser_object=Selenium(auto_close=False)
        try:
            self.browser_object.open_available_browser(url=self.dataUrl,maximized=True)
            
            try:
                try:
                    self.browser_object.wait_until_page_contains_element(CONFIG["LATimes"]["search_button"],timeout=120)
                    self.browser_object.click_element(CONFIG["LATimes"]["search_button"])
                except Exception as e:
                    logging.log(logging.ERROR,f'Page does contain element for {CONFIG["LATimes"]["search_button"]}')
                    return
                     
                logging.log(logging.DEBUG,"The search button for the webpage is clicked")

                try:
                    self.browser_object.wait_until_page_contains_element(CONFIG["LATimes"]["search_text_field"],timeout=120)
                    self.browser_object.input_text(CONFIG["LATimes"]["search_text_field"],self.dataPayload['SEARCH'])
                except Exception as e:
                    logging.log(logging.ERROR,f'Page does contain element for {CONFIG["LATimes"]["search_text_field"]}')
                    return
                
                logging.log(logging.DEBUG,"The search input for the webpage is written")
           
                self.browser_object.click_element_when_clickable(CONFIG["LATimes"]["search_submit_button"])
                logging.log(logging.DEBUG,"The search button for the webpage is clicked")

                try:
                    self.browser_object.wait_until_page_contains_element(CONFIG["LATimes"]["category_selection"],timeout=120)
                except Exception as e:
                    logging.log(logging.ERROR,f'Page does contain element for {CONFIG["LATimes"]["category_selection"]}')
                    return

                if self.browser_object.does_page_contain_element(CONFIG["LATimes"]["category_selection"]):
                    self.browser_object.select_from_list_by_label(CONFIG["LATimes"]["category_selection"],self.dataPayload['CATEGORY'])
                    self.browser_object.wait_until_page_contains_element(CONFIG["LATimes"]["news_results_open_status"],120)
                    sleep(20)             
                                                  
                data=[]
                if self.browser_object.is_list_selection(CONFIG["LATimes"]["category_selection"],self.dataPayload['CATEGORY']):
                    stop_page_scroll=False
                    while self.browser_object.does_page_contain_element(CONFIG["LATimes"]["news_next_page"]) and stop_page_scroll==False:
                        news_title=self.browser_object.get_webelements(CONFIG["LATimes"]["news_title"])
                        news_desc=self.browser_object.get_webelements(CONFIG["LATimes"]["news_data"])
                        news_date=self.browser_object.get_webelements(CONFIG["LATimes"]["news_date"])
                        
                        for x,y,z in zip(news_title,news_desc,news_date):
                            news_timeStamp=self.browser_object.get_text(z)
                            news_data_split=news_timeStamp.split()
                            month=months[news_data_split[0]]

                            if  int(self.current_date.month) - int(month) > int(self.dataPayload['MONTH']):
                                stop_page_scroll=True
                                break
                            data_dict={"title":self.browser_object.get_text(x),"desc":self.browser_object.get_text(y),"date_stamp":self.browser_object.get_text(z)}
                            data.append(data_dict)
                                            
                        self.browser_object.scroll_element_into_view(CONFIG["LATimes"]["news_next_page"])
                        self.browser_object.click_element(CONFIG["LATimes"]["news_next_page"])
                        self.browser_object.wait_until_page_contains_element(CONFIG["LATimes"]["news_results_open_status"],120)
                        sleep(15)
                
                excel_operations=Files()
                workbook=excel_operations.create_workbook(path='./output/results.xlsx',sheet_name="Sheet1")
                excel_operations.set_active_worksheet("Sheet1")
                excel_operations.append_rows_to_worksheet(data,header=True)
                excel_operations.save_workbook()
                
            except Exception as e:
                logging.log(logging.ERROR,e)
                return
        except Exception as e:
            logging.log(logging.ERROR,e)
            return
            
