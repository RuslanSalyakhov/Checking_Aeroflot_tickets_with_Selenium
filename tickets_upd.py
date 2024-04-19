#!/usr/bin/python3.6
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup

from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from datetime import datetime
import requests
from argparse import ArgumentParser

# Token for bot authentication
TOKEN = "Some Telegram token"

# Chat ID
chat_id = "Some Telegram chat ID"

# If tickets for asked dates and below the price threshold found send_message function sends a message to the Telegram chat
def send_message(message):

    mes = ''

    if len(message) == 0:
        return 1
    elif len(message) == 1:
        # Extract the element from the list
        message = message[0]
        mes = f"Найден билет c ценой {message['price']}. \nДата: {message['day']} - {message['number']}"
    else:
        mes = ''
        for i in message:
            mes +=  f"\nНайден билет c ценой {i['price']}. \nДата: {i['day']} - {i['number']}\n"
    mes = "Билеты во Владивосток!\n" + mes + "https://www.aeroflot.ru/sb/subsidized/app/ru-ru#/search?_k=4l6mmq"
    # Url to connect to Telegram bot
    #url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
    #print(requests.get(url).json())
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={chat_id}&text={mes}"

    print(requests.get(url).json()) # this sends the message
    return 0

def get_range_dates(start_date_str: str, end_date_str: str):

    # Convert start and end dates to datetime objects
    start_date = datetime.strptime(start_date_str, "%d.%m.%Y")
    end_date = datetime.strptime(end_date_str, "%d.%m.%Y")

    # Initialize an empty list to store the dates
    date_list = []

    # Iterate over the range of dates and append each date to the list
    current_date = start_date
    while current_date <= end_date:
        date_list.append(current_date.strftime("%d.%m.%Y"))
        current_date += timedelta(days=1)

    # Print the list of dates
    print(date_list)
    return date_list
  
# get_cheap_tickets using as an input Beatiful soup's parser output and price threshold 
# returning the list with nested dicts where the price is stricly below the threshold
def get_cheap_tickets(soup, threshold, range_flag = False):

    # Initialize empty tickets list
    tickets = []
    
    if not range_flag:
        # Use Beatiful soup parsed page to get tickets info
        items =  soup.find_all("div", attrs={"class":"price-chart__item"})
        
        # Iterate over tickets info list checking the tickets with prices lower than a threshold
        for i in items:
            price = i.find("div", class_='price-chart__item-price')
            day = i.find("div", class_='price-chart__item-day')
            number = i.find("div", class_='price-chart__item-number')
            if float(price.text.strip("i ")) < threshold:
                tickets.append({'number': number.text, 'day': day.text, 'price': float(price.text.strip("i "))})
            print(f'{number.text} : {day.text} : {price.text.strip("i ")}')
            
        return tickets
    
    elif range_flag:
        i = soup.find("div", attrs={"class":"price-chart__item price-chart__item--active"})
        
        price = i.find("div", class_='price-chart__item-price')
        day = i.find("div", class_='price-chart__item-day')
        number = i.find("div", class_='price-chart__item-number')
        
        if float(price.text.strip("i ")) < threshold:
            tickets = ({'number': number.text, 'day': day.text, 'price': float(price.text.strip("i "))})
        print(f'{number.text} : {day.text} : {price.text.strip("i ")}')
        
        return tickets
            
        
