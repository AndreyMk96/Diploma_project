import vk_api
import folium
import requests
import plotly.graph_objects as go
import time
import sqlite3

def autorize():
    #Функция авторизации ВК
    #Во избежание утечки данные кодируются
    a = [b'\xff\xfe+\x007\x009\x000\x005\x004\x008\x003\x001\x001\x004\x005\x00'.decode('utf - 16'),
         b'\xff\xfem\x00i\x00k\x00h\x00a\x00i\x00l\x00o\x00'.decode('utf - 16')]
    vk_session = vk_api.VkApi(a[0], a[1])
    vk_session.auth()
    vk = vk_session.get_api()

    print(" ------------------------------------------------ ")
    print("|                                                |")
    print("|                 Программа запущена             |")
    print("|                               v1.2.3           |")
    print("|                                                |")
    print(" ------------------------------------------------ ")

    return vk

def create_sql():
    conn = sqlite3.connect("base.db")  # или :memory: чтобы сохранить в RAM
    cursor = conn.cursor()
    cursor.execute("""CREATE TABLE city
                      (user_city)
                   """)

def create_groups_list():
    groups_list = []
    f = open("vk_groups.txt")
    for line in f:
        line = line.replace("\n", "")
        line = line.replace(" ", '')
        groups_list.append(line)
    return groups_list

