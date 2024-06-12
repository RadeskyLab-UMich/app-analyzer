import requests
from bs4 import BeautifulSoup
import pandas as pd

class GoogleApp:
    def __init__(self, id):
        self.id = id
        self.url = requests.get(f"https://play.google.com/store/apps/details?id={self.id}")
        self.urlprivacy = requests.get(f"https://play.google.com/store/apps/datasafety?id={self.id}")

        self.soup = BeautifulSoup(self.url.content, "html.parser", from_encoding='utf-8')
        self.soupprivacy = BeautifulSoup(self.urlprivacy.content, "html.parser", from_encoding='utf-8')

    def get_icon(self):
        data = self.soup.find("img", attrs={"class":"T75of QhHVZd"})
        if data:
            return data["src"]
        else:
            data = self.soup.find("img", attrs={"class": "T75of nm4vBd arM4bb"})
            return data["src"]

    def get_privacy(self):
        data1 = self.soupprivacy.find("div", attrs={"class": "RGUlu"})
        print(data1.get_text())
        print()

        data2 = self.soupprivacy.findAll("div", attrs={"class": "Mf2Txd"})
        for item in data2:
            print(item.get_text(" | ", strip=True))
            print()

    def get_title(self):
        data = self.soup.find("h1", attrs={"class":"Fd93Bb F5UCq p5VxAd"})
        return data.get_text("\n" , strip=True).split("\n")[0]

# test = GoogleApp("com.duolingo")
# test.get_privacy()

# print()

# test2 = GoogleApp("vitaminshoppe.consumerapp")
# test2.get_privacy()

# print()

# test3 = GoogleApp("com.retroarch")
# test3.get_privacy()