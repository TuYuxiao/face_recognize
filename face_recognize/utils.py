def trim(img):
    height, width, _ = img.shape
    clip_w = width % 4
    clip_h = height % 2
    if clip_w == 0 and clip_h == 0:
        return img
    return img[:width - clip_h, :height - clip_w, :]
