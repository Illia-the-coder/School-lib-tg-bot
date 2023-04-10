import logging
from aiogram import *
from aiogram.types import *
from config import token
from literatureClient import *

bot = Bot(token=token)
dp = Dispatcher(bot)
logging.basicConfig(level=logging.INFO)

user_data ={}
grade_=[f"{n} клас" for n in range(5,12)]
type_=['Світова','Українська']
list_choose = [f'{grade} клас {type}' for grade in range(5, 12) for type in ['Світова', 'Українська']]
commands = ['Автори','🎲random','📃Список книг','🎓Презентації','📔Твори скорочено','📗Аналізи','🔉Аудіокниги творів']
msg_='''Обери:'''


def user_id_cof(message): 
    return user_data[int(message.from_user.id)]

def inline(list_, first_ = False,rows=3):
    list__  = list(list_)+['👈назад'] if not first_ else list_
    return types.InlineKeyboardMarkup(row_width = rows).add(*[InlineKeyboardButton(text=x, callback_data=x) for x in list__])

def func_inline(call,text,arr_but,rows = 3,first = False,html=True):
    if html: return lambda: bot.send_message(call.from_user.id,text, reply_markup=inline(arr_but,first_=first,rows = rows), parse_mode=types.ParseMode.HTML)
    return lambda: bot.send_message(call.from_user.id,text, reply_markup=inline(arr_but,first_=first,rows = rows))

async def update_level(call,func = None,back = False):
    n=1
    try:
        await bot.delete_message(call.from_user.id,call.message.message_id)
        if back: 
            func = user_id_cof(call)['prev'][user_id_cof(call)['level']-1]
            n=-1
        else: user_id_cof(call)['prev'][user_id_cof(call)['level']+1] = func
        await func()
    except Exception as e: 
        await bot.send_message(call.from_user.id,f'Помилка {e}', reply_markup=inline([]))
    user_id_cof(call)['level'] +=n
    
@dp.message_handler(commands="start")
async def start(message: types.Message):
    await message.reply("""Доброго дня 👋.Цей бот допоможе тобі прочитати програму з літератури📚 максимально ефективно⚡⚡⚡! Тут ви зможете знайти:\n🧔Біографії авторів\n 📔Перекази\n 🔉Аудіокниги\n 📗Аналізи творів\n 🎓Презентації по біографіям авторів\n 📃Списки творів за кожен клас""")
    func = func_inline(message,"Обери клас, де ти вчишся:",grade_,first=True)
    user_data[int(message.from_user.id)] = {'prev':{0:func},'level':0}
    await func()

@dp.callback_query_handler(text=grade_) 
async def random_value(call: types.CallbackQuery): 
    user_data[call.from_user.id]['clas']=call.data 
    user_data[call.from_user.id]['BSCH']=BSCH(call.data)
    user_data[call.from_user.id]['subjs']=BSCH(call.data).subj 
    await update_level(call,func_inline(call,'Обери: ',arr_but = ['📓Шкільні підручники','🗂Шкільна література'], html= False,rows=2)) 
    # mesg = 'А тепер час обрати курс літератури: ' 
    # await update_level(call,func_inline(call,mesg,arr_but = type_, html= False)) 
 
@dp.callback_query_handler(text=['📓Шкільні підручники','🗂Шкільна література']) 
async def random_value(call: types.CallbackQuery): 
    if call.data=='📓Шкільні підручники': 
        
        func=func_inline(call,'Обери: ',arr_but = user_id_cof(call)['BSCH'].subj, html= False,rows=1)
        
    elif call.data == '🗂Шкільна література': 
        mesg = 'А тепер час обрати курс літератури: ' 
        func=func_inline(call,mesg,arr_but = type_, html= False) 
    await update_level(call,func) 
 
 
