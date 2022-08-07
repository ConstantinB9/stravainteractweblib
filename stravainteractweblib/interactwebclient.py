import json
import os
import pathlib
import shutil
import subprocess
import sys
import time
from base64 import b64decode
from typing import Optional

import requests
import stravalib.exc
from selenium.webdriver import Firefox
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options

import stravaweblib
from stravaweblib.webclient import BASE_URL


def platform_str() -> str:
    import platform
    mapping = {
        'Windows': 'win',
        'Linux': 'linux',
        'Darwin': 'macos'
    }
    if platform.system() not in mapping:
        raise OSError("Unknown System Platform")
    return mapping[platform.system()]


class InteractiveWebClient(stravaweblib.WebClient):
    """
    An extension to the stravaweblib Webclient to access parts of strava which are not supported by the API
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__driver: Optional[WebDriver] = None
        self.__auth_cookie_set = False
        if kwargs.pop('setup', False):
            self.__ensure_setup()

    def __del__(self):
        """Teardown, quitting the driver instance"""
        if self.__driver_initialized:
            self.__driver.quit()

    def __ensure_setup(self):
        """ Perform setup steps, if setup wasn't performed yet"""
        if not self.__driver_initialized:
            self.__init_driver()
        if not self.__auth_cookie_set:
            self.__login()

    @property
    def __driver_initialized(self) -> bool:
        """Check if the driver was initialized already"""
        return self.__driver is not None

    def __init_driver(self):
        """Initialize the driver with a Firefox instance. Requires geckodriver"""
        opts = Options()
        opts.headless = True
        self.__driver = Firefox(options = opts)
        return

    def __login(self):
        """Set the login cookies, gathered from stravaweblib Client"""
        self.__driver.get(BASE_URL)
        self.__driver.add_cookie(
            {'name': 'strava_remember_id', 'domain': '.strava.com', 'value': self._get_account_id(self.jwt),
             'secure': True})
        self.__driver.add_cookie(
            {'name': 'strava_remember_token', 'domain': '.strava.com', 'value': self.jwt, 'secure': True})
        self.__auth_cookie_set = True

    @staticmethod
    def _get_account_id(jwt) -> str:
        """
        From stravaweblib.WebClient._login_with_jwt
        Extracts the account id from the JWT's 'sub' key
        :param jwt: jwt to extract account id from
        :return: account id
        """
        try:
            payload = jwt.split('.')[1]  # header.payload.signature
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

    def change_stats_visibility(self, activity_id, calories = True, heart_rate = True, speed = True,
                                power = True) -> None:
        """
        Edits the given activity to change the visibility of stats and saves the edit.
        :param activity_id: ID of the activity to edit
        :param calories: weather 'calories' stat should be public
        :param heart_rate: weather 'hear rate' stat should be public
        :param speed: weather 'speed' stat should be public
        :param power: weather 'power' stat should be public
        :return: None
        """
        self.__ensure_setup()

        url = f"{BASE_URL}/activities/{activity_id}/edit"
        self.__driver.get(url)
        if self.__driver.current_url != url:
            raise stravalib.exc.AuthError("Authorization Failed")

        metrics = [('activity_stats_visibility_calories', calories),
                   ("activity_stats_visibility_heart_rate", heart_rate), ("activity_stats_visibility_speed", speed),
                   ("activity_stats_visibility_power", power)]
        for metric_field_id, des_visibility in metrics:
            checkbox = self.__driver.find_element(By.ID, value = metric_field_id)
            if checkbox.get_property('checked') == des_visibility:
                checkbox.click()
        self.__driver.find_element(By.CLASS_NAME, 'media-right').click()

    @staticmethod
    def setup_geckodriver(exec_path: pathlib.Path = None):
        if exec_path is None:
            exec_path = pathlib.Path(__file__).parent.parent.absolute() / 'deps'

        exec_path.mkdir(exist_ok = True)
        is_unix_like = 'win' not in sys.platform
        if (is_unix_like and (exec_path / 'geckodriver').is_file()) \
                or (not is_unix_like and (exec_path / 'geckodriver.exe').is_file()):
            # add deps location to path
            if str(exec_path) not in os.environ["PATH"]:
                os.environ["PATH"] += os.pathsep + str(exec_path)
            return

        # get the newest release of the geckodriver through the GitHub api.
        r = requests.get('https://api.github.com/repos/mozilla/geckodriver/releases/latest')
        data = r.json()

        # download all assets of the latest release
        if r.status_code == requests.codes.ok:
            platform = platform_str()
            bits = '64' if sys.maxsize > 2**32 else '32'
            matching_assets = [asset for asset in data['assets'] if
                               platform in asset["name"] and bits in asset["name"] and (
                                           asset["name"].endswith('gz') or asset["name"].endswith('zip'))]
            if not matching_assets:
                raise OSError("No matching asset found for system")
            asset = matching_assets[0]
            asset_path = exec_path / asset['name']
            with asset_path.open('wb') as f:
                f.write(requests.get(asset['browser_download_url']).content)
            shutil.unpack_archive(asset_path, exec_path)
            asset_path.unlink()

            if is_unix_like:
                # if on unix: make the binary file executable
                subprocess.run(f'chmod +x {(exec_path / "geckodriver")}', shell = True)
        else:
            raise ConnectionRefusedError("Could not retrieve latest release from geckodriver github page. Install "
                                         "manually instead. See https://github.com/mozilla/geckodriver")

        # add deps location to path
        if str(exec_path) not in os.environ["PATH"]:
            os.environ["PATH"] += os.pathsep + str(exec_path)


InteractiveWebClient.__init__.__doc__ = stravaweblib.WebClient.__init__.__doc__ + \
                                        """
        :param setup: Directly perform setup of the driver 
        :type setup: bool
        """
