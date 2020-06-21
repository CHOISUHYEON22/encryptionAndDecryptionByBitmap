from inspect import getabsfile, currentframe
from Clojure_fn import drop_while, partition_by
from random import randint, sample
from functools import reduce
from PIL import Image
import shutil
import hgtk
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


def get_rand(set=randint(0, 255), i=0): return tuple(set if j == i else randint(0, 255) for j in range(3))


def pl_iter(*args): return reduce(lambda s, i: s + i, map(tuple, args))


def build_size(PLAIN: str, LENGTH: int, LENGTH_NAME: int):

    ALIQUOT = tuple(i for i in range(1, int(LENGTH ** 0.5) + 1) if LENGTH % i == 0)

    if len(ALIQUOT) < 2 or ALIQUOT[-1] <= LENGTH_NAME: return build_size(PLAIN + "@", LENGTH + 1, LENGTH_NAME)

    ENDL_RANGE = range(ALIQUOT[-1] - 1, LENGTH - 1, ALIQUOT[-1])

    if len(drop_while(lambda x: PLAIN[x] not in ("$", "뺊") or PLAIN[x] != PLAIN[x + 1], tuple(ENDL_RANGE))) != len(ENDL_RANGE):

        return build_size(PLAIN + "@", LENGTH + 1, LENGTH_NAME)

    return PLAIN, ALIQUOT[-1] + 1, LENGTH // ALIQUOT[-1] + 2


def kr_encrypt(CHAR: str):

    RANGE = ((11, 21), (10, 23), (7, 29))

    if not CHAR: return get_rand()

    CHAR_TUPLE = hgtk.letter.decompose(CHAR)

    return tuple((randint(1, RANGE[i][0]) * RANGE[i][1] + KR_DICT[i][CHAR_TUPLE[i]] for i in range(3)))


def en_encrypt(CHAR: str): return randint(0, 1) * 128 + ord(CHAR)


def handle_plain(FILE_NAME: str, PATH: str):

    shutil.copy(PATH + "\\" + FILE_NAME, "TASK.txt")

    try:

        with open("TASK.txt", "rt") as f: PLAIN = f.read().replace("\n", "`") + "?"

    except UnicodeDecodeError:

        try:

            with open("TASK.txt", "rt", encoding="utf-8") as f: PLAIN = f.read().replace("\n", "`") + "?"

        except UnicodeDecodeError: print("ERROR FILE : " + FILE_NAME); return

    os.remove(r"TASK.txt")

    NAME, EXT = (i + "?" for i in os.path.splitext(FILE_NAME))

    return tuple(''.join(map(lambda x: x if x.isascii() else f"$${x}뺊뺊", map(lambda x: ''.join(x), partition_by(lambda x: x.isascii(), i)))) for i in (PLAIN, NAME, EXT))


def encrypt_process(RAW_PLAIN: str, name_ext: tuple, file_name: str, path: str):

    index = lambda: (WIDTH - 1) * i + j - 1

    PLAIN, WIDTH, HEIGHT = build_size(RAW_PLAIN, len(RAW_PLAIN), len(name_ext[0]))

    IMG_BOARD = Image.new("RGB", (WIDTH, HEIGHT), (255, 255, 255))

    IMG = IMG_BOARD.load()

    NA_EXT_PL = tuple(reduce(lambda s, i: s + i, (tuple(name_ext[i]) + tuple("" for l in range(WIDTH - 1 - len(name_ext[i]))) for i in range(2)))) + tuple(PLAIN)

    CRITERIA = tuple(randint(0, 2) for l in range(HEIGHT))

    for i in range(HEIGHT):

        for j in range(WIDTH):

            if j == 0: IMG[j, i] = get_rand(randint(1, 84) * 3 + CRITERIA[i])

            else:

                TEXT = NA_EXT_PL[index()]

                IMG[j, i] = get_rand(en_encrypt(TEXT), CRITERIA[i]) if TEXT and TEXT.isascii() else kr_encrypt(TEXT)

    IMG_BOARD.save(path + "\\" + file_name + ".bmp")


