from pepeline import screentone, TypeDot, cvt_color, CvtType
import numpy as np
from numpy import random

from ..utils import probability, lq_hq2grays


class ScreentoneLogic:
    """Class for applying screentone effects to images.

    Args:
        screentone_dict (dict): A dictionary containing screentone settings.
            It should include the following keys:
                - "lqhq" (bool, optional): Flag indicating if the high-quality image should be replaced by the low-quality.
                    Defaults to None.
                - "dot_size" (list of int, optional): Range of dot sizes for screentone effects. Defaults to [7].
                - "color" (dict, optional): Dictionary containing color-specific settings.
                    Defaults to None.
                - "probably" (float, optional): Probability of applying screentone effects. Defaults to 1.0.
            The "color" dictionary should include the following keys:
                - "type_halftone" (list of str, optional): List of halftone types to choose from.
                    Defaults to ["rgb"].
                - "c" (list of int, optional): Range of angles for the C (cyan) channel halftone.
                    Defaults to [0, 0].
                - "m" (list of int, optional): Range of angles for the M (magenta) channel halftone.
                    Defaults to [0, 0].
                - "y" (list of int, optional): Range of angles for the Y (yellow) channel halftone.
                    Defaults to [0, 0].
                - "k" (list of int, optional): Range of angles for the K (black) channel halftone.
                    Defaults to [0, 0].
                - "b" (list of int, optional): Range of angles for the B (blue) channel halftone.
                    Defaults to [0, 0].
                - "g" (list of int, optional): Range of angles for the G (green) channel halftone.
                    Defaults to [0, 0].
                - "r" (list of int, optional): Range of angles for the R (red) channel halftone.
                    Defaults to [0, 0].
    """
    def __init__(self, screentone_dict):
        self.lqhq = screentone_dict.get("lqhq")
        self.dot_range = screentone_dict.get("dot_size", [7])
        color = screentone_dict.get("color")
        if color:
            self.type = color.get("type_halftone", ["rgb"])
            self.color_c = color.get("c", [0, 0])
            self.color_m = color.get("m", [0, 0])
            self.color_y = color.get("y", [0, 0])
            self.color_k = color.get("k", [0, 0])
            self.color_b = color.get("b", [0, 0])
            self.color_g = color.get("g", [0, 0])
            self.color_r = color.get("r", [0, 0])
        self.probably = screentone_dict.get("probably", 1.0)

    def __cmyk_halftone(self, lq, hq, dot_size):
        c_angle = random.randint(*self.color_c)
        m_angle = random.randint(*self.color_m)
        y_angle = random.randint(*self.color_y)
        k_angle = random.randint(*self.color_k)
        lq = cvt_color(lq, CvtType.RGB2CMYK)
        lq[..., 0] = screentone(lq[..., 0], dot_size, c_angle)
        lq[..., 1] = screentone(lq[..., 1], dot_size, m_angle)
        lq[..., 2] = screentone(lq[..., 2], dot_size, y_angle)
        lq[..., 3] = screentone(lq[..., 3], dot_size, k_angle)
        return cvt_color(lq, CvtType.CMYK2RGB), hq

    def __not_rot_halftone(self, lq, hq, dot_size):
        lq[..., 0] = screentone(lq[..., 0], dot_size)
        lq[..., 1] = screentone(lq[..., 1], dot_size)
        lq[..., 2] = screentone(lq[..., 2], dot_size)
        return lq, hq

    def __gray_halftone(self, lq, hq, dot_size):
        lq, hq = lq_hq2grays(lq, hq)
        lq = screentone(lq, dot_size)
        return lq, hq

    def __rgb_halftone(self, lq, hq, dot_size):
        r_angle = random.randint(*self.color_r)
        g_angle = random.randint(*self.color_g)
        b_angle = random.randint(*self.color_b)
        lq[..., 0] = screentone(lq[..., 0], dot_size, r_angle)
        lq[..., 1] = screentone(lq[..., 1], dot_size, g_angle)
        lq[..., 2] = screentone(lq[..., 2], dot_size, b_angle)
        return lq, hq

    def run(self, lq, hq):
        """Applies the selected screentone effect to the input image.

        Args:
            lq (numpy.ndarray): The low-quality image.
            hq (numpy.ndarray): The corresponding high-quality image.

        Returns:
            tuple: A tuple containing the screentoned low-quality image and the corresponding high-quality image.
        """
        HALFTONE_TYPE_MAP = {
            "cmyk": self.__cmyk_halftone,
            "rgb": self.__rgb_halftone,
            "not_rot": self.__not_rot_halftone,
            "gray": self.__gray_halftone,
        }
        try:
            if probability(self.probably):
                return lq, hq

            dot_size = random.choice(self.dot_range)
            if np.ndim(lq) != 2:
                color_type = random.choice(self.type)
                lq, hq = HALFTONE_TYPE_MAP[color_type](lq, hq, dot_size)
            else:
                lq = screentone(lq, dot_size)

            if self.lqhq:
                hq = lq
            return lq, hq

        except Exception as e:
            print(f"screentone error {e}")
