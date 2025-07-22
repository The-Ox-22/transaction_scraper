from chrome_bofa_scraper import login_to_bofa
from chrome_bofa_scraper import init_headless_driver
from chrome_bofa_scraper import scrape_accounts_for_month
from chrome_bofa_scraper import close_scrape
import os
from dotenv import load_dotenv
import csv 

load_dotenv()
driver = init_headless_driver()
login_to_bofa(driver, os.environ.get('BOA_USER'), os.environ.get('BOA_PASSWORD'))
input("Please enter <enter> after entering the 2FA on the site")
# TODO: Im just changing the script here dates I want for now
dates_wanted = [(3, 2025), (4, 2025), (5, 2025), (6, 2025)]
for (month, year) in dates_wanted: 
    acc_data = scrape_accounts_for_month(driver, month, year)

    print(acc_data)

    # (mc_balace, mc_transactions) = acc_data['Customized Cash Rewards World Mastercard Card - 7962']
    # print(mc_transactions[0].date)
    for (key, (mc_balance, mc_transactions)) in acc_data.items():
        print(f'{key}\nBalance: {mc_balance}')
        for t in mc_transactions:
            print(f'date: {t.date} amt: {t.amount} desc: {t.desc}')
        print('\n')

    # formatting for csv writing
    csv_list = []
    for (key, (mc_balance, mc_transactions)) in acc_data.items():
            for t in mc_transactions:
                csv_list.append([t.desc, t.amount])

    with open(f'./transactions-{month}-{year}.csv', 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerows(csv_list)

close_scrape(driver)

