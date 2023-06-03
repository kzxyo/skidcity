from ttapi import TikTokApi


tiktok = TikTokApi(debug=True)

await tiktok.video.download_video("https://www.tiktok.com/t/ZTRf85djY/", watermark=True) # Watermarked
await tiktok.video.download_video("https://vm.tiktok.com/ZMNnX3Q4q/", watermark=False) # No watermark