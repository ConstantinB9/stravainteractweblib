import json
import time
from base64 import b64decode

import stravaweblib
from mechanize import Browser
from stravaweblib.webclient import BASE_URL


class InteractiveWebClient(stravaweblib.WebClient):
    """
    An extension to the stravaweblib Webclient to access parts of strava which are not supported by the API
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__browser: Browser = Browser()
        self.__login()

    def __login(self):
        """Set the login cookies, gathered from stravaweblib Client"""
        self.__browser.open(BASE_URL)
        self.__browser.set_simple_cookie(
            name="strava_remember_id",
            domain=".strava.com",
            value=self._get_account_id(self.jwt),
        )
        self.__browser.set_simple_cookie(
            name="strava_remember_token",
            domain=".strava.com",
            value=self.jwt,
        )

    @staticmethod
    def _get_account_id(jwt) -> str:
        """
        From stravaweblib.WebClient._login_with_jwt
        Extracts the account id from the JWT's 'sub' key
        :param jwt: jwt to extract account id from
        :return: account id
        """
        try:
            payload = jwt.split(".")[1]  # header.payload.signature
            payload += "=" * (4 - len(payload) % 4)  # ensure correct padding
            data = json.loads(b64decode(payload))
        except Exception:
            raise ValueError("Failed to parse JWT payload")

        try:
            if data["exp"] < time.time():
                raise ValueError("JWT has expired")
            web_id = str(data["sub"])
            return web_id
        except KeyError:
            raise ValueError("Failed to extract required data from the JWT")

    def set_stats_visibility(
        self, activity_id, calories=True, heart_rate=True, speed=True, power=True
    ) -> None:
        """
        Edits the given activity to change the visibility of stats and saves the edit.
        :param activity_id: ID of the activity to edit
        :param calories: weather 'calories' stat should be public
        :param heart_rate: weather 'hear rate' stat should be public
        :param speed: weather 'speed' stat should be public
        :param power: weather 'power' stat should be public
        :return: None
        """
        url = f"{BASE_URL}/activities/{activity_id}/edit"
        self.__browser.open(url)
        form = [f for f in self.__browser.forms() if f.attrs["id"] == "edit-activity"][
            0
        ]
        metrics = [
            ("activity[stats_visibility][calories]", calories),
            ("activity[stats_visibility][heart_rate]", heart_rate),
            ("activity[stats_visibility][pace]", speed),
            ("activity[stats_visibility][power]", power),
        ]
        for metric_field_name, des_visibility in metrics:
            form.find_control(name=metric_field_name, type="checkbox").get(
                "only_me"
            ).selected = not des_visibility
        req = form.click(name="commit")
        self.__browser.open(req)


InteractiveWebClient.__init__.__doc__ = (
    stravaweblib.WebClient.__init__.__doc__
    + """
        :param setup: Directly perform setup of the driver 
        :type setup: bool
        """
)
