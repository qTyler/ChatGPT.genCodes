import random
import logging
import math
from PIL import Image, ImageDraw, ImageFont, ImageFilter


class Wheel:
    def __init__(self, participants, num_sections, section_size, section_outlines, section_widths, arrow_color, arrow_width, arrow_joint, font):
        self.participants = participants
        self.num_sections = num_sections
        self.section_size = section_size
        self.current_angle = 0
        self.section_outlines = section_outlines
        self.section_widths = section_widths
        self.arrow_color = arrow_color
        self.arrow_width = arrow_width
        self.arrow_joint = arrow_joint
        self.font = font

    def create_gradient(self, size, start_color, end_color):
        gradient = Image.new('RGBA', size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(gradient)
        for i in range(size[0]):
            color = tuple(int(start_color[j] + (end_color[j] - start_color[j]) * i / size[0]) for j in range(3))
            draw.line([(i, 0), (i, size[1])], fill=color)
        return gradient

    def create_section_texture(self, size):
        texture = Image.new('RGBA', size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(texture)
        section_angle = 360/self.num_sections
        for i in range(self.num_sections):
            start_angle = i*section_angle
            end_angle = (i+1)*section_angle
            start_angle_degrees = math.degrees(start_angle)
            end_angle_degrees = math.degrees(end_angle)
            if i % 2 == 0:
                draw.pieslice([(0, 0), size], start_angle_degrees, end_angle_degrees, fill=(255, 0, 0), outline=self.section_outlines[i % len(self.section_outlines)], width=self.section_widths[i % len(self.section_widths)])
            else:
                draw.pieslice([(0, 0), size], start_angle_degrees, end_angle_degrees, fill=(0, 0, 0), outline=self.section_outlines[i % len(self.section_outlines)], width=self.section_widths[i % len(self.section_widths)])
        return texture

    def create_shadow(self, size, color, radius):
        shadow = Image.new('RGBA', size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(shadow)
        draw.ellipse([(0, 0), size], fill=color)
        shadow_blur = shadow.filter(ImageFilter.GaussianBlur(radius))
        return shadow_blur

    def create_depth(self, size, color):
        depth = Image.new('RGBA', size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(depth)
        draw.ellipse([(0, 0), size], fill=color)
        return depth

    def create_twinkle(self, size, color):
        twinkle = Image.new('RGBA', size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(twinkle)
        draw.ellipse([(0, 0), size], fill=color)
        return twinkle

    def create_wheel_image(self, size):
        wheel = Image.new('RGBA', size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(wheel)
        gradient = self.create_gradient(size, (255, 255, 255), (200, 200, 200))
        wheel.alpha_composite(gradient)
        section_texture = self.create_section_texture((self.section_size, self.section_size))
        for i in range(self.num_sections):
            start_angle = i*360/self.num_sections
            end_angle = (i+1)*360/self.num_sections
            shadow = self.create_shadow((self.section_size, self.section_size), (0, 0, 0, 100), int(self.section_size/2))
            section = Image.new('RGBA', size, (255, 255, 255, 0))
            section_draw = ImageDraw.Draw(section)
            section.pieslice([(0, 0), (self.section_size, self.section_size)], start_angle, end_angle, fill=self.section_outlines[i % len(self.section_outlines)], outline=self.section_outlines[i % len(self.section_outlines)], width=self.section_widths[i % len(self.section_widths)])
            section.alpha_composite(shadow, (int((size-self.section_size)/2), int((size-self.section_size)/2)))
            section.alpha_composite(section_texture, (int((size-self.section_size)/2), int((size-self.section_size)/2)))
            depth = self.create_depth((self.section_size, self.section_size), (0, 0, 0, 100))
            section.alpha_composite(depth, (int((size-self.section_size)/2), int((size-self.section_size)/2)))
            twinkle = self.create_twinkle((self.section_size, self.section_size), (255, 255, 255, 100))
            section.alpha_composite(twinkle, (int((size-self.section_size)/2), int((size-self.section_size)/2)))
            wheel.paste(section.rotate(-self.current_angle+i*360/self.num_sections, expand=True), (0, 0), section.rotate(-self.current_angle+i*360/self.num_sections, expand=True))
        arrow_size = min(size)*0.1
        arrow = Image.new('RGBA', (arrow_size, arrow_size), self.arrow_color)
        draw_arrow = ImageDraw.Draw(arrow)
        draw_arrow.polygon([(0, 0), (arrow_size/2, arrow_size), (arrow_size, 0)], fill=self.arrow_color, outline=self.arrow_color, width=self.arrow_width, joint=self.arrow_joint)
        arrow_angle = random.uniform(0, 360)
        arrow_rotated = arrow.rotate(arrow_angle, expand=True)
        wheel.paste(arrow_rotated, (int((size-arrow_rotated.size[0])/2), int((size-arrow_rotated.size[1])/2)), arrow_rotated)
        return wheel

    def rotate_wheel(self):
        self.current_angle += random.uniform(10, 20)

    def get_wheel_image(self, size):
        self.rotate_wheel()
        return self.create_wheel_image(size)


class Animation:
    def __init__(self, participants, duration, loop):
        self.participants = participants
        self.duration = duration
        self.loop = loop

    def generate_animation(self):
        try:
            wheel = Wheel(self.participants, 12, 30, [(255, 0, 0), (0, 0, 0)], [2, 2], (255, 255, 0), 2, 'round', ImageFont.truetype('fonts/Montserrat-Bold.ttf', 20))
            frames = []
            for i in range(self.duration):
                frame = wheel.get_wheel_image((300, 300))
                frames.append(frame)
            for i in range(self.loop):
                frames.append(frames)
                frames[0].save('animation.gif', save_all=True, append_images=frames[1:], optimize=False, duration=50, loop=0)
        except Exception as e:
            logging.error(f"Error generating animation: {e}")


if __name__ == '__main__':
    logging.basicConfig(filename='animation.log', level=logging.ERROR)
    try:
        animation = Animation(['Alice', 'Bob', 'Charlie', 'Dave', 'Eve'], 100, 3)
        animation.generate_animation()
    except Exception as e:
        logging.error(f"Error generating animation: {e}")
