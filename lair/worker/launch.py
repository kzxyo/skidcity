from xxhash import xxh64_hexdigest
from worker2 import Workers
import asyncio
from multiprocessing import Process, Pool

proxy = "http://root:wise@144.172.67.168:31280"
bot_workers = [
    'MTAzNzM3OTQ5ODA5MTQ5OTU3MA.GkxMhR.eW2CS7EKct8zBX7-TZiOSBIalt2cDt_56sxApM',
    'MTAzNDQ4MzE3NzA0MzAxMzc1Mg.GPAZMp.votrj7r33DkWHo8G45WaSiyF82qQZlNS5afAww',
    'ODkzMDgwMDk0MzQ2NzIzMzUw.GplXhU.Pv4-Bz6SxVESU5BdonLizL4LP_kr4CcWxLhyAY'
]
runners = []

if __name__ == "__main__":
    try:
        for token in bot_workers:
            process = Process(target=Workers, args=(token,))
            process.start()
            runners.append(process)
    except:
        pass
    finally:
        for process in runners:
            process.terminate()
            process.kill()
            process.close()