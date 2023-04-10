import pandas as pd
from pytube import Channel
from progress.bar import IncrementalBar

def  get_videos(urls: list):
    data=[]
    for url in urls:
        c = Channel(url)
        bar = IncrementalBar(c.channel_name, max=len(c.videos))
        for v in c.videos:
            watch_li = v.watch_url
            name = v.title
            data.append([name.lower(), watch_li,f"\n<a href = '{watch_li}'>{name}</a>"] )
            bar.next()
        bar.finish()
    df=pd.DataFrame(data)
    df.to_json('video.json')
    return data
get_videos(['https://www.youtube.com/channel/UC8b6w3OflVsRqzkHZink8FQ/videos','https://www.youtube.com/channel/UC8yPGNoiHdtS50UIx2G1hFw'])
