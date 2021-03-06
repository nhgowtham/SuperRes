from matplotlib import pyplot as plt
import numpy as np
import torch

LOW_RES = 32
HIGH_RES = 128
N_SAMPLES = 10000


def show_gray_image(image):
    """
    Plots the image in grey scale, assuming the image is 1 channel of 0-255
    """
    plt.imshow(image, cmap='gray', vmin=0, vmax=255)
    plt.show()


def plot_fake_difference(high_res, netG, device):
    high_res = one_hot_decoding(high_res)
    low_res = cbd_to_grey(high_res)
    low_res = down_sample(low_res)
    low_res = np.expand_dims(low_res, axis=1)
    input_to_g = one_hot_encoding(low_res)
    fake = netG(torch.FloatTensor(input_to_g).to(device)).detach().cpu()
    fake = fractions_to_ohe(fake)
    fake = one_hot_decoding(fake)
    show_three_by_two_gray(high_res, low_res.squeeze(), fake,
                                      'Very vanilla super-res results')


def show_three_by_two_gray(top_images, middle_images, bottom_images, title):

    f, axarr = plt.subplots(3, 3)

    axarr[0,0].imshow(top_images[0, :, :], cmap='gray', vmin=0, vmax=255)
    axarr[0,1].imshow(top_images[1, :, :], cmap='gray', vmin=0, vmax=255)
    axarr[0,2].imshow(top_images[2, :, :], cmap='gray', vmin=0, vmax=255)
    axarr[1, 0].imshow(middle_images[0, :, :], cmap='gray', vmin=0, vmax=255)
    axarr[1, 1].imshow(middle_images[1, :, :], cmap='gray', vmin=0, vmax=255)
    axarr[1, 2].imshow(middle_images[2, :, :], cmap='gray', vmin=0, vmax=255)
    axarr[2, 0].imshow(bottom_images[0, :, :], cmap='gray', vmin=0, vmax=255)
    axarr[2, 1].imshow(bottom_images[1, :, :], cmap='gray', vmin=0, vmax=255)
    axarr[2, 2].imshow(bottom_images[2, :, :], cmap='gray', vmin=0, vmax=255)
    plt.suptitle(title)
    plt.savefig('fake_slices.png')
    plt.close()


def cbd_to_grey(im_with_cbd):
    """
    :return: the image without cbd. cbd -> pore.
    """
    res = np.copy(im_with_cbd)
    res[res == 255] = 0
    return res


def down_sample(orig_image_tensor):
    """
    Average pool twice, then assigns 255 to values closer to 255 and 0 to
    values closer to 0 (Assumes 2 phases!)
    """
    max_im = np.max(orig_image_tensor)
    image_tensor = torch.FloatTensor(np.copy(orig_image_tensor))
    image_tensor = torch.nn.AvgPool2d(2, 2)(image_tensor)
    image_tensor = torch.nn.AvgPool2d(2, 2)(image_tensor)
    # threshold in the middle - arbitrary choice
    image_array = np.array(image_tensor)
    image_array[image_array > max_im/2] = max_im
    image_array[image_array <= max_im/2] = 0
    return torch.FloatTensor(image_array)


def one_hot_encoding(image):
    """
    :param image: a [batch_size, 1, height, width] tensor/numpy array
    :return: a one-hot encoding of image.
    """
    phases = np.unique(image)  # the unique values in image
    im_shape = image.shape

    res = np.zeros([im_shape[0], len(phases), im_shape[2], im_shape[3]])
    # create one channel per phase for one hot encoding
    for cnt, phs in enumerate(phases):
        image_copy = np.zeros(image.shape)  # just an encoding for one
        # channel
        image_copy[image == phs] = 1
        res[:, cnt, :, :] = image_copy.squeeze()
    return res


def one_hot_decoding(image):
    """
    decodes the image back from one hot encoding to grayscale for
    visualization.
    :param image: a [batch_size, phases, height, width] tensor/numpy array
    :return: a [batch_size, height, width] numpy array
    """
    np_image = np.array(image)
    im_shape = np_image.shape
    phases = im_shape[1]
    decodes = [0, 128, 255]
    res = np.zeros([im_shape[0], im_shape[2], im_shape[3]])

    # the assumption is that each pixel has exactly one 1 in its phases
    # and 0 in all other phases:
    for i in range(phases):
        if i == 0:
            continue  # the res is already 0 in all places..
        phase_image = np_image[:, i, :, :]
        res[phase_image == 1] = decodes[i]
    return res


def fractions_to_ohe(image):
    """
    :param image: a [n,3,w,h] image (generated) with fractions in the phases.
    :return: a one-hot-encoding of the image with the maximum rule, i.e. the
    phase which has the highest number will be 1 and all else 0.
    """
    np_image = np.array(image)
    res = np.zeros(np_image.shape)
    # finding the indices of the maximum phases:
    arg_phase_max = np.expand_dims(np.argmax(np_image, axis=1), axis=1)
    # make them 1:
    np.put_along_axis(res, arg_phase_max, 1, axis=1)
    return res


def graph_plot(data, labels, pth, name):
    """
    simple plotter for all the different graphs
    :param data: a list of data arrays
    :param labels: a list of plot labels
    :param pth: where to save plots
    :param name: name of the plot figure
    :return:
    """

    for datum,lbl in zip(data,labels):
        plt.plot(datum, label = lbl)
    plt.legend()
    plt.savefig(pth + '_' + name)
    plt.close()