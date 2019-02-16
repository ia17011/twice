import requests
from bs4 import BeautifulSoup
import csv
import time
from datetime import datetime

# 指定されたTwitterユーザー名のTweetを取得するクラス

class TweetCollector:
    __TWITTER_URL = (
        "https://twitter.com/i/profiles/show/"
        "%(user_name)s/timeline/tweets?include_available_features=1&include_entities=1"
        "%(max_position)s&reset_error_state=false"
    )

    __user_name = ""
    __tweet_data = []

    def __init__(self, user_name):
        self.__user_name = user_name

        row = [
            "ツイートID",
            "名前",
            "ユーザー名",
            "投稿日",
            "本文",
            "リツイート数",
            "いいね数"
        ]

        self.__tweet_data.append(row)

    def collectTweet(self):
        self.nextTweet(0)

    #指定されたポジションを元に次のTweetを収集する
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


        for item in items:
            row = []
            #row.append(item.get("data-item-id"))
            row.append(item.select_one(".fullname").get_text().encode("cp932", "ignore").decode("cp932"))
            row.append(item.select_one(".username").get_text())
            row.append(item.select_one("._timestamp").get_text())
            row.append(item.select_one(".js-tweet-text-container").get_text().strip().encode("cp932", "ignore").decode("cp932"))
            row.append(item.select(".ProfileTweet-actionCountForPresentation")[1].get_text())
            row.append(item.select(".ProfileTweet-actionCountForPresentation")[3].get_text())



            self.__tweet_data.append(row)

        print(str(max_position) + "← このツイートIDのヤツは取得完了したで")
        time.sleep(2)

        if res.json()["min_position"] is not None:
            self.nextTweet(res.json()["min_position"])



    def writeCSV(self):
        today = datetime.now().strftime("%Y%m%d%H%M")
        with open(self.__user_name + "-" + today + ".csv", "w") as f:
            writer = csv.writer(f, lineterminator='\n')
            writer.writerows(self.__tweet_data)

print('このCLIツールでは、入力されたアカウントのお気に入り平均以上のツイートをCSVファイルに出力するで')
inp_un = input('取得したいアカウントのIDを入力してな (@は除く) >> ')

twc = TweetCollector(inp_un)
twc.collectTweet()
twc.writeCSV()



