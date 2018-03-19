import sys
import requests
import pygame


class GUI:
    def __init__(self):
        self.elements = []

    def add_element(self, element):
        self.elements.append(element)

    def render(self, surface):
        for element in self.elements:
            render = getattr(element, "render", None)
            if callable(render):
                element.render(surface)

    def update(self):
        for element in self.elements:
            update = getattr(element, "update", None)
            if callable(update):
                element.update()

    def get_event(self, event):
        for element in self.elements:
            get_event = getattr(element, "get_event", None)
            if callable(get_event):
                element.get_event(event)

    def erase(self, x):
        for i in range(len(self.elements)):
            if self.elements[i] is x:
                self.elements.pop(i)
                break


class Map:
    def __init__(self, map_file, ll, map_type, spnx, spny, add_params):
        self.map_file = map_file
        self.ll = ll
        self.spnx = spnx
        self.spny = spny
        self.l = map_type
        self.params = add_params
        self.request = self.form_request(self.params, ll=ll, spn=str(spnx) + ',' + str(spny), l=map_type)
        self.map_file = self.form_map(self.request_map(self.request))

    def form_request(self, args, **kwargs):
        x = 'http://static-maps.yandex.ru/1.x/'
        if kwargs or args:
            x += '?'
            for i in kwargs.keys():
                x += i + "=" + str(kwargs[i])
                x += '&'
            x = x[:-1:]
            if args:
                if kwargs:
                    x += '&'
                for i in args:
                    x += i
                    x += '&'
            if x[-1] == '&':
                x = x[:-1:]
        return x

    def request_map(self, request):
        response = requests.get(request)
        if not response:
            print("Ошибка выполнения запроса:")
            print(self.request)
            print("Http статус:", response.status_code, "(", response.reason, ")")
            sys.exit(1)
        return response

    def form_map(self, response):
        # Запишем полученное изображение в файл.
        try:
            with open(self.map_file, "wb") as file:
                file.write(response.content)
        except IOError as ex:
            print("Ошибка записи временного файла:", ex)
            sys.exit(2)

        return self.map_file

    def map_change_size(self, delta):
        # Изменяем параметр spn.
        self.spnx = round(self.spnx * delta, 3)
        self.spnx = min(80.0, max(0.002, self.spnx))
        self.spny = round(self.spny * delta, 3)
        self.spny = min(80.0, max(0.002, self.spny))
        self.request = self.form_request(self.params, ll=self.ll, l=self.l, spn=str(self.spnx) + ',' + str(self.spny))
        response = self.request_map(self.request)
        self.map_file = self.form_map(response)

    def change_map_type(self, new_map_type):
        self.l = new_map_type
        self.request = self.form_request(self.params, ll=self.ll, l=self.l, spn=str(self.spnx) + ',' + str(self.spny))
        response = self.request_map(self.request)
        self.map_file = self.form_map(response)

    def move_map(self, move_x, move_y):
        # Изменяем параметр ll.
        new_ll = '{},{}'.format(float(self.ll.split(',')[0]) + move_x, float(self.ll.split(',')[1]) + move_y)
        self.ll = new_ll
        self.request = self.form_request(self.params, ll=self.ll, l=self.l, spn=str(self.spnx) + ',' + str(self.spny))
        response = self.request_map(self.request)
        self.map_file = self.form_map(response)
        # Возвращаем запрос карты с измененным ll.

    def go_to_coords(self, x, y, point):
        self.ll = str(x) + ',' + str(y)
        if point:
            flag = False
            ind = 0
            for k in range(len(self.params)):
                if 'pt=' in self.params[k]:
                    flag = True
                    ind = k
                    break
            if flag:
                self.params[ind] = 'pt={},pm2dgm'.format(self.ll)
            else:
                self.params.append('pt={},pm2dgm'.format(self.ll))
        self.request = self.form_request(self.params, ll=self.ll, spn=str(self.spnx) + ',' + str(self.spny), l=self.l)
        self.map_file = self.form_map(self.request_map(self.request))

    def reset_pt(self):
        for k in range(len(self.params)):
            if self.params[k].startswith('pt='):
                self.params.pop(k)
                break
        self.request = self.form_request(self.params, ll=self.ll, spn=str(self.spnx) + ',' + str(self.spny), l=self.l)
        self.map_file = self.form_map(self.request_map(self.request))


class Label:
    def __init__(self, rect, text, text_color=pygame.Color('black'), background_color=pygame.Color('white')):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.bgcolor = background_color
        self.font_color = text_color
        # Рассчитываем размер шрифта в зависимости от высоты
        self.font = pygame.font.Font('fonts/6551.ttf', self.rect.height - 15)
        self.rendered_text = None
        self.rendered_rect = None

    def render(self, surface):
        if self.bgcolor != -1:
            surface.fill(self.bgcolor, self.rect)
        self.rendered_text = self.font.render(self.text, 1, self.font_color)
        self.rendered_rect = self.rendered_text.get_rect(x=self.rect.x + 2, centery=self.rect.centery)
        # выводим текст
        surface.blit(self.rendered_text, self.rendered_rect)

        # рисуем границу
        pygame.draw.rect(surface, pygame.Color("white"), self.rect, 2)
        pygame.draw.line(surface, pygame.Color("black"), (self.rect.right - 1, self.rect.top),
                         (self.rect.right - 1, self.rect.bottom), 2)
        pygame.draw.line(surface, pygame.Color("black"), (self.rect.left, self.rect.bottom - 1),
                         (self.rect.right, self.rect.bottom - 1), 2)

    def erase(self):
        self.text = ""


