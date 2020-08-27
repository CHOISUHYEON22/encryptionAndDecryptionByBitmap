from inspect import getabsfile, currentframe
from Clojure_fn import drop_while, partition_by, partition_num
from random import randint, sample
from collections import namedtuple
from functools import reduce
from PIL import Image
import shutil
import hgtk
import sys
import os

J_AND_M = (
    ('ㄱ', 'ㄲ', 'ㄴ', 'ㄷ', 'ㄸ', 'ㄹ', 'ㅁ', 'ㅂ', 'ㅃ', 'ㅅ',
     'ㅆ', 'ㅇ', 'ㅈ', 'ㅉ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ', ''),  # 20
    ('ㅏ', 'ㅐ', 'ㅑ', 'ㅒ', 'ㅓ', 'ㅔ', 'ㅕ',
     'ㅖ', 'ㅗ', 'ㅘ', 'ㅙ', 'ㅚ', 'ㅛ', 'ㅜ',
     'ㅝ', 'ㅞ', 'ㅟ', 'ㅠ', 'ㅡ', 'ㅢ', 'ㅣ', ''),  # 22
    ('ㄱ', 'ㄲ', 'ㄳ', 'ㄴ', 'ㄵ', 'ㄶ', 'ㄷ', 'ㄹ', 'ㄺ',
     'ㄻ', 'ㄼ', 'ㄽ', 'ㄾ', 'ㄿ', 'ㅀ', 'ㅁ', 'ㅂ', 'ㅄ',
     'ㅅ', 'ㅆ', 'ㅇ', 'ㅈ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ', '')  # 28
)

KR_DICT = tuple(({J_AND_M[i][j]: j for j in range(len(J_AND_M[i]))} for i in range(3)))


class IncorrectSizingError(Exception):

    def __init__(self, msg="The length of the width and height is set incorrectly."): self.msg = msg

    def __str__(self): return self.msg


def get_rand_rgb(set, i=0) -> tuple: return tuple(set if j == i else randint(0, 255) for j in range(3))


def pl_iter(*args) -> iter: return reduce(lambda s, i: s + i, map(tuple, args))


def build_size(plain: str, length: int, length_of_name: int) -> tuple:

    aliquot = tuple(i for i in range(1, int(length ** 0.5) + 1) if length % i == 0)

    if len(aliquot) < 2 or aliquot[-1] <= length_of_name: return build_size(plain + "@", length + 1, length_of_name)

    endl_range = range(aliquot[-1] - 1, length - 1, aliquot[-1])

    if len(drop_while(lambda x: plain[x] not in ("$", "뺊") or plain[x] != plain[x + 1], tuple(endl_range))) != len(endl_range):

        return build_size(plain + "@", length + 1, length_of_name)

    return plain, aliquot[-1] + 1, length // aliquot[-1] + 2


def kr_encrypt(char: str) -> tuple:

    if not char: return get_rand_rgb(randint(0, 255))  # 처리 필요

    const_of_encrypt_formula = namedtuple('const_of_encrypt_formula', 'max_num_for_under_255 num_of_each_syllables_pl_1')

    const_gathering = tuple(const_of_encrypt_formula(i, j) for i, j in ((11, 21), (10, 23), (7, 29)))

    char_tuple = hgtk.letter.decompose(char)

    return tuple(randint(1, const_gathering[i][0]) * const_gathering[i][1] + KR_DICT[i][char_tuple[i]] for i in range(3))


def en_encrypt(char: str, criteria: int) -> tuple: return get_rand_rgb(randint(0, 1) * 128 + ord(char), criteria)


def handle_plain(file_name: str, path: str) -> iter:

    def get_plain(encoding = None):

        try:

            with open("TASK.txt", "rt", encoding=encoding) as f:

                return f.read().replace("\n", "`") + "?"

        except UnicodeDecodeError: return None if encoding else get_plain("utf-8")

    shutil.copy(path + "\\" + file_name, "TASK.txt")

    plain = get_plain()

    if not plain: print("ERROR FILE : " + file_name); return

    os.remove(r"TASK.txt")

    name, ext = (i + "?" for i in os.path.splitext(file_name))

    return ("".join((j if j.isascii() else f"$${j}뺊뺊" for j in (''.join(k) for k in partition_by(lambda x: x.isascii(), i)))) for i in (plain, name, ext))


def build_key_once(width: int, height: int, path: str, file_name: str):

    img_board = Image.new("RGB", (width, height), (255, 255, 255))

    img = img_board.load()

    key = tuple(tuple(get_rand_rgb(randint(0, 255)) for _ in range(width)) for _ in range(height))

    for h in range(height):

        for w in range(width):

            img[w, h] = key[h][w]

    img_board.save(path + f"/{file_name}_key.bmp")

    return key



