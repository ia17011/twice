import requests
from bs4 import BeautifulSoup
import csv
import time
from datetime import datetime


class TweetCollector:
    __TWITTER_URL = (
        "https://twitter.com/i/profiles/show/"
        "%(user_name)s/timeline/tweets?include_available_features=1&include_entities=1"
        "%(max_position)s&reset_error_state=false"
    )

    __user_name = ""
    __tweet_data = []

    __fav_sum = 0
    __avg = 0


    def __init__(self, user_name):
        self.__user_name = user_name

    def collectTweet(self):
        self.nextTweet(0)

    def nextTweet(self, max_position):
        if max_position == 0:
            param_position = ""
        else:
            param_position = "&max_position=" + max_position

        url = self.__TWITTER_URL % {
            'user_name': self.__user_name,
            'max_position': param_position
        }

        res = requests.get(url)
        soup = BeautifulSoup(res.json()["items_html"], "html.parser")

        items = soup.select(".js-stream-item")
        at_name = "@" + self.__user_name

        for item in items:
            row = []
            row.append(item.select_one(".fullname").get_text().encode("cp932", "ignore").decode("cp932"))
            row.append(item.select_one(".username").get_text())
            row.append(item.select_one("._timestamp").get_text())
            row.append(item.select_one(".js-tweet-text-container").get_text().strip().encode("cp932", "ignore").decode("cp932"))
            if item.select(".ProfileTweet-actionCountForPresentation")[1].get_text():
                rt = item.select(".ProfileTweet-actionCountForPresentation")[1].get_text()
                rt = rt.replace(',', '')
                row.append(int(rt))
            else:
                row.append(0)

            if item.select(".ProfileTweet-actionCountForPresentation")[3].get_text():
                favo = item.select(".ProfileTweet-actionCountForPresentation")[3].get_text()
                favo = favo.replace(',', '')
                row.append(int(favo))
            else:
                row.append(0)

            if row[1] == at_name:
                self.__fav_sum += row[5]
                self.__tweet_data.append(row)
            else:
                continue

        print(str(max_position) + "← このツイートIDのヤツは取得完了したで")
        time.sleep(2)

        if res.json()["min_position"] is not None:
            self.nextTweet(res.json()["min_position"])

    def just_high_avg(self):
        self.__avg = round(self.__fav_sum / len(self.__tweet_data))
        print(self.__avg)
        for item in self.__tweet_data:
            try:
                if self.__avg >= item[5]:
                    item.clear()
                else:
                    continue
            except:
                pass
        self.__tweet_data = [x for x in self.__tweet_data if x]

    def writeCSV(self):
        today = datetime.now().strftime("%Y%m%d%H%M")
        with open(self.__user_name + "-" + today + ".csv", "w") as f:
            writer = csv.writer(f, lineterminator='\n')
            writer.writerows(self.__tweet_data)


print('このCLIツールでは、入力されたアカウントのお気に入り平均以上のツイートをCSVファイルに出力するで')
inp_un = input('取得したいアカウントのIDを入力してな (@は除く) >> ')
print('ちょっとだけ時間かかるから、トイレでも行ってき〜')

twc = TweetCollector(inp_un)
twc.collectTweet()
twc.just_high_avg()
twc.writeCSV()
print('CSVに書き込んだからチェックしてな')
