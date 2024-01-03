import pendulum
import requests

from github_heatmap.loader.base_loader import BaseLoader
from github_heatmap.loader.config import WEREAD_BASE_URL, WEREAD_HISTORY_URL


class WereadLoader(BaseLoader):
    track_color = "#2EA8F7"
    unit = "mins"

    def __init__(self, from_year, to_year, _type, **kwargs):
        super().__init__(from_year, to_year, _type)
        self.weread_cookie = kwargs.get("weread_cookie", "")
        self.session = requests.Session()
        self._make_years_list()

    @classmethod
    def add_loader_arguments(cls, parser, optional):
        parser.add_argument(
            "--weread_cookie",
            dest="weread_cookie",
            type=str,
            required=optional,
            help="",
        )

    def get_api_data(self):
        r = self.session.get(WEREAD_HISTORY_URL)
        if not r.ok:
            # need to refresh cookie WTF the design!!
            if r.json()["errcode"] == -2012:
                self.session.get(WEREAD_BASE_URL)
                r = self.session.get(WEREAD_HISTORY_URL)
            else:
                raise Exception("Can not get weread history data")
        return r.json()

    def make_track_dict(self):
        api_data = self.get_api_data()
        if("readTimes" in api_data):
            readTimes = dict(sorted(api_data["readTimes"].items(), reverse=True))
            for k, v in readTimes.items():
                k = pendulum.from_timestamp(int(k), tz=self.time_zone)
                self.number_by_date_dict[k.to_date_string()] = round(v / 60.0, 2)
            for _, v in self.number_by_date_dict.items():
                self.number_list.append(v)

    def get_all_track_data(self):
        self.session.cookies = self.parse_cookie_string(self.weread_cookie)
        self.make_track_dict()
        self.make_special_number()
        return self.number_by_date_dict, self.year_list
