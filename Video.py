import cv2
import numpy as np
import imageio
from PIL import Image, ImageFont, ImageDraw
from moviepy.editor import VideoFileClip, AudioFileClip

# https://numpy.org/doc/stable/reference/index.html
# Capabilities

# 1. Stacking layers | ✔️
# 2. Putting images on layers | ✔️
# 3. Drawing stuff on layers | ✔️
# 4. Basic animation (fade in/fade out) | ✔️
# 5. Text | ✔️
# 6. Function based animation | ✔️
# 7. Audio | kinda (not really at all)
# 8. Video | ✔️

triggers = ["FrameNumber", "Always"];
effects = ["Alpha_Factor", "DisplayImage", "GraduallyDisplayImage"];

class Layer:
    def __init__(self, name="layer", color=(0,0,0,0), position=(0, 0), alpha=255, default_font_file=""):
        self.name = name;
        self.color = color;
        self.position = position;
        self.alpha = alpha;
        self.trigger_effect_pairs = [];
        self.images = {};
        self.images_traits = {};
        
        self.default_font_file = default_font_file;
    
    def processLayer(self, time, resolution):
        ''' What the layer looks like at given time '''
        return_image = np.full((resolution[1], resolution[0], 4), self.color, dtype=np.float64);
        # print(f"Original Layer: {return_image}");
        # img = Image.fromarray(return_image, 'RGBA');
        # img.show();
        for trigger_effect in self.trigger_effect_pairs:
            transparency = 1;
            # This may need to be more complicated
            passed = False;
            if trigger_effect[0] == "FrameNumber":
                if time > trigger_effect[1]:
                    passed = True;
                rest = trigger_effect[2:];
            elif trigger_effect[0] == "Always":
                passed = True;
                rest = trigger_effect[1:];
            elif trigger_effect[0] == "Function":
                passed = eval(trigger_effect[1], {"frame_num": time});
                rest = trigger_effect[2:];

            if passed:
                if rest[0] == "Function":
                    values = self.images_traits[rest[1]];
                    values["frame_num"] = time;
                    exec(rest[2], values, values);
                if rest[0] == "Transparency": # Should be done last

                    transparency = rest[1];     
                    
                if rest[0] == "DisplayImage" or rest[0] == "GraduallyDisplayImage" or rest[0] == "DisplayVideo":                     
                    if rest[0] == "GraduallyDisplayImage" and time < rest[4]:
                        # print((time - rest[3]) * 1/(rest[4] - rest[3]));
                        transparency = min(1, (time - rest[3]) * 1/(rest[4] - rest[3]));
                    if rest[0] == "DisplayVideo":
                        if len(self.images[rest[1]]) == 0:
                            valid, image = self.images_traits[rest[1]]["VideoPath"].read();
                            if valid:
                                image = np.asarray(image).astype(dtype=np.float64).copy();
                                image = np.flip(image, 2);
                                if np.size(image, axis=2) == 3:
                                    height, width, _ = image.shape;
                                    alpha_array = np.full((height, width, 1), fill_value=255, dtype=np.float64);
                                    image = np.concatenate((image, alpha_array), axis=2);
                        else:
                            image = self.images[rest[1]][time + rest[3]].copy();
                    else:
                        image = self.images[rest[1]].copy();
                    
                    if self.images_traits[rest[1]]["Alpha_Factor"] != 1:
                        transparency = self.images_traits[rest[1]]["Alpha_Factor"]; 
                        
                    if transparency != 1:
                        image[:, :, 3] *= transparency;
                        
                    if self.images_traits[rest[1]]["ColorFactorR"] != 1:
                        image[:, :, 0] *= self.images_traits[rest[1]]["ColorFactorR"];
                    if self.images_traits[rest[1]]["ColorFactorG"] != 1:
                        image[:, :, 1] *= self.images_traits[rest[1]]["ColorFactorG"];
                    if self.images_traits[rest[1]]["ColorFactorB"] != 1:
                        image[:, :, 2] *= self.images_traits[rest[1]]["ColorFactorB"];
                    image = np.clip(image, 0, 255);
                    
                    image_pos = rest[2];
                    image_pos = (image_pos[0] + self.images_traits[rest[1]]["PositionOffsetX"], image_pos[1] + self.images_traits[rest[1]]["PositionOffsetY"]);
                    
                    if image_pos[1] < 0:
                        image = image[abs(image_pos[1]):, :, :];
                        image_pos = (image_pos[0], 0);
                        
                    if image_pos[0] < 0:
                        image = image[:, abs(image_pos[0]):, :];
                        image_pos = (0, image_pos[1]);
                        
                    image = np.pad(image, pad_width=(
                    (max(image_pos[1], 0), max(resolution[1] - (image_pos[1] + np.size(image, axis=0)), 0)),
                    (image_pos[0], max(resolution[0] - (image_pos[0] + np.size(image, axis=1)), 0)),
                    (0, 0)));
                    
                    if np.size(image, axis=0) > resolution[1]:
                        image = image[:resolution[1], :, :];
                        
                    if np.size(image, axis=1) > resolution[0]:
                        image = image[:, :resolution[0], :];
                        
                    fin = np.full((resolution[1], resolution[0]), 255, dtype=np.float64);
                                        
                    alpha_counts = image[..., 3];
                    
                    return_image = np.dstack(
                    (image[:, :, 0] * (alpha_counts/255) + return_image[:, :, 0] * (1 - (alpha_counts/255)),
                    image[:, :, 1] * (alpha_counts/255) + return_image[:, :, 1] * (1 - (alpha_counts/255)),
                    image[:, :, 2] * (alpha_counts/255) + return_image[:, :, 2] * (1 - (alpha_counts/255)),
                    fin));              
                    
        return_image = return_image.reshape(resolution[0] * resolution[1], 4);  
        # img = Image.fromarray(return_image, 'RGBA');
        return return_image;
    
    def loadImage(self, path, name=-1):
        if name == -1:
            name = str(len(images));
        
        image = imageio.imread(path);
        image = np.asarray(image).astype(dtype=np.float64);
        self.images[name] = image;
        self.images_traits[name] = {"Alpha_Factor": 1, "ColorFactorR": 1, "ColorFactorG": 1, "ColorFactorB": 1, "PositionOffsetX": 0, "PositionOffsetY": 0};
    
    def loadVideo(self, path, name=-1, preload=True):
        if name == -1:
            name = str(len(videos));
        
        video = [];
        
        video_capture = cv2.VideoCapture(path);
        if preload:
            print(f"Pre-loading video {path}");
            valid = True;
            count = 0;
            
            length = int(video_capture.get(cv2.CAP_PROP_FRAME_COUNT));
            while valid:
                valid, image = video_capture.read();
                if valid:
                    image = np.asarray(image).astype(dtype=np.float64);
                    video.append(image);
                    count += 1;
                    if count % 100 == 0:
                        print(f"{(count * 100)/length:.02f}%");
            print(f"Done pre-loading video {path}");
        self.images[name] = video;
        self.images_traits[name] = {"Alpha_Factor": 1, "ColorFactorR": 1, "ColorFactorG": 1, "ColorFactorB": 1, "PositionOffsetX": 0, "PositionOffsetY": 0, "InitialFrame": 0, "VideoPath": video_capture};
    
    def loadText(self, name, text, font=-1, size=24, color=(0, 0, 0, 0), alloc=-1, alignment="left"):
        if font == -1:
            font = self.default_font_file;
        if alloc == -1:
            image = Image.new(mode="RGBA", size=(size * len(text) + 30, (size * (1 + text.count("\n"))) + 30), color=(0, 0, 0, 0));
        else:
            image = Image.new(mode="RGBA", size=alloc, color=(0, 0, 0, 0));
            
        draw = ImageDraw.Draw(image);
        
        font = ImageFont.truetype(font, size);
        draw.text((0, 0), text, font = font, align = alignment, fill=color); 
        self.images[name] = np.array(image).astype(dtype=np.float64);
        self.images_traits[name] = {"Alpha_Factor": 1, "ColorFactorR": 1, "ColorFactorG": 1, "ColorFactorB": 1, "PositionOffsetX": 0, "PositionOffsetY": 0};

