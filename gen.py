import asyncio
import random
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np
from moviepy.editor import ImageSequenceClip


class Wheel:
    def __init__(self, participants, section_size=72):
        """
        Конструктор класса Wheel.

        :param participants: список участников.
        :param section_size: размер секции колеса в градусах.
        """
        if len(participants) < 5:
            raise ValueError('Количество участников должно быть больше или равно 5')
        self.participants = participants
        self.num_sections = len(participants)
        self.section_size = section_size
        self.current_angle = 0
        self.section_textures = [self.create_texture() for _ in range(self.num_sections)]
        self.section_outlines = [(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255), random.randint(128, 255)) for _ in range(self.num_sections)]
        self.section_widths = [random.randint(10, 20) for _ in range(self.num_sections)]
        self.arrow_color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        self.arrow_width = random.randint(10, 20)
        self.arrow_joint = 'curve'
        self.font = ImageFont.truetype('fonts/Montserrat-Bold.ttf', 40)

    def create_texture(self):
        """
        Создает текстуру для секции колеса.

        :return: изображение с текстурой.
        """
        texture_img = Image.new('RGBA', (100, 100))
        texture_draw = ImageDraw.Draw(texture_img)
        for i in range(10):
            x1 = random.randint(0, 100)
            y1 = random.randint(0, 100)
            x2 = random.randint(0, 100)
            y2 = random.randint(0, 100)
            color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
            texture_draw.line([(x1, y1), (x2, y2)], fill=color, width=2)
        return texture_img

    def create_wheel_image(self):
        """
        Создает изображение колеса-фортуны.

        :return: изображение колеса-фортуны.
        """
        img = Image.new('RGBA', (500, 500))
        draw = ImageDraw.Draw(img)

        for i in range(self.num_sections):
            start_angle = i * self.section_size
            end_angle = (i + 1) * self.section_size
            text_angle = start_angle + self.section_size / 2
            text_x = 250 + 200 * np.cos(np.deg2rad(text_angle))
            text_y = 250 + 200 * np.sin(np.deg2rad(text_angle))
            draw.text((text_x, text_y), self.participants[i], font=self.font, fill=(255, 255, 255))

            draw.pieslice([(50, 50), (450, 450)], start_angle, end_angle, fill=self.section_outlines[i], outline=self.section_outlines[i], width=self.section_widths[i])

        arrow_points = [(250, 250), (250, 50)]
        arrow_img = Image.new('RGBA', (500, 500))
        arrow_draw = ImageDraw.Draw(arrow_img)
        arrow_draw.line(arrow_points, width=self.arrow_width, fill=self.arrow_color, joint=self.arrow_joint)
        arrow_img = arrow_img.filter(ImageFilter.GaussianBlur(radius=5))
        img.alpha_composite(arrow_img, (0, 0))

        shadow_img = img.filter(ImageFilter.GaussianBlur(radius=10))
        shadow_img = shadow_img.point(lambda x: x * 0.5)
        img.alpha_composite(shadow_img, (0, 0))

        glow_img = Image.new('RGBA', (500, 500))
        glow_draw = ImageDraw.Draw(glow_img)
        glow_draw.ellipse([(50, 50), (450, 450)], fill=(255, 255, 255, 128))
        glow_img = glow_img.filter(ImageFilter.GaussianBlur(radius=50))
        img.alpha_composite(glow_img, (0, 0))

        # Добавляем эффект глубины для колеса
        for i in range(self.num_sections):
            start_angle = i * self.section_size
            end_angle = (i + 1) * self.section_size
            section_width = self.section_widths[i] * 2
            section_draw = ImageDraw.Draw(img)
            section_draw.pieslice([(50, 50), (450, 450)], start_angle, end_angle, fill=None, outline=self.section_outlines[i], width=section_width)

        # Добавляем эффект мерцания для секций колеса
        for i in range(self.num_sections):
            start_angle = i * self.section_size
            end_angle = (i + 1) * self.section_size
            alpha = random.randint(128, 255)
            section_img = Image.new('RGBA', (500, 500))
            section_draw = ImageDraw.Draw(section_img)
            section_draw.pieslice([(50, 50), (450, 450)], start_angle, end_angle, fill=self.section_outlines[i], outline=None)
            section_img.putalpha(alpha)
            img.alpha_composite(section_img, (0, 0))

        draw.pieslice([(200, 200), (300, 300)], self.current_angle - 5, self.current_angle + 5, fill=self.arrow_color)
        wheel_img = img.rotate(self.current_angle, resample=Image.BICUBIC, expand=True)

        return wheel_img

    def rotate_wheel(self):
        # Вращаем колесо на случайный угол
        self.current_angle += random.randint(360, 720)
        self.current_angle %= 360

    def get_wheel_image(self):
        # Получаем изображение колеса с повернутой стрелкой и эффектом мерцания
        img = self.create_wheel_image()
        return img


class Animation:
    def __init__(self, participants, duration=100, loop=0):
        """
        Конструктор класса Animation.

        :param participants: список участников.
        :param duration: длительность анимации в кадрах.
        :param loop: количество повторений анимации (0 - бесконечно).
        """
        self.participants = participants
        self.duration = duration
        self.loop = loop

    async def generate_animation(self):
        """
        Генерирует анимацию колеса-фортуны и сохраняет ее в файл.

        :return: None.
        """
        try:
            wheel = Wheel(self.participants)
            frames = []
            for i in range(self.duration):
                wheel.rotate_wheel()
                img = wheel.get_wheel_image()
                frames.append(img)
                #clip = ImageSequenceClip(frames, fps=30)
                clip = ImageSequenceClip(frames, fps=30).resize(width=frames[0].width, height=frames[0].height)
                #clip = ImageSequenceClip(frames, fps=30, size=frames[0].size)
            if self.loop == 0:
                clip = clip.loop(-1)
            else:
                clip = clip.loop(n=self.loop)
            clip.write_videofile('output.mp4', fps=30)
        except ValueError as e:
            print(e)

if __name__ == '__main__':
    participants = ['Иван', 'Петр', 'Сергей', 'Андрей', 'Дмитрий']
    animation = Animation(participants, duration=30, loop=1)
    asyncio.run(animation.generate_animation())
