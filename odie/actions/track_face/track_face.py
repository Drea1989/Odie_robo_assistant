import logging
import cv2.cv as cv
import cv2
from odie.actions.utils.PCA9685 import Servo
from odie.actions.utils.AlphaBot import AlphaBot
from odie.core.ActionModule import ActionModule
from odie.core.OrderListener import OrderListener


logging.basicConfig()
logger = logging.getLogger("odie")


class Track_face(ActionModule):
    def __init__(self, **kwargs):
        super(Track_face, self).__init__(**kwargs)
        self.calledback = False
        cascade = cv.Load('/usr/share/opencv/haarcascades/haarcascade_frontalface_default.xml')
        frontalface = cv2.CascadeClassifier('/odie/actions/track_face/haarcascade_frontalface_alt2.xml')     # frontal face pattern detection
        profileface = cv2.CascadeClassifier("/odie/actions/track_face/haarcascade_profileface.xml")

        cam_pan = 90
        cam_tilt = 45

        servo = Servo()

        bot = AlphaBot()

        bot.lights(220, 220, 200)

        # Turn the camera to the default position
        servo.pan(cam_pan-90)
        servo.tilt(cam_tilt-90)

        min_size = (15, 15)
        # image_scale = 5
        haar_scale = 1.2
        min_neighbors = 2
        haar_flags = cv.CV_HAAR_DO_CANNY_PRUNING

        cap = cv.CreateCameraCapture(0)
        cap.set(cv.CV_CAP_PROP_FRAME_WIDTH, 300)
        cap.set(cv.CV_CAP_PROP_FRAME_HEIGHT, 300)
        cv.NamedWindow("Tracker", 1)

        if cap:
            frame_copy = None

        self.tracking = True
        while(self.tracking):
            if self.calledback:
                self.calledback = False
                order_listener = OrderListener(callback=self.stop)

            # Capture frame-by-frame
            frame = cv.QueryFrame(cap)
            if not frame:
                cv.WaitKey(0)
                break
            if not frame_copy:
                frame_copy = cv.CreateImage((frame.width, frame.height),
                                            cv.IPL_DEPTH_8U, frame.nChannels)
            if frame.origin == cv.IPL_ORIGIN_TL:
                cv.Flip(frame, frame, -1)

            # Our operations on the frame come here
            small_img = cv.CreateImage((frame.width, frame.height), 8, 1)

            # convert color input image to grayscale
            cv.CvtColor(frame, small_img, cv.CV_BGR2GRAY)

            cv.EqualizeHist(small_img, small_img)

            midFace = None

            if(cascade):
                t = cv.GetTickCount()
                # HaarDetectObjects takes 0.02s
                faces = cv.HaarDetectObjects(small_img, cascade, cv.CreateMemStorage(0),
                                             haar_scale, min_neighbors, haar_flags, min_size)
                t = cv.GetTickCount() - t
                if len(faces) == 0:
                    logger.debug("[FaceTracking] first cascade failed to find face")
                    t = cv.GetTickCount()
                    # HaarDetectObjects takes 0.02s
                    faces = frontalface.detectMultiScale(small_img, 1.3, 4, (cv2.cv.CV_HAAR_DO_CANNY_PRUNING + cv2.cv.CV_HAAR_FIND_BIGGEST_OBJECT + cv2.cv.CV_HAAR_DO_ROUGH_SEARCH), (60, 60))
                    t = cv.GetTickCount() - t
                if faces != ():
                    logger.debug("[FaceTracking] second cascade failed to find face")
                    t = cv.GetTickCount()
                    # HaarDetectObjects takes 0.02s
                    faces = profileface.detectMultiScale(small_img, 1.3, 4, (cv2.cv.CV_HAAR_DO_CANNY_PRUNING + cv2.cv.CV_HAAR_FIND_BIGGEST_OBJECT + cv2.cv.CV_HAAR_DO_ROUGH_SEARCH), (80, 80))
                    t = cv.GetTickCount() - t

                if faces:
                    bot.lights(200 if len(faces) == 0 else 0, 200 if len(faces) > 0 else 0, 30)

                    for ((x, y, w, h), n) in faces:
                        # the input to cv.HaarDetectObjects was resized, so scale the
                        # bounding box of each face and convert it to two CvPoints
                        pt1 = (x, y)
                        pt2 = (x + w, y + h)
                        cv.Rectangle(frame, pt1, pt2, cv.RGB(100, 220, 255), 1, 8, 0)
                        # get the xy corner co-ords, calc the midFace location
                        x1 = pt1[0]
                        x2 = pt2[0]
                        y1 = pt1[1]
                        y2 = pt2[1]

                        midFaceX = x1+((x2-x1)/2)
                        midFaceY = y1+((y2-y1)/2)
                        midFace = (midFaceX, midFaceY)

                        offsetX = midFaceX / float(frame.width/2)
                        offsetY = midFaceY / float(frame.height/2)
                        offsetX -= 1
                        offsetY -= 1

                        cam_pan -= (offsetX * 5)
                        cam_tilt += (offsetY * 5)
                        cam_pan = max(0, min(180, cam_pan))
                        cam_tilt = max(0, min(180, cam_tilt))

                        logger.debug("[FaceTracking] offsetX: {}, offsetY: {}, midFace: {}, cam_pan: {}, cam_tilt: {}".format(offsetX, offsetY, midFace, cam_pan, cam_tilt))

                        servo.pan(int(cam_pan-90))
                        servo.tilt(int(cam_tilt-90))
                        break

            # Display the resulting frame
            cv.ShowImage('Tracker', frame)
            if cv.WaitKey(1) & 0xFF == ord('q'):
                break

        # When everything done, release the capture
        cv.DestroyWindow("Tracker")

    def stop(self, order):
        """
        Receive an order,check if it contains 'stop' and terminate if it does
        :param order: the sentence received
        :type order: str
        """
        logger.debug("[FaceTracking] Order received: %s" % order)
        self.calledback = True
        if order in "stop":
            logger.debug("[FaceTracking] terminating tracking")
            self.tracking = False
