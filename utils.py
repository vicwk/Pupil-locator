import os
import numpy as np
import cv2
from random import shuffle


def check_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)


def rf(low, high):
    """
    return a random float number between [low, high)
    :param low: lower bound
    :param high: higher bound (excluded)
    :return: a float number between [low, high)
    """
    if low >= high:
        return low
    return np.random.uniform(low, high)


def ri(low, high):
    """
    return a random int number between [low, high)
    :param low: lower bound
    :param high: higher bound (excluded)
    :return: an int number between [low, high)
    """
    if low >= high:
        return low
    return np.random.randint(low, high)


def anotator(img, label):
    """
    draw a yellow + on input image based label
    :param img: input image
    :param label: location of pupil
    :return: anotated pupil location
    """
    w, h = img.shape
    rgb = np.zeros(shape=(w, h, 3), dtype=np.uint8)
    rgb[:, :, 0] = img  # TODO: a better way!
    rgb[:, :, 1] = img
    rgb[:, :, 2] = img

    l1xs = int(label[0] - label[2] / 2)
    l1ys = int(label[1])
    l1xe = int(label[0] + label[2] / 2)
    l1ye = int(label[1])

    l2xs = int(label[0])
    l2ys = int(label[1] - label[3] / 2)
    l2xe = int(label[0])
    l2ye = int(label[1] + label[3] / 2)

    rgb = cv2.line(rgb, (l1xs, l1ys), (l1xe, l1ye), (255, 255, 0), 1)
    rgb = cv2.line(rgb, (l2xs, l2ys), (l2xe, l2ye), (255, 255, 0), 1)

    return rgb


def create_noisy_video(data_path='data/valid_data.csv', length=60, fps=5, with_label=False, augmentor=None):
    """
    create a sample video based random image.
    Of course it is not a valid solution to test the model with already seen images.
    It is just to check the speed of model. based on different FPS
    :param data_path: CSV file for input data
    :param length: length of video in second
    :param fps: number of frame per second
    :param with_label: if true, show true label on the video
    :return: a noisy video (file name) for test purpose.
    """

    # read CSV
    data_list = []
    with open(data_path, "r") as f:
        for line in f:
            #  values: [ img_path, x, y, w, h , a]
            values = line.strip().split(",")
            data_list.append([values[0],  # image path
                              values[1],  # x
                              values[2],  # y
                              values[3],  # w
                              values[4],  # h
                              values[5]])  # a

    # number image to make the video
    images_len = fps * length
    start_idx = np.random.randint(0, len(data_list) - images_len)
    selected_images = data_list[start_idx:start_idx + images_len]

    output_fn = 'video_{}s_{}fps.avi'.format(length, fps)
    # TODO: width/height are hard coded
    video = cv2.VideoWriter(output_fn, cv2.VideoWriter_fourcc(*"XVID"), fps, (192, 192))

    for i in selected_images:
        img = cv2.imread(i[0], cv2.IMREAD_GRAYSCALE)
        x = float(i[1])
        y = float(i[2])
        w = float(i[3])
        h = float(i[4])
        label = [x, y, w, h]
        if augmentor is not None:
            img, label = augmentor.addNoise(img, label)
            img = np.asarray(img, dtype=np.uint8)

        if with_label:
            img = anotator(img, label)
        else:
            img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)

        video.write(img)

    cv2.destroyAllWindows()
    video.release()

    return output_fn
