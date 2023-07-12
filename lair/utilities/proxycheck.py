import requests
import threading
import queue

q = queue.Queue()

with open("/root/lair-v2/p.txt", "r") as f:
    proxies = f.read().split("\n")
    for p in proxies:
        q.put(p)


def check():
    global q
    while not q.empty():
        proxy = q.get()
        try:
            res = requests.get("http://ipinfo.io/json", proxies={"http": proxy, "https": proxy})

        except:
            continue

        if res.status_code == 200:
            with open("/root/lair-v2/proxies.txt", "a") as f:
                f.write(proxy + "\n")


for _ in range(10):
    threading.Thread(target=check).start()