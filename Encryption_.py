from inspect import getabsfile, currentframe
from random import randint, sample
from PIL import Image
import shutil
import hgtk
import os

j_and_m = (
    ('ㄱ', 'ㄲ', 'ㄴ', 'ㄷ', 'ㄸ', 'ㄹ', 'ㅁ', 'ㅂ', 'ㅃ', 'ㅅ',
     'ㅆ', 'ㅇ', 'ㅈ', 'ㅉ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ', ''),  # 20
    ('ㅏ', 'ㅐ', 'ㅑ', 'ㅒ', 'ㅓ', 'ㅔ', 'ㅕ',
     'ㅖ', 'ㅗ', 'ㅘ', 'ㅙ', 'ㅚ', 'ㅛ', 'ㅜ',
     'ㅝ', 'ㅞ', 'ㅟ', 'ㅠ', 'ㅡ', 'ㅢ', 'ㅣ', ''),  # 22
    ('ㄱ', 'ㄲ', 'ㄳ', 'ㄴ', 'ㄵ', 'ㄶ', 'ㄷ', 'ㄹ', 'ㄺ',
     'ㄻ', 'ㄼ', 'ㄽ', 'ㄾ', 'ㄿ', 'ㅀ', 'ㅁ', 'ㅂ', 'ㅄ',
     'ㅅ', 'ㅆ', 'ㅇ', 'ㅈ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ', '')  # 28
)

KR_DICT = tuple(({j_and_m[i][j]: j for j in range(len(j_and_m[i]))} for i in range(3)))


class IncorrectSizingError(Exception):

    def __init__(self, msg="The length of the width and height is set incorrectly."): self.msg = msg

    def __str__(self): return self.msg


def build_size(plain: str, length: int, length_name: int):

    while True:

        try:

            aliquot = [i for i in range(1, int(length**0.5) + 1) if length % i == 0]

            if len(aliquot) < 2 or aliquot[-1] <= length_name: raise Warning

            for i in range(aliquot[-1] - 1, length - 1, aliquot[-1]):

                if plain[i] in ("$", "뺊") and plain[i] == plain[i + 1]: raise Warning

            else: break

        except Warning: plain, length = plain + "@", length + 1

    return plain, aliquot[-1] + 1, length // aliquot[-1] + 2


def kr_encrypt(char: str):

    Range = ((11, 21), (10, 23), (7, 29))

    char_tuple = hgtk.letter.decompose(char)

    return tuple((randint(1, Range[i][0]) * Range[i][1] + KR_DICT[i][char_tuple[i]] for i in range(3)))


def en_encrypt(char: str): return randint(0, 1) * 128 + ord(char)


def handle_plain(file_name: str, path: str):

    shutil.copy(path + "\\" + file_name, "TASK.txt")

    try:

        with open("TASK.txt", "rt") as f: plain = f.read().replace("\n", "`")

    except UnicodeDecodeError:

        try:

            with open("TASK.txt", "rt", encoding="utf-8") as f: plain = f.read().replace("\n", "`")

        except UnicodeDecodeError: print("ERROR FILE : " + file_name); return

    os.remove(r"TASK.txt")

    name, ext = os.path.splitext(file_name)

    name, ext, plain = name + "?", ext + "?", plain + "?"

    data = {"plain" : plain, "name" : name, "ext" : ext}

    insert_str = lambda index: v[:index] + ("뺊뺊" if kr_ing else "$$") + v[index:]

    for k in data.keys():

        count, kr_ing, v = 0, False, data[k]

        for i, u in enumerate(data[k]):

            if (not u.isascii() and not kr_ing) or (u.isascii() and kr_ing):

                v, kr_ing, count = insert_str(i + 2 * count), not kr_ing, count + 1

        if kr_ing: v += "뺊뺊"

        data[k] = v

    return tuple(data.values())


def encrypt_process(plain: str, name_ext: tuple, file_name: str, path: str):

    get_rand = lambda set=randint(0, 255), i=0: tuple((set if j == i else randint(0, 255) for j in range(3)))

    index = lambda : (width - 1) * (i - 2) + j - 1

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

    img_board.save(path + "\\" + file_name + ".bmp")


def question(ques: str, cond):

    while True:

        scan = input(ques)

        if cond(scan): print(); return scan

        print("Please enter a valid value.\n")


def singular(file_name, OorR: str, DorP: str, file_tuple: tuple = None):

    Range = [chr(i) for i in list(range(65, 91)) + list(range(97, 123))] + ["~", "!", "#", "_", "$", "^", "%", "(", ")", ".", ";"]

    if file_tuple and file_name.isdecimal(): file_name = file_tuple[int(file_name)]

    path, file_name = os.path.split(file_name)

    if not path: path = "./"

    temp_hp = handle_plain(file_name, path)

    if temp_hp:

        plain, name, ext = temp_hp[0], temp_hp[1], temp_hp[2]

        will = name if OorR == "O" else "".join(sample(Range, randint(4, 10)))

        print(f"{file_name} -> {will}.bmp")

        encrypt_process(plain, (name, ext), will, path)

    if DorP == "D": os.remove(rf"{path}\\{file_name}")


def plural(path: str, OorR: str, DorP: str, ext_t: tuple):

    tuple(singular(os.path.join(p, v), OorR, DorP) for p, _, fs in os.walk(path) if os.access(p, os.X_OK)
          for v in fs if os.path.splitext(v)[1] in ext_t and v != getabsfile(currentframe()))


def file_tuple():

    file_tuple = tuple(v for v in os.listdir(".") if os.path.isfile(v))

    print(f"\n{' List Of Files In The Current Directory ':=^61}\n")

    for i, v in enumerate(file_tuple): print(f"  [{i:0>3}] : {v}")

    print(f"\n{' END ':=^61}\n")

    return file_tuple


if __name__ == '__main__':

    print(f"\n{'[ENCRYPTION]':^61}")

    want2plural = question("Do you want to encrypt all the files in the folder you want and its subfolders?\n[Y]es OR [N]o : ", lambda x: x in ("Y", "N"))

    naming = question("What would you like to name the encrypted file?\n[O]riginal OR [R]andom : ", lambda x: x in ("O", "R"))

    del_preserve = question("What about the remaining bitmap file after encoding?\n[D]elete OR [P]reserve : ", lambda x: x in ("D", "P"))

    if want2plural == "Y":

        path = question("Enter the path of the folder you want to encrypt.\n : ", lambda x: os.path.isdir(x))

        ext_t = question("Enter the extension you want to encrypt(e.g. .txt .py).\n : ", lambda x: False not in map(lambda y: y[0] == ".", x.split(" "))).split(" ")

        plural(path, naming, del_preserve, tuple(ext_t))

    else:

        file_tuple = file_tuple()

        file_sig = question("file name(or number) : ", lambda x: x in file_tuple + tuple(str(i) for i in range(len(file_tuple))))

        singular(file_sig , naming, del_preserve, file_tuple)

    input('\nSuccessfully.\n\nIf you want to quit, press any button. ')
