import pygame
import requests
import sys
import os

API_KEY_STATIC = 'f3a0fe3a-b07e-4840-a1da-06f18b2ddf13'

def show_map(ll_spn=None, add_params=None):
    if ll_spn:
        map_request = f"https://static-maps.yandex.ru/v1?apikey={API_KEY_STATIC}&{ll_spn}"
    else:
        map_request = f"https://static-maps.yandex.ru/v1?apikey={API_KEY_STATIC}&"

    if add_params:
        map_request += "&" + add_params
    response = requests.get(map_request)

    if not response:
        print("Ошибка выполнения запроса:")
        print(map_request)
        print("Http статус:", response.status_code, "(", response.reason, ")")
        sys.exit(1)

    # Запишем полученное изображение в файл.
    map_file = "map.png"
    try:
        with open(map_file, "wb") as file:
            file.write(response.content)
    except IOError as ex:
        print("Ошибка записи временного файла:", ex)
        sys.exit(2)

    # Инициализируем pygame
    pygame.init()
    screen = pygame.display.set_mode((600, 450))
    # Рисуем картинку, загружаемую из только что созданного файла.
    screen.blit(pygame.image.load(map_file), (0, 0))
    # Переключаем экран и ждем закрытия окна.
    pygame.display.flip()
    while pygame.event.wait().type != pygame.QUIT:
        pass

    pygame.quit()
    # Удаляем за собой файл с изображением.
    os.remove(map_file)


if __name__ == '__main__':
    show_map("ll=37.530887,55.703118&spn=0.002,0.002")