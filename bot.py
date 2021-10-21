from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from datetime import datetime
from time import sleep
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions, wait
import time
import selenium
from PyQt5.QtCore import *
from random import randrange
start_time = time.time()


class Bot:
    running = False
    log_signal = None
    """Your discord account"""
    def __init__(self, email, password, url, interval, channel_id, msg):
        # Your username and password
        self.email = email
        self.password = password

        # Url of the website you want to automatically access
        self.url = url

        # other
        self.interval = interval
        self.channel_id = channel_id
        self.msg = msg

    def is_settings_valid(self):
        if not self.email or not self.password or not self.channel_id or not self.msg:
            return False
        return True
        
    def log(self, msg):
        now_time = time.time()
        elapsed_min = int( (now_time - start_time) / 60)
        dt_str = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
        output = "{}: [{} min(s)]  {}".format(dt_str, elapsed_min, msg)

        print(output)
        # write to file
        log_file = open("log.txt", "a",encoding='utf-8')
        log_file.write("{}\n".format(output))
        log_file.close()
        # generate signal
        self.log_signal.emit(output)

    def login(self):
        """Login to discord"""
        self.driver.find_element_by_name('email').send_keys(self.email)
        self.driver.find_element_by_name('password').send_keys(self.password)
        self.driver.find_element_by_name('password').send_keys(Keys.ENTER)

    def close_student_hubs_dialog(self):
        """Close Student Hubs Dialog"""
        try:
            self.driver.find_element_by_xpath('//*[@id="app-mount"]/button[@type="button"][@aria-label="Close"]').click()
            return True
        except:
            self.log('Student Hubs dialog did not appear')
            return False
    
    def close_dialog(self):
        """Close Dialog"""
        try:
            self.driver.find_element_by_xpath('//div[@role="button"][@aria-label="Close"][@tabindex="0"]').click()
            self.log('Closed dialog.')
            return True
        except Exception as e:
            self.log('Close dialog did not appear')
            return False

    def select_channel(self, id):
        """Select channel to send message"""
        while True:
            try:
                url = "https://discord.com" + id
                self.driver.get(url)
                sleep(3)
                break
            except:
                continue      

    def check_too_many(self):
        text = "You are sending too many new direct messages."
        if text in self.driver.page_source:
            self.log("Too many messages: sleeping for 2.5 mins")
            sleep(150)
        
    def send_message(self):
        """Send messages one by one"""
        # Driver of the browser you use
        self.driver = webdriver.Chrome("chromedriver.exe")
        self.browse = self.driver.get(self.url)
        # start log
        self.log("Bot started ...")
        # Login to discord
        self.login()
        sleep(5)

        # Close student hubs dialog
        if self.close_student_hubs_dialog():
            sleep(5)
        
        # aside_tag = self.driver.find_element_by_xpath('//aside')
        # aside_height = aside_tag.size['height']
        # log('aside height', aside_height)


        # list_container = self.driver.find_element_by_xpath('//aside/div/div')
        # list_height = list_container.size["height"]
        # log('height:', list_height)

        # some settings
        FINISH_COUNT = 300
        
        visited_members = [] # list of already visited memebrs
        previous_time = 0 # previous sent time
        total_sent = 0
        finish_counter = FINISH_COUNT
        scroll_downed = False # if scroll downed?
        while self.running:
            # select channel first
            if not scroll_downed: # if scroll downed, do not refresh channel
                self.select_channel(self.channel_id)
            scroll_downed = False
            self.log("[Finding members]")
            try:
                timestamp = WebDriverWait(self.driver, 60).until(expected_conditions.presence_of_element_located((By.XPATH, '//aside/div/div/div[@role="listitem"]')))
                sleep(1)
            except:
                sleep(60)
                self.log("Finding members failed.")
                continue
            # members count
            members = self.driver.find_elements_by_xpath('//aside/div/div/div[@role="listitem"]')
            members_count = len(members)

            sent_message = False
            new_member_clicked = False # sent message to a new member ?
            # find member to send message
            new_member = None
            new_member_id = None
            for member in members:
                try:
                    member_id = member.find_element_by_xpath(".//div/div[2]/div[1]").text.replace("\n", " ")
                except:
                    break # if not mounted yet, skip

                if member_id in visited_members:
                    continue
                new_member = member
                new_member_id = member_id
                break
        
            # click member && send message
            try:
                if new_member.is_displayed():
                    self.log('[clicking {}]'.format(new_member_id) )
                    try:
                        new_member.click()
                    except selenium.common.exceptions.ElementClickInterceptedException as e:
                        continue

                    self.log('clicked {}'.format(new_member_id) )
                    visited_members.append(new_member_id)
                    self.log('[Finding message box input]')
                    timestamp = WebDriverWait(self.driver, 30).until(expected_conditions.presence_of_element_located((By.XPATH, '//input[@maxlength="999"]')))
                    self.log('Found message box input')

                    new_member_clicked = True # visited a new member
                    #check time
                    cur_time = time.time()
                    wait_time = (self.interval  - (cur_time - previous_time)) /2 # wait 3 part
                    if wait_time <= 0: 
                        wait_time = 0.5 
                    # #input text

                    chat_input = self.driver.find_element_by_xpath('//input[@maxlength="999"]')
                    chat_input.send_keys(self.msg + "\n")
                    time.sleep(wait_time)

                    # # press enter
                    time.sleep(wait_time)
                    total_sent += 1
                    self.log('Sent message to {}   (Total: {})'.format(new_member_id, total_sent) )
                    previous_time = time.time()
                    # check if too many messages
                    self.check_too_many()
            except Exception as e:
                self.log('Could not send message:{}'.format(str(e)))
                # if there is dialog, for example server boost , close it
                if self.close_dialog():
                    sleep(5)
                    continue # no need to finish or scroll down
            
            
            if not new_member_clicked:

                finish_counter -= 1
                if finish_counter == 4:
                    a = 5
                # check if finish
                if finish_counter == 0:
                    self.log("Finished sending message.")
                    self.running = False
                # scroll down
                try:
                    self.log("Members count: {}".format(members_count))
                    middle = int(members_count * 0.7) + randrange(3)
                    if 0< members_count - 4 < middle:
                        middle = members_count - 4
                    middle_id = members[middle].find_element_by_xpath(".//div/div[2]/div[1]").text.replace("\n", " ")
                    self.log("[Finish counter: {}, Scroll downing to {}]".format(finish_counter, middle_id))
                    self.driver.execute_script('arguments[0].scrollIntoView(true);', members[middle])
                    self.log('Scroll down success.' )
                    scroll_downed = True
                    sleep(2)
                except Exception as e:
                    self.log('Scroll down failed: {}'.format(str(e)))
            else:
                finish_counter = FINISH_COUNT
        # close driver
        self.driver.close()


            

  