@dp.callback_query_handler(text=type_) 
async def random_value(call: types.CallbackQuery): 
    datalist=user_id_cof(call) 
    user_data[call.from_user.id]['data'] = f'{datalist["clas"]} {call.data}'
    await update_level(call,func_inline(call,msg_,commands,2)) 
    

@dp.callback_query_handler(text= commands)
async def choosing_next(call: types.CallbackQuery):
    DF=DB(user_id_cof(call)['data'])
    if call.data == 'Автори':
        func = func_inline(call,'Оберіть автора: ',DF.authors ,2)
    elif call.data == '📃Список книг':
        func = func_inline(call,DF.list_all(),[] ,1)
    elif call.data == '🎓Презентації':
        PR=DF.pres_data
        user_id_cof(call).update({'pres':PR})
        func = func_inline(call,f'{call.data}\nОберіть автора: ',PR.keys(),1)
    elif call.data == '🎲random':
        DF_rnd=DF.get_rnd()
        RND_auth = DF_rnd[0]
        RND_book = DF_rnd[1]
        DF_RND = DF_rnd[2]
        decs =f"<img src = '{DF_RND['img_src']}'><h3>Біографія</h3>\n{DF_RND['bio']}\n{DF.get_content_tlgrph(RND_auth,RND_book)[1]}"
        user_id_cof(call).update({'author':DF.rnd_auth,'book':DF.rnd_book})
        func = func_inline(call, create_tlgrph(f'{RND_auth}/{RND_book}', decs), [],1)
    elif call.data in ['📔Твори скорочено', '📗Аналізи', '🔉Аудіокниги творів']:
        user_id_cof(call)['add']= DF.get_adding(call.data)
        func = func_inline(call,f'{call.data}\nОберіть автора: ', DF.get_adding(call.data).keys() ,1)
    await update_level(call,func)


@dp.callback_query_handler(text=['👈назад'])
async def back(call: types.CallbackQuery):
    await update_level(call,back = True)


@dp.callback_query_handler()
async def base(call: types.CallbackQuery):
    data_list=user_id_cof(call)
    if 'add' in data_list.keys() or 'pres' in data_list.keys():
        if call.data[0] in ['📗','📔','🔉']:
            if call.data in data_list['add'].keys():
                user_id_cof(call)['add_author']= call.data
                func = func_inline(call,f'<b>{call.data}</b>\n\nОберіть твір:', data_list['add'][call.data].keys(), 1)
            elif 'add_author' in data_list.keys() and call.data in data_list['add'][data_list['add_author']].keys():
                    add_book_data= data_list['add'][data_list['add_author']][call.data]
                    func = func_inline(call, create_tlgrph(call.data,add_book_data), [],1)
            await update_level(call,func)
        elif call.data[0] == '🎓':
            func = func_inline(call,create_tlgrph(f'{call.data}(Презентації)',user_id_cof(call)['pres'][call.data]) ,[],1)
            await update_level(call,func)
            
    elif 'data' in data_list.keys():
        DF = DB(data_list['data'])

        if call.data in DF.authors:
            user_id_cof(call)['author'] = call.data
            author_data= DF.get_bio(call.data)
            keyboard =inline(DF.get_books(call.data),rows =1)
            func = lambda: bot.send_photo(call.from_user.id, author_data['img_src'],caption=f"{author_data['bio']}\nОберіть твір", parse_mode=types.ParseMode.HTML, reply_markup=keyboard)
        
        elif 'author' in data_list.keys():
            if call.data in DF.get_books(data_list['author']):
                user_id_cof(call)['book'] = call.data
                func = func_inline(call, create_tlgrph( *DF.get_content_tlgrph(data_list['author'], call.data)), [])
    #School books 
    elif 'subjs' in data_list.keys(): 
        print('v`')
        if call.data in user_data[call.from_user.id]['subjs']: 
            func=func_inline(call,user_data[call.from_user.id]['BSCH'][call.data],arr_but= []) 
        
    await update_level(call,func)

    
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
    
