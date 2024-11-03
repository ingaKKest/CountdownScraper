from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import  expected_conditions as EC
import time
import re
from selenium.webdriver import ActionChains
from selenium.common.exceptions import TimeoutException


def login(driver):
    user_email = "kelvinannan2006@gmail.com"
    user_password = "Coding123"
    log_in = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Sign in or Register')]"))
    )
    log_in.click()
    sign_in_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Sign In')]"))
    )
    sign_in_button.click()
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "emailInput"))
    )
    email = driver.find_element(By.ID, "emailInput")
    email.send_keys(user_email + Keys.ENTER)
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "password"))
    )
    password = driver.find_element(By.ID, "password")
    password.send_keys(user_password + Keys.ENTER)


def searcher(user_input, driver):
    WebDriverWait(driver, 25).until(
        EC.presence_of_element_located((By.CLASS_NAME, "inputText"))
    )

    search = driver.find_element(By.CLASS_NAME, "inputText")
    search.clear()
    search.send_keys(user_input + Keys.ENTER)
    time.sleep(0.5)


    WebDriverWait(driver, 6).until(
        EC.presence_of_element_located((By.CLASS_NAME, "ng-star-inserted"))
    )
    food_array = []

    # search by unit cost:
    time.sleep(2)
    try:
        sorter = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "select-trigger"))
        )
    except TimeoutException:
        return None
    sorter.click()

    sort_option = driver.find_element("xpath", "//li[label[text()='Unit Price Low to High']]")
    sort_option.click()

    # get more relvant searches
    relvance = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[@data-testid='select-button' and contains(@class, 'select-trigger') and .//span[contains(text(), 'Categories:')]]"))
    )
    relvance.click()
    time.sleep(2)

    button = driver.find_element(By.XPATH, "(//li[contains(@class, 'sort-option ng-star-inserted')])[2]")
    button.click()


    time.sleep(2)


    price_list = []
    food_text_list = []
    time.sleep(2.5)
    h3_elements = driver.find_elements(By.TAG_NAME, "h3")
    for h3 in h3_elements:
        if "ng-star-inserted" in h3.get_attribute("class"):
            food_text_list.append(h3)

    prices = driver.find_elements(By.XPATH, "//cdx-card")



    # Iterate over each price card
    for i in prices:
        # Check if the card contains an <h3> tag with class 'ng-star-inserted'
        h3_elements = i.find_elements(By.XPATH, ".//h3[contains(@class, 'ng-star-inserted')]")

        if h3_elements:  # Proceed only if such <h3> tags are found
            # Find all span elements containing 'kg' or 'ea' within the current card
            price_elements = i.find_elements(By.XPATH, ".//span[(contains(text(), 'g') or contains(text(), 'ea') or contains(text(), 'L')) and not(contains(@class, 'noMemberCupPrice'))]")
            for element in price_elements:
                if re.search(r'\d+', element.text):
                    element = element.text.replace("$", "")
                    if "100g" in element or "100mL" in element:
                        element = element.split(" ")[0]
                        element = float(element) * 10
                    elif "10g" in element:
                        element = element.split(" ")[0]
                        element = float(element) * 100
                    else:
                        element = element.split(" ")[0]
                    price_list.append(element)


    for food_text, price in zip(food_text_list, price_list):
        food_array.append([ food_text.text, price])

    return food_array

def add_to_cart(name, driver, quantity):
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "inputText"))
    )

    search = driver.find_element(By.CLASS_NAME, "inputText")
    search.clear()
    search.send_keys(name + Keys.ENTER)
    time.sleep(1)
    cart = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Add to trolley')]"))
    )
    driver.execute_script("arguments[0].scrollIntoView(false);", cart)

    time.sleep(2)
    while True:
        try:
            cart = driver.find_element(By.XPATH, "//button[contains(text(), 'Add to trolley')]")
            cart.click()
            break
        except Exception:
            ActionChains(driver) \
                .scroll_to_element(cart) \
                .perform()
    time.sleep(1)
    if quantity != 1:
        for i in range(quantity-1):
            quantity_increase = driver.find_element(By.CSS_SELECTOR, 'button[aria-label="Increase quantity"]')
            time.sleep(0.8)
            quantity_increase.click()




