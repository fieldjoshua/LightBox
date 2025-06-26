def animate(pixels, config, frame):
    """Simple solid red animation for testing"""
    # Set all pixels to red
    for i in range(len(pixels)):
        pixels[i] = (255, 0, 0)