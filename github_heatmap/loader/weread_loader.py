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
        print(r.text)
        if not r.ok:
            # need to refresh cookiepython3 -m github_heatmap weread --weread_cookie "RRK=8j/1EX6Sec; ptcz=51984f3350dde3a3b4b4721f9d1a4a68531dfd33e75556dde5bfbe28c04f6944; wr_fp=2027173264; wr_gid=230035142; wr_vid=382797066; wr_rt=web%40RE54QUTsAtNEc2UDhJ4_AL; wr_localvid=07332540816d1050a07361b; wr_name=%E6%9C%89%E6%84%8F%E8%AF%86%E7%9A%84%E6%8B%99.; wr_avatar=https%3A%2F%2Fthirdwx.qlogo.cn%2Fmmopen%2Fvi_32%2FmticjmrhDj3iccCWxG32eYWJ40YxAOlYtsP2WJx0T8sicicNlMmYv3BMmT7SUIXej0KyICMBPh7aFv5IOjG0mWPMbkRkZYQ6r6KdUUBIibDv8cdw%2F132; wr_gender=0; wr_skey=1LcUXouR; wr_pf=NaN" --year 2024 --me malinkang --with-animation --background-color=#ffffff --track-color=#ACE7AE --special-color1=#69C16E --special-color2=#549F57 --dom-color=#EBEDF0 --text-color=#000000 WTF the design!!
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
