#!/usr/bin/python3.6
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup

from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from datetime import datetime, timedelta
import requests
from argparse import ArgumentParser

# Token for bot authentication
TOKEN = "Some Telegram token"

# Chat ID
chat_id = "Some Telegram chat ID"

# If tickets for asked dates and below the price threshold found send_message function sends a message to the Telegram chat
def send_message(message: list, to_city: str):

    mes = ''

    if len(message) == 0:
        return 1
    elif len(message) == 1:
        # Extract the element from the list
        message = message[0]
        mes = f"Найден билет c ценой {message['price']} \nДата: {message['day']} - {message['number']} \nВремя вылета: {message['depart_time']} \n"
    else:
        mes = 'Найдены билеты: \n'
        for i in message:
            mes +=  f"\nЦена: {i['price']} \nДата: {i['day']} - {i['number']}  \nВремя вылета: {i['depart_time']} \n"
    mes = f"Билеты в {str(to_city)}!\n" + mes + "https://www.aeroflot.ru/sb/subsidized/app/ru-ru#/search?_k=4l6mmq"
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
def get_cheap_tickets(soup, threshold):

    # Initialize empty tickets list
    tickets = []
    
    i = soup.find("div", attrs={"class":"price-chart__item price-chart__item--active"})
    if i == None:
        return tickets
    else:
        price = i.find("div", class_='price-chart__item-price')
        day = i.find("div", class_='price-chart__item-day')
        number = i.find("div", class_='price-chart__item-number')

        if price is None or day is None or number is None:
            print(f"None values found for price, day or number variables!!! price - {price}, day - {day}, number - {number}")
            return tickets

        elif float(price.text.strip("i ")) < threshold:
            # Find tickets' elements with class 'row flight-search__inner'
            locate_ticket_box = soup.find_all("div", attrs={"class":"row flight-search__inner"})
            #div_elements = soup.find_all("div", attrs={"class": "time-destination__from"})
            
            if locate_ticket_box:
                # Since we can have multiple tickets for the same date with price lower than a threshold we track the sequence number of each ticket
                ticket_seq = 0
                for t in locate_ticket_box:
                    price_t = t.find("div", attrs={"class":"flight-search__price-text"})
                    price_t = float(price_t.text.strip("i "))
                    
                    depart_t = t.find("span", attrs={"class": "time-destination__time"})
                    
                    if price_t and depart_t and (price_t < threshold):
                        
                        tickets.append({'number': number.text, 'day': day.text, 'price': price_t, 'depart_time': depart_t.text, 'ticket_sequence': ticket_seq})   
                     
                    print(f'{number.text} : {day.text} : {price_t} : {depart_t.text} : ord - {ticket_seq}')
                    ticket_seq += 1

        return tickets
                    
# check_tickets function checks tickets for specific date and strictly below the specific price threshhold
def check_tickets(date= '23.05.2024', threshold = 15000, from_city = 'Санкт-Петербург', to_city = 'Владивосток', end_date = '', depart_time = ''):
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

    # The pop up window confirm location can appear so for first we are going to wait for 30 seconds
    wait = WebDriverWait(driver, 60)
    try:
        element = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button.button.button--wide.js-notification-close')))
    
    except: 
        print("Confirm location window didn't appear!")
        element = None
        
    # If pop up appeared and button is clickable the element will be returned as True so we can proceed with
    if element:
        confirm_geo_button = driver.find_element(By.CSS_SELECTOR, ".button.button.button--wide.js-notification-close")
        confirm_geo_button.click()

    # Waiting for subsidized program dropdown list appear to click on it
    try:
        # Wait till the required element is clickable on the page
        element = WebDriverWait(driver, 60).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="root"]/div/div/div/div/div[2]/div/section[1]/div/div[2]/button')))

    except:
        print("Loading page took too much time!")
        
    # Find and click on element for opening a list of subsidized programs
    try:
        # Wait till the required element is clickable on the page
        subsidized_program = WebDriverWait(driver, 60).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="root"]/div/div/div/div/div[2]/div/section[1]/div/div[2]/button')))
        subsidized_program.click()
        
    except:
        print("The subsidized programs loading took too much time!")
        print("Quiting the driver...")
        driver.quit()
        return None
        
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
            found_items = WebDriverWait(driver, 30).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="chart-week-4"]/div[5]/div')))
        except:
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
            
            soup_found = False
            try:
            # Wait till tickets info downloaded by checking if the element button is clickable
                while not soup_found:
                    found_item = WebDriverWait(driver, 30).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, ".button.button--wide.button--lg")))
                    
                    # Parse a page using BeatifulSoup saving output to the variable
                    soup = BeautifulSoup(driver.page_source, 'html.parser')
                    
                    # Checking if we can find price info for the active element
                    soup_check = soup.find("div", attrs={"class":"price-chart__item price-chart__item--active"})

                    if soup_check == None:
                        # Click on Find button
                        find_tickets.click()
                    else:
                        soup_found = True
                
            except:
                print("Cannot click on Find element and extract data!")
            time.sleep(4)
            # Parse a page using BeatifulSoup saving output to the variable
            soup = BeautifulSoup(driver.page_source, 'html.parser')

            soup_found = soup.find("div", attrs={"class":"price-chart__item price-chart__item--active"})
            
            # Get tickets with price lower than a threshold
            ticket = get_cheap_tickets(soup, threshold)
            
            
            if len(ticket) >= 1:
                # Extend the ticket if there are more than one element in the ticket list
                tickets.extend(ticket)  

    if len(tickets) == 0:

        print(f"\nNO TICKETS FOUND with price lower than limit -  {threshold} !")
        # Wait 10 seconds before closing driver
        time.sleep(10)
        driver.quit()

        return False

    else:
        print(f"\nget_cheap_tickets() output: {tickets} \n")
        # Send tickets to Telegram
        send_message(tickets, to_city)

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
    #parser.add_argument('end_date', type=str, help='The end date of the date range in the format: DD.MM.YYYY; i.e 20.08.2023')

    # Add optional positional argument for the end date of date range
    parser.add_argument('end_date', type=str, nargs='?', default='', help='The end date of the date range in the format: DD.MM.YYYY; i.e 20.08.2023 (optional)')

    # Add optional argument for the flight departure time
    parser.add_argument('--depart_time', type=int, default='', help='The flight departure time (default: '')')

    args = parser.parse_args()

    # Initiate a counter
    count = 0

    # Setup a flag for triggering while loop
    run_flag = True
    while run_flag:
        print(f"\nRunning script for date: {args.from_date} ; price limit: {args.limit} - timestamp: {datetime.now()}")

        return_flag = None
        try:
            return_flag = check_tickets(date=args.from_date, threshold=args.limit, from_city=args.from_city, to_city=args.to_city, end_date=args.end_date, depart_time = args.depart_time)
            
        except Exception as e:
            print("Error during return_flag function execution occurred! - ", e)
            # Wait for 10 seconds 
            print("Repeat to run the check_tickets function in 10 seconds")
            time.sleep(10)
        
        if return_flag:
            # Setup counter to count number of send notifications via Telegram bot
            count += 1
            
            # Counter will be counting up to 10 before stoping the script
            if count == 10:
                # Break the loop
                break
        elif return_flag == None:
            continue
        # Reset count when a value of return_flag is false         
        elif return_flag == False:
            count = 0
            
        # Sleep 300 seconds - 5 minutes till next run.
        time.sleep(300)
