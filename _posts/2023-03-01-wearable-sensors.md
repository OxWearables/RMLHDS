---
layout: post
---

* This will become a table of contents (this text will be scrapped).
{:toc}

# Setting up devices
Over the next few days, you will be collecting and analysing your own physical activity data using two devices: a wearable camera and a wrist-mounted accelerometer.

By going through this practical, we hope that you will learn more about both the promise of, but also ethical considerations with, using technologies such as wearable cameras and accelerometers for health research. You might also find it interesting to see how you can use these devices to measure your own activity and begin deploying custom algorithms on your own data. 

In this practical, we will set up your devices so that you can begin collecting your own daily living data. Then, in the next practical, we will annotate the collected data. 

A lot of what we will be doing today stems from the CAPTURE-24 study. Previously, many lifestyle behaviours were captured using self-reported data in time-use diaries, and this study sought to compare this to using wearable devices. Take a moment to look through this foundational study: [Testing Self-Report Time-Use Diaries against Objective Instruments in Real Time (Gershuny et al., 2020)](https://journals.sagepub.com/doi/abs/10.1177/0081175019884591). 

# 0. Requirements
Before starting this tutorial, we expect you to have the following:
- A recent version of Python installed on your machine.
- The following Python packages:
    - [pandas](https://pandas.pydata.org) (used for working with tabular data)
    - [Pillow](https://pillow.readthedocs.io/en/stable/) (used for image processing)
    - [tqdm](https://tqdm.github.io) (used to display progress bars)
    - [Tkinter](https://docs.python.org/3/library/tkinter.html) (used for the annotation interface). By default, this seems to be installed with Python on Windows. On mac, you may have to install this separately. You can check this is installed by running `python -m tkinter` 
- For Mac users, the browser [Google Chrome](https://www.google.co.uk/chrome/).

Though you are free to set these up in whichever way you seem suitable, we have tested the following set-up instructions on both a Windows and Mac computer.

## Windows
1. Install Python through [miniconda](https://docs.conda.io/en/latest/miniconda.html). Select the relevant installer on the downloads page, likely `Miniconda3 Windows 64-bit`, and follow the installer instructions. 
> Check the installation is successful by going into the Anaconda prompt (which is installed alongside miniconda) and typing `python --version`. It should return something like `Python 3.11.0`

2. In the Anaconda prompt, set up a virtual environment called `sensorsetup` by running:
```shell
conda create --name sensorsetup
```
> You can activate the virtual environment using `conda activate sensorsetup` and deactivate it using `conda deactivate`. 

3. Activate the virtual environemnt and install `pandas`, `Pillow`  and `tqdm`.
```shell
conda activate sensorsetup
conda install pandas Pillow tqdm
```

4. Lastly, check that Tkinter, which should have automatically been installed alongside Python, works on your machine. You can verify this by typing:
```shell
python -m tkinter
```
If Tkinter is correctly set-up, a pop-up window should appear saying, "This is Tcl/Tk version 8.6. This should be a cedilla: ç". The exact version number does not matter too much, provided it is relatively recent. If this is not working, see [TkDocs](https://tkdocs.com/tutorial/install.html).

At this stage, you should be all setup for the tutorial.

## Mac
0. Install [homebrew](https://brew.sh). This can be done by opening the terminal and typing:
```
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

1. Install [Google Chrome](https://www.google.co.uk/chrome/) using [homebrew](https://formulae.brew.sh/cask/google-chrome#default). This can be done by opening the terminal and typing:
```
brew install --cask google-chrome
```

2. Install Python through [miniforge](https://github.com/conda-forge/miniforge). This can be done by opening the terminal and typing:
```
brew install miniforge
```
and then initialising conda for the zshell:
```
conda init zsh
```

> Check the installation is successful by going into the terminal and typing `python --version`. It should return something like `Python 3.11.0`

3. Install Tkinter using [homebrew](https://formulae.brew.sh/formula/python-tk@3.11#default). This can can done by opening the terminal and typing:
```
brew install python-tk@3.11
```
Check that Tkinter works on your machine. You can verify this by typing:
```shell
python -m tkinter
```
If Tkinter is correctly set-up, a pop-up window should appear saying, "This is Tcl/Tk version 8.6. This should be a cedilla: ç". The exact version number does not matter too much, provided it is relatively recent. If this is not working, see [TkDocs](https://tkdocs.com/tutorial/install.html).

4. In the terminal, set up a virtual environment called `sensorsetup` by running:
```shell
conda create --name sensorsetup
```
> You can activate the virtual environment using `conda activate sensorsetup` and deactivate it using `conda deactivate`. 

5. Activate the virtual environemnt and install `pandas`, `Pillow`  and `tqdm`.
```shell
conda activate sensorsetup
conda install pandas Pillow tqdm
```

At this stage, you should be all setup for the tutorial.

## Practical code
We have also prepared code for this practical. This can be found [here on GitHub](https://github.com/OxWearables/RMLHDS).

Either clone or download the repository to your computer and take note of where you save it to. You will later have to navigate to the Python scripts in it.

## Collect devices
Collect your devices from your tutors, who will go through the camera and accelerometer set-up with you. You should have been given 1 wearable camera (Vicon Autographer), 1 wrist-worn accelerometer, and 1 micro-USB cable. 


# 1. Wearable cameras

The wearable camera is designed to capture first-person perspective images to log participant behaviour and activity. This camera does not take video or audio, but captures still images approximately every 30 seconds. 
Wearable camera data is particularly useful for training models based on other types of wearables devices. When participants wear accelerometers, for instance, it is hard to tell from the accelerometer readings which activities participants were actually involved in. Instead, we often make participants additionally wear cameras, which can then be used to inform the ground-truth labels for their activity.



![](./assets/figs/wear_two.jpg) 

 On a typical day of wear, the camera may take up to 3,000 images depicting your everyday life, where you go and the kinds of activities you engage in (e.g. walking to the shop, cycling, socialising). Some images are displayed below for you to get an idea of the content and quality of images that are recorded:

![](./assets/figs/camera_photos.png)



## 1.1. Important points on data collection and processing
- You will be able to delete all data captured at the end this module, and at any point during the module, you will also be able to review and delete any images captured without question.
- The camera does not record any sounds, voices or conversations.
- All images will be treated with the strictest confidence, and the devices are encrypted (‘scrambled’).
- You are free to take off or pause the device at any time, without giving a reason and you should not feel obliged to wear the device in situations where wearing it may make you (or others) feel uncomfortable. If others around you feel uncomfortable with you wearing the camera, you should offer to remove or temporarily switch it off. Places where wearing the camera may not be appropriate include changing rooms, swimming pools, or in and around schools.  

## 1.2 Instructions for setup

We need to first sync up the camera's clock to your computer's, and erase any previous data it may contain. Then you will wear the camera until the next practical session. Please remember all the important points in section 1.1. 

Plug your camera into your computer using the provided cable and make a note of the camera directory (e.g., `D:/` for Windows, and `/Volumes/` for Mac)

From the Anaconda prompt (Windows), or terminal (Mac), navigate to the `scripts` directory that you downloaded above. We will use the script `autographer.py` to set up our cameras. Start the `sensorsetup` virtual environment that you created. 

### Mac
Run the following to wipe the camera clean:
```shell 
python autographer.py --delete True
```
To set your camera's time, run:
```shell 
python autographer.py --setTime True
```

### Windows
Run the following to wipe the camera clean:
```shell 
python autographer.py --delete True --cameraDir D:/
```
To set your camera's time, run:
```shell 
python autographer.py --setTime True --cameraDir D:/
```

### Continue here

Eject and unplug the device. 

The camera operating instructions are as follows:

| Action | Description |
| -------------: |:-------------:|
| Turn on / off | Press the “ACTION” button to the side of the device for a few seconds. The screen will say 'hello'/ 'goodbye'. |
| Camera Status | Press the “MENU” button for an update on the battery status, number of pictures taken, and amount of memory space used. |


Turn the camera on, and check that only the screen below shows when pressing the 'Menus' button:

![](./assets/figs/camera_screen.png)

Once you are ready, start wearing the camera on a lanyard around your neck.

- Wear the camera around your neck so that it feels comfortable. The camera unit should be at chest height with the lens facing horizontally forwards.
- The height can be adjusted with the black cord (lanyard).
- Wear the camera outside of your clothes and be careful that your coat doesn’t obscure the lens!
- There is also a clip, if you prefer to attach the camera to clothes.
- Try not to get the camera wet.

---


# 2. Accelerometer 

The accelerometer is a device which measures the amount of acceleration in the X, Y and Z axes relative to the device, and can be used to quantify the overall and type of physical activity that you are involved in throughout the day. 

The accelerometer is robust and water-proof, and has been designed to be worn when working or sleeping, having a bath or shower, or playing all types of sport (including swimming). Extremes of temperature may damage the battery so it should be taken off while you have a sauna. If you are able to fit any of these activities into the time between these practicals we would be very impressed, especially the sauna.
The device has a long battery life (at least a week), so you do not need to charge it. As it is completely silent, you will not be able to tell that it is running. Here's how to set it up.

## 2.1 Instructions for setup

### Mac
We are going to use the [Open Movement](https://config.openmovement.dev/) website to setup the accelerometer. In order to use this, you need to open it in Google Chrome. If you do not have it already installed, you can install it with homebrew:
```shell
$ brew install --cask google-chrome
```

Now, go to `https://config.openmovement.dev/`.

![](./assets/figs/ax_config.jpg)


0. Plug in your accelerometer into the computer with the provided cable. Wait until the light on the device has stopped flashing red, 
1. Go to the website and click `Connect USB device..` on the wesbite and select the plugged-in accelerometer which will be listed as `AX3 Composite Device...`. Click `Connect`.
2. Write a session ID number, e.g. `42`
3. Change the sampling frequency to 100Hz and the +/- 8 g.
4. Change the start date to today.
5. Leave the rest to the default settings.

Finally, click `Configure` and if it succeeds, you should see the message "Configured - please disconnect device". If the web interface does not work ask your tutor to help you! The local time of the accelerometer will be synced to the machine you set it up on. 

### Windows
For the Windows users, you can download [OMGUI](https://github.com/digitalinteraction/openmovement/wiki/AX3-GUI) and follow the [instructions](./assets/pdfs/accSetup.pdf). Note that you should pay attention to several key parameters which might be different from the setup manual:

0. Plug in your accelerometer into the computer with the provided cable. Wait until the light on the device has stopped flashing red.
1. Open OMGUI and select the plugged-in accelerometer.
2. Select `Clear` to wipe the device.
3. After selecting `Record`, write a session ID number, e.g. `42`.
4. Change the sampling frequency to 100Hz and the range to +/- 8 g.
5. Change the recording time to `Immediately on Disconnet`.
6. Select `Flash during recording`. 
7. Leave the rest to the default settings.



### Continue here


You can now add the wearable accelerometer to your growing personal wearable ecosystem. Please wear the accelerometer on the wrist of the hand that you usually use to write (i.e. your right wrist if you are right-handed). Generally, this will be most convenient for people since it is typical to wear a watch on the other wrist. However, if for some reason you cannot wear the accelerometer on the wrist of the hand that you use to write, then please wear it on the other wrist. The heart-beat symbol should be on the inside of your wrist (i.e. facing towards you).
![arrow_alignment](https://user-images.githubusercontent.com/45289908/142623930-4c2ef153-acb5-442f-a65b-84f8eb051fd8.png)


At this point, you should have an accelerometer mounted on your wrist, and a camera worn on a lanyard around your neck. If you feel sufficiently surveilled, call over one of your tutors to check you have done everything correctly, and then try to pack in as many fun activities for the rest of the practical. In the next practical session, we will annotate these activities. 

It is also worth taking this time to reflect on the various ethical implications raised by using wearable devices in research. Are wearables actually a more unbiased means of recording lifestyle behaviours? Are there, for instance, certain behaviours which people would normally do, but would be less likely to when wearing wearable devices? 

---

# Camera FAQs

**How should I wear the camera?**
Please wear the camera on a lanyard around your neck (or clipped to your clothing), with the camera unit at chest height and the lens facing horizontally forwards.
* Please do not give the camera to anyone else. Please keep it away from children and pets to avoid accidents.

**When should I start wearing the camera?**
* Please start wearing the camera as soon as you have set it up to begin recording.

**How long do I need to wear the camera for?**
We would like you to wear the camera for the time between this practical session and the practical this afternoon. If you feel uneasy about wearing the device at any point, feel free to close the lense cover, hide it away or take it off. 

**How do I charge the camera?**
The camera will be fully charged before the practical, **but we recommend checking its battery percentage at the start of each day**. You do this by turning the camera on and pressing the “MENU” button to the side of the device. The battery percentage should then appear at the top of the display screen. If the battery percentage is <100%, please charge the camera using the yellow micro-USB cable provided.

**Should I wear the camera while sleeping?**
No, you should take the camera off just before preparing for bed in the evening.

**When should I NOT wear the camera?**
The camera is not waterproof, so please remove it during water-based activities (e.g., swimming). For safety reasons, please also remove the camera if operating machinery. It is important for you to understand that you are free to take off or pause the device at any time, without giving a reason. Pausing the camera for brief intervals throughout the day will not affect your input to the study. You should not feel obliged to wear the device in situations where wearing it may make you (or others) feel uncomfortable. If others around you feel uncomfortable with you wearing the camera, you should offer to remove or temporarily switch it off. Places where wearing the camera may not be appropriate include changing rooms, swimming pools, or in and around schools. We appreciate that in some places (e.g. hospitals or airports) it may not be appropriate to wear the camera and you should feel free to remove it at any time. You do not need to wear the camera while participating in contact or water based sports (e.g. rugby or swimming), although we would like you to record your journey there and back.

**Does the camera record sound or conversations?**
The camera captures images automatically every 20-120 seconds but does not record sound or conversations. The camera has a wide-angle lens, so if worn at chest height, it captures everything within the wearer’s view.

![](./assets/figs/wear_two.jpg) 


**Personal privacy**
* The camera has a privacy lens which allows the wearer to pause image recording. You can remove the camera or stop/pause recording at any time if you are feeling uncomfortable.  Some people find it easier to hide the camera under their clothing or in a pocket for short periods of privacy.
* The camera will be encrypted so that only the research team can download and view your images.
* Over the course of the data collection day you may forget you are wearing the camera and take images that are too personal, unwanted or unflattering. At the end of the period for which you are wearing the camera, you will have the opportunity to view and, if necessary, delete any images that you do not wish to be included in the study.
* All images will be treated with the strictest confidence and you will be given the option to review and delete any or all images before analysis.

**Privacy of others**
We recommend that you check in advance that friends, family, and co-workers understand the nature of the study and are happy for you to take part. Their behavior will not be reported as part of the research and images of them will never be shown without your and their written permission. They are welcome to contact the research team if they have any questions or concerns. If you are worried that the camera may have taken images of others that they would feel uncomfortable with, both you and the third party are free to request for those images to be deleted without giving any reason.

* Please seek verbal permission prior to wearing the camera in someone’s home, whether it is a family member, cohabitant, friend, or acquaintance.
* Please seek verbal permission from your manager/supervisor prior to wearing the camera at work. Also, please inform direct co-workers about the camera and remove it if they ask you to.
* Please remove the camera if you find yourself recording strangers in places where privacy might reasonably be expected (e.g., a changing room, swimming pool, school, bank, hospital, or airport) or where photography is disapproved of or considered inappropriate (e.g., certain church communities).

**Other ethical considerations**
The devices are encrypted (‘scrambled’) so that the data can only be accessed by members of the research team. This restricts participants and/or third parties to access the images or make sense of them. Data of illegal activities may not be protected by confidentiality and may be passed to law enforcement. 

**Personal safety**
Remove the camera in any situation where you feel unsafe. For example, if you happen to be out on your own late at night, you may prefer to hide the camera to avoid unwanted attention. If someone tries to take the camera off you, do not attempt to stop them.

If you are engaged in certain manual tasks or using machinery the camera sometimes swings around. For example, if you are using gardening machinery, we advise you remove the device until the activity is finished to avoid discomfort or the possibility of the device getting caught in a dangerous way.


**What are the possible disadvantages of collecting this data?**
We do not anticipate any significant effects on your lifestyle. You will also be able to check and delete any images taken prior to anyone viewing the images. However, it is possible that while wearing the camera you may be asked about the device by members of the public. In this case we suggest that you say the following:

“I am volunteering for a research project. The device is a wearable camera and the images will be used to record my daily activities. I am happy to remove it if you would like me to.”


