def cheapest(array):
    if not array:
        return None

    cheap = float('inf')
    cheap_item = None

    for item in array:
        if len(item) >= 2:
            try:
                price = float(item[1])
                if price < cheap:
                    cheap = price
                    cheap_item = item[0]
            except ValueError:
                continue

    return cheap_item, cheap

def user_products():
    user_product_list = []
    quantity_list = []
    print("Type -1 to stop")
    print("Type Remove to Remove Item from List")
    print("Type Meal to select from meal choices\n")
    removed = False
    while True:
        print("\n")
        user_input = input("What product are you looking for? ")
        if user_input == "-1":
            break
        elif user_input.lower() == "remove":
            found = False
            remover = input("What product would you like to remove? ")
            for i in range(len(user_product_list)):
                if remover.lower() == user_product_list[i].lower():
                    user_product_list.pop(i)
                    quantity_list.pop(i)
                    found = True
                    break
            if not found:
                print("This product is not on your list. ")
            removed = True
        elif user_input.lower() == "meal":
            meals(user_product_list, quantity_list)
            removed = True
        for i in range(len(user_product_list)):
            if user_input.lower() == user_product_list[i].lower():
                quantity_list[i] += 1
                removed = True

        if not removed:
            while True:
                try:
                    quantity = int(input("How many? "))
                    break
                except ValueError:
                    print("Please enter an integer")
            while True:
                if int(quantity) < 0 or int(quantity) > 100:
                    print("Please enter a value from 1 to 100")
                    quantity = input("How many? ")
                else:
                    break
            user_product_list.append(user_input)
            quantity_list.append(quantity)
        removed = False
        if len(user_product_list) > 0:
            print("\nYour shopping list so far: ")
        for i in range(len(user_product_list)):
            print(f"{user_product_list[i]}, Quantity: {quantity_list[i]}")
    return user_product_list, quantity_list



def meals(user_product_list, quantity_list):
    meals = {
        "Chicken and Rice": {
            "Chicken breast": "1",
            "Rice": "1",
            "Salt": "1",
            "Pepper": "1",
        },
        "Spaghetti": {
            "Pasta": "1",
            "Tomato Sauce": "1",
            "Salt": "1",
        },
        "Roast Chicken": {
            "Whole Chicken": "1",
            "Salt": "1",
            "Pepper": "1",
            "Herbs": "1",
        },
        "Burger": {
            "Ground Beef": "1",
            "Burger Bun": "1",
            "Lettuce": "1",
            "Tomato": "2",
            "Cheese": "1",
            "Ketchup": "1"
        },
        "Chicken Nuggets and Chips": {
            "Chicken Nuggets": "1",
            "Fries": "1",

        }
    }
    print("\nMeals are:")

    for all_meals in meals:
        print(all_meals)
    user_choice = None
    print("\nType Exit if you want exit")
    while user_choice != "exit":
        user_choice = input("\nPlease select a meal ")
        for meal in meals:
            if meal.lower() == user_choice.lower():
                for component, quantity in meals[meal].items():
                    for i in range(len(user_product_list)):
                        if component.lower() == user_product_list[i].lower():
                            quantity_list[i] += int(quantity)
                            break
                    else:
                        user_product_list.append(component)
                        quantity_list.append(int(quantity))
                return
        print("That meal does not exit")




def main():
    user_product_list, quantity_list = user_products()
    #user_email = input("Whats your email? ")
    #user_password = input("Whats your password? ")
    driver = webdriver.Chrome()
    driver.get("https://www.woolworths.co.nz")
    login(driver)
    for i in range(len(user_product_list)):
        prices = searcher(user_product_list[i], driver)
        if prices is not None:
            name, price = cheapest(prices)
            add_to_cart(name, driver, quantity_list[i])
    input("Press Enter to exit...")

main()


