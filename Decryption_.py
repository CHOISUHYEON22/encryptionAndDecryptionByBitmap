from hgtk.exception import NotHangulException
from functools import reduce
from PIL import Image
from glob import glob
import hgtk
import os

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

KR_DICT = tuple(({j : j_and_m[i][j] for j in range(len(j_and_m[i]))} for i in range(3)))


def find_all(COLL, ELEMENT, PRE_INDEX=0):

    try: INDEX = COLL.index(ELEMENT)

    except ValueError: return ()

    return (PRE_INDEX + INDEX,) + find_all(COLL[INDEX + len(ELEMENT):], ELEMENT, PRE_INDEX +  INDEX + len(ELEMENT))


def partition_by_index(COLL, INDEX):

    if len(INDEX) == 1: return (COLL[INDEX[0]:],)

    return (COLL[INDEX[0]:INDEX[1]],) + partition_by_index(COLL, INDEX[1:])


def kr_decrypt(RGB: tuple):

    try:

        RES = [KR_DICT[i][RGB[i] % v] for i, v in enumerate((21, 23, 29))]

        KO = hgtk.letter.compose(RES[0], RES[1], RES[2])

    except (KeyError, NotHangulException): return " "

    return next(filter(lambda v: v != "", RES)) if RES.count("") == 2 else KO


def en_decrypt(CRITERIA: int, RGB: tuple): return chr(RGB[CRITERIA] % 128)


def decrypt_process(IMG_NAME: str, PATH: str):

    IMG = Image.open(os.path.join(PATH, IMG_NAME))

    PIX = IMG.load()

    WIDTH, HEIGHT = IMG.size

    CRITERIA = tuple(PIX[0, i][0] % 3 for i in range(HEIGHT))

    INDEX = tuple((i, j) for j in range(HEIGHT) for i in range(1, WIDTH))

    EN_DEC = reduce(lambda s, i: s + en_decrypt(CRITERIA[i[1]], PIX[i[0], i[1]]), INDEX, "")

    KR_DEC = reduce(lambda s, i: s + kr_decrypt(PIX[i[0], i[1]]), INDEX, "")

    DELIMITER = tuple(sorted(reduce(lambda s, i: s + find_all(i[0], i[1]), ((EN_DEC, "$$"), (KR_DEC, "뺊뺊")), ())))

    EN_KO_PARTITION = tuple(tuple(i[1][2:] if i[0] != 0 else i[1] for i in enumerate(partition_by_index(j, (0,) + DELIMITER))) for j in (EN_DEC, KR_DEC))

    AMASS_STR = reduce(lambda s, i: s + EN_KO_PARTITION[i % 2][i], range(len(EN_KO_PARTITION[0])), "")

    AMASS_PARTITION = tuple(x[:x.rindex("?")] for x in partition_by_index(AMASS_STR, (0,) + tuple(i * (WIDTH - 1) for i in (1, 2))))

    ABS_TEMP_DIR = os.path.join(PATH, "RESULT.txt")

    PRE_RESULT_NAME = AMASS_PARTITION[0] + AMASS_PARTITION[1]

    IS_IN_DIR = PRE_RESULT_NAME in os.listdir(PATH)

    RESULT_NAME = IMG_NAME[:-4] + AMASS_PARTITION[1] if IS_IN_DIR else PRE_RESULT_NAME

    with open(ABS_TEMP_DIR, "w+t") as f: f.write(AMASS_PARTITION[2].replace("`", "\n"))

    os.rename(ABS_TEMP_DIR, os.path.join(PATH, RESULT_NAME))

    return RESULT_NAME, IS_IN_DIR


def input_proc(QUES: str, COND = lambda X: X in ('Y', 'N'), RAISE_ERROR: bool = False):

    if RAISE_ERROR: print("Please enter a valid value.\n")

    INPUT = input(QUES)

    try: return INPUT if COND(INPUT) else input_proc(QUES, COND, True)

    except (FileNotFoundError, OSError): return input_proc(QUES, COND, True)


def singular(I_PATH, D_P, FILE_TUPLE: tuple = None):

    POSSBLE_PATH, I_NAME = os.path.split(FILE_TUPLE[int(I_PATH)] if FILE_TUPLE and I_PATH.isdecimal() else I_PATH)

    PATH = POSSBLE_PATH if POSSBLE_PATH else "./"

    WILL, IS_IN_DIR = decrypt_process(I_NAME, PATH)

    if IS_IN_DIR: print("\nA file that matches both the name and extension\n"
                  "of the decryption target exists in this folder.\n"
                  "Decryption will proceed with the name of the encryption file.\n")

    print(f"{I_NAME} -> {WILL}")

    if D_P == "D": os.remove(rf"{PATH}\\{I_NAME}")


def plural(PATH: str, D_P: str):

    tuple(singular(os.path.join(p, v), D_P) for p, _, _ in os.walk(PATH) if os.access(p, os.X_OK) for v in glob(os.path.join(p, "*.bmp")))


def file_tuple():

    FILE_TUPLE = tuple(glob("*.bmp"))

    print(f"\n{'List Of Bitmap Files In The Current Directory':=^80}",
          reduce(lambda s, i: s + f"  [{i[0]:0>3}] : {i[1]}\n", enumerate(FILE_TUPLE), ""),
          f"{'END':=^80}\n", sep="\n")

    return FILE_TUPLE


if __name__ == '__main__':

    print(f"\n{'[DECRYPTION]':^61}")

    WANT2PLURAL = input_proc("Do you want to decrypt all the files in the folder you want and its subfolders?\n[Y]es OR [N]o : ", lambda x: x in ("Y", "N"))

    DEL_PRESERVE = input_proc("What about the remaining bitmap file after decoding?\n[D]elete OR [P]reserve : ", lambda x: x in ("D", "P"))

    if WANT2PLURAL == "Y":

        PATH = input_proc("Enter the path of the folder you want to encrypt.\n : ", lambda x: os.path.isdir(x))

        plural(PATH, DEL_PRESERVE)

    else:

        FILE_TUPLE = file_tuple()

        FILE_SIG = input_proc("file name(or number) : ", lambda x: x in FILE_TUPLE + tuple((str(i) for i in range(len(FILE_TUPLE)))))

        singular(FILE_SIG, DEL_PRESERVE, FILE_TUPLE)

    input("\nSuccessfully.\n\nIf you want to quit, press any button. ")
