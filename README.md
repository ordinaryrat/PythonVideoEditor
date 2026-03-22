Very basic python video editor.   
Mainly built for experimentation and why not. Uses numpy, so doesn't take forever but still will take a decent amount of time (several minutes) to render even moderately complex videos at hd resolution for several hundred frames.   
Allows for images, videos, text as well as custom frame rates/resolution.   
You can have video editing effects as well like you can have motion/color change.   
You can put in custom functions for effects which allow for any operations related to position/color/opacity.   

I have very little experience with creating documentation and I am not expecting anyone to see this besides maybe a friend, apologies for brevity.  

Also importantly, most audio features are lacking. You can only set the global audio for the entire video.

requires modules:
- cv2
- numpy
- imageio
- PIL
- moviepy

HOW TO USE:

Recommend use:  
from Video import Video, Layer  

You create a new video with Video()  
  Parameters and default values:  
    name="TempVideo.avi", // Output video file name  
    length=100, // Number of frames  
    resolution=(1280, 720), // The size of the video  
    frame_rate=30, // Frame rate  
    audio_track=-1, // If you include an audio track, put the path to the audio here  
    codec="libx264" // Codec. Honestly don't know what codecs are in detail but you can use libx265 for lower quality but smaller file size, libx264 is default.  

You then must define layers with Layer()  
  Parameters and default values:    
    name="layer", // Name of layer. Doesn't really do much    
    color=(0,0,0,0), // Background color of this layer (must include alpha)
    position=(0, 0), // where the layer is (NOT IMPLEMENTED)  
    alpha=255, // transparency of this layer (NOT IMPLEMENTED)  
    default_font_file="" // use this to load a text font if you are using text  
  
Layers have functions. Media loaded in a layer is exclusive to that layer (although there are work arounds if you copy/paste the storage spots for the layer objects).  
Functions of layer:  
loadImage()  
  Parameters:  
    path, // path to image  
    name=-1 // name is NOT irrelevant. If you use this in a trigger/effect you must use this name. It must be unique (at least to this layer).  

loadVideo()  
    Parameters:  
      path, // path to video  
      name=-1, // same with image. must be unique to all media in this layer.  
      preload=False // just keep this at false. your ram will thank you. (tries to load all frames in so it can quickly use it later, only really possible to use for really really short videos depending on how much ram you have).  

loadText()  
  Parameters:  
      name, // same with image. must be unique to all media in this layer.  
      text, // The actual text  
      font=-1, // text font (if none is provided uses the default text font file s defined in the Video()).  
      size=24, // text size  
      color=(0, 0, 0, 0), // text color  
      alloc=-1, // how much area you are allocating for this text. what the code does is write the text on an image and this is how big you want the image to be. If you are unsure just set it to your resolution.  
      alignment="left" // alignment of text on aforementioned image  
  
  
Now to actually display things you need to use a trigger_effect_pair.  

IMPORTANT: For all functions, the current frame number is stored in frame_num.  
  
These are stored in your layer in layername.trigger_effect_pairs. So just append a new tuple.  

Example:  
NewLayer.trigger_effect_pairs.append(  
    (  
        "Always",  
        "DisplayImage",  
        "Text",  
        (0, 0)  
    )  
);  

# --- TRIGGERS ---  
First bit is the trigger. You can have "FrameNumber", "Always" or "Function".  
FrameNumber enabled it if it > (not >=) to the input frame. This input goes into the next input of the tuple after the trigger:  
    (  
        "FrameNumber",  
        5,  
        "DisplayImage",  
        "Text",  
        (0, 0)  
    )  

For Function just write python code in second part that evaluates:  
    (  
        "Function",  
        "frame_num > 10;",  
        "DisplayImage",  
        "Text",  
        (0, 0)  
    )  

# --- EFFECTS ---  
Next you put the effect.  
As you can see in the above examples "DisplayImage" is one.  
Then you put the referenced name of the media (image/text but not video though)  
Then you put position.  
  
Others are "Transparency" to set transparency of object (second (including effect name) option is transparency value)  
"GraduallyDisplayImage" to make an object gradually display (second option is start frame, third option is end frame)  
"DisplayVideo" to display a video. Parameters are almost the same as with the video (second option is name of media, third is position, fourth is start frame (doesn't work yet, just put 0))  
You can also make a function with "Function". Second parameter is just the code. You can modify the variables "AlphaFactor": 1, "ColorFactorR": 1, "ColorFactorG": 1, "ColorFactorB": 1, "PositionOffsetX": 0, "PositionOffsetY": 0  
Example:  
NewLayer.trigger_effect_pairs.append(  
    (  
        "Always",   
        "Function",  
        "HelloText",  
        "from math import sin; ColorFactorB = 1 - abs(sin(frame_num/50)**(4)); ColorFactorG = 1 - abs(sin(frame_num/50)**(4));"  
    ),  
);  
  
Then just append the layer and start rendering the video:  
  
NewVideo.layers.append(NewLayer);  
NewVideo.renderVideo();  
  
# Example code:  
from Video import Video, Layer  
  
RESOLUTION = (600, 600);  
  
NewVideo = Video(name="TempVideoAudio.mp4", length=665, resolution=RESOLUTION, frame_rate=30, audio_track="media/music.mp3");  
  
NewLayer = Layer(color=(0,0,0,0));  
  
NewLayer.loadImage(name="StarBackground", path="media/starback.png");  
NewLayer.loadImage(name="TerranEmblem", path="media/terran.png");  
  
NewLayer.loadText(name="HelloText", text="THE TERRAN STATE\n\nStretching from Mercury to the Terran Flags\non Trappist 1-e the Humans have progressed far.\nHowever, this progress only serves to hide the\ncentury long decay of the Terran State. Years of\nmismanagement and corruption have led to worsening\nconditions and increasing unrest across their worlds,\nwhile a exploitative clique of elites does\nnothing to prevent it. Yet it’s greatest trial is\nabout to come in the form of the Rodentian Imperium.", font="media/Roboto-Bold.ttf", size=20, color=(255, 255, 255), alloc=(600, 300), alignment="center");  
  
  
NewLayer.trigger_effect_pairs.append(  
    (  
        "Always",   
        "Function",  
        "TerranEmblem",  
        "from math import sin; Alpha_Factor = 0.2 + (abs(sin(frame_num/40))/6);"  
    ),  
);  
NewLayer.trigger_effect_pairs.append(  
    (  
        "Always",   
        "Function",  
        "HelloText",  
        "PositionOffsetY = -int(1.3 * frame_num);"  
    ),  
);  
NewLayer.trigger_effect_pairs.append(  
    (  
        "Always",   
        "Function",  
        "HelloText",  
        "from math import sin; ColorFactorB = 1 - abs(sin(frame_num/50)**(4)); ColorFactorG = 1 - abs(sin(frame_num/50)**(4));"  
    ),  
);  
NewLayer.trigger_effect_pairs.append(  
    (  
        "Always",    
        "DisplayImage",
        "StarBackground",  
        (0, 0)  
    )  
);  
NewLayer.trigger_effect_pairs.append(  
    (  
        "Always",  
        "DisplayImage",
        "TerranEmblem",  
        (0, 0)  
    )  
);  
NewLayer.trigger_effect_pairs.append(  
    (  
        "Always",  
        "DisplayImage",  
        "HelloText",  
        (50, 600)  
    )  
);  
  
NewVideo.layers.append(NewLayer);  

NewVideo.renderVideo();  
