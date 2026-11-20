from vpython import *

# 빛나는 컬러 피아노: 건반을 누르면 그 음의 색으로 빛나고, 버튼으로 악기를 바꾸거나 곡을 연주합니다.
scene.background = vector(0.03, 0.03, 0.07)
scene.center = vector(0, 0.4, 0)
scene.range = 5.4
scene.ambient = vector(197, 33, 33)(0.9)  # 흰 건반이 밝게 보이도록 환경광을 올립니다

# 악기: (이름, 소리 종류, 조명 색)
instruments = [
    ('피아노', 'piano', color.cyan),
    ('오르골', 'musicbox', color.magenta),
    ('플루트', 'sine', vector(0.4, 1, 0.6)),
    ('8비트', 'square', color.yellow),
    ('신시사이저', 'sawtooth', color.orange),
    ('부드러운 건반', 'triangle', vector(0.6, 0.6, 1)),
]
current = 0

# 곡: (음, 박) 목록. None은 쉼표입니다.
# 작은별·코로베이니키(러시아 민요)는 저작권이 끝난 곡이고, 우주 모험은 이 작품을 위해 새로 지은 곡입니다.
songs = {
    '작은별': [('도', 2), ('도', 2), ('솔', 2), ('솔', 2), ('라', 2), ('라', 2), ('솔', 4),
              ('파', 2), ('파', 2), ('미', 2), ('미', 2), ('레', 2), ('레', 2), ('도', 4)],
    '코로베이니키(민요)': [('시', 2), ('파#', 1), ('솔', 1), ('라', 2), ('솔', 1), ('파#', 1),
                    ('미', 2), ('미', 1), ('솔', 1), ('시', 2), ('라', 1), ('솔', 1),
                    ('파#', 3), ('솔', 1), ('라', 2), ('시', 2), ('솔', 2), ('미', 2), ('미', 4)],
    '우주 모험(오리지널)': [('도', 1), ('미', 1), ('솔', 1), ('도5', 1), ('시', 1), ('솔', 1), ('미', 2),
                     ('라', 1), ('파', 1), ('레', 1), ('파', 1), ('솔', 2), (None, 1),
                     ('미', 1), ('솔', 1), ('도5', 2), ('시', 1), ('라#', 1), ('도5', 4)],
}
song = []      # 연주 중인 곡
song_pos = 0   # 다음에 연주할 음의 위치
wait = 0       # 다음 음까지 남은 프레임
BEAT = 7       # 한 박의 프레임 수(30프레임 = 1초)

white_notes = ['도', '레', '미', '파', '솔', '라', '시', '도5']
black_notes = [('도#', 0), ('레#', 1), ('파#', 3), ('솔#', 4), ('라#', 5)]

keys = {}         # 건반 id → (음, 건반, 원래 색, 빛 색)
note_to_key = {}  # 음 이름 → (음, 건반, 원래 색, 빛 색)
start_x = -3.5
for i, name in enumerate(white_notes):
    glow = color.hsv_to_rgb(vector(i / 8, 0.8, 1))  # 음마다 무지개 색 하나
    k = box(pos=vector(start_x + i, 0, 0), size=vector(0.95, 3, 0.4), color=vector(0.92, 0.92, 0.95))
    keys[k._id] = (name, k, k.color, glow)
    note_to_key[name] = keys[k._id]
    box(pos=vector(start_x + i, -1.65, 0.1), size=vector(0.9, 0.12, 0.3), color=glow, emissive=True)
    label(pos=vector(start_x + i, -2.1, 0), text=name, height=14, color=glow, box=False)

for name, i in black_notes:
    glow = color.hsv_to_rgb(vector((i + 0.5) / 8, 0.9, 1))
    k = box(pos=vector(start_x + i + 0.5, 0.6, 0.35), size=vector(0.55, 1.8, 0.4), color=vector(0.08, 0.08, 0.1))
    keys[k._id] = (name, k, k.color, glow)
    note_to_key[name] = keys[k._id]

bar = box(pos=vector(0, 2.1, 0), size=vector(8.2, 0.15, 0.3), color=instruments[0][2], emissive=True)
lamp = local_light(pos=vector(0, 1.5, 3), color=vector(0, 0, 0))
status = label(pos=vector(0, 3.0, 0), text='건반을 클릭해 보세요 · 악기: 피아노', height=18, color=color.white, box=False)

lit = []     # [건반, 원래 색, 남은 프레임]
sparks = []  # [빛 구슬, 남은 프레임]

def play_key(name, k, base, glow, length=0.7):
    inst_name, sound_type, inst_color = instruments[current]
    play_note(name, length, sound_type, 0.4)
    k.color = glow
    k.emissive = True
    k.pos = k.pos + vector(0, 0, -0.15)
    lamp.color = glow
    bar.color = glow
    status.text = name + ' · 악기: ' + inst_name
    lit.append([k, base, 14])
    sparks.append([sphere(pos=k.pos + vector(0, 1.6, 0.4), radius=0.18, color=glow, emissive=True), 20])

def on_click(evt):
    if evt.pick in keys:
        name, k, base, glow = keys[evt.pick]
        play_key(name, k, base, glow)

def choose(index):
    global current
    current = index
    inst_name, sound_type, inst_color = instruments[index]
    bar.color = inst_color
    status.text = '악기: ' + inst_name + ' · 건반을 눌러 보세요'
    play_note('도5', 0.3, sound_type, 0.3)  # 바뀐 악기 소리를 미리 들려줍니다

def start_song(title):
    global song, song_pos, wait
    song = songs[title]
    song_pos = 0
    wait = 0

def stop_song():
    global song
    song = []

scene.bind('click', on_click)
for i, inst in enumerate(instruments):
    button(text=inst[0], bind=lambda b, index=i: choose(index))
for title in songs:
    button(text='♪ ' + title, bind=lambda b, t=title: start_song(t))
button(text='■ 곡 멈춤', bind=lambda b: stop_song())

while True:
    rate(30)
    # 곡 연주: 박자마다 다음 음의 건반을 눌러 소리와 빛을 함께 냅니다
    if song:
        if wait <= 0:
            if song_pos < len(song):
                name, beats = song[song_pos]
                if name in note_to_key:
                    n, k, base, glow = note_to_key[name]
                    play_key(n, k, base, glow, beats * BEAT / 30)
                wait = beats * BEAT
                song_pos += 1
            else:
                song = []
        wait -= 1
    for item in lit[:]:
        item[2] -= 1
        if item[2] <= 0:
            item[0].color = item[1]
            item[0].emissive = False
            item[0].pos = item[0].pos + vector(0, 0, 0.15)
            lit.remove(item)
    for item in sparks[:]:
        item[0].pos = item[0].pos + vector(0, 0.08, 0)
        item[0].radius = item[0].radius * 0.95
        item[1] -= 1
        if item[1] <= 0:
            item[0].visible = False
            sparks.remove(item)
    lamp.color = lamp.color * 0.9  # 조명이 서서히 꺼집니다
