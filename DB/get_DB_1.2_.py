import aiohttp
import asyncio
from requests_html import HTML
import numpy as np
import pandas as pd
from alive_progress import alive_bar
import json
# from functools import cache

base_url = "https://www.ukrlib.com.ua/"
dov_url='https://dovidka.biz.ua/'

def get_domain(url,prime):
    url = url.replace(base_url,'')
    url=url[:url.index('/')]
    return url if not prime else ''

# 🔍 Web scraping tools


async def get_html(urls,prime=False,base_url_ = base_url):
    html_arr = []
    # Create an aiohttp client session
    async with aiohttp.ClientSession() as session:
        # create a list of tasks to fetch the URLs
        tasks = [asyncio.ensure_future(fetch(session, url)) for url in urls]
        # Wait for all tasks to complete and store the results
        html_arr = [HTML(html = html.replace('charset="windows-1251"',''),url=base_url_+get_domain(url,prime)+'/') for html,url in zip(await asyncio.gather(*tasks),urls)]
    # Return the dictionary of URLs and the corresponding HTML objects
    return html_arr
    
async def fetch(session, url):
    # Fetch the text of a single URL
    async with session.get(url) as response:
        return await response.text()


def get_data(li,html,type_):
    array = html.find('article.post')
    if len(array):
        # 🔍 Determine the type of data to extract
        if type_ in ['add','bio']:
            # 🔍 Filter the articles that contain the 'h2' element
            return '\n'.join([f'<b>{x.find("h2",first=True).text}</b>\n{x.find("a")[-1].text}\n{get_download(list(x.find("a")[-1].absolute_links)[0])}' for x in list(filter(lambda x: not x.find('h2', first=True)== None, html.find('article.post')))])
        elif type_ =='review':
            return '\n'.join([f'<b>{x.find("h2",first=True).text}</b>\n{get_download(list(x.absolute_links)[0], review=True)}' for x in html.find('article.post.post-preview h2')])
    else:
        return f'Читати повністю →\n{get_download(li)}' if type_ in ['add','bio'] else f'<a href = "{li}">Онлайн</a>'



def get_download(link,review = False):
    link_down = link.replace('printit', 'getfile')
    types = [[link, 'Онлайн']] if review else [[f'{link_down}&type=1', 'PDF'], [f'{link_down}&type=2', 'EPUB'], [link, 'Онлайн']]
    result = [f" <a target='_blank' href = '{f[0]}'>{f[1]}</a>" for f in types]
    return ''.join(result)



def read_json(name): return pd.read_json(f'resource/{name}.json')

pres=read_json('pres')
audio_base = read_json('video')

# @cache
async def parse():
    # Create a list of URLs to be fetched
    urls = [f'{base_url}school{add}/?klas={clas}' for add in ['', '-zl'] for clas in range(5, 12)]
    html_dict  = await get_html(urls,True)
    html_dict = dict(zip(urls,html_dict))
    data_all={}
    for type in ['Світова','Українська']:
        for clas in range(5, 12):
            add = '-zl' if type == "Світова" else ''
            r = html_dict[f'{base_url}school{add}/?klas={clas}']
            auhtor_block = list(filter(lambda x: not 'add' in str(x), r.find('div.bl-bio')))
            with alive_bar(len(auhtor_block),  title=f'{clas} клас {type}') as bar:
                bios_l = [list(block.find('h2', first=True).absolute_links)[0] for block in auhtor_block]
                bios=await get_html(bios_l)
                bar.text = f'-> Loading bios'
                data = {'books':{},'pres':{}}
                # #chronologichna 
                authors=[block.find('h2', first=True).text for block in auhtor_block]
                # html_auth = await get_html([f'https://dovidka.biz.ua/?s={auth.lower().replace(" ","+")}+хронологічна+таблиця' for auth in authors],base_url_=dov_url)
                # urls_auth_dov = [x.find('div.post-card__title span a') for x in  html_auth]
                
                for index,block in enumerate(auhtor_block):
                    author = authors[index]
                    bar.text = f'-> {author}'
                    bio_data, image_link = "", ""
                    image_link = 'https://www.ukrlib.com.ua' + block.find('img', first=True).attrs['src']
                    if not "Автор Невідомий" in author:
                        bio_data = get_data(bios_l[index],bios[index],'bio')
                    else: bio_data=""
                    
                    # auth_dov = urls_auth_dov[index]
                    # if len(auth_dov):
                    #     arc=auth_dov[0]
                    #     bio_data+=f'<a href ="{list(arc.absolute_links)[0]}">{arc.text}</a>'
                        
                    books_data = {}
                    
                    book_blocks = [list(filter(lambda x: not x.attrs, block.find('li'))) for block in auhtor_block]
                    for index,i in enumerate(book_blocks[index]):
                        name = i.find('a', first=True).text
                        bar.text = f'->> {name}'
                        link = list(i.find('a', first=True).absolute_links)[0]
                        text = {'Читати повністю':f'<b>{name}</b>\n{get_download(link)}\n'}
                        
                        DF = audio_base[audio_base[0].str.find(name.lower()) != -1]
                        bar.text = f'->>> {name} audio'
                        if len(DF): 
                            text['Аудіокниги'] = f"<b>Аудіокниги:</b>{''.join(list(DF[2]))}"
                        add_min = i.find('span.short')
                        if len(add_min):
                            bar.text = f'->>> {name} time'
                            #time
                            if not "🕒" == add_min[-1].text[0]:
                                text['Читати повністю'] += f"<i>🕒 менше 15 хвилин</i>\n"
                            else:
                                text['Читати повністю'] += f"<i>{add_min[-1].text}</i>\n"
                                
                            # addings
                            sorted_adds = [f for f in add_min if f.text in ['Читати скорочено','Скорочено','Аналіз']]
                            if len(sorted_adds):
                                links= [list(f.absolute_links)[0] for f in sorted_adds]
                                htmls= await get_html(links)
                                for f,link,html in zip(sorted_adds,links,htmls):
                                    text[f.text]=get_data(link,html,('review' if 'Аналіз' == f.text else 'add'))
                        
                        books_data[name]=text
                    data['books'][author]={'img_src':image_link, 'bio':bio_data,'books':books_data}
                    try:
                        Df='\n'.join(np.intersect1d(*[list(pres[pres[0].str.find(x) != -1][1]) for x in author.lower().split(' ')]))
                        if len(Df): 
                            data['pres'][f'🎓{author}']=Df
                    except Exception as e: pass #print(e)
                    data_all[f'_{clas} клас {type}']=data
                    bar()
    json_object = json.dumps(data_all)
    with open(f'resource/data_all.json', "w") as outfile:
        outfile.write(json_object)
    
# 🚀 Execute the parse function
if __name__ == "__main__":
    asyncio.run(parse())
    