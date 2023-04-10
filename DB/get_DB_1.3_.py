import pandas as pd
import grequests
from requests_html import HTMLSession,HTML
from progress.bar import IncrementalBar
import numpy as np
from markdownify import markdownify as md

# Creating an HTML session to interact with the website
session = HTMLSession()

# Base URL of the website
base_url = "https://www.ukrlib.com.ua/"

# Replacements for different types of pages
rplc_df={'Читати скорочено':'short','Скорочено':'short','Аналіз':'review'}

def get_html():
    # Constructing URLs for different pages of the website
    urls = [f'{base_url}school{add}/?klas={clas}' for add in ['', '-zl'] for clas in range(5, 12)]
    # Sending concurrent GET requests to the URLs using grequests
    rs = (grequests.get(u) for u in urls)
    # Adding 'charset' attribute to the HTML of the page
    html_arr = [HTML(html = html.text.replace('charset="windows-1251"',''),url=base_url) for html in grequests.map(rs)]
    # returnin a dictionary of URLs and the respective HTMLs
    return dict(zip(urls,html_arr))



def get_data(li):
    data_=''
    # Check if the page is a review page
    if not 'review' in li:
        # Get the HTML of the page
        li_site = session.get(li).html
        # Filter the articles that have a h2 tag
        array = list(filter(lambda x: not x.find('h2', first=True)== None, li_site.find('article.post')))
        for x in array:
            # Extract the title of the book and the summary 
            data_+=f'<b>{x.find("h2",first=True).text}</b>\n{x.find("a")[-1].text}\n{get_download(list(x.find("a")[-1].absolute_links)[0])}\n'
    else:
        # Get the HTML of the page
        li_site = session.get(li).html
        for x in li_site.find('article.post.post-preview h2'):
            # Extract the title of the book and the download links
            data_+=f'<b>{x.text}</b>\n{ get_download(list(x.absolute_links)[0], review=True)}\n'
    if not len(data_):
        if 'printit' in li:
            # Extract the download links
            data_=f'Читати повністю →\n{get_download(li)}'
        else:
            # Extract the online link
            data_ = f'<a href = "{li}">Онлайн</a>'
    # Return the extracted data
    return data_


def get_download(link,review = False):
    # Construct the download link
    link_down = link.replace('printit', 'getfile')
    types = [[link, 'Онлайн']] if review else [[f'{link_down}&type=1', 'PDF'], [f'{link_down}&type=2', 'EPUB'], [link, 'Онлайн']]
    result = [f" <a target='_blank' href = '{f[0]}'>{f[1]}</a>" for f in types]
    # Return the download links
    return ''.join(result)

# Function to read JSON files
def read_json(name): return pd.read_json(f'{name}.json')

# Reading JSON files
pres=read_json('pres')
audio_base = read_json('video')

def parse():
    df_book = []
    df_auhtor = []
    html_dict= get_html()
    for type in ['Світова','Українська']:
        for grade in range(5, 12):
            add = '-zl' if type == "Світова" else ''
            r = html_dict[f'{base_url}school{add}/?klas={grade}']
            auhtor_block = list(filter(lambda x: not 'add' in str(x), r.find('div.books.books-large.bl-bio')))
            
            bar = IncrementalBar(f'{grade} клас {type}', max=len(auhtor_block))
            for block in auhtor_block:
                author = block.find('h2', first=True).text
                bio_data, image_link = "", ""
                image_link = 'https://www.ukrlib.com.ua' + block.find('img', first=True).attrs['src']
                
                if not "Автор Невідомий" in author:
                    bio_data = md(get_data(list(block.find('h2', first=True).absolute_links)[0]))
                else: 
                    bio_data=""
                    author= author+' (фолкльор)'
                
                for i in list(filter(lambda x: not x.attrs, block.find('li'))):
                    name = i.find('a', first=True).text
                    link = list(i.find('a', first=True).absolute_links)[0]
                    book_data = {'name':name,'grade':grade,'type':type, 'down_link':md(f'<b>{name}</b>\n{get_download(link)}\n'),'audio':'','time':''}
                    try:
                        DF=audio_base[audio_base[0].str.contains(name.lower())]
                        if len(DF): book_data['audio'] = md(f"<b>Аудіокниги:</b>{''.join(list(DF[2]))}")
                    except: pass
                    for f in i.find('span.short')[::-1]:
                        if "🕒" in f.text:
                            book_data['time'] += md(f"<i>{f.text}</i>\n")
                        elif f.text in ['Читати скорочено','Скорочено','Аналіз']:
                            book_data[rplc_df[f.text]]=md(f"<b>{f.text}</b>\n{get_data(list(f.absolute_links)[0])}\n")
                    df_book.append(book_data)
                pres_data =''
                try:
                    Df='\n'.join(np.intersect1d(*[list(pres[pres[0].str.contains(x)][1]) for x in author.lower().split(' ')]))
                    if len(Df): pres_data=md(Df)
                except Exception as e: pass #print(e)
                df_auhtor.append({'auhtor':author,'grade':grade,'type':type,'img_src':image_link, 'bio':bio_data,'pres_data':pres_data})
                bar.next()
    df_book = pd.DataFrame(columns=['name', 'grade','type', 'author', 'time','audio','review','short'],data  = df_book)
    df_auhtor = pd.DataFrame(columns=['author','grade','type', 'bio', 'img_src','pres_data'],data = df_auhtor)
    df_auhtor.to_csv('Auhtors.csv')
    df_book.to_csv('Books.csv')
    
if __name__ == "__main__":
    import time

    start_time = time.time()
    parse()
    # code you want to measure
    end_time = time.time()

    print("Time taken: ", end_time - start_time)
