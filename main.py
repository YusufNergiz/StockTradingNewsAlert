import ast
import os
from dotenv import load_dotenv
from twilio.http.http_client import TwilioHttpClient
from twilio.rest import Client
import requests
from datetime import date, datetime, timedelta

load_dotenv()

STOCK = "TSLA"
COMPANY_NAME = "Tesla Inc"
ALPHA_API_KEY = os.environ.get("ALPHA_API_KEY")
NEWS_API_KEY = os.environ.get("NEWS_API_KEY")
TWILIO_SID = os.environ.get("TWILIO_SD")
TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN")

parameters = {
    "function": "TIME_SERIES_DAILY_ADJUSTED",
    "symbol": "TSLA",
    "apikey": ALPHA_API_KEY
}

#####  GETS ACCESS FROM THE ALPHA API AND PUTS TSLA INFO INTO DATA  #####
response = requests.get("https://www.alphavantage.co/query", params=parameters)
response.raise_for_status()
data_for_alpha = response.json()

#####  DATE OF THE CURRENT DAY  #####
current_date = date.today()

yesterday = current_date - timedelta(days=1)
before_yesterday = current_date - timedelta(days=2)

parameters_2 = {
    "q": "Tesla",
    "from": f"{before_yesterday}",
    "sortBy": "popularity",
    "apiKey": NEWS_API_KEY
}

#####  GETS ACCESS FROM THE NEWS API  #####
response_2 = requests.get("https://newsapi.org/v2/everything", params=parameters_2)
response_2.raise_for_status()
data_for_news = response_2.json()
new_data_for_news = str(data_for_news)
data_for_news = ast.literal_eval(str(new_data_for_news))

#####  GETS THREE NEWS ABOUT TESLA FROM DAY BEFORE YESTERDAY AND PUTS IT INSIDE three_news-about_the_company LIST  #####
three_news_about_the_company = []

for news_number in range(3):
    top_3_news = data_for_news["articles"][news_number]["description"]
    three_news_about_the_company.append(f"{top_3_news}")

latest_news_about_the_company = three_news_about_the_company[0]

##### THE OPENING PRICE OF TSLA BEFORE YESTEDAY  #####
before_yesterday_stock_price = float(data_for_alpha["Time Series (Daily)"][f"{before_yesterday}"]["1. open"])

##### THE CLOSING PRICE OF YESTERDAY MARKET FOR TSLA
yesterday_stock_price = float(data_for_alpha["Time Series (Daily)"][f"{yesterday}"]["4. close"])


#####  FIGURING OUT THE DECRESE OR INCREASE PRECENTAGE  #####

difference_of_two_days = yesterday_stock_price - before_yesterday_stock_price

#####  THE FINAL PERCENTAGE DIFFERENCE  #####
# percentile_of_difference = (float(difference_of_two_days) * 100)/before_yesterday_stock_price
percentile_of_difference = 12

direction_of_price = ""
if float(percentile_of_difference) < 0 and float(percentile_of_difference) <= -5:
    direction_of_price = "🔻"
elif float(percentile_of_difference) > 0 and float(percentile_of_difference) >= 5:
    direction_of_price = "🔺"


proxy_client = TwilioHttpClient()
client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)

message = client.messages \
                .create(
                     body=f"{data_for_alpha['Meta Data']['2. Symbol']}: {direction_of_price}{round(percentile_of_difference)}%\n"
                        f"Headline: {data_for_news['articles'][0]['title']}\n"
                        f"Brief: {latest_news_about_the_company}",
                     from_='+14752514656',
                     to='+48 883 277 736'
                 )

print(message.status)



#####  IF THE STOCK PRICE INCREASED OR DECREASED BY 5% IT PRINTS THREE POPULAR NEWS ABOUT THE COMPANY  #####
if float(percentile_of_difference) < 0 and float(percentile_of_difference) <= -5:
    print(latest_news_about_the_company)
elif float(percentile_of_difference) > 0 and float(percentile_of_difference) >= 5:
    print(latest_news_about_the_company)
else:
    print("No Need For News the change in the market isn't greater than 5%")






## STEP 1: Use https://www.alphavantage.co
# When STOCK price increase/decreases by 5% between yesterday and the day before yesterday then print("Get News").

## STEP 2: Use https://newsapi.org
# Instead of printing ("Get News"), actually get the first 3 news pieces for the COMPANY_NAME. 

## STEP 3: Use https://www.twilio.com
# Send a seperate message with the percentage change and each article's title and description to your phone number. 


#Optional: Format the SMS message like this: 
"""
TSLA: 🔺2%
Headline: Were Hedge Funds Right About Piling Into Tesla Inc. (TSLA)?. 
Brief: We at Insider Monkey have gone over 821 13F filings that hedge funds and prominent investors are required to file by the SEC The 13F filings show the funds' and investors' portfolio positions as of March 31st, near the height of the coronavirus market crash.
or
"TSLA: 🔻5%
Headline: Were Hedge Funds Right About Piling Into Tesla Inc. (TSLA)?. 
Brief: We at Insider Monkey have gone over 821 13F filings that hedge funds and prominent investors are required to file by the SEC The 13F filings show the funds' and investors' portfolio positions as of March 31st, near the height of the coronavirus market crash.
"""

