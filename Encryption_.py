from typing import Dict, List
from random import randint, sample
from PIL import Image
import shutil
import hgtk
import os


class IncorrectSizingError(Exception):

    def __init__(self, msg="The length of the width and height is set incorrectly."): self.msg = msg

    def __str__(self): return self.msg


def build_size(plain: str, length: int, length_name: int):

    def size_control(plain, length):  return plain + "@", length + 1

    while True:

        try:

            aliquot = [i for i in range(1, int(length**0.5) + 1) if length % i == 0]

            if len(aliquot) < 2 or aliquot[-1] <= length_name: raise Warning

            for i in range(aliquot[-1] - 1, length - 1, aliquot[-1]):

                if plain[i] in ("$", "뺊") and plain[i] == plain[i + 1]: raise Warning

            else: break

        except Warning: plain, length = size_control(plain, length)

    return plain, aliquot[-1] + 1, length // aliquot[-1] + 2


def kr_dict():
    j_and_m_dict: List[Dict[str, int]] = [{}, {}, {}]
    j_and_m = (
        ('ㄱ', 'ㄲ', 'ㄴ', 'ㄷ', 'ㄸ', 'ㄹ', 'ㅁ', 'ㅂ', 'ㅃ','ㅅ',
         'ㅆ', 'ㅇ', 'ㅈ', 'ㅉ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ', ''), #20
        ('ㅏ', 'ㅐ', 'ㅑ', 'ㅒ', 'ㅓ', 'ㅔ', 'ㅕ',
         'ㅖ', 'ㅗ', 'ㅘ', 'ㅙ', 'ㅚ', 'ㅛ', 'ㅜ',
         'ㅝ', 'ㅞ', 'ㅟ', 'ㅠ', 'ㅡ', 'ㅢ', 'ㅣ', ''), #22
        ('ㄱ', 'ㄲ', 'ㄳ', 'ㄴ', 'ㄵ', 'ㄶ', 'ㄷ', 'ㄹ', 'ㄺ',
         'ㄻ', 'ㄼ', 'ㄽ', 'ㄾ', 'ㄿ', 'ㅀ', 'ㅁ', 'ㅂ', 'ㅄ',
         'ㅅ', 'ㅆ', 'ㅇ', 'ㅈ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ', '') #28
    )

    for i in range(3):

        for j in range(len(j_and_m[i])):

            j_and_m_dict[i][j_and_m[i][j]] = j

    return j_and_m_dict

def kr_encrypt(char: str):

    global KR_DICT

    Range = ((11, 21), (10, 23), (7, 29))

    char_tuple = hgtk.letter.decompose(char)

    return tuple([randint(1, Range[i][0]) * Range[i][1] + KR_DICT[i][char_tuple[i]] for i in range(3)])


def en_encrypt(char: str): return randint(0, 1) * 128 + ord(char)


def handle_plain(path: str):

    shutil.copy(path, "TASK.txt")

    try:

        with open("TASK.txt", "rt") as f: plain = f.read().replace("\n", "`")

    except UnicodeDecodeError:

        with open("TASK.txt", "rt", encoding="utf-8") as f: plain = f.read().replace("\n", "`")

    os.remove("TASK.txt")

    if path[0] == ".": path = path[path.rindex("/") + 1:]

    name, ext = os.path.splitext(path)

    name, ext, plain = name + "?", ext + "?", plain + "?"

    data = {"plain" : plain, "name" : name, "ext" : ext}

    for k in data.keys():

        index = [[], []]
        kr_ing = False
        count = 0

        for i, v in enumerate(data[k]):

            if (not v.isascii() and not kr_ing) or (v.isascii() and kr_ing):

                index[int(kr_ing)].append(i + 2 * count)

                kr_ing = not kr_ing

                count += 1

        try:

            for i in range(len(index[0])):

                for j, v in ((0, "$$"), (1, "뺊뺊")):

                    data[k] = data[k][:index[j][i]] + v + data[k][index[j][i]:]

        except IndexError: data[k] += "뺊뺊"

    return tuple(data.values())


def encrypt_process(plain: str, name_ext: tuple, file_name):

    def index(): return (width - 1) * (i - 2) + j - 1

    def get_rand(set = randint(0, 255), i = 0):

        rand = [randint(0, 255), randint(0, 255)]

        rand.insert(i, set)

        return tuple(rand)

    plain, width, height = build_size(plain, len(plain), len(name_ext[0]))

    img_board = Image.new("RGB", (width, height), (255, 255, 255))

    img = img_board.load()

    kr_ing = False

    for i in range(height):

        criteria = randint(0, 2)

        img[0, i] = get_rand(randint(1, 84) * 3 + criteria)

        for j in range(1, width):

            isOpen = i in range(2)

            try:

                data, data_1 = (name_ext[i][j - 1], name_ext[i][j - 2]) if isOpen else (plain[index()], plain[index() - 1])

                img[j, i] = kr_encrypt(data) if kr_ing else get_rand(en_encrypt(data), criteria)

                if data in ("$", "뺊") and data == data_1: kr_ing = not kr_ing

            except IndexError:

                if isOpen: img[j, i] = get_rand()

                else: raise IncorrectSizingError

    img_board.save(file_name + ".bmp")


def question(ques: str, cond: tuple):

    while True:

        scan = input(ques)

        if scan in cond: break

        print("Please enter a valid value.\n")

    print()

    return scan


def singular(file_name: str, OorR: str):

    def naming(): return "".join(sample(Range, randint(4, 10)))

    Range = [chr(i) for i in list(range(65, 91)) + list(range(97, 123))] + \
            ["~", "!", "#", "_", "$", "^", "%", "(", ")", ".", ";"]

    plain, name, ext = handle_plain(file_name)

    will = naming() if OorR == "R" else name

    print(f"{file_name} -> {will}.bmp")

    encrypt_process(plain, (name, ext), will)


if __name__ == '__main__':

    KR_DICT = kr_dict()

    print("[ENCRYPTION]")

    singular(question("file name : ", tuple(os.listdir("."))),
             question("What would you like to name the encrypted file?\n[O]riginal OR [R]andom : ", ("O", "R")))

    print('\nSuccessfully.')

    input('\nIf you want to quit, press any button. ')
