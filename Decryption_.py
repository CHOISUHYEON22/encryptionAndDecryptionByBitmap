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

is_not_printed = True


def kr_decrypt(rgb: tuple):

    res = [KR_DICT[i][rgb[i] % v] for i, v in enumerate((21, 23, 29))]

    return next(filter(lambda v: v != "", res)) if res.count("") == 2 else hgtk.letter.compose(res[0], res[1], res[2])


def en_decrypt(rgb: tuple, criteria: int): return chr(rgb[criteria] % 128)


def decrypt_process(i_name: str, path: str):

    img = Image.open(os.path.join(path, i_name))

    pix = img.load()

    width, height = img.size

    name_ext, plain = [[str()], [str()]], [str()]

    kr_ing = False

    for i in range(height):

        criteria = pix[0, i][0] % 3

        isOpen = i in range(2)

        for j in range(1, width):

            using = name_ext[i] if isOpen else plain

            using[0] += kr_decrypt(pix[j, i]) if kr_ing else en_decrypt(pix[j, i], criteria)

            if len(using[0]) > 1 and using[0][-1] in ("$", "뺊") and using[0][-1] == using[0][-2]:

                using[0] = using[0][:-2]

                kr_ing = not kr_ing

            if len(using[0]) > 1 and isOpen and using[0][-1] == "?":

                using[0] = using[0][:-1]

                break

    abs_temp_dir = os.path.join(path, "RESULT.txt")

    with open(abs_temp_dir, "w+t") as f: print(plain[0][:plain[0].rindex("?")].replace("`", "\n"), file=f)

    result_name = name_ext[0][0] + name_ext[1][0]

    if result_name in os.listdir(path): result_name =  i_name[:-4] + name_ext[1][0]

    os.rename(abs_temp_dir, os.path.join(path, result_name))

    return result_name


def question(ques: str, cond):

    while True:

        scan = input(ques)

        if cond(scan): print(); return scan

        print("Please enter a valid value.\n")


def singular(i_name, DorP, file_tuple: tuple = None):

    if file_tuple and i_name.isdecimal(): i_name = file_tuple[int(i_name)]

    path, i_name = os.path.split(i_name)

    if not path: path = "./"

    will = decrypt_process(i_name, path)

    if will[:will.rindex(".")] == i_name[:i_name.rindex(".")] and is_not_printed:

        print("\nA file that matches both the name and extension\n"
              "of the decryption target exists in this folder.\n"
              "Decryption will proceed with the name of the encryption file.\n")

        globals()['is_not_printed'] = False

    print(f"{i_name} -> {will}")

    if DorP == "D": os.remove(rf"{path}\\{i_name}")


def plural(path: str, DorP: str):

    tuple(singular(os.path.join(p, v), DorP) for p, _, _ in os.walk(path) if os.access(p, os.X_OK) for v in glob(os.path.join(p, "*.bmp")))


def file_tuple():

    file_tuple = tuple(glob("*.bmp"))

    print(f"\n{'List Of Bitmap Files In The Current Directory':=^80}\n")

    for i, v in enumerate(file_tuple): print(f"  [{i:0>3}] : {v}")

    print(f"\n{'END':=^80}\n")

    return file_tuple


if __name__ == '__main__':

    print(f"\n{'[DECRYPTION]':^61}")

    want2plural = question("Do you want to decrypt all the files in the folder you want and its subfolders?\n[Y]es OR [N]o : ", lambda x: x in ("Y", "N"))

    del_preserve = question("What about the remaining bitmap file after decoding?\n[D]elete OR [P]reserve : ", lambda x: x in ("D", "P"))

    if want2plural == "Y":

        path = question("Enter the path of the folder you want to encrypt.\n : ", lambda x: os.path.isdir(x))

        plural(path, del_preserve)

    else:

        file_tuple = file_tuple()

        file_sig = question("file name(or number) : ", lambda x: x in file_tuple + tuple((str(i) for i in range(len(file_tuple)))))

        singular(file_sig, del_preserve, file_tuple)

    input("\nSuccessfully.\n\nIf you want to quit, press any button. ")
