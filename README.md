# first-order-model-tf
Tensorflow port of first-order model. TF Lite compatible, supports the original's checkpoints and implements in-graph kp processing, but inference only (no training). 
 
Original pytorch version can be found at [AliaksandrSiarohin/first-order-model](https://github.com/AliaksandrSiarohin/first-order-model). Copy the checkpoint tars into the checkpoint folder. If you intend to run the fashion-trained model, be sure to rename the checkpoint file for that model from fashion.pth.tar to fashion-cpk.pth.tar (the original filename for that dataset doesn't fit into the naming scheme for others for some reason, and that messes up the load process). To generate saved_models and lite models run build.py. After that, you can run inference using saved_models with test.py and using tf lite with testlite.py (take a peek inside for the CL arguments). Alternatively, you can run inference directly using run.py. 

## Inference details

 * First, the kps and the jacobian for the source image are detected through the kp_detector model.
 * Then, for each batch of driving video frames, kps and jacobians are detected using the kp_detector model.
 * Processing of the resultant driving video frame kps and jacobians is done using process_kp_driving model (with source image and video kps/jacobians, and boolean parameters *use_relative_motion*, *use_relative_jacobian*, and *adapt_movement_scale* as inputs).
 * Finally, for each batch of driving video frame kps, the generator model is used (with source image, source image kps/jacobian, and the video frame batch's kps/jacobians as inputs) to generate the outputs.
 
For more details, take a look inside animate.py or the generated tensorboard files in ./log.
 
One thing I didn't implement from the original is the find_best_frame option, which used [face-alignment](https://github.com/1adrianb/face-alignment) to find the frame in the driving video that is closest to the source image in terms of face alignment. I didn't want to include outside dependencies and this was only relevant to vox models.

## Bragging section

Boy, was making this thing work with the original's checkpoints with tf lite and with >1 frame batches a journey. Some stuff I had to do to achieve that:

 * Translate the internals of pytorch's bilinear interpolation op into tf code
 * Same with nearest-interpolation
 * Same with F.grid_sample
 * Implement a static in-graph calculation of the area of a 2D convex hull given the number of points (for processing kps in-graph; original uses scipy.spatial, which itself uses qhull, and I wanted everything to be handled in-graph so that the three tf lite models would be able to handle the full inference pipeline from the source image and the driving video all the way to the inferred video).
 * Translate numpy-like indexings into equivalent tf.gather_nd calls.
 * Translate all the weird little constructs of the original into keras layers (all the stuff used in the dense motion network module in particular made me cry a few times).
 * Get rid of all the autoamtic shape broadcasting that'd make life a little easier because apparently they make tf lite crash.
 * Do some seriously complicated math to derive equivalent sequences of tensor reshapes and transpositions.
 * Take all those tf ops that are really pretty and elegant and replace them with esoteric magic so that tf doesn't complain.
 * Export intermediate outputs during inference at two dozen places in both tf and torch code to manually compare differences until they evaporated.
 * Some other stuff I barely remember.

In the end, it actually turned out a little faster than the original. Kudos to me.

### Attribution
[first-order-model](https://github.com/AliaksandrSiarohin/first-order-model) by [AliaksandrSiarohin](https://github.com/AliaksandrSiarohin), used under [CC BY-NC](https://creativecommons.org/licenses/by-nc/4.0/) / Ported to Tensorflow
