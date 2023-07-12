import itertools, os #python_anticaptcha, time,
import requests

class Main:
    def __init__(self):
        self.proxies = []
        self.tokens = []
        with open('proxies.txt', 'r', encoding = 'UTF-8') as file:
            for _ in file.read().splitlines():
                self.proxies.append(_)
        with open('tokens.txt', 'r', encoding = 'UTF-8') as file:
            for _ in file.read().splitlines():
                self.tokens.append(_)
        self.proxy_pool = itertools.cycle(self.proxies)
        self.token_pool = itertools.cycle(self.tokens)

    def get_proxy(self):
        proxy = next(self.proxy_pool)
        return {
            'http': 'http://%s' % proxy,
            'https': 'http://%s' % proxy
        }

    def get_token(self):
        return next(self.proxy_pool)

    def get_cookie(self):
        response = requests.Session().get('https://discord.com/app')
        cookie = str(response.cookies)
        return cookie.split('dcfduid=')[1].split(' ')[0], cookie.split('sdcfduid=')[1].split(' ')[0], cookie.split('cfruid=')[1].split(' ')[0]

    # def get_captcha(self):
    #     json = {
    #         'clientKey': capmonster_key,
    #         'task': {
    #             'type': 'HCaptchaTaskProxyless',
    #             'websiteURL': 'https://discord.com/',
    #             'websiteKey': 'a9b5fb07-92ff-493f-86fe-352a2803b3df'
    #         }
    #     }
    #     response = requests.post('https://api.capmonster.cloud/createTask', json = json)
    #     json = {
    #         'clientKey': capmonster_key,
    #         'taskId': response.json()['taskId']
    #     }
    #     while True:
    #         time.sleep(3)
    #         response = requests.post('https://api.capmonster.cloud/getTaskResult/', json = json)
    #         if response.json()['status'] == 'ready':
    #             print(response.json()['solution']['gRecaptchaResponse'])
    #             return response.json()['solution']['gRecaptchaResponse']
    def bypass_hcap(self):
        resp = requests.get('https://www.hcaptcha.com/', json={'key':'a9b5fb07-92ff-493f-86fe-352a2803b3df', 'url':'https://discord.com/'})
        return resp.json()['task_answer']
    # def get_captcha(self):
    #     client = python_anticaptcha.AnticaptchaClient(anti_captcha_key)
    #     task = python_anticaptcha.HCaptchaTaskProxyless('https://discord.com/', 'a9b5fb07-92ff-493f-86fe-352a2803b3df')
    #     job = client.createTask(task)
    #     job.join()
    #     response = job.get_solution_response()
    #     print(response)
    #     return response

    def get_fingerprint(self):
        return requests.get('https://discordapp.com/api/v9/experiments').json()['fingerprint']

    def create_session(self):
        session = requests.Session()

        # session.proxies.update(self.get_proxy())
        session.headers.update({
            'accept': '*/*',
            'accept-encoding': 'application/json',
            'accept-language': 'en-US,en;q=0.5',
            'authorization': 'MTIwMjc4OTQ1MDQzMDU0NTky.G8rj3Z.Rdfhw1JIfQ_FlP8fPmf1plUirNBc_poRLJFxxo',
            'content-length': '2',
            'content-type': 'application/json',
            'cookie': '__dcfduid=%s; __sdcfduid=%s; locale=en-US; __cfruid=%s' % self.get_cookie(),
            'origin': 'https://discord.com',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'sec-gpc': '1',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36',
            'x-context-properties': 'eyJsb2NhdGlvbiI6IkpvaW4gR3VpbGQiLCJsb2NhdGlvbl9ndWlsZF9pZCI6IjEwMjE5Mjc3NzE0Njg5OTY2MTkiLCJsb2NhdGlvbl9jaGFubmVsX2lkIjoiMTAyNDMzNDc0NTAzMjcyNDUxMCIsImxvY2F0aW9uX2NoYW5uZWxfdHlwZSI6MH0=',
            'x-debug-options': 'bugReporterEnabled',
            'x-discord-locale': 'en-US',
            # 'x-fingerprint': self.get_fingerprint(),
            'x-super-properties': 'eyJvcyI6Ik1hYyBPUyBYIiwiYnJvd3NlciI6IkNocm9tZSIsImRldmljZSI6IiIsInN5c3RlbV9sb2NhbGUiOiJlbi1VUyIsImJyb3dzZXJfdXNlcl9hZ2VudCI6Ik1vemlsbGEvNS4wIChNYWNpbnRvc2g7IEludGVsIE1hYyBPUyBYIDEwXzE1XzcpIEFwcGxlV2ViS2l0LzUzNy4zNiAoS0hUTUwsIGxpa2UgR2Vja28pIENocm9tZS8xMDYuMC4wLjAgU2FmYXJpLzUzNy4zNiIsImJyb3dzZXJfdmVyc2lvbiI6IjEwNi4wLjAuMCIsIm9zX3ZlcnNpb24iOiIxMC4xNS43IiwicmVmZXJyZXIiOiIiLCJyZWZlcnJpbmdfZG9tYWluIjoiIiwicmVmZXJyZXJfY3VycmVudCI6IiIsInJlZmVycmluZ19kb21haW5fY3VycmVudCI6IiIsInJlbGVhc2VfY2hhbm5lbCI6InN0YWJsZSIsImNsaWVudF9idWlsZF9udW1iZXIiOjE1MDQ4OSwiY2xpZW50X2V2ZW50X3NvdXJjZSI6bnVsbH0='
        })
        return session

    def join(self):
        session = self.create_session()
        print('\x1b[38;5;33m trying \x1b[0m')
        response = session.post('https://discord.com/api/v9/invites/server', json = {})
        print('\x1b[38;5;33m posted \x1b[0m')
        if response.status_code == 400:
            json = {
                'captcha_key': self.bypass_hcap(),
                'captcha_rqtoken': response.json()['captcha_rqtoken']
            }
            response = session.post('https://discord.com/api/v9/invites/server', json = json)
            print(response.status_code, response.json())
        else:
            print(response.json())

    def run(self):
        self.join()

if __name__ == '__main__':
    Main().run()
