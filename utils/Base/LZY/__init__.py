import json
import logging
from logging import Logger

import requests


class LanZouYun:
    def __init__(self, cookies, headers, params, parent_logger: Logger = ""):
        if isinstance(parent_logger, str):
            self.logger = logging.getLogger("蓝奏云API")
        else:
            self.logger = parent_logger.getChild("蓝奏云API")

        self._host_url = 'https://pan.lanzouo.com'
        self._doupload_url = 'https://pc.woozooo.com/doupload.php'
        self._account_url = 'https://pc.woozooo.com/account.php'
        self._mydisk_url = 'https://pc.woozooo.com/mydisk.php'
        self._download_url="https://developer-oss.lanrar.com"
        self.cookies = cookies
        self.headers = headers
        self.params = params
        self._uid = self.cookies.get("ylogin")

    def login(self):
        response = requests.get(self._account_url, params=self.params, cookies=self.cookies, headers=self.headers)
        if response.status_code == 200:
            print("Login successful")
            return True
        else:
            print("Login failed")
            return False

    def get_dir_list(self):
        data = {
            'task': '47',
            'folder_id': '-1',
        }
        response = requests.post(
            self._doupload_url,
            params=self.params,
            cookies=self.cookies,
            headers=self.headers,
            data=data
        )
        print(json.dumps(response.json(), indent=4, ensure_ascii=False))

    def get_file_list(self):
        data = {
            'task': '5',
            'folder_id': '12590431',
            'pg': '1',
            'vei': 'BFVUVgFTAw8DAVNWXFI=',
        }
        response = requests.post(
            self._doupload_url,
            params=self.params,
            cookies=self.cookies,
            headers=self.headers,
            data=data
        )
        print(json.dumps(response.json(), indent=4, ensure_ascii=False))

    def get_file_out_url(self):
        cookies = {
            '_uab_collina': '175854964418338165486867',
            'ylogin': '4778246',
            'uag': '941e002410f07c20e566af45eba01d2f',
            'phpdisk_info': 'V2dTZg1oV2MOPgVhDmIDUFA0UllcNAJmVWJTNQUyCjtRYgM3DGYCPwYwDldcNFBuUWIAMglhAmQDYgQ2BDEBMlcyU2cNOlc6DjQFNg5iAz9QZVJpXDACZlVuUzMFZQo8UWwDNww9AmgGPA46XA9QO1EyADYJZgJkAzMEYwQ0ATtXYlNl',
            'PHPSESSID': 'tdtheh23fsvf1mmghdsa1gjml6rort4c',
            'folder_id_c': '12590431',
        }

        headers = {
            'accept': 'application/json, text/javascript, */*; q=0.01',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
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
            # 'cookie': '_uab_collina=175854964418338165486867; ylogin=4778246; uag=941e002410f07c20e566af45eba01d2f; phpdisk_info=V2dTZg1oV2MOPgVhDmIDUFA0UllcNAJmVWJTNQUyCjtRYgM3DGYCPwYwDldcNFBuUWIAMglhAmQDYgQ2BDEBMlcyU2cNOlc6DjQFNg5iAz9QZVJpXDACZlVuUzMFZQo8UWwDNww9AmgGPA46XA9QO1EyADYJZgJkAzMEYwQ0ATtXYlNl; PHPSESSID=tdtheh23fsvf1mmghdsa1gjml6rort4c; folder_id_c=12590431',
        }
        data = {
            'task': '22',
            'file_id': '255026271',
        }

        response = requests.post('https://pc.woozooo.com/doupload.php', cookies=cookies, headers=headers, data=data)
        print(json.dumps(response.json(), indent=4, ensure_ascii=False))

    def get_file_direct_url(self):
        params = {
            'file': '255026271',
        }

        data = {
            'action': 'downprocess',
            'sign': 'AWdSbA4_aATABCFZpCjpWalU9BDRfNQAyBzIHN1c5BjAAMVMiWnNVPFUyAGFRMFNqUT0GMlA9BDBWYFtk',
            'kd': '1',
            'p': 'xbjf',
        }

        response = requests.post('https://xbjf.lanzoul.com/ajaxm.php', params=params, cookies=self.cookies, headers=self.headers, data=data)
        print(json.dumps(response.json(), indent=4, ensure_ascii=False))

    def download_file(self):
        temp_url = self._download_url+"/file"+"/"+"?AGZQbgo7AzJTWlZuU2YBbVFuVGxQPVRmAzYEN10sU2JQaVIoWjUAZgILC2wBZFR4VTtUZwByADBXZFZ+XThaawA4UDYKZwNgUytWcFNpAWdRLVQ3UGZUOgNhBF1daFM2UG1SN1oyAGECZAtvAWNUZ1U4VGAAeQBkVyNWbV04Wm0AM1AzCmMDYVMjVnBTdwE9UTlUYVA9VGMDKwQyXThTfVBiUjdaKAAxAjcLbAFkVGdVbVRlAGsAZldpVmBdMFptAGRQMgpkA25TZlY1U2YBYVE/VGZQbVQzA2cEZ11kU2BQaFJnWjEAegIkCzMBMlRzVXpUIgA6AHBXOVY0XTxabwA3UDAKbwNlUzFWNlMhAXRRYlQ8UGpUMAM5BDNdNlNnUGhSM1o2AGcCYAttAWVUe1UhVHcAOQBuVydWbV0wWmwANVA/CmEDZlM3VjBTMQE2US1UJFB/VCEDOQQzXTZTZ1BoUjBaMgBnAmILZQFkVHNVelQ4AC8AP1diVmJdM1p1ADFQMQpvA3lTMVYxUykBMlE9VH9QKVQyA2sEdV1vUw1QM1JuWjoAZAJ6C3sBIVQsVX9UNAAAAHdXMVZtXTE="
        response = requests.get(temp_url, cookies=self.cookies, headers=self.headers, stream=True)
        with open('downloaded_file', 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        print("File downloaded successfully")
    def delete(self):
        pass


if __name__ == "__main__":
    cookies = {
        '_uab_collina': '175854964418338165486867',
        'ylogin': '4778246',
        'uag': '941e002410f07c20e566af45eba01d2f',
        'phpdisk_info': 'V2dTZg1oV2MOPgVhDmIDUFA0UllcNAJmVWJTNQUyCjtRYgM3DGYCPwYwDldcNFBuUWIAMglhAmQDYgQ2BDEBMlcyU2cNOlc6DjQFNg5iAz9QZVJpXDACZlVuUzMFZQo8UWwDNww9AmgGPA46XA9QO1EyADYJZgJkAzMEYwQ0ATtXYlNl',
        'PHPSESSID': 'tdtheh23fsvf1mmghdsa1gjml6rort4c',
        'folder_id_c': '-1',
    }

    headers = {
        'accept': 'application/json, text/javascript, */*; q=0.01',
        'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
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
        # 'cookie': '_uab_collina=175854964418338165486867; ylogin=4778246; uag=941e002410f07c20e566af45eba01d2f; phpdisk_info=V2dTZg1oV2MOPgVhDmIDUFA0UllcNAJmVWJTNQUyCjtRYgM3DGYCPwYwDldcNFBuUWIAMglhAmQDYgQ2BDEBMlcyU2cNOlc6DjQFNg5iAz9QZVJpXDACZlVuUzMFZQo8UWwDNww9AmgGPA46XA9QO1EyADYJZgJkAzMEYwQ0ATtXYlNl; PHPSESSID=tdtheh23fsvf1mmghdsa1gjml6rort4c; folder_id_c=-1',
    }

    params = {
        'uid': '4778246',
    }
    lzy = LanZouYun(cookies, headers, params)
    # lzy.login()
    # lzy.get_dir_list()
    # lzy.get_file_list()
    # lzy.get_file_out_url()
    lzy.download_file()
