import requests
import json
from datetime import datetime
from tqdm import tqdm
from time import sleep

VK_ID = ...
VK_TOKEN = ...
DISK_TOKEN = ...
path = '/Netology/Coursework_Dolinkin'


# Достаем информацию по фоткам

def get_photos(user_id, access_token, album_id='profile'):
    url = 'https://api.vk.com/method/photos.get'
    params = {'user_id': user_id, 'access_token': access_token, 'v': '5.131', 'album_id': album_id, 'extended': '1'}
    resp = requests.get(url, params=params)
    result = []
    for photo in resp.json()['response']['items']:
        size_max = {'height': 0}
        for size in photo['sizes']:
            if size['height'] > size_max['height']:
                size_max = size
        photo_dict = {'date': photo['date'], 'likes': photo['likes']['count'], 'size': size_max['type'],
                      'url': size_max['url']}
        result.append(photo_dict)
    return result


# Загружаем фотки на яндекс диск

# Создание папки

def create_folder(token, path):
    headers = {'Accept': 'application/json', 'Authorization': token}
    params = {'path': path}
    url = 'https://cloud-api.yandex.net/v1/disk/resources'
    requests.put(url, params=params, headers=headers)


# Загружаем файл

def upload_file(token, data_dict, path):
    headers = {'Accept': 'application/json', 'Authorization': token}
    url = 'https://cloud-api.yandex.net/v1/disk/resources/upload'
    params = {'path': path, 'url': data_dict['url']}
    requests.post(url, params=params, headers=headers)


# Получаем информацию по файлам на диске

def get_disk_info(token, path):
    headers = {'Accept': 'application/json', 'Authorization': token}
    url = 'https://cloud-api.yandex.net/v1/disk/resources'
    params = {'path': path}
    resp = requests.get(url, params=params, headers=headers)
    return resp


# Получаем список словарей с данными по фоткам, получаем информацию по файлам на диске, создаем папку, если нужно

photos_list = get_photos(VK_ID, VK_TOKEN)
disk_info = get_disk_info(DISK_TOKEN, path)
if disk_info.status_code != 200:
    create_folder(DISK_TOKEN, path)
    disk_info = get_disk_info(DISK_TOKEN, path)

# Получаем список файлов, которые уже лежат на диске

file_names = []
if disk_info.json()['_embedded']['items']:
    for item in disk_info.json()['_embedded']['items']:
        file_names.append(item['name'].strip('.jpg'))

# Список с информацией по загруженным файлам

upload_info = []

# Проверяем наличие фото на диске и загружаем

for photo in tqdm(photos_list, desc='upload_files'):
    upload_path = ''
    file_name = ''
    date = datetime.utcfromtimestamp(photo['date']).strftime('%d-%m-%Y')
    if str(photo['likes']) in file_names:
        file_name = str(photo['likes']) + '_' + date + '.jpg'
        upload_path = path + '/' + file_name
    else:
        file_name = str(photo['likes']) + '.jpg'
        upload_path = path + '/' + file_name
    if (str(photo['likes']) + '_' + date) in file_names:
        pass
    else:
        upload_file(DISK_TOKEN, photo, upload_path)
        upload_info.append(f'Загружен файл: {file_name}, размер: {photo["size"]}')
        sleep(0.01)

# Записываем данные о загруженных на диск фотках в файл

with open('upload_info.json', 'w') as f:
    json.dump(upload_info, f, ensure_ascii=False)
