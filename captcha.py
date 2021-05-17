import pytesseract
from PIL import Image, ImageFilter
from collections import defaultdict
from time import sleep


def show_image(img):
    img.show()
    sleep(0.2)


def validation(width, height, x, y, pix):

    direct = [(1, 0), (0, 1), (-1, 0), (0, -1)]
    diff = same = 0

    for dx, dy in direct:
        nx, ny = x + dx, y + dy
        if nx >= 0 and nx < width and ny >= 0 and ny < height:
            if pix[x, y] == pix[nx, ny]:
                same += 1
            else:
                diff += 1
        else:
            diff += 1

    if diff == 4:
        return 0  # invalid
    elif same == 4:
        return 1  # full valid
    else:
        return 3  # partial valid


def refine(char):
    if len(char) > 1:
        return char[0]
    if char == "¥":
        return "Y"
    else:
        return char


def captcha_to_string(img):

    rgb_dict = defaultdict(int)
    ans = ""

    # show_image(img)

    pix = img.load()
    width = img.size[0]
    height = img.size[1]
    for x in range(width):
        for y in range(height):
            res_code = validation(width, height, x, y, pix)
            if res_code == 1:
                for dx, dy in [(1, 0), (0, 1), (-1, 0), (0, -1)]:
                    nx, ny = x + dx, y + dy
                    rgb_dict[pix[nx, ny]] += 10
                rgb_dict[pix[x, y]] += 10
            elif res_code == 3:
                rgb_dict[pix[x, y]] += 1
            else:
                img.putpixel((x, y), (255, 255, 255))

    # show_image(img)

    rank = sorted(rgb_dict.items(), key=lambda k_v: k_v[1])
    color_set = {color[0] for color in rank[-4:]}

    pix = img.load()

    for x in range(width):
        for y in range(height):
            p = (255, 255, 255) if pix[x, y] not in color_set else (0, 0, 0)
            img.putpixel((x, y), p)

    # phase2 = "phase2_" + filename
    # img.save(phase2)
    # show_image(img)

    # cut image vertically for recognition
    left = right = top = 0
    bottom = height - 1
    is_white = True
    is_char = False

    for x in range(width):
        for y in range(height):

            rgb = pix[x, y][:3]

            if y == 0:
                is_white = True
            elif rgb == (0, 0, 0):
                is_white = False

            if not is_white and not is_char:
                is_char = True
                left = x - 3

        if is_char and is_white:
            is_char = False
            right = x + 3
            c_img = img.crop((left, top, right, bottom))
            c_img = c_img.resize((c_img.size[0] * 2, c_img.size[1] * 2))
            c_img = c_img.filter(ImageFilter.GaussianBlur(radius=1))

            # show_image(c_img)

            char = refine(
                pytesseract.image_to_string(
                    c_img,
                    lang="eng",
                    config=(
                        # "-c tessedit"
                        # "tessedit_char_whitelist=abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
                        " --psm 10"
                        # " -l osd"
                    ),
                )
            )
            ans += char

    return ans


# a = captcha_to_string(Image.open("capcha/05-17 03:56:46.png"))
# print(a)

# a = captcha_to_string(Image.open("capcha/05-17 03:56:56.png"))
# print(a)

