[![HitCount](http://hits.dwyl.io/thenewcoder/unofficial-sketchfab-exporter.svg)](http://hits.dwyl.io/thenewcoder/unofficial-sketchfab-exporter)

# The Unofficial Sketchfab Exporter add-on for Blender 2.8

This is a slightly modified and highly expanded version of the official add-on for Blender 2.7x. But most importantly, it now works in Blender 2.8. The add-on has been tested on both Windows 10 and Ubuntu 18.04. Since Sketchfab, as of this writing, can't read  Blender 2.8 .blend files, this add-on overcomes the issue by first converting the .blend file to an .fbx in the background and then uploads that instead. 

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
5. Click the checkbox for "Object: Unofficial Sketchfab Exporter" to activiate it
6. Click "Save Preferences" and close the preferences window

## Usage

After installing the add-on it can be found in the 3D Viewport's sidebar menu by pressing the **'n'** key in **Object Mode**. Either copy your Api Key from your sketchfab page (found in your settings) or click "Claim Your Token" in the add-on which will send your Api Key to your email. Once you have entered the key into the add-on you are now ready. Enter any relevant information about your model and then click "Upload".

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
    
2. **Blender 2.8 Beta limitations** <br />
   While Blender 2.8 is in Beta, there will inevitably still be bugs that can cause some issues. And if any of those bugs are        related to FBX exporting, or to anything specfic you are doing in the scene, then maybe the upload will fail or cause weird issues with the uploaded model.

3. **Materials & Textures** <br />
   If your objects are missing their materias/textures after upload here are some references to help out: <br />
   &nbsp;&nbsp;[Materials and Textures](https://help.sketchfab.com/hc/en-us/articles/202600873-Materials-and-Textures) <br />
   &nbsp;&nbsp;[Why does my model upload white?](https://help.sketchfab.com/hc/en-us/articles/360000538863-Why-does-my-model-upload-white-) <br />
   &nbsp;&nbsp;[Blender Materials](https://help.sketchfab.com/hc/en-us/articles/209143886-Blender-Materials)

4. **Other** <br />
   There might be other "issues" with uploading, but for the most part they will probably just be caused by either Sketchfab rules/limitations or bugs in Blender 2.8.

## Disclaimer

I'm not the author to the official Sketchfab exporter add-on. I did this project mostly to teach myself how to create add-ons for Blender and to help out fellow "Blenderers". It's possible that there are still some bugs in the code, since the workaround isn't perfect. But after long hours of testing and filling my Sketchfab page with cubes, cones, cylinders etc and simple animations, the add-on does work as the original. Hopefully it can still be useful to you until such a time Sketchfab updates their official add-on and can accept Blender 2.8 .blend files.

![Image of Unofficial Sketchfab add-on in Blender 2.8](https://s3.amazonaws.com/cgcookie-rails/uploads%2F1556209674014-sketchfab+addon.png)
