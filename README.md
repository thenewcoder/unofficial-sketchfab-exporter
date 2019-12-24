[![HitCount](http://hits.dwyl.io/thenewcoder/unofficial-sketchfab-exporter.svg)](http://hits.dwyl.io/thenewcoder/unofficial-sketchfab-exporter)

<i> Update: Sketchfab has released an updated official Blender 2.8 add-on now. It seems to still be in Beta but it's many times better than their previous one, with tons of cool updates that were only possible after an extension update to their API. The new official Sketchfab add-on incorporates a lot of features that I was trying to learn how to do myself, but would have really been impossible without the new download API extension. So I highly recommend you check it out: [Official Sketchfab plugin on github](https://github.com/sketchfab/blender-plugin/releases). Feel free to use my "outdated" version to teach yourself or as a starting point to create your own Sketchfab exporter. :)

# The Unofficial Sketchfab Exporter add-on for Blender 2.8

This is a slightly modified and highly expanded version of the official add-on for Blender 2.7x. But most importantly, it now works in Blender 2.8. The add-on has been tested on both Windows 10 and Ubuntu 18.04. <s>Since Sketchfab, as of this writing, can't read  Blender 2.8 .blend files, this add-on overcomes the issue by first converting the .blend file to an .fbx in the background and then uploads that instead.</s> Sketchfab finally supports native Blender 2.8 .blend files, and you no longer need to convert/export to other file types, and I have updated the add-on accordingly!

## Other Changes

1. Updated the Sketchfab API that was used from v1 to v3.
2. Added a choice for adding a category for your model
3. Added the option to publish or just export as a draft
4. Added the choice to make your model inspectable
5. Added the choice to make your model downloadable on Sketchfab
6. Added a choice for choosing a license if you make your model downloadable

## Installation

1. Download the .zip file from this github repository
2. Open Blender 2.8
3. Open Edit -> Preferences -> Add-ons
4. Click "Install" and find the .zip file you downloaded (make sure you install the .zip file itself, **not** individual .py files)
5. Click the checkbox for "Import-Export: Unofficial Sketchfab Exporter" to activiate it
6. Click "Save Preferences" and close the preferences window if you don't have 'Auto-save preferences' turned on

## Usage

After installing the add-on it can be found in the 3D Viewport's sidebar menu by pressing the **'n'** key in **Object Mode**. Either copy your Api Key from your sketchfab page (found in your Sketchfab settings) or click "Claim Your Token" in the add-on which will send your Api Key to your email. Once you have entered the key into the add-on you are now ready. Enter any relevant information about your model and then click "Upload".

## Limitations & Issues

Unfortunately nothing is perfect. There are a few limitations when it comes to uploading, and they are mostly with Sketchfab or with the development of Blender 2.8.

1. **Sketchfabs limitations with animation** <br />
   They don't support any custom rigs or other "fancy" stuff. According to their website they support the following:
    1. Skeleton and Bones
    2. Solid
    3. Morph Targets

    *References:* <br />
      &nbsp;&nbsp;[Animations](https://help.sketchfab.com/hc/en-us/articles/203058018-Animations) <br />
      &nbsp;&nbsp;[Blender - Animation](https://help.sketchfab.com/hc/en-us/articles/206223646)
    
2. **Blender 2.8 to Sketchfab issues** <br /> 
<b><i>Important!</i></b> Before uploading your model to Sketchfab, make sure you don'that have some objects with applied scale/rotation and some objects without. Either you apply for all the objects, or apply for none. Because it will most likely cause issues with your model on Sketchfab. I have only been able to reproduce this issue when using files from Blender 2.8. It seems to work fine when exporting from 2.79.

3. **Materials & Textures** <br />
If your objects are missing their materials/textures after upload here are some references to help out: <br />
   &nbsp;&nbsp;[Materials and Textures](https://help.sketchfab.com/hc/en-us/articles/202600873-Materials-and-Textures) <br />
   &nbsp;&nbsp;[Why does my model upload white?](https://help.sketchfab.com/hc/en-us/articles/360000538863-Why-does-my-model-upload-white-) <br />
   &nbsp;&nbsp;[Blender Materials](https://help.sketchfab.com/hc/en-us/articles/209143886-Blender-Materials)

4. **Other** <br />
I'm very happy that Sketchfab can finally handle native Blender 2.8 files, but there are still a couple of things that can cause issues.
   1. If you set an object to be hidden in the viewport, that object will still upload to Sketchfab. In Blender 2.79, those objects would not         show up, at least not when using the official add-on.
   2. If you set <b>ANY</b> object to be disabled in the viewport or for renders, the upload to Sketchfab will fail completely! It doesn't matter if you use the add-on or upload through the website.
   Hopefully they will fix these issues soon, but until then I have implemented a few workarounds to make sure your uploads to Sketchfab will go as smoothly as possible.

## Disclaimer

I'm not the author to the official Sketchfab exporter add-on. I did this project mostly to teach myself how to create add-ons for Blender and to help out fellow "Blenderers". It's possible that there are still some bugs in the code, since the workaround isn't perfect. But after long hours of testing and filling my Sketchfab page with cubes, cones, cylinders and simple animations, the add-on does work as the original. Hopefully it can still be useful to you.

![Image of Unofficial Sketchfab add-on in Blender 2.8](https://s3.amazonaws.com/cgcookie-rails/uploads%2F1556209674014-sketchfab+addon.png)
