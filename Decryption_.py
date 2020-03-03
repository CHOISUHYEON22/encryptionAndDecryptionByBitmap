from typing import Dict, List
from PIL import Image
import hgtk
import os


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

            j_and_m_dict[i][j] = j_and_m[i][j]

    return j_and_m_dict


def kr_decrypt(rgb: tuple):

    global KR_DICT

    modular = (21, 23, 29)

    result = [KR_DICT[i][rgb[i] % modular[i]] for i in range(3)]

    if result.count("") == 2:

        for v in result:

            if v != "": return v

    return hgtk.letter.compose(result[0], result[1], result[2])


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

        if scan in cond: break

        print("Please enter a valid value.\n")

    print()

    return scan


def singular(i_name: str, DorP):

    will = decrypt_process(i_name)

    if will[:-4] == i_name[:-4]:

        print("A file that matches both the name and extension\n"
              "of the decryption target exists in this folder.\n"
              "Decryption will proceed with the name of the encryption file.\n")

    print(f"{i_name} -> {will}")

    if DorP == "D": os.remove(rf"{i_name}")


if __name__ == '__main__':

    KR_DICT = kr_dict()

    print("[DECRYPTION]")

    singular(question("file name : ", tuple(os.listdir("."))),
             question("What about the remaining bitmap file after decoding?\n[D]elete OR [P]reserve : ", ("D", "P")))

    print('\nSuccessfully.')

    input('\nIf you want to quit, press any button. ')
