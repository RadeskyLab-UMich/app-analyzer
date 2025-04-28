import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
# import google.cloud.logging
# import logging

class AmazonApp:
    def __init__(self, id):
        HEADERS = ({'User-Agent':
           'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36',
            'Accept-Language': 'en-US, en;q=0.5'})
        # client = google.cloud.logging.Client()
        # client.setup_logging()

        self.app_issue = False
        self.id = id
        if "." not in self.id:
            self.url = requests.get(f"https://www.amazon.com/dp/{self.id}", headers=HEADERS)
            self.soup = BeautifulSoup(self.url.content, "html.parser", from_encoding='utf-8')

            if "Page Not Found" in self.soup.get_text():
                self.app_issue = True
        else:
            self.url = requests.get(f"https://www.amazon.com/s?k={self.id}&i=mobile-apps", headers=HEADERS)
            self.soup = BeautifulSoup(self.url.content, "html.parser", from_encoding='utf-8')
            # logging.warning(self.soup.get_text())

            if f"No results for {self.id} in Apps & Games" in self.soup.get_text():
                self.app_issue = True
                self.asin = ""
            else:
                self.asin = self.soup.find_all('div', {'data-dib-asin': True})


            r = len(self.asin)
            if r > 3:
                r = 3

            for i in range(r):
                asin = self.asin[i]['data-dib-asin']
                self.url = requests.get(f"https://www.amazon.com/dp/{asin}", headers=HEADERS)
                self.soup = BeautifulSoup(self.url.content, "html.parser", from_encoding='utf-8')

                package = self.get_app_package_name()
                print(package)
                print(self.id)

                if package == self.id:
                    self.asin = asin
                    self.app_issue = False
                    break
                else:
                    self.app_issue = True

    def get_app(self):
        """
        Function to collect all data scraped for an app and return it as a dictionary

        Parameters
        ----------
        None

        Returns
        -------
        app - dict of key value pairs of the data
        """
        if self.app_issue == True:
            return {}
        app = {}
        today = datetime.now()
        formatted_date = today.strftime("%m/%d/%Y")

        app["date_scraped"] = formatted_date
        app["title"] = self.get_title()
        app["appId"] = self.get_app_id()
        app["app_package_name"] = self.get_app_package_name()
        app["url"] = self.get_url()
        app["description"] = self.get_description()
        app["releaseNotes"] = self.get_latest_updates()
        app["productFeatures"] = self.get_product_features()

        app["price"] = self.get_price()
        if "Free" in app["price"]:
            app["free"] = True
        else:
            app["free"] = False
        app["offersIAP"] = self.get_iap()

        details = self.get_product_details()
        app["released"] = details[1].split(":")[1]
        app["developer"] = details[2].split(":")[1]
        if "Be the first to write a review" in details[-1].split(":")[1]:
            app["reviews"] = details[-1].split(":")[1]
            app["score"] = "Be the first to give a rating"
        else:
            app["reviews"] = details[-1].split(":")[1].split("stars")[-1]
            app["score"] = details[-1].split(":")[1].split("stars")[0]

        dev_info = self.get_developer_info()
        app["developerEmail"] = dev_info[0]
        if len(dev_info) > 1:
            if dev_info[1] == "More apps by this developer":
                app["developerWebsite"] = ""
            else:
                app["developerWebsite"] = dev_info[1]

        details = self.get_technical_details()
        app["size"] = details.split('\n')[1]
        app["version"] = details.split('\n')[3]
        app["applicationPermissions"] = details.split("Application Permissions:")[1].split("Minimum Operating")[0].split(")")[1]

        app["privacy_policy"] = self.get_privacy_policy()
        app["privacy"] = self.get_privacy()

        if "does not collect" in app["privacy"] or "Information not provided" in app["privacy"]:
            app["collectsData"] = False
        else:
            app["collectsData"] = True

        app = self.get_privacy_info_collects(app)
        app = self.get_privacy_info_shares(app)

        return app




    def get_app_id(self):
        """
        Function to get app ID (ASIN).

        Parameters
        ----------
        None

        Returns
        -------
        int of app ID (ex: 389801252)
        """
        meta_tag = self.soup.find('meta', {'name': 'appstore:store_id'})

        if meta_tag:
            content_value = meta_tag.get('content')
            return content_value

    def get_app_package_name(self):
        """
        Function to get app package name.

        Parameters
        ----------
        None

        Returns
        -------
        name of app package (ex: com.openlattice.chronicle)
        """
        meta_tag = self.soup.find('meta', {'name': 'appstore:bundle_id'})

        if meta_tag:
            content_value = meta_tag.get('content')
            return content_value

    def get_description(self):
        """
        Function to get the description of an app.

        Parameters
        ----------
        None

        Returns
        -------
        str of the app's description
        """
        data = self.soup.find("div", attrs={"id":"mas-product-description"})

        return "\n".join(data.get_text("\n", strip=True).split("\n")[1:])

    def get_developer_info(self):
        """
        Function to get developer info such as email and website

        Parameters
        ----------
        None

        Returns
        -------
        List of developer info
        """
        test = self.soup.get_text("\n", strip=True).split("Developer info")[1].split("Product features")[0]

        return test.split("\n")[1:-1]

    def get_iap(self):
        """
        Function to determine if in-app purchases exist. Based on if a id in the webpage exists.

        Parameters
        ----------
        None

        Returns
        -------
        True/False on whether or not IAP's exist
        """
        if self.soup.find("span", attrs={"id":"offer_inapp_popover"}):
            return True
        else:
            return False

    def get_latest_updates(self):
        """
        Function to get the text on the "latest updates"

        Parameters
        ----------
        None

        Returns
        -------
        String of the latest updates provided by the devloper
        """
        if self.soup.find("div", attrs={"id":"mas-latest-updates"}):
            data = self.soup.find("div", attrs={"id":"mas-latest-updates"})

            return "\n".join(data.get_text("\n", strip=True).split("\n")[1:])
        else:
            return "Updates Non-Existent"

    def get_price(self):
        """
        Function to get the price of an app.

        Parameters
        ----------
        None

        Returns
        -------
        String of the price (includes $, or if free, will say "Free")
        """
        data = self.soup.find("div", attrs={"id":"actualPriceRow"})

        return "\n".join(data.get_text("\n", strip=True).split("\n")[1:])

    def get_privacy(self):
        """
        Funciton to get info on the privacy settings of an app (whether data is collected/shared if the info is provided)

        Parameters
        ----------
        None

        Returns
        -------
        String of the privacy info
        """
        data = self.soup.find("div", attrs={"id":"mas-privacy-lables"})

        return "\n".join(data.get_text("\n", strip=True).split("\n")[1:])

    def get_privacy_info_collects(self, app):
        """
        Function to get True/False values on if certain categories of user data is collected

        Parameters
        ----------
        app - dict of the app itself

        Returns
        -------
        app - dict of app with additional k/v pairs
        """
        if app["collectsData"] == False:
            app["data_collected_user_info"] = False
            app["data_collected_financial_info"] = False
            app["data_collected_device_info"] = False
            app["data_collected_health_fitness"] = False
            app["data_collected_location"] = False
            app["data_collected_browsing_history"] = False
            app["data_collected_photos_videos"] = False
            app["data_collected_audio_files"] = False
            app["data_collected_app_info"] = False
            app["data_collected_app_activity"] = False
            app["data_collected_messages"] = False
            app["data_collected_files_docs"] = False
            app["data_collected_calendar"] = False
            app["data_collected_contacts"] = False

            return app
        else:
            collects_text = app["privacy"].split("Learn what data is transferred to third party")[0]

            if "User Info" in collects_text:
                app["data_collected_user_info"] = True
            else:
                app["data_collected_user_info"] = False

            if "Financial Info" in collects_text:
                app["data_collected_financial_info"] = True
            else:
                app["data_collected_financial_info"] = False

            if "Device or other IDs" in collects_text:
                app["data_collected_device_info"] = True
            else:
                app["data_collected_device_info"] = False

            if "Health & Fitness" in collects_text:
                app["data_collected_health_fitness"] = True
            else:
                app["data_collected_health_fitness"] = False

            if "Location" in collects_text:
                app["data_collected_location"] = True
            else:
                app["data_collected_location"] = False

            if "Web Browsing" in collects_text:
                app["data_collected_browsing_history"] = True
            else:
                app["data_collected_browsing_history"] = False

            if "Photos or Videos" in collects_text:
                app["data_collected_photos_videos"] = True
            else:
                app["data_collected_photos_videos"] = False

            if "Audio Files" in collects_text:
                app["data_collected_audio_files"] = True
            else:
                app["data_collected_audio_files"] = False

            if "App info and performance" in collects_text:
                app["data_collected_app_info"] = True
            else:
                app["data_collected_app_info"] = False

            if "App activity" in collects_text:
                app["data_collected_app_activity"] = True
            else:
                app["data_collected_app_activity"] = False

            if "Messages" in collects_text:
                app["data_collected_messages"] = True
            else:
                app["data_collected_messages"] = False

            if "Files and docs" in collects_text:
                app["data_collected_files_docs"] = True
            else:
                app["data_collected_files_docs"] = False

            if "Calendar" in collects_text:
                app["data_collected_calendar"] = True
            else:
                app["data_collected_calendar"] = False

            if "Contacts" in collects_text:
                app["data_collected_contacts"] = True
            else:
                app["data_collected_contacts"] = False

            return app

    def get_privacy_info_shares(self, app):
        """
        Function to get True/False values on if certain categories of user data is shared with third parties

        Parameters
        ----------
        app - dict of the app itself

        Returns
        -------
        app - dict of app with additional k/v pairs
        """
        try:
            shares_text = app["privacy"].split("Learn what data is transferred to third party")[1]
        except:
            shares_text = False

        if app["collectsData"] == False or shares_text == False:
            app["data_shared_user_info"] = False
            app["data_shared_financial_info"] = False
            app["data_shared_device_info"] = False
            app["data_shared_health_fitness"] = False
            app["data_shared_location"] = False
            app["data_shared_browsing_history"] = False
            app["data_shared_photos_videos"] = False
            app["data_shared_audio_files"] = False
            app["data_shared_app_info"] = False
            app["data_shared_app_activity"] = False
            app["data_shared_messages"] = False
            app["data_shared_files_docs"] = False
            app["data_shared_calendar"] = False
            app["data_shared_contacts"] = False

            return app
        else:
            if "User Info" in shares_text:
                app["data_shared_user_info"] = True
            else:
                app["data_shared_user_info"] = False

            if "Financial Info" in shares_text:
                app["data_shared_financial_info"] = True
            else:
                app["data_shared_financial_info"] = False

            if "Device or other IDs" in shares_text:
                app["data_shared_device_info"] = True
            else:
                app["data_shared_device_info"] = False

            if "Health & Fitness" in shares_text:
                app["data_shared_health_fitness"] = True
            else:
                app["data_shared_health_fitness"] = False

            if "Location" in shares_text:
                app["data_shared_location"] = True
            else:
                app["data_shared_location"] = False

            if "Web Browsing" in shares_text:
                app["data_shared_browsing_history"] = True
            else:
                app["data_shared_browsing_history"] = False

            if "Photos or Videos" in shares_text:
                app["data_shared_photos_videos"] = True
            else:
                app["data_shared_photos_videos"] = False

            if "Audio Files" in shares_text:
                app["data_shared_audio_files"] = True
            else:
                app["data_shared_audio_files"] = False

            if "App info and performance" in shares_text:
                app["data_shared_app_info"] = True
            else:
                app["data_shared_app_info"] = False

            if "App activity" in shares_text:
                app["data_shared_app_activity"] = True
            else:
                app["data_shared_app_activity"] = False

            if "Messages" in shares_text:
                app["data_shared_messages"] = True
            else:
                app["data_shared_messages"] = False

            if "Files and docs" in shares_text:
                app["data_shared_files_docs"] = True
            else:
                app["data_shared_files_docs"] = False

            if "Calendar" in shares_text:
                app["data_shared_calendar"] = True
            else:
                app["data_shared_calendar"] = False

            if "Contacts" in shares_text:
                app["data_shared_contacts"] = True
            else:
                app["data_shared_contacts"] = False

            return app

    def get_privacy_policy(self):
        """
        Funciton to get info on the privacy policy settings of an app (whether data is collected/shared if the info is provided)

        Parameters
        ----------
        None

        Returns
        -------
        String of the privacy policy url
        """
        data = self.soup.find("div", attrs={"class":"privacy-label-learn-more"})

        try:
            a = data.find("a", href=True)
            return a["href"]
        except:
            return ""

    def get_product_details(self):
        """
        Function to get the product details section of an app (release date, developer, reviews, etc.)

        Parameters
        ----------
        None

        Returns
        -------
        Strings of release_date, date_listed, developed_by, and ratings
        """
        test = self.soup.get_text(strip=True).split("Product Details")[1].split("Developer info")[0]
        #print(test)
        release_date = test.split("Date first listed")[0]
        date_listed = test.split("Developed By")[0][test.find("Date first listed"):]
        developed_by = test.split("ASIN")[0][test.find("Developed By"):]
        ratings = test[test.find("reviews:"):]

        # print(release_date)
        # print(date_listed)
        # print(developed_by)
        # print(ratings)

        return release_date, date_listed, developed_by, ratings

    def get_product_features(self):
        """
        Function to get the product features section (usually a list on the website)

        Parameters
        ----------
        None

        Returns
        -------
        String of the product features
        """
        data = self.soup.find("div", attrs={"id":"mas-product-feature"})

        return "\n".join(data.get_text("\n", strip=True).split("\n")[1:])

    def get_technical_details(self):
        """
        Function to get technical details of an app (size, devloper, access, etc.)

        Parameters
        ----------
        None

        Returns
        -------
        String of the technical details
        """
        data = self.soup.find("div", attrs={"id":"masTechnicalDetails-btf"})

        return "\n".join(data.get_text("\n", strip=True).split("\n")[1:])

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
        data = self.soup.find("h1", attrs={"class":"parseasinTitle"})

        return data.get_text("\n" , strip=True).split("\n")[0]

    def get_url(self):
        """
        Function to get the url of the app

        Parameters
        ----------
        None

        Returns
        -------
        str of app url
        """
        if "." not in self.id:
            return f"https://www.amazon.com/dp/{self.id}"
        else:
            return f"https://www.amazon.com/dp/{self.asin}"