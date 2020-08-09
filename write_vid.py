import  numpy as np

#saves the video when motino is detected
def record_video(frame,writer, h2,w2):
    # construct the final output frame, storing the original frame
    output = np.zeros((h2, w2, 3), dtype="uint8")
    output[0:h2, 0:w2] = frame

    # write the output frame to file
    writer.write(output)