from selenium import webdriver 
from selenium.webdriver.common.by import By
from datetime import datetime

class Transaction:
    date_format = "%m/%d/%Y"
    def __init__(self):
        self.amount: float = 0.0
        self.date: datetime.date = datetime.strptime("01/01/1997", "%m/%d/%Y") 
        self.desc: str = ""

def init_headless_driver() -> webdriver.Chrome:
    options = webdriver.ChromeOptions()
    options.accept_insecure_certs = False 
    options.headless = True # doesnt seem to actually work.. maybe try some of the below?
    # chrome_options.add_argument("--disable-extensions")
    # chrome_options.add_argument("--disable-gpu")
    # chrome_options.add_argument("--no-sandbox") # linux only
    # chrome_options.add_argument("--headless=new") # for Chrome >= 109
    # chrome_options.add_argument("--headless")
    # chrome_options.headless = True # also works
    return webdriver.Chrome(options=options)


def login_to_bofa(driver: webdriver.Chrome, username: str, passcode: str):
    driver.set_window_size(1280, 972)
    driver.get("https://www.bankofamerica.com/")
    driver.find_element(By.ID, "onlineId1").send_keys(username)
    driver.find_element(By.ID, "passcode1").send_keys(passcode)
    driver.find_element(By.ID, "signIn").submit()

    if driver.current_url == "https://secure.bankofamerica.com/login/sign-in/signOnSuccessRedirect.go":
        driver.find_element(By.ID, "btnARContinue").click()
        driver.find_element(By.CLASS_NAME, "authcode").send_keys(input())
        driver.find_element(By.ID, "yes-recognize").click()
        driver.find_element(By.ID, "continue-auth-number").click()

    if driver.current_url.startswith('https://secure.bankofamerica.com/myaccounts/'):
        print("Succeeded Logging in")
        return True
    else:
        print("Failed Logging in")
        return False

def goto_prev_transactions(driver: webdriver.Chrome) -> bool:
    for el in driver.find_elements(By.TAG_NAME, "a"):
        if el.get_attribute("name") == "goto_previous_transactions_top":
            # unsure why but just doing 'el.click()' fails here
            el.parent.find_element(By.LINK_TEXT, "Previous transactions").click()
            return True
    return False

def gather_transactions_of_month(driver: webdriver.Chrome, month: int, year: int) -> list:
    if not month in [1,2,3,4,5,6,7,8,9,10,11,12]:
        print(f"{month} is not a valid month. Grabbing all transactions - not implemented yet") #TODO: implement this..

    reached_prev_month_or_year = False
    finished = False

    transactions = []
    # for row in driver.find_elements(By.CLASS_NAME, "activity-row"):
    # transaction_elements = driver.find_elements(By.CLASS_NAME, "even").append(driver.find_elements("odd"))
    while not finished: # TODO: I hate this while.. but doing it with recursion seems.. a little gross with python not really passing anything by ref?
        transaction_elements = driver.find_elements(By.TAG_NAME, "tr")
        for row in transaction_elements:
            t = Transaction()
            col_elems = row.find_elements(By.TAG_NAME, "td")
            was_pending = False
            for col in col_elems:
                if "trans-amount-cell" in col.get_attribute("class"):
                    t.amount = float(col.text.replace(",", "").replace("$", ""))
                if "trans-date-cell" in col.get_attribute("class"):
                    if 'Pending' in col.text: # TODO: just throwing out pending transactions for the moment
                        was_pending = True
                        break
                    t.date = datetime.strptime(col.text, Transaction.date_format)
                if "trans-desc-cell" in col.get_attribute("class"):
                    t.desc = col.text.replace("\nView/Edit", "")
            if was_pending:
                continue
            # if transaction is within given month, append it, otherwise dont?
            # after for loop, check size of transactions if 0, or if a returned bool for found prev month
            # is not true, the load prev transactions
            if t.amount == 0.0: # TODO: I'm getting a number of false transactions for some reason. trying to skip them, but would be nice to know if they are just malformed.. or something else
                continue
            if t.date.month == month:
                transactions.append(t)
            elif t.date.month < month or t.date.year < year:
                print(f"Reached prev month/year with transaction amt: {t.amount} date: {t.date} desc: {t.desc}")
                reached_prev_month_or_year = True
                finished = True
                break 
            print(f"Transaction found: amt: {t.amount} date: {t.date}")
        if not reached_prev_month_or_year:
            print("Attempting to find previous transactions")
            if not goto_prev_transactions(driver): #FIXME: this isnt working.. We dont ever collect the prev transactions
                print("Successfully found prev transactions")
                finished = True
            else: 
                print("Failed to find prev transactions")
    return transactions

    

def scrape_accounts_for_month(driver: webdriver.Chrome, month: int, year: int) -> dict:
    try:
        out = {}
        for acc_element in driver.find_elements(By.CLASS_NAME, "AccountItem"):
            acc_name = acc_element.find_element(By.TAG_NAME, "a").get_attribute("innerHTML")
            acc_balance = float(acc_element.find_element(By.CLASS_NAME, "balanceValue").get_attribute("innerHTML").replace("$", "").replace(",", ""))
            print(f"Account: {acc_name} has balance: {acc_balance}")
            acc_page_url = acc_element.find_element(By.TAG_NAME, "a").get_attribute("href")
            driver.execute_script('window.open()') # this opens the tab for this specific account. need to close after use.
            driver.switch_to.window(driver.window_handles[1]) # this I think moves us to the tab we opened
            driver.get(acc_page_url)
            transactions = gather_transactions_of_month(driver, month, year)
            print(f"Found {len(transactions)} transactions in account {acc_name}")
            out[acc_name] = (acc_balance, transactions)        
            driver.execute_script('window.close()')
            driver.switch_to.window(driver.window_handles[0])
        return out
    except Exception as e:
        print(f"Failed with exception {e}")
        close_scrape(driver)


def close_scrape(driver: webdriver.Chrome): # TODO: might also be smart to click the logout button? I think closing will probably automatically logout though
    driver.execute_script('window.close()')
    driver.quit()
    
# general process is
# driver = init_headless_driver()
# login_to_bofa(driver, user, pass)
# acc_date = scrape_accounts(driver)
# close_scrape(driver)