class TextBox(Label):
    def __init__(self, rect, text=''):
        super().__init__(rect, text)
        self.active = False
        self.blink = True
        self.blink_timer = 0
        self.cursor = 0

    def get_event(self, event):
        if event.type == pygame.KEYDOWN and self.active:
            if event.key in [pygame.K_TAB]:
                return True
            elif event.key == pygame.K_BACKSPACE:
                if len(self.text) > 0 and self.cursor != 0:
                    self.text = self.text[:self.cursor - 1] + self.text[self.cursor:]
                    self.cursor -= 1
            elif event.key == pygame.K_LEFT:
                self.cursor -= 1
                self.cursor %= len(self.text) + 1
            elif event.key == pygame.K_RIGHT:
                self.cursor += 1
                self.cursor %= len(self.text) + 1
            else:
                if event.unicode != '':
                    x = self.font.render(self.text, 2, self.font_color).get_rect().width
                    try:
                        y = self.font.render(event.unicode, 2, self.font_color).get_rect().width
                    except pygame.error:
                        return
                    if x + y < self.rect.width - 5:
                        self.text = self.text[:self.cursor] + event.unicode + self.text[self.cursor:]
                        self.cursor += 1
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.active = self.rect.collidepoint(*event.pos)

    def update(self):
        if pygame.time.get_ticks() - self.blink_timer > 200:
            self.blink = not self.blink
            self.blink_timer = pygame.time.get_ticks()

    def render(self, surface):
        super(TextBox, self).render(surface)
        if self.blink and self.active:
            #self.rendered_text = self.font.render(self.text, 1, self.font_color)
            #self.rendered_rect = self.rendered_text.get_rect(x=self.rect.x + 2, centery=self.rect.centery)
            x = self.font.render(self.text[:self.cursor], 2, self.font_color)
            y = x.get_rect(x=self.rect.x + 2, centery=self.rect.centery).right
            pygame.draw.line(surface, pygame.Color("black"),
                             (y, self.rendered_rect.top + 2),
                             (y, self.rendered_rect.bottom - 2))
        # рисуем границу
        pygame.draw.rect(surface, pygame.Color("white"), self.rect, 2)
        pygame.draw.line(surface, pygame.Color("black"), (self.rect.right - 1, self.rect.top),
                         (self.rect.right - 1, self.rect.bottom), 2)
        pygame.draw.line(surface, pygame.Color("black"), (self.rect.left, self.rect.bottom - 1),
                         (self.rect.right, self.rect.bottom - 1), 2)

    def erase(self):
        self.cursor = 0
        self.text = self.text[:self.cursor]


class Button(Label):
    def __init__(self, rect, text):
        super().__init__(rect, text)
        self.bgcolor = pygame.Color('white')
        self.pressed = False
        self.active = False

    def render(self, surface):
        surface.fill(self.bgcolor, self.rect)
        self.rendered_text = self.font.render(self.text, 1, self.font_color)
        if not self.pressed:
            color1 = pygame.Color("white")
            color2 = pygame.Color("black")
            self.rendered_rect = self.rendered_text.get_rect(x=self.rect.x + 5, centery=self.rect.centery)
        else:
            color1 = pygame.Color("black")
            color2 = pygame.Color("white")
            self.rendered_rect = self.rendered_text.get_rect(x=self.rect.x + 7, centery=self.rect.centery + 2)

        # рисуем границу
        pygame.draw.rect(surface, color1, self.rect, 2)
        pygame.draw.line(surface, color2, (self.rect.right - 1, self.rect.top), (self.rect.right - 1, self.rect.bottom),
                         2)
        pygame.draw.line(surface, color2, (self.rect.left, self.rect.bottom - 1),
                         (self.rect.right, self.rect.bottom - 1), 2)
        # выводим текст
        surface.blit(self.rendered_text, self.rendered_rect)

    def get_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.pressed = True
            return False
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1 and self.pressed:
            self.pressed = False
        elif event.type == pygame.MOUSEMOTION:
            if self.rect.collidepoint(event.pos):
                self.font_color = pygame.Color('green')
            if not self.rect.collidepoint(event.pos):
                self.font_color = pygame.Color('blue')
            return False


class CheckBox:
    def __init__(self, rect, text):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.font = pygame.font.Font('fonts/6551.ttf', self.rect.height - 15)
        self.pressed = False

    def render(self, surface):
        if self.pressed:
            pygame.draw.circle(surface, pygame.Color('blue'), (self.rect.x + self.rect.width // 2, self.rect.y + self.rect.height // 2), 10)
            rendered_text = self.font.render(self.text, 1, pygame.Color('black'))
            surface.blit(rendered_text, (self.rect.x - self.rect.width,  self.rect.y + 8))
        else:
            rendered_text = self.font.render(self.text, 1, pygame.Color('black'))
            surface.blit(rendered_text, (self.rect.x - self.rect.width,  self.rect.y + 8))
            pygame.draw.circle(surface, pygame.Color('blue'),
                               (self.rect.x + self.rect.width // 2, self.rect.y + self.rect.height // 2), 10, 1)

    def get_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.pressed = not self.pressed
