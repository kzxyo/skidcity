from ttapi import TikTokApi

tiktok = TikTokApi(debug=True)

fyp_videos = await tiktok.feed.for_you()

for video in fyp_videos:
    await tiktok.video.download_video(video["video_url"])