def users_list(groups_list):
    #Данная функция  получает на вход список групп ВК, с которых необходимо получить данные,
    #и возвращает список идентификаторов пользователей

    id_list = []#список для занесения полученных идентификаторов

    for i in groups_list:
        #Получаем количество пользователей в группе
        temp = vk.groups.get_members(group_id=i)
        count = temp.get("count")

        # получаем спиок пользователей сообщества
        for j in range(count//1000 + 1):
            a = vk.groups.get_members(group_id=i, offset=j * 1000)
            id_list.extend(a.get('items'))
        print("Количество пользователей в сообществе " + i + " " + str(len(id_list)))#выводим длину полученного списка
        #удаляем из спика одинаковые элементы
        new_id_list = list(set(id_list))

    print("")
    print("Получен список уникальных идентификаторов пользователей")
    print("Уникальных пользователей " + str(len(new_id_list)))
    print("Время работы программы: " + str(time.time() - start_time )+ " секунд")

    #возвращаем список из уникальных идентификаторов пользователей
    return new_id_list

def cities_list(new_id_list):
    #функция получает на вход список идентификаторов пользователей
    #и возвращает список городов, которые указаны как город проживания на странице пользователей

    conn = sqlite3.connect("base.db")
    cursor = conn.cursor()
    cursor.execute("""CREATE TABLE city
                          (user_city, user_city2, value)
                       """)
    i = 0
    vlg_list = []
    cities_list = []#Список для занесения городов
    counter = 0#счетчик количества обработанных страниц
    f = open('cities_res.txt', 'r', encoding="utf-8")
    for line in f:
        vlg_list.append(line[0:len(line) - 1])
    f.close()

    #for i in range(len(new_id_list)):
    while i < len(new_id_list):
        if counter % 100 == 0:
            print("")
            print("обработано " + str(counter) + " записей")
            print("Время работы программы " + str(int((time.time() - start_time)//60)) + " минут " +
                  str(int((time.time() - start_time) % 60))+" секунд")
            print("")
        try:
            temp = vk.users.get(user_id=new_id_list[i], fields='city')
            counter += 1
            i = i + 1
        except:
            print("ВНИМАНИЕ, ПРОБЛЕМА С ПОДКЛЮЧЕНИЕМ!")
            time.sleep(3)

        temp1 = " ".join(str(temp) for x in temp)
        if "title" in temp1:
            start = temp1.find("title") + 9
            end = len(temp1) - 4
            name_city = temp1[start:end]
            if len(name_city) >= 2:
                if (name_city not in vlg_list) and (ord(name_city[0]) >= 1040 and ord(name_city[0]) <= 1071):
                    cities_list.append(name_city)
                    cursor.execute("""INSERT INTO city
                                      VALUES ('%s','','')
                                      """%(name_city))
                    conn.commit()
                    print(name_city)

    print(" ")
    print("Получен список городов пользователей")

    return cities_list

def cities_dict(cities_list):
    con = sqlite3.connect('base.db')
    cities_list_2 = []
    with con:
        cur = con.cursor()
        cur.execute("SELECT * FROM city")
        rows = cur.fetchall()

        for row in rows:
            cities_list_2.append(''.join(row))


    d = {}
    for i in cities_list_2:
        if i in d:
            v = d[i]
            del (d[i])
            d[i] = v + 1
        else:
            d[i] = 1
    print(d)
    return d

def sort_cities_dict(d):
    # данная функция делает из словаря два отсортированных по возрастанию списка
    # и возвращает их
    b = []#список городов
    c = []#список с населением
    con = sqlite3.connect('base.db')
    cursor = con.cursor()

    #добавление элементов из словаря в список
    for k, v in d.items():
        b.append(k)
        c.append(v)
        cursor.execute("""INSERT INTO city
                                                      VALUES ('','%s','%s')
                                                      """ % (k, v))
        con.commit()
    #сортировка по возрастанию населения(необходимо для некоторых типов вывода)
    #используется сортировка пузырьком
    n = 1
    while n < len(c):
        for i in range(len(c) - n):
            if c[i] > c[i + 1]:
                c[i], c[i + 1] = c[i + 1], c[i]
                b[i], b[i + 1] = b[i + 1], b[i]
        n += 1

    #возвращаются два списка
    print(b)
    print(c)
    print(len(b), len(c))
    create_diagram(b, c)
    return b, c

def open_map():
    #Данная функция создает карту OpenStreetMap
    #и возвращает ее в программу
    map = folium.Map(location=[52.6041877, 39.5936899], zoom_start=8, tiles="OpenStreetMap")
    return map

def create_coors_array(cities_list):
    #Функиця создает список координат городов, полученных из списка cities_list
    #Функция возвращает список из координат городов

    temp = []#список для занесения координат городов
    i = 0

    for i in range(len(cities_list)):
        if i % 50 == 0:
            print("")
            print("----------------------|")
            print("Получено " + str(i) + " Координат|")
            print("----------------------|")
            print("")

        temp1 = []
        #координаты получаем при помощи запроса через Яндекс - геокодер
        response = requests.get(
            'https://geocode-maps.yandex.ru/1.x/?apikey=534639cd-c71f-4af2-8610-f4263e7f0cad&geocode=' + str(
                cities_list[i]))
        b = response.content.decode("UTF - 8")
        #print(b)
        #lat = (b[b.find('<Envelope><lowerCorner>') + 23:b.find('<Envelope><lowerCorner>') + 31])
        start = b.find('<pos>') + 5
        end = b.find(' ',start,len(b))
        lat = b[start:end]
        lon = b[end + 1:b.find('</pos>')]
        print(str(cities_list[i]),lat, lon)
        try:
            lat = float(lat)
            lon = float(lon)
            temp1.append(lon)
            temp1.append(lat)
            temp.append(temp1)
        except:
            print("error")

    print(" ")
    print("Получен список координат городов")
    print("Всего " + str(len(temp)) + "координат")
    print("")

    # возвращается список из координат городов
    return temp

def marker_map(temp, c, map):
    # функция принимает список городов и координат,
    # и наносит отметки на карту

    icon_url = '1.png'
    markers = 0

    for i in range(len(temp)):
        size = c[i]
        if (size > 70):
            size = 70
        if size < 20:
            size = 20
        if "error" not in temp[i]:
            icon = folium.features.CustomIcon(icon_url, icon_size=(size, size))
            folium.Marker(location=temp[i], icon=icon).add_to(map)
            markers += 1
        if i % 50 == 0:
            print("Нанесено " + str(i) + " маркеров")
    map.save("map1.html")

    print("ненесено отметок " + str(markers))
    print()
    print("программа завершена")

def create_diagram(b,c):
    #функция принимает отсортированные списки с городами пользователей, и населением
    #и рисует диаграм на основании 25 наиболее популярных для миграции городов

    #Диаграмма строится по 30 городам, если их количество в списке больше 30
    #или по количеству городов в списке, если их меньше 30
    if len(b) >=30 or len(c) >= 30:
        n = 30
    else:
        n = len(b)
    b.reverse()
    c.reverse()
    labels = []
    values = []
    for i in range(n):
        labels.append(b[i])
        values.append(c[i])

    fig = go.Figure(data=[go.Pie(labels=labels, values=values)])
    fig.show()
    #fig.write_image("fig1.png")
    #fig.write_image("fig1.jpeg")
    print(" ")
    print("Диаграма получена")


#засекаем время началd работы программы
start_time = time.time()
#авторизация
vk = autorize()
#Получение отсортированного списка городов по населению
#И отсортированного списка с населением этих городов
sort_cities_list, sort_population_list = sort_cities_dict(cities_dict(cities_list(users_list(create_groups_list()))))
#Получение списка координат городов,
#Создание OSM карты
#Нанесение меток на карту
marker_map(create_coors_array(sort_cities_list), sort_population_list, open_map())

