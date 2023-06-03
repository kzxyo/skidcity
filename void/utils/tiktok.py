import json, datetime, time, aiohttp
from datetime import datetime

    
async def set_pull_type(min_cursor, max_cursor, count):
    if max_cursor and min_cursor == "0":
        return '4'
    if max_cursor == "0" and min_cursor != "0":
        return '2'

      
async def set_req_from(min_cursor, max_cursor):
    if min_cursor != "0" and max_cursor == "0":
        return 'req_from'
    else:
        return 'req_from=enter_auto'

    
async def for_you(count="1000", max_cursor="1", min_cursor="1", region="US", raw_data=False):
    try:
        pull_type = await set_pull_type(min_cursor, max_cursor, count)
        _rticket = str(time.time() * 1000).split(".")[0]
        ts = str(time.time()).split(".")[0]
        req_from = await set_req_from(min_cursor, max_cursor)
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://api2-19-h2.musical.ly/aweme/v1/feed/?type=0&max_cursor={max_cursor}&min_cursor={min_cursor}&count={count}&{req_from}&volume=0.2&pull_type={pull_type}&ts={ts}&_rticket={_rticket}&address_book_access=1&gps_access=2&os_api=25&device_type=SM-G973N&dpi=320&uoo=0&region={region}&carrier_region={region}&app_name=musical_ly") as feed_request:
                res = await feed_request.json()
                res=res["aweme_list"]
        videos = []
        for vid in res:
            if raw_data:
                videos.append(vid)
            else:
                formatted_video_data = await video_data_formatter(vid)
                videos.append(formatted_video_data)
        return videos
    except json.JSONDecodeError as e:
        print(e)

    
async def video_data_formatter(video_data):
    data = {"download_urls": {}, "author": {}, "stats": {}, "music": {}}
    data["created_at_timestamp"] = video_data["create_time"]
    data["created_at"] = str(datetime.fromtimestamp(video_data["create_time"]))
    data["video_url"] = f'https://tiktok.com/@{video_data["author"]["unique_id"]}/video/{video_data["aweme_id"]}'
    data["video_id"] = video_data["aweme_id"]
    data["download_urls"]["no_watermark"] = video_data['video']['play_addr']['url_list'][0]
    data["download_urls"]["watermark"] = video_data["video"]["play_addr"]["url_list"][2]
    data["author"]["avatar_url"] = video_data["author"]["avatar_larger"]["url_list"][0].replace("webp", "jpeg")
    data["author"]["username"] = video_data["author"]["unique_id"]
    data["author"]["nickname"] = video_data["author"]["nickname"]
    data["author"]["sec_uid"] = video_data["author"]["sec_uid"]
    data["author"]["user_id"] = video_data["author"]["uid"]
    data["description"] = video_data["desc"]
    data["video_length"] = video_data["video"]["duration"]/1000
    data["stats"] = {
        "comment_count": video_data["statistics"]["comment_count"],
        "likes": video_data["statistics"]["digg_count"],
        "downloads": video_data["statistics"]["download_count"],
        "views": video_data["statistics"]["play_count"],
        "shares": video_data["statistics"]["share_count"],
    }
    data["music"] = {
        "music_id": video_data["music"]["mid"],
        "album": video_data["music"]["album"],
        "title": video_data["music"]["title"],
        "author": video_data["music"]["author"],
         "length": video_data["music"]["duration"] 
     }
    return data