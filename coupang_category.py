import hmac
import hashlib
import urllib.parse
import urllib.request
import ssl
import json
from time import strftime, gmtime, time


def yaml_load(key_path='keys.yaml'):
    import yaml
    
    with open(key_path) as f:
        keys = yaml.load(f, Loader=yaml.FullLoader)

    return keys


class CategoryFinder:
    def __init__(self):
        self.init_time = time()
        self.keys = yaml_load()
        self.method = "POST"
        self.path = "/v2/providers/openapi/apis/api/v1/categorization/predict"
        self.authorization = self.generate_hmac()
        

    def generate_hmac(self):
        method = self.method
        path = self.path

        # replace with your own accesskey
        accesskey = self.keys['ACCEESS_KEY']
        # replace with your own secretKey
        secretkey = self.keys['SECRET_KEY']

        date_GMT = strftime('%y%m%d', gmtime())
        time_GMT = strftime('%H%M%S', gmtime())
        datetime = date_GMT + 'T' + time_GMT + 'Z'

        message = datetime + method + path

        # ********************************************************#
        # authorize, demonstrate how to generate hmac signature here
        signature = hmac.new(secretkey.encode('utf-8'), message.encode('utf-8'), hashlib.sha256).hexdigest()
        authorization = "CEA algorithm=HmacSHA256, access-key=" + accesskey + ", signed-date=" + datetime + ", signature=" + signature
        return authorization

    def get_coup_category(self, keyword):
        path = self.path
        method = self.method

        now_time = time()
        if (now_time - self.init_time) > 210:
            print('Regenerate HMAC')
            self.authorization = self.generate_hmac()

        authorization = self.authorization

        strjson = {'productName': keyword}
        data = json.dumps(strjson).encode("utf-8")

        url = "https://api-gateway.coupang.com" + path

        # print('BEGIN REQUEST++++++++++++++++++++++++++++++++++++')
        req = urllib.request.Request(url)

        req.add_header("Content-type", "application/json;charset=UTF-8")
        req.add_header("Authorization", authorization)

        req.get_method = lambda: method

        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

        # print('RESPONSE++++++++++++++++++++++++++++++++++++')
        ret = []
        try:
            resp = urllib.request.urlopen(req, data, context=ctx)
        except urllib.request.HTTPError as e:
            print(e.code)
            print(e.reason)
            print(e.fp.read())
        except urllib.request.URLError as e:
            print(e.errno)
            print(e.reason)
            print(e.fp.read())
        else:
            # 200
            body = resp.read().decode(resp.headers.get_content_charset())
            result = json.loads(body)
            if result['code'] == 200:
                ret = [result['data']['predictedCategoryName'],
                       result['data']['predictedCategoryId']]

        return ret


if __name__ == '__main__':
    while True:
        keyword = input('상품명: ')
        cat = CategoryFinder()
        print(cat.get_coup_category(keyword), end='\n')
