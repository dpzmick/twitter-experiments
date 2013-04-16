import pygame
from math import sqrt, floor
import sys

# nearest perfect square
def nps(n):
    while floor(sqrt(n)) != sqrt(n):
        n += 1
    return n

# build input_data array containing tuples
# (relevance, total_retweets, non df percent)
# data file is CSV file with format
# ID, REL, DF_RT, IN_RT, TOT_RT, RT_PERCENT
data_file_name = 'intruige/BarackObama.csv'
data_file = open(data_file_name)
input_data = []

# skip header
data_file.next()
for line in data_file:
    dat = line.strip().split(',')
    rel = float(dat[1])
    tot = float(dat[4])
    perc = 1 - float(dat[5])
    _id = dat[0]
    input_data.append((rel, tot, perc, _id))

max_rel = max(map(lambda el: el[0], input_data))
max_trc = max(map(lambda el: el[1], input_data))
max_perc = max(map(lambda el: el[2], input_data))

# colors
colors = [(237, 248, 233),
          (186, 228, 179),
          (116, 196, 118),
          (49, 163, 84),
          (0, 109, 44)]

image_side_length = 800
pieces = nps(len(input_data))
plot_side_length = floor(image_side_length / sqrt(pieces))
max_v = plot_side_length - 0.05*plot_side_length

scaled_data = []
for el in input_data:
    color_index = int(((el[2]*(len(colors) - 1))/max_perc ))
    color = colors[color_index]
    scaled_data.append(((el[0]*max_v)/max_rel, (el[1]*max_v)/max_trc, color,
        el[3]))

pygame.init()
screen = pygame.display.set_mode((image_side_length + 200, image_side_length))

tracker = {}

x = y = 0
for el in scaled_data:
    r = (   range(int(x), int(x + plot_side_length)),
            range(int(y), int(y + plot_side_length)))
    tracker[el[3]] = r
    xc = x + ((plot_side_length - el[0]) / 2)
    yc = y + (plot_side_length - el[1]) / 2
    pygame.draw.rect(screen, el[2], (xc, yc, el[0], el[1]), 0)
    x += plot_side_length
    if x > image_side_length - plot_side_length:
        y += plot_side_length
        x = 0

# make legend
color_bar_x = 50
color_bar_y = 10
x = image_side_length + 200 - color_bar_x
y = 10
for color in colors:
    pygame.draw.rect(screen, color, (x,y,color_bar_x,color_bar_y), 0)
    y += 10

# the rest of the legend will be added to saved images

pygame.display.update()
pygame.image.save(screen, 'out.jpg')

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit(); sys.exit();
        if event.type == pygame.MOUSEBUTTONUP:
            pos = pygame.mouse.get_pos()
            for _id, r in tracker.iteritems():
                if pos[0] in r[0] and pos[1] in r[1]:
                    print _id
