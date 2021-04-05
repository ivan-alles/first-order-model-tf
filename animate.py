import math
import tensorflow as tf
from tqdm import tqdm

# General inference scheme:
# Step 0: determine batch size based on available memory
# Step 1: get kp_source
# Step 2: get kp_driving in batches
# Step 3: process kp_driving
# Step 4: get predictions in batches
def animate(source_image, driving_video, generator, kp_detector, process_kp_driving, batch_size=4, relative=True, adapt_movement_scale=True):
    l = len(driving_video)
    source_image = tf.convert_to_tensor(source_image, "float32")

    tf.profiler.experimental.start("./log")

    # Step 1: get kp_source
    kp_source, kp_source_jacobian = kp_detector(source_image)

    # Step 2: get kp_driving in batches
    kp_driving = []
    kp_driving_jacobian = []
    for i in tqdm(range(math.floor(l / batch_size))):
        start = i * batch_size
        end = (i + 1) * batch_size
        driving_video_tensor = tf.convert_to_tensor(driving_video[start:end])
        kp_driving_frame_kp, kp_driving_frame_jacobian = kp_detector(driving_video_tensor)
        kp_driving.append(kp_driving_frame_kp)
        kp_driving_jacobian.append(kp_driving_frame_jacobian)
    kp_driving = tf.concat(kp_driving, 0)
    kp_driving_jacobian = tf.concat(kp_driving_jacobian, 0)
    del driving_video

    # Step 3: process kp_driving
    kp_driving, kp_driving_jacobian = process_kp_driving(
        kp_driving, kp_driving_jacobian, kp_driving[0], kp_driving_jacobian[0], kp_source, kp_source_jacobian, relative, relative, adapt_movement_scale
    )

    # Step 4: get predictions in batches
    predictions = []
    for i in tqdm(range(math.floor(l / batch_size))):
        start = i * batch_size
        end = (i + 1) * batch_size
        kp_driving_tensor = kp_driving[start:end]
        kp_driving_jacobian_tensor = kp_driving_jacobian[start:end]
        predictions.append(generator([source_image, kp_driving_tensor, kp_driving_jacobian_tensor, kp_source, kp_source_jacobian]))

    tf.profiler.experimental.stop()
    return tf.concat(predictions, 0).numpy()