def encrypt_once(raw_plain: str, name_ext: tuple, file_name: str, path: str):

    try: plain, width, height = build_size(raw_plain, len(raw_plain), len(name_ext[0]))

    except RecursionError:

        print("\nA recursive error occurred while calculating the size of the encryption file.\nPlease allow more memory.")

        return False

    key = build_key_once(width, height, path, file_name)

    img_board = Image.new("RGB", (width, height), (255, 255, 255))

    img = img_board.load()

    criteria = tuple(randint(0, 2) for _ in range(height))

    formulaic_na_ext_pl = tuple(name_ext[i] + " " * (width - 1 - len(name_ext[i])) for i in range(2)) + partition_num(width - 1, True, plain)

    pre_encryption = tuple((get_rand_rgb(criteria[h]), ) + tuple(en_encrypt(t, criteria[h]) if t and t.isascii() else kr_encrypt(t) for t in w) for h, w in enumerate(formulaic_na_ext_pl))

    encryption_result = tuple(tuple(tuple(pre_encryption[h][w][c] ^ key[h][w][c] for c in range(3)) for w in range(width)) for h in range(height))

    for h in range(height):

        for w in range(width):

            img[w, h] = encryption_result[h][w]

    img_board.save(path + "/" + file_name + ".bmp")

    return True


def input_proc(ques: str, cond = lambda X: X in ('Y', 'N'), raise_error: bool = False):

    if raise_error: print("Please enter a valid value.\n")

    input_data = input(ques).replace("\\", "\\")

    try: return input_data if cond(input_data) else input_proc(ques, cond, True)

    except (FileNotFoundError, OSError): return input_proc(ques, cond, True)


def singular(file_path, original_rand: str, del_preserve: str, file_tuple: tuple = None):

    possible_char_in_file_name = tuple(chr(i) for i in pl_iter(range(65, 91), range(97, 123))) + ("~", "!", "#", "_", "$", "^", "%", "(", ")", ".", ";")

    possible_path, file_name = os.path.split(file_tuple[int(file_path)] if file_tuple and file_path.isdecimal() else file_path)

    path = possible_path if possible_path else "."

    try:

        plain, name, ext = handle_plain(file_name, path)

        will = name if original_rand == "O" else "".join(sample(possible_char_in_file_name, randint(4, 10)))

        print(f"{file_name} -> {will}.bmp")

        is_normal = encrypt_once(plain, (name, ext), will, path)

        if is_normal and del_preserve == "D": os.remove(rf"{path}\\{file_name}")

    except TypeError: pass


def get_accessible_path_file(path: str, ext_t: tuple) -> iter:

    return (os.path.join(p, f) for p, _, fs in os.walk(path) if os.access(p, os.X_OK) for f in fs if os.path.splitext(f)[1] in ext_t and f != getabsfile(currentframe()))


def plural(accessible_path_file: iter, original_rand: str, del_preserve: str):

    try:

        singular(next(accessible_path_file), original_rand, del_preserve)

        plural(accessible_path_file, original_rand, del_preserve)

    except StopIteration: pass


def file_tuple():

    file_tuple = tuple(v for v in os.listdir(".") if os.path.isfile(v))

    print(f"\n{' List Of Files In The Current Directory ':=^61}")

    print(reduce(lambda s, i: s + f"  [{i[0]:0>3}] : {i[1]}\n", enumerate(file_tuple), ""))

    print(f"{' END ':=^61}")

    return file_tuple


if __name__ == '__main__':

    print(f"\n{'[ENCRYPTION]':^61}")

    want2plural = input_proc("Do you want to encrypt all the files in the folder you want and its subfolders?\n[Y]es OR [N]o : ")

    naming = input_proc("What would you like to name the encrypted file?\n[O]riginal OR [R]andom : ", lambda x: x in ("O", "R"))

    del_preserve = input_proc("What about the remaining bitmap file after encoding?\n[D]elete OR [P]reserve : ", lambda x: x in ("D", "P"))

    max_recursion = input_proc("How much memory can you allocate (default is 1000 recursions)?\n : ", lambda x: x.isdecimal())

    sys.setrecursionlimit(int(max_recursion))

    if want2plural == "Y":

        path = input_proc("Enter the path of the folder you want to encrypt.\n : ", lambda x: os.path.isdir(x))

        ext_t = input_proc("Enter the extension you want to encrypt(e.g. .txt .py).\n : ", lambda x: False not in map(lambda y: y[0] == ".", x.split(" "))).split(" ")

        plural(get_accessible_path_file(path, tuple(ext_t)), naming, del_preserve)

    else:

        file_tuple = file_tuple()

        file_sig = input_proc("file name(or number) : ", lambda x: x in file_tuple + tuple(str(i) for i in range(len(file_tuple))))

        singular(file_sig, naming, del_preserve, file_tuple)

    input('\n\nIf you want to quit, press any button. ')
