import requests
import json
import datetime

BOT_TOKAN = "your token"
BOT_UPDATE_API = f"https://api.telegram.org/bot{BOT_TOKAN}/getUpdates"
BOT_MESSAGE_API = f"https://api.telegram.org/bot{BOT_TOKAN}/sendMessage"
AV_API_key = "X98Y79TAZLIF3FAF"
AV_API_ENDPOINT = "https://www.alphavantage.co/query"
NEWS_API_KEY = "your key"
NEWS_API_ENDPOINT = "https://newsapi.org/v2/everything"


while True:

    bot_responce = requests.get(BOT_UPDATE_API)
    bot_responce.raise_for_status()
    update_deta = bot_responce.json()["result"][-1]
    message = update_deta["message"]["text"]
    message_id = update_deta["message"]["message_id"]
    from_id = update_deta["message"]["from"]["id"]
    from_name = update_deta["message"]["from"]["first_name"]
    try:
        is_commond = update_deta["message"]["entities"][-1]["type"]
    except KeyError:
        is_commond = ""
    try:
        with open("./messageid.txt","r") as messageid:
            mes_no = messageid.read()

        with open("./messageid.txt","w") as messageid:
            messageid.write(f"{message_id}")

    except FileNotFoundError:
        mes_no = message_id
        with open("./messageid.txt","w") as messageid:
            messageid.write(f"{message_id}")
    if int(message_id) > int(mes_no):

        if (is_commond == "bot_command") and (message == "/start"):
            gretings = f'''Hii..! {from_name},
            welcome to Stocks
            here you can find update of any stocks
            get started send the "NAME" of stock
            For Indian stocks use the key word "nse:"
            eg: "bse:sbin" 
            eg: ibm
            '''
            gretings_param = {
                "chat_id":from_id,
                "text":gretings
            }
            requests.get(BOT_MESSAGE_API,params=gretings_param)

        elif is_commond != "bot_command":
            options = '''
            To get minute data- /now
            To get daily data- /day
            to get weekly data- /week
            to get news - /news
            '''
            options_params = {
                "chat_id": from_id,
                "text": options
            }
            requests.get(BOT_MESSAGE_API,params=options_params)
            user_data = {
                from_id:{
                    "user_name": from_name,
                    "user_request": message
                }
            }
            try:
                with open("./user_data.json","r") as json_file:
                    temp = json.load(json_file)
                    temp[from_id] = user_data[from_id]
                with open("./user_data.json", "w") as json_file:
                    json_object = json.dumps(temp)
                    json_file.write(json_object)

            except FileNotFoundError:
                json_object = json.dumps(user_data)
                with open("./user_data.json","w") as json_file:
                    json_file.write(json_object)

        elif (is_commond == "bot_command") and (message == "/day"):
            with open("./user_data.json", "r") as json_file:
                user_request = json.load(json_file)[f"{from_id}"]['user_request']
            day_param = {
                "function":"TIME_SERIES_DAILY",
                "symbol":user_request,
                "apikey":AV_API_key
            }
            request_responce = requests.get(AV_API_ENDPOINT,params=day_param)
            request_responce.raise_for_status()
            request_data = request_responce.json()
            try:
                last_refreshed = request_data["Meta Data"]["3. Last Refreshed"]
                time_zone = request_data["Meta Data"]["5. Time Zone"]
                day_data = request_data["Time Series (Daily)"][f"{last_refreshed}"]
                day_open = day_data["1. open"]
                day_close = day_data["4. close"]
                day_high = day_data["2. high"]
                day_low = day_data["3. low"]
                difference = float(day_open)-float(day_close)
                final_day_output = f'''
                {user_request}:
                Last Refreshed : {last_refreshed}
                     Time Zone : {time_zone}
                          Open : {day_open}
                         Close : {day_close}
                          High : {day_high}
                           Low : {day_low}
                   fluctuation : {difference}
                '''
                final_day_output_params = {
                    "chat_id": from_id,
                    "text": final_day_output
                }
                requests.get(BOT_MESSAGE_API, params=final_day_output_params)
            except KeyError:
                final_day_output_params = {
                    "chat_id": from_id,
                    "text": "invalid name of name of the equity of your choice\nMarket may be close now try /day or /week\n Use bse for Indian market eg: bse:sbin\neg:ibm"
                }
                requests.get(BOT_MESSAGE_API, params=final_day_output_params)

        elif (is_commond == "bot_command") and (message == "/week"):
            with open("./user_data.json", "r") as json_file:
                user_request = json.load(json_file)[f"{from_id}"]['user_request']

            today = datetime.date.today()
            idx = (today.weekday() + 1) % 7
            sat = today - datetime.timedelta(7 + idx - 5)

            week_param = {
                "function":"TIME_SERIES_WEEKLY",
                "symbol":user_request,
                "apikey":AV_API_key
            }
            request_responce = requests.get(AV_API_ENDPOINT,params=week_param)
            request_responce.raise_for_status()
            request_data = request_responce.json()
            try:
                last_refreshed = request_data["Meta Data"]["3. Last Refreshed"]
                time_zone = request_data["Meta Data"]["4. Time Zone"]
                week_data = request_data["Weekly Time Series"][f"{sat}"]
                week_open = week_data["1. open"]
                week_close = week_data["4. close"]
                week_high = week_data["2. high"]
                week_low = week_data["3. low"]
                difference = float(week_open)-float(week_close)
                final_week_output = f'''
                {user_request}:
                Last Refreshed : {sat}
                     Time Zone : {time_zone}
                          Open : {week_open}
                         Close : {week_close}
                          High : {week_high}
                           Low : {week_low}
                   fluctuation : {difference}
                '''
                final_week_output_params = {
                    "chat_id": from_id,
                    "text": final_week_output
                }
                requests.get(BOT_MESSAGE_API, params=final_week_output_params)
            except KeyError:
                final_week_output_params = {
                    "chat_id": from_id,
                    "text": "invalid name of name of the equity of your choice\nMarket may be close now try /day or /week\n Use bse for Indian market eg: bse:sbin\neg:ibm"
                }
                requests.get(BOT_MESSAGE_API, params=final_week_output_params)


        elif (is_commond == "bot_command") and (message == "/now"):
            with open("./user_data.json", "r") as json_file:
                user_request = json.load(json_file)[f"{from_id}"]['user_request']


            min_param = {
                "function":"TIME_SERIES_INTRADAY",
                "symbol":user_request,
                "apikey":AV_API_key,
                "interval":"1min"
            }
            request_responce = requests.get(AV_API_ENDPOINT,params=min_param)
            request_responce.raise_for_status()
            request_data = request_responce.json()
            try:
                last_refreshed = request_data["Meta Data"]["3. Last Refreshed"]
                time_zone = request_data["Meta Data"]["6. Time Zone"]
                interval = request_data["Meta Data"]["4. Interval"]
                min_data = request_data["Time Series (1min)"][f"{last_refreshed}"]
                min_open = min_data["1. open"]
                min_close = min_data["4. close"]
                min_high = min_data["2. high"]
                min_low = min_data["3. low"]
                difference = float(min_open)-float(min_close)
                final_min_output = f'''
                {user_request}:
                Last Refreshed : {last_refreshed}
                      Interval : 5sec
                     Time Zone : {time_zone}
                          Open : {min_open}
                         Close : {min_close}
                          High : {min_high}
                           Low : {min_low}
                   fluctuation : {difference}
                '''
                final_min_output_params = {
                    "chat_id": from_id,
                    "text": final_min_output
                }
                requests.get(BOT_MESSAGE_API, params=final_min_output_params)
            except KeyError:
                final_week_output_params = {
                    "chat_id": from_id,
                    "text": "invalid name of name of the equity of your choice\nMarket may be close now try /day or /week\n Use bse for Indian market eg: bse:sbin\neg:ibm"
                }
                requests.get(BOT_MESSAGE_API, params=final_week_output_params)

        elif (is_commond == "bot_command") and (message == "/news"):
            with open("./user_data.json", "r") as json_file:
                user_request = json.load(json_file)[f"{from_id}"]['user_request']

            today = datetime.date.today()
  
            news_params = {
                "q":user_request,
                "from":f"{today}",
                "sortBy":"popularity",
                "apiKey":NEWS_API_KEY
            }
            try:
              news_responce = requests.get(NEWS_API_ENDPOINT,params=news_params)
              news_responce.raise_for_status()
              no_artical = len(news_responce.json()['articles'])
              
              if no_artical>=5:
                news_data=news_responce.json()['articles'][:6]

                for i in news_data:
                    author = i["author"]
                    title = i["title"]
                    description = i["description"]
                    content = i["content"]
                    link = i["url"]

                    final_news_output = f'''
                    {user_request}:
                    author:
                    {author}
                    Title:
                    {title}

                    Description:
                    {description}

                    Content:
                    {content}

                    Read More:
                    {link}
                        '''

                    final_news_param = {
                      "chat_id": from_id,
                      "text": final_news_output

                    }
          
                    news_responce=requests.get(BOT_MESSAGE_API, params=final_news_param)
                    news_responce.raise_for_status()

              else:
                for i in news_responce.json()['articles']:
                    author = i["author"]
                    title = i["title"]
                    description = i["description"]
                    content = i["content"]
                    link = i["url"]

                    final_news_output = f'''
                    {user_request}:
                    author:{author}
                    Title:
                    {title}

                    Description:
                    {description}

                    Content:
                    {content}

                    Read More:
                    {link}
                        '''

                    news_param = {
                      "chat_id": from_id,
                      "text": final_news_output

                    }
                    requests.get(BOT_MESSAGE_API, params=news_params)
                
            except KeyError:
                final_week_output_params = {
                    "chat_id": from_id,
                    "text": "invalid name of name of the equity of your choice\neg:ibm"
                }
                requests.get(BOT_MESSAGE_API, params=final_week_output_params)
    else:
        pass
