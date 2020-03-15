from PIL import Image
import hgtk
import os


def kr_dict():

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

    return tuple(({j : j_and_m[i][j] for j in range(len(j_and_m[i]))} for i in range(3)))


def kr_decrypt(rgb: tuple):

    global KR_DICT

    res = [KR_DICT[i][rgb[i] % v] for i, v in enumerate((21, 23, 29))]

    return next(filter(lambda v: v != "", res)) if res.count("") == 2 else hgtk.letter.compose(res[0], res[1], res[2])


def en_decrypt(rgb: tuple, criteria: int): return chr(rgb[criteria] % 128)


def decrypt_process(i_name):

    img = Image.open(i_name)

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

    with open("RESULT.txt", "w+t") as f: print(plain[0][:plain[0].rindex("?")].replace("`", "\n"), file=f)

    result_name = name_ext[0][0] + name_ext[1][0]

    if result_name in os.listdir("."): result_name =  i_name[:-4] + name_ext[1][0]

    os.rename('RESULT.txt', result_name)

    return result_name


def question(ques: str, cond: tuple):

    while True:

        scan = input(ques)

        if scan in cond:

            print()

            return scan

        print("Please enter a valid value.\n")


def singular(i_name, DorP, file_tuple: tuple):

    try: i_name = file_tuple[int(i_name)]

    except ValueError: pass

    will = decrypt_process(i_name)

    if will[:will.rindex(".")] == i_name[:i_name.rindex(".")]:

        print("A file that matches both the name and extension\n"
              "of the decryption target exists in this folder.\n"
              "Decryption will proceed with the name of the encryption file.\n")

    print(f"{i_name} -> {will}")

    if DorP == "D": os.remove(rf"{i_name}")


def file_tuple(listdir):

    file_tuple = tuple((v for v in listdir if v[-3:] == "bmp"))

    print(f"\n{'List Of Bitmap Files In The Current Directory':=^80}\n")

    for i, v in enumerate(file_tuple): print(f"  [{i:0>3}] : {v}")

    print(f"\n{'END':=^80}\n")

    return file_tuple


if __name__ == '__main__':

    KR_DICT = kr_dict()
    listdir = os.listdir(".")

    print(f"\n{'[DECRYPTION]':^61}")

    file_tuple = file_tuple(listdir)

    singular(question("file name(or number) : ", file_tuple + tuple((str(i) for i in range(len(file_tuple))))),
             question("What about the remaining bitmap file after decoding?\n[D]elete OR [P]reserve : ", ("D", "P")), file_tuple)

    input("\nSuccessfully.\n\nIf you want to quit, press any button. ")
