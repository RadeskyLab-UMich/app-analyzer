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

    def get_app(self):
        """
        Function to get a dictionary of all variables in the Google Play Store scraper.

        Parameters
        ----------
        None

        Returns
        -------
        dict of key value pairs for an app (ex: {collectsData: True})
        """

        app = {}
        app["privacy"] = self.get_privacy_info()

        if "doesn't collect or share any user data" in app["privacy"][0]:
            app["collectsData"] = False

            app["data_shared_location"] = False
            app["data_shared_personal_info"] = False
            app["data_shared_financial_info"] = False
            app["data_shared_health_fitness"] = False
            app["data_shared_messages"] = False
            app["data_shared_photos_videos"] = False
            app["data_shared_audio_files"] = False
            app["data_shared_files_docs"] = False
            app["data_shared_calendar"] = False
            app["data_shared_contacts"] = False
            app["data_shared_app_activity"] = False
            app["data_shared_browsing_history"] = False
            app["data_shared_diagnostics"] = False
            app["data_shared_identifiers"] = False

            app["data_collected_location"] = False
            app["data_collected_personal_info"] = False
            app["data_collected_financial_info"] = False
            app["data_collected_health_fitness"] = False
            app["data_collected_messages"] = False
            app["data_collected_photos_videos"] = False
            app["data_collected_audio_files"] = False
            app["data_collected_files_docs"] = False
            app["data_collected_calendar"] = False
            app["data_collected_contacts"] = False
            app["data_collected_app_activity"] = False
            app["data_collected_browsing_history"] = False
            app["data_collected_diagnostics"] = False
            app["data_collected_identifiers"] = False
        elif "Information about how this app collects and uses your data isn't available" in app["privacy"][0]:
            return app
        else:
            app["collectsData"] = True
            shared = 0
            collected = 0

            for item in app["privacy"]:
                if "Data shared" in item:
                    app = self.get_privacy_info_shared(item, app)
                    shared = 1
                if "Data collected" in item:
                    app = self.get_privacy_info_collected(item, app)
                    collected = 1

            if shared == 0:
                app = self.get_privacy_info_shared(item, app)
            if collected == 0:
                app = self.get_privacy_info_collected(item, app)

        return app


    def get_icon(self):
        data = self.soup.find("img", attrs={"class":"T75of QhHVZd"})
        if data:
            return data["src"]
        else:
            data = self.soup.find("img", attrs={"class": "T75of nm4vBd arM4bb"})
            return data["src"]

    def get_privacy_info(self):
        """
        Function to get the data collected information for an app

        Parameters
        ----------
        None

        Returns
        -------
        accum (list) - list of every category of data collected by the app and the specific types, if any.
        """

        accum = []

        data1 = self.soupprivacy.find("div", attrs={"class": "RGUlu"})
        accum.append(data1.get_text())

        data2 = self.soupprivacy.findAll("div", attrs={"class": "Mf2Txd"})
        for item in data2:
            accum.append(item.get_text(" | ", strip=True))

        return accum

    def get_privacy_info_collected(self, item, app):
        if "Location" in item:
            app["data_collected_location"] = True
        else:
            app["data_collected_location"] = False

        if "Personal info" in item:
            app["data_collected_personal_info"] = True
        else:
            app["data_collected_personal_info"] = False

        if "Financial info" in item:
            app["data_collected_financial_info"] = True
        else:
            app["data_collected_financial_info"] = False

        if "Health and fitness" in item:
            app["data_collected_health_fitness"] = True
        else:
            app["data_collected_health_fitness"] = False

        if "Messages" in item:
            app["data_collected_messages"] = True
        else:
            app["data_collected_messages"] = False

        if "Photos and videos" in item:
            app["data_collected_photos_videos"] = True
        else:
            app["data_collected_photos_videos"] = False

        if "Audio files" in item:
            app["data_collected_audio_files"] = True
        else:
            app["data_collected_audio_files"] = False

        if "Files and docs" in item:
            app["data_collected_files_docs"] = True
        else:
            app["data_collected_files_docs"] = False

        if "Calendar" in item:
            app["data_collected_calendar"] = True
        else:
            app["data_collected_calendar"] = False

        if "Contacts" in item:
            app["data_collected_contacts"] = True
        else:
            app["data_collected_contacts"] = False

        if "App activity" in item:
            app["data_collected_app_activity"] = True
        else:
            app["data_collected_app_activity"] = False

        if "Web browsing" in item:
            app["data_collected_browsing_history"] = True
        else:
            app["data_collected_browsing_history"] = False

        if "App info and performance" in item:
            app["data_collected_diagnostics"] = True
        else:
            app["data_collected_diagnostics"] = False

        if "Device or other IDs" in item:
            app["data_collected_identifiers"] = True
        else:
            app["data_collected_identifiers"] = False

        return app

    def get_privacy_info_shared(self, item, app):
        if "Location" in item:
            app["data_shared_location"] = True
        else:
            app["data_shared_location"] = False

        if "Personal info" in item:
            app["data_shared_personal_info"] = True
        else:
            app["data_shared_personal_info"] = False

        if "Financial info" in item:
            app["data_shared_financial_info"] = True
        else:
            app["data_shared_financial_info"] = False

        if "Health and fitness" in item:
            app["data_shared_health_fitness"] = True
        else:
            app["data_shared_health_fitness"] = False

        if "Messages" in item:
            app["data_shared_messages"] = True
        else:
            app["data_shared_messages"] = False

        if "Photos and videos" in item:
            app["data_shared_photos_videos"] = True
        else:
            app["data_shared_photos_videos"] = False

        if "Audio files" in item:
            app["data_shared_audio_files"] = True
        else:
            app["data_shared_audio_files"] = False

        if "Files and docs" in item:
            app["data_shared_files_docs"] = True
        else:
            app["data_shared_files_docs"] = False

        if "Calendar" in item:
            app["data_shared_calendar"] = True
        else:
            app["data_shared_calendar"] = False

        if "Contacts" in item:
            app["data_shared_contacts"] = True
        else:
            app["data_shared_contacts"] = False

        if "App activity" in item:
            app["data_shared_app_activity"] = True
        else:
            app["data_shared_app_activity"] = False

        if "Web browsing" in item:
            app["data_shared_browsing_history"] = True
        else:
            app["data_shared_browsing_history"] = False

        if "App info and performance" in item:
            app["data_shared_diagnostics"] = True
        else:
            app["data_shared_diagnostics"] = False

        if "Device or other IDs" in item:
            app["data_shared_identifiers"] = True
        else:
            app["data_shared_identifiers"] = False

        return app

    def get_title(self):
        """
        Function to get the title of the app

        Parameters
        ----------
        None

        Returns
        -------
        str of app title (ex: Instagram)
        """

        data = self.soup.find("h1", attrs={"class":"Fd93Bb F5UCq p5VxAd"})
        return data.get_text("\n" , strip=True).split("\n")[0]

# test = GoogleApp("com.duolingo")
# print(test.get_app())

# print()

# test2 = GoogleApp("vitaminshoppe.consumerapp")
# print(test2.get_app())

# print()

# test3 = GoogleApp("com.retroarch")
# print(test3.get_app())