class Video:
    def __init__(self, name="TempVideo.avi", length=100, resolution=(1280, 720), frame_rate=30, audio_track=-1, codec="libx264"):
        self.name = name;
        self.length = length;
        self.resolution = resolution;
        self.audio_track = audio_track;
        
        background_layer = Layer(name="Background", color=(255,255,255,255), position=(0, 0));
        
        self.layers = [background_layer];
        self.frame_rate = frame_rate;
        self.codec = codec;
    
    def renderVideo(self):
        video = cv2.VideoWriter(self.name + "VIDEO.avi", cv2.VideoWriter_fourcc(*'DIVX'), self.frame_rate, self.resolution);
        for frame_num in range(self.length):
            remaining_alpha_layer = np.full((self.resolution[0] * self.resolution[1]), 255, dtype=np.float64);
            alpha_counts = np.full((self.resolution[0] * self.resolution[1]), 0, dtype=np.float64);
            color_sum = np.full((self.resolution[0] * self.resolution[1], 3), (0, 0, 0), dtype=np.float64);
            layer_id = len(self.layers) - 1;
            while layer_id >= 0:
                new_frame = self.layers[layer_id].processLayer(frame_num, self.resolution).copy();
                rgb_layer = new_frame[:, :3].copy();
                alpha_layer = new_frame[:, 3].copy();
                
                color_sum += np.dstack((rgb_layer[:, 0] * ((1 - alpha_counts/255) * alpha_layer/255), rgb_layer[:, 1] * ((1 - alpha_counts/255) * alpha_layer/255), rgb_layer[:, 2] * ((1 - alpha_counts/255) * alpha_layer/255)))[0];
                alpha_counts += ((1 - alpha_counts/255) * alpha_layer);
                layer_id -= 1;
            color_sum[:] = color_sum[:].round();
            color_sum = color_sum.astype(dtype=np.uint8).reshape(self.resolution[1], self.resolution[0], 3)[:, :, ::-1];
            
            video.write(color_sum.copy());
            if frame_num % 100 == 0:
                print(f"Finished Frame: {frame_num}");
        video.release();
        cv2.destroyAllWindows();
        
        video_clip = VideoFileClip(self.name + "VIDEO.avi");
        
        if self.audio_track != -1:
            audio_clip = AudioFileClip(self.audio_track).subclip(0, self.length/self.frame_rate);
            video_clip = video_clip.set_audio(audio_clip);
        
        video_clip.write_videofile(self.name, fps=self.frame_rate, threads=1, codec=self.codec);