def input_proc(QUES: str, COND = lambda X: X in ('Y', 'N'), RAISE_ERROR: bool = False):

    if RAISE_ERROR: print("Please enter a valid value.\n")

    INPUT = input(QUES).replace("\\", "\\")

    try: return INPUT if COND(INPUT) else input_proc(QUES, COND, True)

    except (FileNotFoundError, OSError): return input_proc(QUES, COND, True)


def singular(FILE_PATH, O_R: str, D_P: str, FILE_TUPLE: tuple = None):

    RANGE = tuple(chr(i) for i in pl_iter(range(65, 91), range(97, 123))) + ("~", "!", "#", "_", "$", "^", "%", "(", ")", ".", ";")

    POSSIBLE_PATH, FILE_NAME = os.path.split(FILE_TUPLE[int(FILE_PATH)] if FILE_TUPLE and FILE_PATH.isdecimal() else FILE_PATH)

    PATH = POSSIBLE_PATH if POSSIBLE_PATH else "./"

    TEMP_HP = handle_plain(FILE_NAME, PATH)

    input("DEBUG : ") # debug

    if TEMP_HP:

        PLAIN, NAME, EXT = TEMP_HP[0], TEMP_HP[1], TEMP_HP[2]

        WILL = NAME if O_R == "O" else "".join(sample(RANGE, randint(4, 10)))

        print(f"{FILE_NAME} -> {WILL}.bmp")

        encrypt_process(PLAIN, (NAME, EXT), WILL, PATH)

    if D_P == "D": os.remove(rf"{PATH}\\{FILE_NAME}")


def plural(PATH: str, O_R: str, D_P: str, EXT_T: tuple):

    set(singular(os.path.join(p, v), O_R, D_P) for p, _, fs in os.walk(PATH) if os.access(p, os.X_OK) for v in fs if os.path.splitext(v)[1] in EXT_T and v != getabsfile(currentframe()))


def file_tuple():

    FILE_TUPLE = tuple(v for v in os.listdir(".") if os.path.isfile(v))

    print(f"\n{' List Of Files In The Current Directory ':=^61}",
          reduce(lambda s, i: s + f"  [{i[0]:0>3}] : {i[1]}\n", enumerate(FILE_TUPLE), ""),
          f"{' END ':=^61}\n", sep="\n")

    return FILE_TUPLE


if __name__ == '__main__':

    print(f"\n{'[ENCRYPTION]':^61}")

    WANT2PLURAL = input_proc("Do you want to encrypt all the files in the folder you want and its subfolders?\n[Y]es OR [N]o : ")

    NAMING = input_proc("What would you like to name the encrypted file?\n[O]riginal OR [R]andom : ", lambda x: x in ("O", "R"))

    DEL_PRESERVE = input_proc("What about the remaining bitmap file after encoding?\n[D]elete OR [P]reserve : ", lambda x: x in ("D", "P"))

    if WANT2PLURAL == "Y":

        PATH = input_proc("Enter the path of the folder you want to encrypt.\n : ", lambda x: os.path.isdir(x))

        EXT_T = input_proc("Enter the extension you want to encrypt(e.g. .txt .py).\n : ", lambda x: False not in map(lambda y: y[0] == ".", x.split(" "))).split(" ")

        plural(PATH, NAMING, DEL_PRESERVE, tuple(EXT_T))

    else:

        FILE_TUPLE = file_tuple()

        FILE_SIG = input_proc("file name(or number) : ", lambda x: x in FILE_TUPLE + tuple(str(i) for i in range(len(FILE_TUPLE))))

        singular(FILE_SIG, NAMING, DEL_PRESERVE, FILE_TUPLE)

    input('\nSuccessfully.\n\nIf you want to quit, press any button. ')
