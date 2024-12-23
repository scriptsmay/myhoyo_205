"""
@Project   : genshinhelper
@Author    : y1ndan
@Blog      : https://www.yindan.me
@GitHub    : https://github.com/y1ndan
"""

from .exceptions import GenshinHelperException
from .core import Client, get_headers
from .utils import request, log, merge_dicts, nested_lookup, extract_subset_of_dict, config, _

_LANG_DICT = {
    'zh': 'zh-cn',
    'en': 'en-us'
}


class Genshin(Client):
    def __init__(self, cookie: str = None):
        super().__init__(cookie)
        self.headers = get_headers(oversea=True)
        self.api = 'https://hk4e-api-os.mihoyo.com'
        self.act_id = 'e202102251931481'
        self.game_biz = 'hk4e_global'
        self.required_keys.update({
            'total_sign_day', 'today', 'is_sign', 'first_bind',
            'current_primogems', 'current_mora'
        })

        self.lang = _LANG_DICT.get(config.LANGUAGE, '')
        self.roles_info_url = 'https://api-os-takumi.mihoyo.com/binding/api/getUserGameRolesByCookie?game_biz={}'
        self.sign_info_url = f'{self.api}/event/sol/info?lang={self.lang}&act_id={self.act_id}'
        self.rewards_info_url = f'{self.api}/event/sol/home?lang={self.lang}&act_id={self.act_id}'
        self.sign_url = f'{self.api}/event/sol/sign?lang={self.lang}'

        self._travelers_dairy = None
        self.travelers_dairy_url = f'{self.api}/event/ysledgeros/month_info?lang={self.lang}&' + 'uid={}&region={}&month={}'

    @property
    def sign_info(self):
        if not self._sign_info:
            log.info(_('Preparing to get check-in information ...'))
            url = self.sign_info_url
            response = request('get', url, headers=self.headers, cookies=self.cookie).json()
            # log.debug(response)
            data = nested_lookup(response, 'data', fetch_first=True)
            if data:
                del data['region']
            self._sign_info.append(extract_subset_of_dict(data, self.required_keys))
        return self._sign_info

    @property
    def travelers_dairy(self):
        roles_info = self.roles_info
        self._travelers_dairy = [
            self.get_travelers_dairy(i['game_uid'], i['region'])
            for i in roles_info
        ]
        return self._travelers_dairy

    def get_travelers_dairy(self, uid: str, region: str, month: int = 0):
        log.info(_("Preparing to get traveler's dairy ..."))
        url = self.travelers_dairy_url.format(uid, region, month)
        response = request('get', url, headers=self.headers, cookies=self.cookie).json()
        # log.debug(response)
        return nested_lookup(response, 'data', fetch_first=True)

    @property
    def month_dairy(self):
        raw_month_data = nested_lookup(self.travelers_dairy, 'month_data')
        return [
            extract_subset_of_dict(i, self.required_keys)
            for i in raw_month_data
        ]

class GlobalGenshin(Client):
    def __init__(self, cookie: str = None):
        super().__init__(cookie)
        self.headers = get_headers(oversea=True)
        self.api = 'https://sg-hk4e-api.hoyolab.com'
        self.bbsapi = 'https://bbs-api-os.hoyolab.com'
        self.act_id = 'e202102251931481'
        self.game_biz = 'hk4e_global'
        self.required_keys.update({
            'total_sign_day', 'today', 'is_sign',
            'sign_cnt_missed', 'region'
        })

        self.lang = _LANG_DICT.get(config.LANGUAGE, '')
        # 本日签到信息
        self.sign_info_url = f'{self.api}/event/sol/info?lang={self.lang}&act_id={self.act_id}'
        # resign info
        self.resign_info_url = f'{self.api}/event/sol/resign_info?lang={self.lang}&act_id={self.act_id}'
        # 本月活动信息
        self.rewards_info_url = f'{self.api}/event/sol/home?lang={self.lang}&act_id={self.act_id}'
        # 签到提交url
        self.sign_url = f'{self.api}/event/sol/sign?lang={self.lang}'

        self.roles_info_url = f'{self.bbsapi}/game_record/app/card/api/getGameRecordCard' + '?uid={}'


    @property
    def sign_info(self):
        if not self._sign_info:
            log.info(_('Preparing to get check-in information ...'))
            url = self.sign_info_url
            response = request('get', url, headers=self.headers, cookies=self.cookie, timeout=50).json()
            log.info(response)
            data = nested_lookup(response, 'data', fetch_first=True)
            # if data:
            #     del data['region']
            self._sign_info.append(extract_subset_of_dict(data, self.required_keys))
        return self._sign_info

    @property
    def user_data(self):
        sign_info = self.sign_info
        current_reward = self.current_reward

        for i in range(len(sign_info)):
            d2 = sign_info[i]
            d3 = current_reward[i]
            # ps region of d2 is empty
            merged = merge_dicts(d2, d3)
            self._user_data.append(merged)
        return self._user_data


class HKStarRail(Client):
    def __init__(self, cookie: str = None):
        super().__init__(cookie)
        
        tmp_key = extract_subset_of_dict(self.cookie, ['account_id_v2'])
        self.uid = tmp_key.get('account_id_v2')
        # log.info(self.uid)

        # return
        self.headers = get_headers(oversea=True)
        self.api = 'https://sg-public-api.hoyolab.com'
        # self.api = 'https://bbs-api-os.hoyolab.com'
        self.bbsapi = 'https://bbs-api-os.hoyolab.com'
        self.act_id = 'e202303301540311'
        self.game_biz = 'hkrpg_global'
        self.required_keys.update({
            'total_sign_day', 'today', 'is_sign',
            'sign_cnt_missed', 'region', 'game_role_id'
        })

        self.lang = _LANG_DICT.get(config.LANGUAGE, '')

        # 本日签到信息
        self.sign_info_url = f'{self.api}/event/luna/hkrpg/os/info?lang={self.lang}&act_id={self.act_id}'
        # resign info
        self.resign_info_url = f'{self.api}/event/luna/hkrpg/os/resign_info?lang={self.lang}&act_id={self.act_id}'
        # 本月活动信息
        self.rewards_info_url = f'{self.api}/event/luna/hkrpg/os/home?lang={self.lang}&act_id={self.act_id}'
        # 签到提交url
        self.sign_url = f'{self.api}/event/luna/hkrpg/os/sign?lang={self.lang}'

        # 角色卡片信息
        self.roles_info_url = f'{self.api}/event/game_record/card/wapi/getGameRecordCard?uid={self.uid}'
    @property
    def sign_info(self):
        if not self._sign_info:
            log.info(_('Preparing to get check-in information ...'))
            url = self.sign_info_url
            response = request('get', url, headers=self.headers, cookies=self.cookie, timeout=50).json()
            # log.info(response)
            data = nested_lookup(response, 'data', fetch_first=True)
            # if data:
            #     del data['region']
            self._sign_info.append(extract_subset_of_dict(data, self.required_keys))
        return self._sign_info

    