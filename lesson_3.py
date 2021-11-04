
# я не успеваю сделать домашку, но расчитываю сегодня, завтра
# до обеда её сделать.
# чтобы не обращаться в техподдержку (просто она очень долно отвечает)
# решил пойти на небольшую хитрость.
# сейчас закоммичу этот файл. Обновления запушу следующим коммитом )))
# надеюсь это не будет расценено как злостное нарушение.
# постараюсь больше так не делать.

import requests
from bs4 import BeautifulSoup as bs
import json
import pandas as pd
import csv
from pprint import pprint

# https://spb.hh.ru/search/vacancy?text=python


search_str = input('Введите текст для поиска вакансий: ').strip() or 'python'

try:
    page_count = int(input('Введите количество страниц: '))
except:
    page_count = 1

def currancy(cur_in):
    ''' Обработка валюты '''
    if cur_in == 'руб.':
        cur_out = 'RUB'
    elif cur_in == 'USD':
        cur_out = 'USD'
    elif cur_in == 'EUR':
        cur_out = 'EUR'
    elif cur_in == 'грн.':
        cur_out = 'UAH'
    elif cur_in == 'KZT':
        cur_out = 'KZT'
    elif cur_in == 'сум':
        cur_out = 'UZS'
    else:
        cur_out = 'Nan'
    return cur_out

url = 'https://spb.hh.ru'
params1 = {
           # 'area': 2,
           # 'fromSearchLine': True,
           # 'items_on_page': 50, # я не понял почему получается выдача только по 20 вакансий
           # еероятно это настройки сайта hh.ru - я такой сделал вывод.
           # я прав?
           'page': 1,
           'text': search_str}

header1 = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) \
                          AppleWebKit/537.36 (KHTML, like Gecko) \
                          Chrome/95.0.4638.54 Safari/537.36'}

vac_list = []
len_vac_array = 0

while params1['page'] <= page_count:

    resp1 = requests.get(url + '/search/vacancy', params=params1, headers=header1)
    dom1 = bs(resp1.text, 'html.parser')
    vacancy_array = dom1.find_all('div', {'class': 'vacancy-serp-item'})
    len_vac_array += len(vacancy_array)
    # print(len(vacancy_array))

    if resp1.ok and vacancy_array:
        for vacancy in vacancy_array:
            vac_dict = {}
            vac_info = vacancy.find('a', {'class': "bloko-link"})
            # 1. Наименование вакансии.
            vac_name = vac_info.text
            # 2. Предлагаемая зарплата
            compensation = vacancy.find('span', {'data-qa': "vacancy-serp__vacancy-compensation"})

            # 3. Ссылка на саму вакансию.
            vac_link = vac_info['href']

            # 4. Сайт, откуда была собрана вакансия.
            # Я не совсем понимаю о чем речь, но предполагаю, что это ссылка на страницу работодателя на сайте hh.ru
            employer_link = 'https://spb.hh.ru' + \
                                vacancy.find('a', {'data-qa': 'vacancy-serp__vacancy-employer'})['href']

            employer_name = vacancy.find('a', {'data-qa': 'vacancy-serp__vacancy-employer'}).text#.replace('\xa0', ' ')
            # почему то в консоле верхняя строчка отрабатывала штатно, а в модуле отказывалась(((
            # пока не закомментировал replace
            employer_name = employer_name.replace('\xa0', ' ')

            vac_dict['vac_name'] = vac_name
            vac_dict['employer_name'] = employer_name

            if compensation is None:
                vac_dict['sal_min'] = None
                vac_dict['sal_cur'] = None
                vac_dict['sal_max'] = None
            # \u202f - узкий неразрывный пробел; print() преобразует его автоматически
            else:
                l = compensation.text.split(' ')
                if l[0] == 'от':
                    vac_dict['sal_min'] = int(l[1].replace('\u202f', ''))
                    vac_dict['sal_cur'] = currancy(l[2])
                    # if l[2] == 'руб.':
                    #     vac_dict['sal_cur'] = 'RUB'
                    # elif l[2] == 'USD':
                    #     vac_dict['sal_cur'] = 'USD'
                    # elif l[2] == 'EUR':
                    #     vac_dict['sal_cur'] = 'EUR'
                    # else:
                    #     vac_dict['sal_cur'] = 'Nan'
                    vac_dict['sal_max'] = None
                elif l[0] == 'до':
                    vac_dict['sal_min'] = None
                    vac_dict['sal_cur'] = currancy(l[2])
                    vac_dict['sal_max'] = int(l[1].replace('\u202f', ''))
                elif len(l) == 4 and l[1] == chr(8211):
                    vac_dict['sal_min'] = int(l[0].replace('\u202f', ''))
                    vac_dict['sal_cur'] = currancy(l[3])
                    vac_dict['sal_max'] = int(l[2].replace('\u202f', ''))
            vac_dict['vac_link'] = vac_link
            vac_dict['employer_link'] = employer_link
            # pprint(vac_dict)
            vac_list.append(vac_dict)
        print(f'Обаработана {params1["page"]:0>2} страница; +{len(vacancy_array)}, Итого записей: {len_vac_array:0>3}')
        params1['page'] += 1
    else:
        break
# pprint(vac_list)

with open ('vac_list.json', 'w') as f_obj:
    json.dump(vac_list, f_obj)

with open ('vac_list.csv', 'w', encoding='utf-8', newline='') as f_obj:
    wrt = csv.DictWriter(f_obj, fieldnames=vac_dict.keys())
    wrt.writeheader()
    wrt.writerows(vac_list)

vac_frame = pd.DataFrame(vac_list)
vac_frame.to_csv('vac_frame.csv', index=False, encoding='utf-8', sep=',')
# print(vac_frame)