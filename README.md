# pi-robot
Robot cart build on top of Raspberry-Pi and Adafruit DC and stepper motor hat

Author: Tomas Kuchta

Date:   22 March 2015
Project Page: https://www.tomask.org/noticeBoard/raspberryPiCartRobot.html

Dependencies:

Hardware:
* Robot Cart Chassis Kit
      https://www.amazon.com/INSMA-Chassis-Encoder-Battery-Arduino/dp/B01BXPETQG/ref=sr_1_2?ie=UTF8&qid=1475182454&sr=8-2&keywords=robot+car+chassis
* Raspberry Pi - Model A+ (chosen for its size and low power consumption, otherwise it can be any Pi)
      https://www.raspberrypi.org/products/model-a-plus/
* USB Wifi Dongle (can be any dongle which works with Linux or Pi)
      Selected Panda 300Mbps Wireless N USB Adapter because it lists Linux compatibility and supports both infrastructure and ad-hoc modes. I intend to use Infrastructure mode to use PI as hotspot and connect to it rather than accessing it through existing hotspot inside the house. https://www.amazon.com/Panda-300Mbps-Wireless-USB-Adapter/dp/B00EQT0YK2/ref=sr_1_17?s=pc&ie=UTF8&qid=1475183544&sr=1-17&keywords=usb+wifi+dongle
* Adafruit DC and stepper motor hat
      https://www.adafruit.com/products/2348
* Rechargeable USB Power Bank for powering Raspberry Pi (can be almost any type capable powering Pi)
      Selected PNY T4400 (4400 mAh) can run Pi + USB Wifi module for about 8 hours https://www.amazon.com/PNY-T4400-PowerPack-Universal-Rechargeable/dp/B00LCAFV1U/ref=sr_1_13?ie=UTF8&qid=1475183039&sr=8-13&keywords=usb%2Bpower%2Bbank%2Bpny&th=1
* AA Battery case holder for powering the motors
      https://www.amazon.com/uxcell-Switch-Battery-Holder-Leads/dp/B00P26O0K8/ref=sr_1_3?s=pc&ie=UTF8&qid=1475184402&sr=1-3&keywords=aa+battery+case+holder
* Screw and stand-off kit for mounting things together
      https://www.amazon.com/Haobase-Spacers-Stand-off-Accessories-Assortment/dp/B01CCKC37I/ref=sr_1_18?ie=UTF8&qid=1475186966&sr=8-18&keywords=nylon+screw+assortment
      
Software:
* Adafruit Motor Hat Python Library
       https://github.com/adafruit/Adafruit-Motor-HAT-Python-Library.git

Hardware Setup:

1. Mount Raspberry Pi on the robot shasis using small (M3) bolts and nuts.
   In order to drill the mounting holes in the right places, print a template marking the Pi holes, fix it to the cart and dril through the paper marks.
2. Solder in the motor hat connectors and mount the hat on the Pi.
   The best way to mount the cart, Pi and the hat together is using nylon stand offs.
3. Connect power to PI
4. Wire motor hat to motors
5. Wire motor power to the motor hat
6. Mount power/battery packs to the cart using self adhesive velcro strips, I used this one, but there are cheaper options out there https://www.amazon.com/gp/product/B00006RSWT/ref=oh_aui_detailpage_o06_s00?ie=UTF8&psc=1

Software Installation and Configuration

Description:
The robot is controlled by connecting to Wi-Fi access point presented by the robot, logging into the robot by ssh from a laptop or a PC (can use putty from Windows PC) and executing the ./run start up script.

Use arrows to control the speed and direction; Space bar stops the robot immediately.

Acceleration and direction changes are by gradual motor ramp to configurable speed step. The motor acceleration/deceleration ramp speed is also configurable. See "# Constants" code section in motor_control.py for acceleration and turning steps and their ramp rate. Max motor PWM speed value is 255, and acceleration is in in number of PWM speed steps per second.

Robot control key bindings can be chosen (or modified) from preconfigured patters (vi/minecraft or arrows) by useControlKeys variable in "# Control keys" section.
