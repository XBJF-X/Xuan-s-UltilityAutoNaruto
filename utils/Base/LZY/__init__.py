import requests


class LanZouYun:
    def __init__(self, cookies, headers, params):
        self._host_url = 'https://pan.lanzouo.com'
        self._doupload_url = 'https://pc.woozooo.com/doupload.php'
        self._account_url = 'https://pc.woozooo.com/account.php'
        self._mydisk_url = 'https://pc.woozooo.com/mydisk.php'
        self.cookies = cookies
        self.headers = headers
        self.params = params
        self._uid = None

    def login(self):
        self._uid = self.cookies.get("ylogin")
        response = requests.get(self._account_url, params=self.params, cookies=self.cookies, headers=self.headers)
        if response.status_code == 200:
            print("Login successful")
            return True
        else:
            print("Login failed")
            return False
    def get_dir_list(self):
        pass


if __name__ == "__main__":
    cookies = {
        'PHPSESSID': 'rupbo949m2a49mjc6b7i9r8q2s7hoa97',
        '_uab_collina': '175854964418338165486867',
        'ylogin': '4778246',
        'uag': '941e002410f07c20e566af45eba01d2f',
        'phpdisk_info': 'V2dTZg1oV2MOPgVhDmIDUFA0UllcNAJmVWJTNQUyCjtRYgM3DGYCPwYwDldcNFBuUWIAMglhAmQDYgQ2BDEBMlcyU2cNOlc6DjQFNg5iAz9QZVJpXDACZlVuUzMFZQo8UWwDNww9AmgGPA46XA9QO1EyADYJZgJkAzMEYwQ0ATtXYlNl',
        'folder_id_c': '12590431',
    }

    headers = {
        'accept': 'application/json, text/javascript, */*; q=0.01',
        'accept-language': 'zh-CN,zh;q'
                           '=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'origin': 'https://pc.woozooo.com',
        'priority': 'u=1, i',
        'referer': 'https://pc.woozooo.com/mydisk.php?item=files&action=index&u=4778246',
        'sec-ch-ua': '"Microsoft Edge";v="141", "Not?A_Brand";v="8", "Chromium";v="141"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36 Edg/141.0.0.0',
        'x-requested-with': 'XMLHttpRequest',
        # 'cookie': 'PHPSESSID=rupbo949m2a49mjc6b7i9r8q2s7hoa97; _uab_collina=175854964418338165486867; ylogin=4778246; uag=941e002410f07c20e566af45eba01d2f; phpdisk_info=V2dTZg1oV2MOPgVhDmIDUFA0UllcNAJmVWJTNQUyCjtRYgM3DGYCPwYwDldcNFBuUWIAMglhAmQDYgQ2BDEBMlcyU2cNOlc6DjQFNg5iAz9QZVJpXDACZlVuUzMFZQo8UWwDNww9AmgGPA46XA9QO1EyADYJZgJkAzMEYwQ0ATtXYlNl; folder_id_c=-1',
    }

    params = {
        'uid': '4778246',
    }
    lzy = LanZouYun(cookies, headers, params)
    lzy.login()

