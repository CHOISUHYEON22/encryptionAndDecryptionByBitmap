from hgtk.exception import NotHangulException
from functools import reduce
from PIL import Image
from glob import glob
import hgtk
import os

J_AND_M = (
    ('ㄱ', 'ㄲ', 'ㄴ', 'ㄷ', 'ㄸ', 'ㄹ', 'ㅁ', 'ㅂ', 'ㅃ','ㅅ',
     'ㅆ', 'ㅇ', 'ㅈ', 'ㅉ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ', ''), #20
    ('ㅏ', 'ㅐ', 'ㅑ', 'ㅒ', 'ㅓ', 'ㅔ', 'ㅕ',
     'ㅖ', 'ㅗ', 'ㅘ', 'ㅙ', 'ㅚ', 'ㅛ', 'ㅜ',
     'ㅝ', 'ㅞ', 'ㅟ', 'ㅠ', 'ㅡ', 'ㅢ', 'ㅣ', ''), #22
    ('ㄱ', 'ㄲ', 'ㄳ', 'ㄴ', 'ㄵ', 'ㄶ', 'ㄷ', 'ㄹ', 'ㄺ',
     'ㄻ', 'ㄼ', 'ㄽ', 'ㄾ', 'ㄿ', 'ㅀ', 'ㅁ', 'ㅂ', 'ㅄ',
     'ㅅ', 'ㅆ', 'ㅇ', 'ㅈ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ', '') #28
)

KR_DICT = tuple(({j : J_AND_M[i][j] for j in range(len(J_AND_M[i]))} for i in range(3)))


def find_all(coll, element, pre_index=0):

    try: index = coll.index(element)

    except ValueError: return ()

    return (pre_index + index,) + find_all(coll[index + len(element):], element, pre_index + index + len(element))


def partition_by_index(coll, index):

    if len(index) == 1: return (coll[index[0]:],)

    return (coll[index[0]:index[1]],) + partition_by_index(coll, index[1:])


def kr_decrypt(rgb: tuple):

    try:

        RES = [KR_DICT[i][rgb[i] % v] for i, v in enumerate((21, 23, 29))]

        KO = hgtk.letter.compose(RES[0], RES[1], RES[2])

    except (KeyError, NotHangulException): return " "

    return next(filter(lambda v: v != "", RES)) if RES.count("") == 2 else KO


def en_decrypt(criteria: int, rgb: tuple): return chr(rgb[criteria] % 128)


def get_img2info(path, img_name):

    img = Image.open(os.path.join(path, img_name))

    pix = img.load()

    width, height = img.size

    return tuple(tuple(pix[w, h] for w in range(width)) for h in range(height)), width, height


def decrypt_process(img_name: str, key_name, path: str):

    key_tuple, _, _ = get_img2info(path, key_name)

    img_tuple, width, height = get_img2info(path, img_name)

    will_decrypt = tuple(tuple(tuple(img_tuple[h][w][c] ^ key_tuple[h][w][c] for c in range(3)) for w in range(width)) for h in range(height))

    criteria = tuple(will_decrypt[i][0][0] % 3 for i in range(height))

    index = tuple((i, j) for j in range(height) for i in range(1, width))

    en_dec = reduce(lambda s, i: s + en_decrypt(criteria[i[1]], will_decrypt[i[1]][i[0]]), index, "")

    kr_dec = reduce(lambda s, i: s + kr_decrypt(will_decrypt[i[1]][i[0]]), index, "")

    delimiter = tuple(sorted(reduce(lambda s, i: s + find_all(i[0], i[1]), ((en_dec, "$$"), (kr_dec, "뺊뺊")), ())))

    en_ko_partition = tuple(tuple(i[1][2:] if i[0] != 0 else i[1] for i in enumerate(partition_by_index(j, (0,) + delimiter))) for j in (en_dec, kr_dec))

    amass_str = reduce(lambda s, i: s + en_ko_partition[i % 2][i], range(len(en_ko_partition[0])), "")

    amass_partition = tuple(x[:x.rindex("?")] for x in partition_by_index(amass_str, (0,) + tuple(i * (width - 1) for i in (1, 2))))

    abs_temp_dir = os.path.join(path, "RESULT.txt")

    pre_result_name = amass_partition[0] + amass_partition[1]

    is_in_dir = pre_result_name in os.listdir(path)

    result_name = img_name[:-4] + amass_partition[1] if is_in_dir else pre_result_name

    with open(abs_temp_dir, "w+t") as f: f.write(amass_partition[2].replace("`", "\n"))

    os.rename(abs_temp_dir, os.path.join(path, result_name))

    return result_name, is_in_dir


def input_proc(ques: str, cond = lambda X: X in ('Y', 'N'), raise_error: bool = False):

    if raise_error: print("Please enter a valid value.\n")

    input_data = input(ques)

    try: return input_data if cond(input_data) else input_proc(ques, cond, True)

    except (FileNotFoundError, OSError): return input_proc(ques, cond, True)


def singular(img, key, del_preserve, file_tuple: tuple = None):

    possible_path, i_name = os.path.split(file_tuple[int(img)] if file_tuple and img.isdecimal() else img)

    _, key_name = os.path.split(file_tuple[int(key)] if file_tuple and key.isdecimal() else key)

    path = possible_path if possible_path else "./"

    will, is_in_dir = decrypt_process(i_name, key_name, path)

    if is_in_dir: print("\nA file that matches both the name and extension\n"
                  "of the decryption target exists in this folder.\n"
                  "Decryption will proceed with the name of the encryption file.\n")

    print(f"{i_name} -> {will}")

    if del_preserve == "D": os.remove(rf"{path}\\{i_name}")


def file_tuple():

    file_tuple = tuple(glob("*.bmp"))

    num_name = reduce(lambda s, i: s + f"  [{i[0]:0>3}] : {i[1]}\n", enumerate(file_tuple), "")

    print(f"\n{'List Of Bitmap Files In The Current Directory':=^80}", num_name, f"{'END':=^80}\n", sep="\n")

    return file_tuple


if __name__ == '__main__':

    print(f"\n{'[DECRYPTION]':^61}")

    del_preserve = input_proc("What about the remaining bitmap file after decoding?\n[D]elete OR [P]reserve : ", lambda x: x in ("D", "P"))

    files = file_tuple()

    file_sig = input_proc("file name(or number) : ", lambda x: x in files + tuple((str(i) for i in range(len(files)))))

    key_sig = input_proc("key name(or number) : ", lambda x: x in files + tuple((str(i) for i in range(len(files)))))

    singular(file_sig, key_sig, del_preserve, files)

    input("\nSuccessfully.\n\nIf you want to quit, press any button. ")
