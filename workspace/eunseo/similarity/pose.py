import cv2
from vidgear.gears import CamGear
import pafy
import tensorflow as tf
import posenet
import time

model=101
cam_id=0
cam_width=1280
cam_height=720
scale_factor=.7125
file=None

class pose():
    def __init__(self,vid):
        #self.url='https://www.youtube.com/watch?v=1W9gMxLoW6Q'
        #self.video = pafy.new(self.url)
        self.vid=vid
        #image = self.best.read()

    #def __del__(self):
        #self.stream.release()

    def get_pose(self):
        #ret, jpeg = cv2.imencode('.jpg', image)
        with tf.Session() as sess:
            model_cfg, model_outputs = posenet.load_model(model,sess)
            output_stride = model_cfg['output_stride']

            """
            if args.file is not None:
                cap = cv2.VideoCapture(args.file)
            else:
                cap = cv2.VideoCapture(args.cam_id)
            """

            cap = cv2.VideoCapture(self.vid)
            #cap.set(3, args.cam_width)
            #cap.set(4, args.cam_height)

            start = time.time()
            frame_count = 0


            #ret, frame=cap.read()
            #ret, jpeg = cv2.imencode('.jpg', frame)
        
            while True:
                
                input_image, display_image, output_scale = posenet.utils.read_cap(
                cap, scale_factor=scale_factor, output_stride=output_stride)

                heatmaps_result, offsets_result, displacement_fwd_result, displacement_bwd_result = sess.run(
                    model_outputs,
                    feed_dict={'image:0': input_image}
                )

                pose_scores, keypoint_scores, keypoint_coords = posenet.decode_multi.decode_multiple_poses(
                    heatmaps_result.squeeze(axis=0),
                    offsets_result.squeeze(axis=0),
                    displacement_fwd_result.squeeze(axis=0),
                    displacement_bwd_result.squeeze(axis=0),
                    output_stride=output_stride,
                    max_pose_detections=10,
                    min_pose_score=0.15)

                keypoint_coords *= output_scale
                yield ("%s\n" % pose_scores[0])

                #yield(pose_scores.encode)
                #print(pose_scores[0])
                # TODO this isn't particularly fast, use GL for drawing and display someday...

                
                overlay_image = posenet.utils.draw_skel_and_kp(
                    display_image, pose_scores, keypoint_scores, keypoint_coords,
                    min_pose_score=0.15, min_part_score=0.1)

                #cv2.imshow('posenet', overlay_image)

                frame_count += 1
                #if cv2.waitKey(1) & 0xFF == ord('q'):
                #    break
            



                """
                print('Average FPS: ', frame_count / (time.time() - start))
                ret, jpeg = cv2.imencode('.jpg', overlay_image)
                return jpeg.tobytes()
                """