# check_tickets function checks tickets for specific date and strictly below the specific price threshhold
def check_tickets(date= '23.05.2024', threshold = 15000, from_city = 'Санкт-Петербург', to_city = 'Владивосток', end_date = ''):
    # For Google Chrome webdriver
    #driver = webdriver.Chrome(executable_path=r"C:\Users\seymo\Documents\chromium\chromedriver.exe")
    # Starting from Selenium version Selenium 4.6 or greater
    #service = webdriver.ChromeService(executable_path=r"C:\Users\seymo\Documents\chromium\chromedriver.exe")
    #driver = webdriver.Chrome(service=service)
    
    # Define driver we are going to use. Chrome executable location should be added in the variable Path
    driver = webdriver.Firefox()

    # Url of page to check tickets
    url = "https://www.aeroflot.ru/sb/subsidized/app/ru-ru#/search?_k=b6hc4k"

    # Open URL
    driver.get(url)

    # The pop up window confirm location can appear so for first we are going to wait of it 5 seconds
    wait = WebDriverWait(driver, 20)
    element = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '.button.button--wide.js-notification-close')))

    # If pop up appeared and button is clickable the element will be returned as True so we can proceed with
    if element:
        confirm_geo_button = driver.find_element(By.CSS_SELECTOR, ".button.button.button--wide.js-notification-close")
        confirm_geo_button.click()

    # Waiting for subsidized program dropdown list appear to click on it
    try:
        # Wait till the required element is clickable on the page
        element = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="root"]/div/div/div/div/div[2]/div/section[1]/div/div[2]/button')))

    except NoSuchElementException:
        print("Loading page took too much time!")
    # Find and click on element for opening a list of subsidized programs
    subsidized_program = driver.find_element(By.XPATH, '//*[@id="root"]/div/div/div/div/div[2]/div/section[1]/div/div[2]/button')
    subsidized_program.click()

    # Find and click the button for required program
    dv_button = driver.find_element(By.CSS_SELECTOR, ".button.button--clear.h-align--left")
    dv_button.click()

    # Enter origin location
    source = driver.find_element(By.XPATH, '//*[@placeholder="Откуда"]')
    source.clear()
    source.send_keys(from_city)
    source.send_keys(Keys.ENTER)

    # Enter destination place

    target = driver.find_element(By.XPATH, '//*[@placeholder="Куда"]')
    target.clear()
    target.send_keys(to_city)
    target.send_keys(Keys.ENTER)

    # Select class  and the number of tickets
    select_class = driver.find_element(By.XPATH, '//*[@id="select_classsearch-form-1"]')
    select_class.click()
    select_button = driver.find_element(By.XPATH, '//*[@id="select-passangers"]/div/div/div[1]/div/div/div[2]/input')
    select_button.clear()
    select_button.send_keys("1")

    # Close class selection window
    close_button = driver.find_element(By.XPATH, '//*[@id="select-passangers"]/div/div/a')
    close_button.click()
    
    if len(end_date) == 0:
    
        # Enter date of the trip
        from_date = driver.find_element(By.XPATH, '//*[@id="root"]/div/div/div/div/div[2]/div/section[1]/div/div[3]/form/fieldset/div[1]/div[3]/div/div/div/input')
        from_date.clear()
        from_date.send_keys(date)
        from_date.send_keys(Keys.ENTER)

        # Click on Find button
        find_tickets = driver.find_element(By.CSS_SELECTOR, ".button.button--wide.button--lg")
        #find_tickets = driver.find_element(By.XPATH, '//*[@id="root"]/div/div/div/div/div[2]/div/section[1]/div/div[3]/form/fieldset/div[2]/div[3]/button')
        find_tickets.click()

        try:
            # Wait till tickets info downloaded by checking if the element button is clickable
            found_items = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="chart-week-4"]/div[5]/div')))
        except NoSuchElementException:
            print("Cannot click on date element and extract data!")
        
        # Parse a page using BeatifulSoup saving output to the variable
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        # Get tickets with price lower than a threshold
        tickets = get_cheap_tickets(soup, threshold)
            
    else:
        # Locate date of the trip button
        from_date = driver.find_element(By.XPATH, '//*[@id="root"]/div/div/div/div/div[2]/div/section[1]/div/div[3]/form/fieldset/div[1]/div[3]/div/div/div/input')
        
        # Locate Find button
        find_tickets = driver.find_element(By.CSS_SELECTOR, ".button.button--wide.button--lg")
        
        # Convert range of dates to the list 
        range_dates = get_range_dates(date, end_date)
        
        # Initialize a variable to keep tickets with price below threshold for the range of dates
        tickets = []
        
        for d in range_dates:
            print(d)
            #from_date = driver.find_element(By.XPATH, '//*[@id="root"]/div/div/div/div/div[2]/div/section[1]/div/div[3]/form/fieldset/div[1]/div[3]/div/div/div/input')
            from_date.clear()
            from_date.send_keys(Keys.CONTROL + "a")
            from_date.send_keys(Keys.DELETE)
            # Enter date of the trip
            from_date.send_keys(d)
            from_date.send_keys(Keys.ENTER)
            
            # Click on Find button
            find_tickets.click()
            #time.sleep(5)
            
            try:
            # Wait till tickets info downloaded by checking if the element button is clickable
                found_item = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, ".button.button--wide.button--lg")))
            except NoSuchElementException:
                print("Cannot click on Find element and extract data!")
            
            # Parse a page using BeatifulSoup saving output to the variable
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            
            # Get tickets with price lower than a threshold
            ticket = get_cheap_tickets(soup, threshold, range_flag = True)
            
            
            if len(ticket) > 0:
                
                # Append the ticket to the tickets list
                tickets.append(ticket)                
                


    if len(tickets) == 0:

        print(f"\nNO TICKETS FOUND with price lower than limit -  {threshold} !")
        # Wait 10 seconds before closing driver
        time.sleep(10)
        driver.quit()

        return False

    else:
        print(f"\nget_cheap_tickets() output: {tickets} \n")
        # Send tickets to Telegram
        send_message(tickets)

        # Wait 10 seconds before closing driver
        time.sleep(10)
        driver.quit()

        return True

    # default quit driver statement
    driver.quit()

# Define entry point for the script
if __name__ == "__main__":

    # Init object of ArgumentParser class
    parser = ArgumentParser()

    # Add argument for flight date
    parser.add_argument('from_date', type=str, help='Ticket date in the format: DD.MM.YYYY; i.e 11.08.2023')

    # Add argument for ticket price limit. So the script will be looking for tickets with price lower than limit
    parser.add_argument('limit', type=float, help='The price limit for ticket in format: 20000; any number')

    # Add argument for city of departure
    parser.add_argument('from_city', type=str, help='The departure city')

    # Add argument for destination city
    parser.add_argument('to_city', type=str, help='The destination city')

    # Add argument for the end date of date range
    parser.add_argument('end_date', type=str, help='The end date of the date range in the format: DD.MM.YYYY; i.e 20.08.2023')

    args = parser.parse_args()

    # Initiate a counter
    count = 0

    # Setup a flag for triggering while loop
    run_flag = True
    while run_flag:
        print(f"\nRunning script for date: {args.from_date} ; price limit: {args.limit} - timestamp: {datetime.now()}")
        return_flag = check_tickets(date=args.from_date, threshold=args.limit, from_city=args.from_city, to_city=args.to_city)

        # Sleep 600 seconds - 10 minutes till next run.
        time.sleep(600)

        if return_flag:
            # Setup counter to count number of send notifications via Telegram bot
            count += 1

            # Counter will be counting up to 10 before stoping the script
            if count == 10:
                # Break the loop
                break
