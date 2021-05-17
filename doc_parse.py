import re
from pathlib import Path
from typing import List

import PyPDF2
from PyPDF2.utils import PdfReadError

import pytesseract
from PIL import Image


"""
Формат данных: JPG, PDF
Шаблоны данных: N
Количество номеров на файл: N
"""


# TODO: PDF to Image
def pdf_image_extract(pdf_path: Path, images_path: Path) -> List[Path]:
    result = []
    with pdf_path.open("rb") as file:
        try:
            pdf_file = PyPDF2.PdfFileReader(file)
        except PdfReadError as error:
            print(error)
            return result
        for page_num, page in enumerate(pdf_file.pages, 1):
            image_name = f"{pdf_path.name}_{page_num}"
            img_path = images_path.joinpath(image_name)
            img_path.write_bytes(page["/Resources"]["/XObject"]["/Im0"]._data)
            result.append(img_path)
    return result


# TODO: Image to Text
def get_serial_numbers(image_path: Path) -> List[str]:
    result = []
    image = Image.open(image_path)
    text_rus = pytesseract.image_to_string(image, "rus")
    pattern = re.compile(r"(заводской.*[номер|№])")
    matches = len(re.findall(pattern, text_rus))
    if matches:
        text_eng = pytesseract.image_to_string(image, "eng").split("\n")
        for idx, line in enumerate(text_rus.split("\n")):
            if re.match(pattern, line):
                result.append(text_eng[idx].split()[-1])
                if len(result) == matches:
                    break
    return result


if __name__ == "__main__":
    images_path = Path(__file__).parent.joinpath("images")
    if not images_path.exists():
        images_path.mkdir()

    pdf_path = Path(__file__).parent.joinpath("8416_4.pdf")

    images = pdf_image_extract(pdf_path, images_path)
    numbers = map(get_serial_numbers, images)
    print(1)
