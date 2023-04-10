import pandas as pd
import random as rnd
import json
from telegraph import Telegraph

telegraph = Telegraph()
telegraph.create_account(short_name='1337')

def create_tlgrph(title,text):
    response = telegraph.create_page(
    title,
    html_content=text.replace('\n','<br>')
    )  
    link = f'<a href = "{response["url"]}">{title}</a>'
    return link

class BSCH:
    def __init__(self, name):
        main_DB=json.load(open(f"resource/Workbooks.json"))[name]
        self.data_ = main_DB
        self.subj =list(self.data_.keys())

class DB:
    def __init__(self, name):
        main_DB=json.load(open(f"resource/data_all.json"))[f'_{name}']
        self.name=name
        self.data_ = pd.DataFrame(main_DB[f'books'])
        self.pres_data = main_DB['pres']
        self.authors =list(self.data_.columns)

    def list_all(self):
        text=''
        for item in self.authors:
            text+=f'<h3><b>{item}</b></h3><ul>'
            for book in self.data_[item]['books'].keys():
                read_all=self.data_[item]['books'][book]['Читати повністю'].split('\n')[1]
                text+=f"<li><b>{book}</b> <br><i>{read_all}</i></li>"
            text+='</ul>'
        return create_tlgrph(f'Список творів ({self.name})',text)

    
    def get_books(self, author):
        return list(self.data_[author]['books'].keys())
    
    def get_bio(self, author):
        return dict(self.data_[author][:2])
    
    def get_content_tlgrph(self, author, name):
        book_data = dict(self.data_)[author]['books'][name]
        parts= book_data.keys()
        text =f'<h3>📑{author}</h3><h3>🔖{name}</h3><br>'
        for i in parts:
            text+=f'<h3>{i}</h3><br><ul><li><p>{book_data[i]}</p></li></ul>'
        return [name,text]
    
    def get_content(self, author, name):
        return dict(self.data_)[author]['books'][name]

    def get_rnd(self):
        self.rnd_auth=rnd.choice(self.authors)
        self.rnd_book=rnd.choice(self.get_books(self.rnd_auth))
        BIO =self.get_bio(self.rnd_auth)
        BIO.update({'book':self.get_content(self.rnd_auth,self.rnd_book)})
        return [self.rnd_auth,self.rnd_book,BIO]
    
    def get_adding(self,command):
        modes = {'📔Твори скорочено':'Скорочено', '📗Аналізи':'Аналіз', '🔉Аудіокниги творів':'Аудіокниги'}
        data={}
        for author in self.authors:
            data_={}
            for book in self.get_books(author):
               for key in self.get_content(author, book):
                   if  modes[command] == key:
                       data_[f"{command[0]}{book}"] = f'<b>{book}</b>\n{self.get_content(author, book)[key]}'
                       break
            if len(data_.keys()):
                data[f'{command[0]}{author}']=data_
        return data
