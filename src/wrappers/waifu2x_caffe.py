#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Name: Waifu2x Caffe Driver
Author: K4YT3X
Date Created: Feb 24, 2018
Last Modified: May 4, 2020

Description: This class is a high-level wrapper
for waifu2x-caffe.
"""

# built-in imports
import argparse
import os
import shlex
import subprocess
import threading

# third-party imports
from avalon_framework import Avalon


class WrapperMain:
    """This class communicates with waifu2x cui engine

    An object will be created for this class, containing information
    about the binary address and the processing method. When being called
    by the main program, other detailed information will be passed to
    the upscale function.
    """

    def __init__(self, driver_settings):
        self.driver_settings = driver_settings
        self.print_lock = threading.Lock()

    @staticmethod
    def parse_arguments(arguments):
        parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter, add_help=False)
        parser.add_argument('--help', action='help', help='show this help message and exit')
        parser.add_argument('-t', '--tta', type=int, choices=range(2), help='8x slower and slightly high quality')
        parser.add_argument('--gpu', type=int, help='gpu device no')
        parser.add_argument('-b', '--batch_size', type=int, help='input batch size')
        parser.add_argument('--crop_h', type=int, help='input image split size(height)')
        parser.add_argument('--crop_w', type=int, help='input image split size(width)')
        parser.add_argument('-c', '--crop_size', type=int, help='input image split size')
        parser.add_argument('-d', '--output_depth', type=int, help='output image chaneel depth bit')
        parser.add_argument('-q', '--output_quality', type=int, help='output image quality')
        parser.add_argument('-p', '--process', choices=['cpu', 'gpu', 'cudnn'], help='process mode')
        parser.add_argument('--model_dir', type=str, help='path to custom model directory (don\'t append last / )')
        parser.add_argument('-h', '--scale_height', type=int, help='custom scale height')
        parser.add_argument('-w', '--scale_width', type=int, help='custom scale width')
        parser.add_argument('-s', '--scale_ratio', type=float, help='custom scale ratio')
        parser.add_argument('-n', '--noise_level', type=int, choices=range(4), help='noise reduction level')
        parser.add_argument('-m', '--mode', choices=['noise', 'scale', 'noise_scale'], help='image processing mode')
        parser.add_argument('-e', '--output_extension', type=str, help='extention to output image file when output_path is (auto) or input_path is folder')
        parser.add_argument('-l', '--input_extention_list', type=str, help='extention to input image file when input_path is folder')
        # parser.add_argument('-o', '--output', type=pathlib.Path, help='path to output image file (when input_path is folder, output_path must be folder)')
        # parser.add_argument('-i', '--input_file', type=pathlib.Path, help='(required)  path to input image file')
        return parser.parse_args(arguments)

    def upscale(self, input_directory, output_directory, scale_ratio, scale_width, scale_height, image_format, bit_depth):
        """This is the core function for WAIFU2X class

        Arguments:
            input_directory {string} -- source directory path
            output_directory {string} -- output directory path
            width {int} -- output video width
            height {int} -- output video height
        """

        # overwrite config file settings
        self.driver_settings['input_path'] = input_directory
        self.driver_settings['output_path'] = output_directory

        if scale_ratio:
            self.driver_settings['scale_ratio'] = scale_ratio
        elif scale_width and scale_height:
            self.driver_settings['scale_width'] = scale_width
            self.driver_settings['scale_height'] = scale_height

        self.driver_settings['output_extention'] = image_format
        self.driver_settings['output_depth'] = bit_depth

        # list to be executed
        # initialize the list with waifu2x binary path as the first element
        execute = [self.driver_settings.pop('path')]

        for key in self.driver_settings.keys():

            value = self.driver_settings[key]

            # null or None means that leave this option out (keep default)
            if value is None or value is False:
                continue
            else:
                if len(key) == 1:
                    execute.append(f'-{key}')
                else:
                    execute.append(f'--{key}')

                # true means key is an option
                if value is not True:
                    execute.append(str(value))

        # return the Popen object of the new process created
        self.print_lock.acquire()
        Avalon.debug_info(f'[upscaler] Subprocess {os.getpid()} executing: {shlex.join(execute)}')
        self.print_lock.release()
        return subprocess.Popen(execute)
