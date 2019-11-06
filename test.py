import vk_api
import folium
import requests

def autorize():
    #Функция авторизации ВК
    vk_session = vk_api.VkApi('+79054831145', 'mikhailo')
    vk_session.auth()
    vk = vk_session.get_api()
    return vk
def users_list(groups):
    #Данная функция  получает на вход списокь групп ВК, с которых необходимо получить данные,
    #и возвращает список идентификаторов пользователей

    id_list = []#список для занесения полученных идентификаторов

    for i in groups:
        #Получаем количество пользователей в группе
        temp = vk.groups.get_members(group_id=i)
        count = temp.get("count")

        # получаем спиок пользователей сообщества
        for j in range(count//1000 + 1):
            a = vk.groups.get_members(group_id=i, offset=j * 1000)
            id_list.extend(a.get('items'))
            print(len(id_list))#выводим длину полученного списка
        #удаляем из спика одинаковые элементы
        new_id_list = list(set(id_list))
    print("Получен список уникальных идентификаторов пользователей")
    return new_id_list
def cities_list(id_list):
    #функция получает на вход список идентификаторов пользователей
    #и возвращает список городов, которые указаны как город проживания на странице пользователей

    cities_list = []#Список для занесения городов
    counter = 0#счетчик количества обработанных страниц

    for i in id_list:
        if counter % 100 == 0:
            print("обработано " + str(counter) + " записей")
        temp = vk.users.get(user_id=i, fields='city')
        temp1 = " ".join(str(temp) for x in temp)
        if "title" in temp1:
            start = temp1.find("title") + 9
            end = len(temp1) - 4
            cities_list.append(temp1[start:end])
            print(temp1[start:end])
        counter += 1
    print("Получен список городов пользователей")
    return cities_list
def cities_dict(cities_list):
    d = {}
    for i in cities_list:
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

    b = []
    c = []

    for k, v in d.items():
        b.append(k)
        c.append(v)
    n = 1
    while n < len(c):
        for i in range(len(c) - n):
            if c[i] > c[i + 1]:
                c[i], c[i + 1] = c[i + 1], c[i]
                b[i], b[i + 1] = b[i + 1], b[i]
        n += 1
    return b, c
def open_map():
    map = folium.Map(location=[52.6041877, 39.5936899], zoom_start=8, tiles="OpenStreetMap")
    return map
def create_coors_array(cities_list):
    temp = []
    for i in range(len(cities_list)):
        temp1 = []
        response = requests.get(
            'https://geocode-maps.yandex.ru/1.x/?apikey=534639cd-c71f-4af2-8610-f4263e7f0cad&geocode=' + str(
                cities_list[i]))
        b = response.content.decode("UTF - 8")
        lat = float(b[b.find('<Envelope><lowerCorner>') + 23:b.find('<Envelope><lowerCorner>') + 31])
        lon = float(b[b.find('<Envelope><lowerCorner>') + 33:b.find('<Envelope><lowerCorner>') + 40])
        b = b.replace(' ', ', ')
        temp1.append(lon)
        temp1.append(lat)
        temp.append(temp1)
    return temp
def marker_map(temp, c, map):
    icon_url = '1.png'
    for i in range(len(temp)-1):
        icon = folium.features.CustomIcon(icon_url, icon_size=(c[i]*3, c[i]*3))
        folium.Marker(location=temp[i],icon = icon).add_to(map)
        map.save("map1.html")
        print("программа завершена")

vk = autorize()
groups = ["vstu.footballeague"]
#groups = ["newsv1", "podslyshano_volgograd"]
id_list = users_list(groups)
cities_list = cities_list(id_list)
d = cities_dict(cities_list)
b,c = sort_cities_dict(d)
map = open_map()
temp = create_coors_array(b)
print(temp, c)
marker_map(temp, c, map)

