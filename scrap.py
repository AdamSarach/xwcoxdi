import requests
import time
import random
import os
import json

from soup_manipulation import get_payload

from dotenv import load_dotenv
from selenium.webdriver import Firefox
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup
import pymongo
from pymongo import MongoClient




class ElementHasDifferentMetaDescriptionContent(object):
  """An expectation for checking that an element has a particular css class.

  locator - used to find the element
  returns the WebElement once it has the particular css class
  """
  def __init__(self, head_meta_description_content):
    self.head_meta_description_content = head_meta_description_content

  def __call__(self, driver):
    element = driver.find_element_by_xpath("//meta[@name='description']").get_attribute("content")   # Finding the referenced element
    if self.head_meta_description_content == element:
        return False
    else:
        return element


def get_target_website_html(driver):

    # Get env data
    load_dotenv()
    my_pass = os.getenv("SECRET")
    my_login = os.getenv("LOGIN")
    my_website = os.getenv("TARGET_HOST")
    tab_to_click = os.getenv("MAIN_TAB")

    # Navigate to target page
    driver.get(my_website)
    time.sleep(random.uniform(4.8, 6.9))
    login_field = driver.find_element_by_name("username")
    login_field.send_keys(my_login)
    time.sleep(random.uniform(0.7, 1.65))
    password = driver.find_element_by_name("password")
    password.send_keys(my_pass)
    password.send_keys(Keys.ENTER)
    time.sleep(random.uniform(3.8, 5.9))
    club_tab = driver.find_element_by_link_text(tab_to_click)
    club_tab.click()
    time.sleep(random.uniform(2.8, 4.9))

    meetings = []
    main_payload = {}
    head_meta_description_content = ""

    for _ in range(5):
        # Get previous page
        previous_meeting = driver.find_element_by_link_text("Previous")
        previous_meeting.click()

        # MaxRetryError - blocked long polling
        # content = driver.find_element_by_xpath("//meta[@name='description']").get_attribute("content")
        # try:
        #     # Wait until an element with "//meta[@name='description']" has different description  - to be sure previous page has been loaded
        #     wait = WebDriverWait(driver, 10)
        #     content = wait.until(ElementHasDifferentMetaDescriptionContent(head_meta_description_content))
        # finally:
        #     driver.quit()
        # print("Content before: ", head_meta_description_content)
        # head_meta_description_content = content
        # print("Content after: ", head_meta_description_content)
        # time.sleep(random.uniform(1.5, 2.5))
        time.sleep(random.uniform(3.9, 5.5))

        payload = resolve_soup_object(driver.page_source)
        
        if payload:
            meetings.append(payload)
        else:
            continue

    main_payload['meetings'] = meetings

    # Add data to mongo
    mongo = MongoOperations()
    collection = mongo.connect()
    mongo.insert_meetings(collection, main_payload)
    mongo.print_all(collection)
    return


def resolve_soup_object(html):

    soup = BeautifulSoup(html, 'html.parser')
    payload = get_payload(soup)
    return payload


def main_function():
    driver = Firefox()
    get_target_website_html(driver)
    driver.quit()


def add_to_mongo_and_show_all(payload):
    my_host = os.getenv("MONGO_HOST")
    cluster = MongoClient(my_host)
    db = cluster["pymongo_db"]
    meetings = db["meetings"]
    post1 = payload

    meetings.insert_one(post1)

    cursor = meetings.find({})
    for document in cursor:
        print(document)


class MongoOperations:

    def connect(self):
        my_host = os.getenv("MONGO_HOST")
        cluster = MongoClient(my_host)
        db = cluster["pymongo_db"]
        meetings_collection = db["meetings"]
        return meetings_collection

    def insert_meetings(self, meetings_collection, payload):
        meetings_collection.insert_one(payload)

    def clear_collection(self, meetings_collection):
        meetings_collection.drop()

    def print_all(self, meetings_collection):
        cursor = meetings_collection.find({})
        for document in cursor:
            print(document)


if __name__ == '__main__':
    main_function()





