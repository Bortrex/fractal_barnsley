import argparse
import random
from PIL import Image, ImageColor



class BarnsleyFern(object):
    def __init__(self, img_width, img_height, paint_color=(100, 150, 0),
                 bg_color=(0, 0, 0)): # or white - bg_color=(255, 255, 255)
        self.img_width, self.img_height = img_width, img_height
        self.paint_color = paint_color
        self.x, self.y = 0, 0
        self.age = 0

        self.fern = Image.new('RGB', (img_width, img_height), bg_color)
        self.pix = self.fern.load()
        self.pix[self.scale(0, 0)] = paint_color

    def scale(self, x, y):
        h = (x + 2.182)*(self.img_width - 1)/4.8378
        k = (9.9983 - y)*(self.img_height - 1)/9.9983
        return h, k

    def transform(self, x, y):
        rand = random.uniform(0, 100)
        if rand < 1:
            return 0, 0.16*y
        elif 1 <= rand < 86:
            return 0.85*x + 0.04*y, -0.04*x + 0.85*y + 1.6
        elif 86 <= rand < 93:
            return 0.2*x - 0.26*y, 0.23*x + 0.22*y + 1.6
        else:
            return -0.15*x + 0.28*y, 0.26*x + 0.24*y + 0.44

    def iterate(self, iterations):
        for _ in range(iterations):
            self.x, self.y = self.transform(self.x, self.y)
            self.pix[self.scale(self.x, self.y)] = self.paint_color
        self.age += iterations

def parse_color(value):
    try:
        color = ImageColor.getrgb(value)
    except ValueError:
        raise argparse.ArgumentTypeError("use a color name or #RRGGBB hex color")
    if len(color) != 3:
        raise argparse.ArgumentTypeError("use an RGB color without transparency")
    return color


def main():
    parser = argparse.ArgumentParser(description="Generate a Barnsley fern image.")
    parser.add_argument("--iterations", type=int, default=1_000_000,
                        help="number of iterations (default: 1_000_000)")
    parser.add_argument("--seed", type=int,
                        help="random seed for reproducible output")
    parser.add_argument("--color", type=parse_color, default=(100, 150, 0),
                        help="fern color name or #RRGGBB (default: #649600)")
    parser.add_argument("--background", type=parse_color, default=(0, 0, 0),
                        help="background color name or #RRGGBB (default: black)")
    parser.add_argument("--output", default="barnsley.png",
                        help="output image path (default: barnsley.png)")
    parser.add_argument("--gallery", action="store_true",
                        help="save four presets; uses --seed but ignores other rendering options")
    args = parser.parse_args()
    if not args.gallery and args.iterations < 0:
        parser.error("--iterations must be non-negative")

    if args.seed is not None:
        random.seed(args.seed)
    if args.gallery:
        # Each preset is (output, iterations, fern color, background color).
        renders = [
            ("barnsley_classic.png", 1_000_000, (100, 150, 0), (0, 0, 0)),
            ("barnsley_autumn.png", 1_000_000, ImageColor.getrgb("darkorange"),
             ImageColor.getrgb("maroon")),
            ("barnsley_blue.png", 1_000_000, ImageColor.getrgb("deepskyblue"),
             ImageColor.getrgb("midnightblue")),
            ("barnsley_high_density.png", 3_000_000, (100, 150, 0), (0, 0, 0)),
        ]
    else:
        renders = [(args.output, args.iterations, args.color, args.background)]

    for output, iterations, color, background in renders:
        fern = BarnsleyFern(1_000, 1_000, color, background)
        fern.iterate(iterations)
        try:
            fern.fern.save(output)
        except (OSError, ValueError) as error:
            parser.error("cannot save output: {}".format(error))
        if not args.gallery:
            fern.fern.show()


if __name__ == "__main__":
    main()
