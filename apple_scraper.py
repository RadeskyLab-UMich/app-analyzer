import requests
from bs4 import BeautifulSoup
import pandas as pd

class AppleApp:
    def __init__(self, id):
        self.id = id
        self.url = requests.get(f"https://apps.apple.com/us/app/id{self.id}")
        self.soup = BeautifulSoup(self.url.content, "html.parser", from_encoding='utf-8')

    def get_app(self):
        """
        Function to get a dictionary of all variables in the Apple App Store scraper.

        Parameters
        ----------
        None

        Returns
        -------
        dict of key value pairs for an app (ex: {title: YouTube Kids})
        """
        app = {}

        # app["title"] = self.get_title()
        app["subtitle"] = self.get_subtitle()
        # app["developer"] = self.get_developer()
        # app["description"] = self.get_description()
        # app["appId"] = self.get_app_id()
        app["age_rating"] = self.get_age_rating()
        app["price"] = self.get_price()
        app["iap"] = self.get_iap()
        app["privacy"] = self.get_privacy_info()
        # app["score"] = self.get_ratings_score()

        if app["price"] == "Free":
            app["free"] = True
        else:
            app["free"] = False

        if app["iap"] == {}:
            app["offersIAP"] = False
        else:
            app["offersIAP"] = True

        if "Data Not Collected" in app["privacy"][0]:
            app["CollectsData"] = False
        elif "No Details Provided" in app["privacy"][0]:
            return app
        else:
            app["CollectsData"] = True

        if app["CollectsData"] == False:
            app["data_track_purchases"] = False
            app["data_track_location"] = False
            app["data_track_contact_info"] = False
            app["data_track_contacts"] = False
            app["data_track_identifiers"] = False
            app["data_track_user_content"] = False
            app["data_track_usage_data"] = False
            app["data_track_diagnostics"] = False
            app["data_track_health_fitness"] = False
            app["data_track_financial_info"] = False
            app["data_track_search_history"] = False
            app["data_track_browsing_history"] = False
            app["data_track_sensitive_info"] = False
            app["data_track_body"] = False
            app["data_track_surroundings"] = False
            app["data_track_other_data"] = False

            app["data_linked_purchases"] = False
            app["data_linked_location"] = False
            app["data_linked_contact_info"] = False
            app["data_linked_contacts"] = False
            app["data_linked_identifiers"] = False
            app["data_linked_user_content"] = False
            app["data_linked_usage_data"] = False
            app["data_linked_diagnostics"] = False
            app["data_linked_health_fitness"] = False
            app["data_linked_financial_info"] = False
            app["data_linked_search_history"] = False
            app["data_linked_browsing_history"] = False
            app["data_linked_sensitive_info"] = False
            app["data_linked_body"] = False
            app["data_linked_surroundings"] = False
            app["data_linked_other_data"] = False

            app["data_not_linked_purchases"] = False
            app["data_not_linked_location"] = False
            app["data_not_linked_contact_info"] = False
            app["data_not_linked_contacts"] = False
            app["data_not_linked_identifiers"] = False
            app["data_not_linked_user_content"] = False
            app["data_not_linked_usage_data"] = False
            app["data_not_linked_diagnostics"] = False
            app["data_not_linked_health_fitness"] = False
            app["data_not_linked_financial_info"] = False
            app["data_not_linked_search_history"] = False
            app["data_not_linked_browsing_history"] = False
            app["data_not_linked_sensitive_info"] = False
            app["data_not_linked_body"] = False
            app["data_not_linked_surroundings"] = False
            app["data_not_linked_other_data"] = False
        else:
            linked = 0
            not_linked = 0
            tracked = 0

            for item in app["privacy"]:
                if "Data Used to Track You" in item:
                    app = self.get_privacy_info_track(item, app)
                    tracked = 1
                elif "Data Linked to You" in item:
                    app = self.get_privacy_info_linked(item, app)
                    linked = 1
                else:
                    app = self.get_privacy_info_not_linked(item, app)
                    not_linked = 1

            if tracked == 0:
                app = self.get_privacy_info_track(app["privacy"][0], app)
            if linked == 0:
                app = self.get_privacy_info_linked(app["privacy"][0], app)
            if not_linked == 0:
                app = self.get_privacy_info_not_linked(app["privacy"][0], app)

        if all("Data Used to Track You" not in s for s in app["privacy"]):
            app["data_track_purchases"] = False
            app["data_track_location"] = False
            app["data_track_contact_info"] = False
            app["data_track_contacts"] = False
            app["data_track_identifiers"] = False
            app["data_track_user_content"] = False
            app["data_track_usage_data"] = False
            app["data_track_diagnostics"] = False
            app["data_track_health_fitness"] = False
            app["data_track_financial_info"] = False
            app["data_track_search_history"] = False
            app["data_track_browsing_history"] = False
            app["data_track_sensitive_info"] = False
            app["data_track_body"] = False
            app["data_track_surroundings"] = False
            app["data_track_other_data"] = False

        if all("Data Linked to You" not in s for s in app["privacy"]):
            app["data_linked_purchases"] = False
            app["data_linked_location"] = False
            app["data_linked_contact_info"] = False
            app["data_linked_contacts"] = False
            app["data_linked_identifiers"] = False
            app["data_linked_user_content"] = False
            app["data_linked_usage_data"] = False
            app["data_linked_diagnostics"] = False
            app["data_linked_health_fitness"] = False
            app["data_linked_financial_info"] = False
            app["data_linked_search_history"] = False
            app["data_linked_browsing_history"] = False
            app["data_linked_sensitive_info"] = False
            app["data_linked_body"] = False
            app["data_linked_surroundings"] = False
            app["data_linked_other_data"] = False

        if all("Data Not Linked to You" not in s for s in app["privacy"]):
            app["data_not_linked_purchases"] = False
            app["data_not_linked_location"] = False
            app["data_not_linked_contact_info"] = False
            app["data_not_linked_contacts"] = False
            app["data_not_linked_identifiers"] = False
            app["data_not_linked_user_content"] = False
            app["data_not_linked_usage_data"] = False
            app["data_not_linked_diagnostics"] = False
            app["data_not_linked_health_fitness"] = False
            app["data_not_linked_financial_info"] = False
            app["data_not_linked_search_history"] = False
            app["data_not_linked_browsing_history"] = False
            app["data_not_linked_sensitive_info"] = False
            app["data_not_linked_body"] = False
            app["data_not_linked_surroundings"] = False
            app["data_not_linked_other_data"] = False

        return app

    def get_age_rating(self):
        """
        Function to get the age rating of an app

        Parameters
        ----------
        None

        Returns
        -------
        str of age rating (ex: 12+)
        """
        # data = self.soup.find("h1", attrs={"class":"product-header__title app-header__title"})
        data = self.soup.find("span", attrs={"class":"svelte-km1qy2"})

        # return data.get_text("\n" , strip=True).split("\n")[1]
        return data.get_text()

    def get_app_id(self):
        """
        Function to get app ID.

        Parameters
        ----------
        None

        Returns
        -------
        int of app ID (ex: 389801252)
        """
        return self.id

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
        data = self.soup.find("div", attrs={"class":"section__description"})
        return "\n".join(data.get_text("\n", strip=True).split("\n")[1:])

    def get_developer(self):
        """
        Function to get developer/publisher info of an app

        Parameters
        ----------
        None

        Returns
        -------
        str of developer/publisher name (ex: Instagram, Inc.)
        """
        data = self.soup.find("h2", attrs={"class":"product-header__identity app-header__identity"})
        return data.get_text(strip=True)

    def get_info_general(self):
        data = self.soup.find("dl", attrs={"class":"information-list information-list--app medium-columns l-row"})
        print(data.text)

    def get_iap(self):
        """
        Function to get the in-app purchase options that exist for an app.

        Parameters
        ----------
        None

        Returns
        -------
        combined (dict) - dictionary either empty or filled with keys of the in-app purchase options and the values being their price
        """
        # iap = self.soup.findAll("li", attrs={"class":"list-with-numbers__item"})
        iap = self.soup.findAll("div", attrs={"class":"text-pair svelte-1a9curd"})
        combined = {}

        if iap:
            for i in iap:
                t = i.get_text("||", strip=True)
                combined[t.split("||")[0]] = t.split("||")[1]
            # titles = self.soup.findAll("span", attrs={"class":"truncate-single-line truncate-single-line--block"})
            # prices = self.soup.findAll("span", attrs={"class":"list-with-numbers__item__price medium-show-tablecell"})
            # for title, price in zip(titles, prices):
            #     combined[title.text] = price.text

        return combined

    def get_picture(self):
        data = self.soup.find("picture", attrs={"class":"we-artwork we-artwork--downloaded product-hero__artwork we-artwork--fullwidth we-artwork--ios-app-icon"})
        print(data)

    def get_price(self):
        """
        Function to get price of an app

        Parameters
        ----------
        None

        Returns
        -------
        str of price (ex: $1.99 -or- Free)
        """
        try:
            data = self.soup.findAll("p", attrs={"class":"attributes svelte-1bm25t"})

            for d in data:
                if "$" in d.get_text() or "Free" in d.get_text():
                    return d.get_text(strip=True).split()[0]
            # data = self.soup.find("li", attrs={"class":"inline-list__item inline-list__item--bulleted app-header__list__item--price"})
            return ""
        except:
            return "Subscribe to Apple Arcade"

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
        # data = self.soup.findAll("div", attrs={"class":"app-privacy__card"})
        data = self.soup.find("section", attrs={"id": "privacyTypes"})
        # print(data)
        accum = []
        for item in data.find("ul", attrs={"class": "grid svelte-7iyek8"}):
            accum.append(item.get_text(" | ", strip=True))
            # print("hi")
        # for item in data:
        #     accum.append(item.get_text(" | ", strip=True))

        return accum

    def get_privacy_info_linked(self, item, app):
        if "Purchases" in item:
            app["data_linked_purchases"] = True
        else:
            app["data_linked_purchases"] = False

        if "Location" in item:
            app["data_linked_location"] = True
        else:
            app["data_linked_location"] = False

        if "Contact Info" in item:
            app["data_linked_contact_info"] = True
        else:
            app["data_linked_contact_info"] = False

        if "Contacts" in item:
            app["data_linked_contacts"] = True
        else:
            app["data_linked_contacts"] = False

        if "Identifiers" in item:
            app["data_linked_identifiers"] = True
        else:
            app["data_linked_identifiers"] = False

        if "User Content" in item:
            app["data_linked_user_content"] = True
        else:
            app["data_linked_user_content"] = False

        if "Usage Data" in item:
            app["data_linked_usage_data"] = True
        else:
            app["data_linked_usage_data"] = False

        if "Diagnostics" in item:
            app["data_linked_diagnostics"] = True
        else:
            app["data_linked_diagnostics"] = False

        if "Health & Fitness" in item:
            app["data_linked_health_fitness"] = True
        else:
            app["data_linked_health_fitness"] = False

        if "Financial Info" in item:
            app["data_linked_financial_info"] = True
        else:
            app["data_linked_financial_info"] = False

        if "Search History" in item:
            app["data_linked_search_history"] = True
        else:
            app["data_linked_search_history"] = False

        if "Browsing History" in item:
            app["data_linked_browsing_history"] = True
        else:
            app["data_linked_browsing_history"] = False

        if "Sensitive Info" in item:
            app["data_linked_sensitive_info"] = True
        else:
            app["data_linked_sensitive_info"] = False

        if "Body" in item:
            app["data_linked_body"] = True
        else:
            app["data_linked_body"] = False

        if "Surroundings" in item:
            app["data_linked_surroundings"] = True
        else:
            app["data_linked_surroundings"] = False

        if "Other Data" in item:
            app["data_linked_other_data"] = True
        else:
            app["data_linked_other_data"] = False

        return app

    def get_privacy_info_not_linked(self, item, app):
        if "Purchases" in item:
            app["data_not_linked_purchases"] = True
        else:
            app["data_not_linked_purchases"] = False

        if "Location" in item:
            app["data_not_linked_location"] = True
        else:
            app["data_not_linked_location"] = False

        if "Contact Info" in item:
            app["data_not_linked_contact_info"] = True
        else:
            app["data_not_linked_contact_info"] = False

        if "Contacts" in item:
            app["data_not_linked_contacts"] = True
        else:
            app["data_not_linked_contacts"] = False

        if "Identifiers" in item:
            app["data_not_linked_identifiers"] = True
        else:
            app["data_not_linked_identifiers"] = False

        if "User Content" in item:
            app["data_not_linked_user_content"] = True
        else:
            app["data_not_linked_user_content"] = False

        if "Usage Data" in item:
            app["data_not_linked_usage_data"] = True
        else:
            app["data_not_linked_usage_data"] = False

        if "Diagnostics" in item:
            app["data_not_linked_diagnostics"] = True
        else:
            app["data_not_linked_diagnostics"] = False

        if "Health & Fitness" in item:
            app["data_not_linked_health_fitness"] = True
        else:
            app["data_not_linked_health_fitness"] = False

        if "Financial Info" in item:
            app["data_not_linked_financial_info"] = True
        else:
            app["data_not_linked_financial_info"] = False

        if "Search History" in item:
            app["data_not_linked_search_history"] = True
        else:
            app["data_not_linked_search_history"] = False

        if "Browsing History" in item:
            app["data_not_linked_browsing_history"] = True
        else:
            app["data_not_linked_browsing_history"] = False

        if "Sensitive Info" in item:
            app["data_not_linked_sensitive_info"] = True
        else:
            app["data_not_linked_sensitive_info"] = False

        if "Body" in item:
            app["data_not_linked_body"] = True
        else:
            app["data_not_linked_body"] = False

        if "Surroundings" in item:
            app["data_not_linked_surroundings"] = True
        else:
            app["data_not_linked_surroundings"] = False

        if "Other Data" in item:
            app["data_not_linked_other_data"] = True
        else:
            app["data_not_linked_other_data"] = False

        return app

    def get_privacy_info_track(self, item, app):
        if "Purchases" in item:
            app["data_track_purchases"] = True
        else:
            app["data_track_purchases"] = False

        if "Location" in item:
            app["data_track_location"] = True
        else:
            app["data_track_location"] = False

        if "Contact Info" in item:
            app["data_track_contact_info"] = True
        else:
            app["data_track_contact_info"] = False

        if "Contacts" in item:
            app["data_track_contacts"] = True
        else:
            app["data_track_contacts"] = False

        if "Identifiers" in item:
            app["data_track_identifiers"] = True
        else:
            app["data_track_identifiers"] = False

        if "User Content" in item:
            app["data_track_user_content"] = True
        else:
            app["data_track_user_content"] = False

        if "Usage Data" in item:
            app["data_track_usage_data"] = True
        else:
            app["data_track_usage_data"] = False

        if "Diagnostics" in item:
            app["data_track_diagnostics"] = True
        else:
            app["data_track_diagnostics"] = False

        if "Health & Fitness" in item:
            app["data_track_health_fitness"] = True
        else:
            app["data_track_health_fitness"] = False

        if "Financial Info" in item:
            app["data_track_financial_info"] = True
        else:
            app["data_track_financial_info"] = False

        if "Search History" in item:
            app["data_track_search_history"] = True
        else:
            app["data_track_search_history"] = False

        if "Browsing History" in item:
            app["data_track_browsing_history"] = True
        else:
            app["data_track_browsing_history"] = False

        if "Sensitive Info" in item:
            app["data_track_sensitive_info"] = True
        else:
            app["data_track_sensitive_info"] = False

        if "Body" in item:
            app["data_track_body"] = True
        else:
            app["data_track_body"] = False

        if "Surroundings" in item:
            app["data_track_surroundings"] = True
        else:
            app["data_track_surroundings"] = False

        if "Other Data" in item:
            app["data_track_other_data"] = True
        else:
            app["data_track_other_data"] = False

        return app

    def get_ranking(self):
        #if exists: pass
        pass

    def get_ratings_score(self):
        """
        Function to
        """
        data = self.soup.find("figcaption", attrs={"class":"we-rating-count star-rating__count"})
        return data.get_text().split()[0]

    def get_screenshots(self):
        #data = self.soup.findAll("section", attrs={"class":"l-content-width section section--bordered"})
        data = self.soup.findAll("section", attrs={"class":"l-row l-row--peek we-screenshot-viewer__screenshots-list"})
        print(data.get_text())

    def get_subtitle(self):
        """
        Function to get the subtitle of the app

        Parameters
        ----------
        None

        Returns
        -------
        str of app subtitle (ex: Your Friends, Your Moments)
        """
        try:
            data = self.soup.find("h2", attrs={"class":"subtitle svelte-1bm25t"})
            # data = self.soup.find("h2", attrs={"class":"product-header__subtitle app-header__subtitle"})
            return data.get_text(strip=True)
        except:
            return None

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
        data = self.soup.find("h1", attrs={"class":"product-header__title app-header__title"})
        print(data)
        return data.get_text("\n" , strip=True).split("\n")[0]

    def get_version(self):
        pass

    def get_whats_new(self):
        data = self.soup.findAll("section", attrs={"class":"l-content-width section section--bordered whats-new"})
        print(data)


# test = AppleApp(id="1287282214")
# print(test.url)
# print(test.soup)
# print(test.get_app())