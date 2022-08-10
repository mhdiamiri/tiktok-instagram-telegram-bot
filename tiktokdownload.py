import re
import json
import requests
from tenacity import *
import wget

@retry(stop=stop_after_attempt(3), wait=wait_random(min=1, max=2))
def tiktok(original_url):
    headers =  {
        'user-agent': 'Mozilla/5.0 (Linux; Android 8.0; Pixel 2 Build/OPD3.170816.012) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Mobile Safari/537.36 Edg/87.0.664.66'
    }
    if '@' not in original_url:
        response = requests.get(url=original_url, headers=headers, allow_redirects=False)
        true_link = response.headers['Location'].split("?")[0]
        original_url = true_link
        if '.html' in true_link:
            response = requests.get(url=true_link, headers=headers, allow_redirects=False)
            original_url = response.headers['Location'].split("?")[0]

    try:
        video_id = re.findall('/video/(\d+)?', original_url)[0]
        try:
            tiktok_headers = {
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                "authority": "www.tiktok.com",
                "Accept-Encoding": "gzip, deflate",
                "Connection": "keep-alive",
                "Host": "www.tiktok.com",
                "User-Agent": "Mozilla/5.0  (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) coc_coc_browser/86.0.170 Chrome/80.0.3987.170 Safari/537.36",
            }
            html = requests.get(url=original_url, headers=tiktok_headers)
            resp = re.search('"ItemModule":{(.*)},"UserModule":', html.text).group(1)
            resp_info = ('{"ItemModule":{' + resp + '}}')
            result = json.loads(resp_info)            
        except:
            return None
        tiktok_api_link = 'https://api.tiktokv.com/aweme/v1/aweme/detail/?aweme_id={}'.format(video_id)
        response = requests.get(url=tiktok_api_link, headers=headers).text
        result = json.loads(response)
        for i in result["aweme_detail"]:
            if i != 'image_post_info':
                nwm_video_url = result["aweme_detail"]["video"]["play_addr"]["url_list"][0]
                return nwm_video_url
    except Exception as e:
        return None

def downloader(video_data, video_name):
    filename = f'{video_name}.mp4'
    try:
        wget.download(video_data, filename)
        return filename
    except:
        return None
