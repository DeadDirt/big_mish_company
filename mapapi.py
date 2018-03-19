#coding:utf-8
import os
from classes import *
from geocoder import *


def search(text, cur_map, chan=True, cord=None):
    if not chan:  # Если нет координат тыка
        #  Ищем введенный в строку поиска объект, если нет координат тыка
        lat, lon = get_coordinates(text)
    else:  # Иначе подставляем готовые координаты
        lat, lon = cord

    if lat is None or lon is None:
        print('Не нашлось')
        return
    lat, lon = round(lat, 3), round(lon, 3)
    if chan:
        cur_map.go_to_coords(lat, lon, True)  # перемещаем карту если нужно


def show_map(ll=None, spnx=0.02, spny=0.02, map_type='map', add_params=[]):
    # инициализируем карту
    cur_map = Map(map_file='map.png', ll=ll, map_type=map_type, spnx=spnx, spny=spny, add_params=add_params)
    # Инициализируем pygame
    pygame.init()
    screen = pygame.display.set_mode((600, 450))
    screen.blit(pygame.image.load(cur_map.map_file), (0, 0))
    # объявляем объекты gui
    gui = GUI()
    search_box = TextBox((0, 0, 370, 30))  # строка поиска
    address_box = Label((0, 30, 600, 30), "")  # вывод полного адреса
    postal_code = CheckBox((560, 30, 50, 30), "ZIP code")  # показ почтового индекса
    search_button = Button((370, 0, 80, 30), 'искать')  # кнопка поиска
    # кнопки переключения вида карты
    map_button = Button((450, 0, 50, 30), 'map')
    sat_button = Button((500, 0, 50, 30), 'sat')
    skl_button = Button((550, 0, 50, 30), 'skl')
    gui.add_element(search_box)
    gui.add_element(map_button)
    gui.add_element(sat_button)
    gui.add_element(skl_button)
    gui.add_element(search_button)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                # {'pos': (286, 170), 'button': 1}
                if event.dict['button'] == 1:
                    search(search_box.text, cur_map, False, (142, 113)) # здесь вместо нулей нужно вставить чёртовы координаты, Вась
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_PAGEUP:
                    cur_map.map_change_size(2)  # увеличиваем область показа
                elif event.key == pygame.K_PAGEDOWN:
                    cur_map.map_change_size(0.5)  # уменьшаем область показа
                elif event.key == pygame.K_RIGHT:
                    if search_box.active:
                        search_box.get_event(event)
                    else:
                        cur_map.move_map(cur_map.spnx * 3, 0)  # перемещаем карту вправо
                elif event.key == pygame.K_LEFT:
                    if search_box.active:
                        search_box.get_event(event)
                    else:
                        cur_map.move_map(-cur_map.spnx * 3, 0)  # перемещаем карту влево
                elif event.key == pygame.K_DOWN:
                    if search_box.active:
                        search_box.get_event(event)
                    else:
                        cur_map.move_map(0, -cur_map.spny)  # перемещаем карту вниз
                elif event.key == pygame.K_UP:
                    if search_box.active:
                        search_box.get_event(event)
                    else:
                        cur_map.move_map(0, cur_map.spny)  # перемещаем карту вверх
                else:
                    search_box.get_event(event)
                screen.blit(pygame.image.load(cur_map.map_file), (0, 0))
            else:
                gui.get_event(event)

        if search_button.pressed:
            if search_button.text == "искать":  # если была нажата кнопка искать
                search(search_box.text, cur_map)  # осуществляем поиск
                search_button.text = "сбросить"  # меняем текст кнопки на "сбросить"
                formatted_address = get_formatted_address(search_box.text)  # получаем полный адрес объекта
                zip_code = get_postal_code(search_box.text)  # получаем почтовый индекс
                address_box.text = "Адрес: {}".format(formatted_address)
                gui.add_element(address_box)
                gui.add_element(postal_code)
                screen.blit(pygame.image.load(cur_map.map_file), (0, 0))
            elif search_button.text == "сбросить":  # если была нажата кнопка сбросить
                cur_map.reset_pt()  # сбрасываем метку
                search_button.text = "искать"  # меняем текст кнопки на "искать"
                address_box.erase()  # очищаем строку с адресом
                search_box.erase()  # очищаем поисковую строку
                postal_code.pressed = False  # сбрасываем нажатие checkbox'а
                gui.erase(address_box)
                gui.erase(postal_code)
                screen.blit(pygame.image.load(cur_map.map_file), (0, 0))

        if address_box in gui.elements:  # если показывается строка с адресом
            if postal_code.pressed:  # показ почтового индекса
                if zip_code:
                    address_box.text = "Адрес: {}, ZIP: {}".format(formatted_address, zip_code)
                else:
                    address_box.text = "Адрес: {}, ZIP: {}".format(formatted_address, "Not found")
            else:
                address_box.text = "Адрес: {}".format(formatted_address)

        # переключение вида карты
        if map_button.pressed and cur_map.l != "map":
            cur_map.change_map_type("map")
            screen.blit(pygame.image.load(cur_map.map_file), (0, 0))
        if sat_button.pressed and cur_map.l != "sat":
            cur_map.change_map_type("sat")
            screen.blit(pygame.image.load(cur_map.map_file), (0, 0))
        if skl_button.pressed and cur_map.l != "sat,skl":
            cur_map.change_map_type("sat,skl")
            screen.blit(pygame.image.load(cur_map.map_file), (0, 0))

        gui.update()
        gui.render(screen)
        pygame.display.flip()

    pygame.quit()
    # Удаляем за собой файл с изображением.
    os.remove(cur_map.map_file)
