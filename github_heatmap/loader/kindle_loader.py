import requests

from github_heatmap.html_parser import parse_kindle_text_to_list
from github_heatmap.loader.base_loader import BaseLoader, LoadError
from github_heatmap.loader.config import (
    KINDLE_CN_HISTORY_URL,
    KINDLE_HEADER,
    KINDLE_HISTORY_URL,
)


class KindleLoader(BaseLoader):
    track_color = "#2A4A7B"
    unit = "days"

    def __init__(self, from_year, to_year, _type, **kwargs):
        super().__init__(from_year, to_year, _type)
        self.kindle_cookie = kwargs.get("kindle_cookie", "")
        self.session = requests.Session()
        self.header = KINDLE_HEADER
        self.is_cn = kwargs.get("cn", False)
        self.KINDLE_URL = KINDLE_CN_HISTORY_URL if self.is_cn else KINDLE_HISTORY_URL
        self._make_years_list()

    @classmethod
    def add_loader_arguments(cls, parser, optional):
        parser.add_argument(
            "--kindle_cookie",
            dest="kindle_cookie",
            type=str,
            required=optional,
            help="",
        )

    def get_api_data(self):
        r = self.session.get(self.KINDLE_URL, headers=self.header)
        if not r.ok:
            raise LoadError("Can not get kindle calendar data, please check cookie")
        yield from parse_kindle_text_to_list(r.text)

    def make_track_dict(self):
        data_list = self.get_api_data()
        for d in data_list:
            self.number_by_date_dict[d] = 1
            self.number_list.append(1)

    def get_all_track_data(self):
        self.session.cookies = self.parse_cookie_string(self.kindle_cookie)
        self.make_track_dict()
        self.make_special_number()
        return self.number_by_date_dict, self.year_list
