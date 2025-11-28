### ArkOS 4.4 Kernel Support for Clone Devices

This repository aims to bring **ArkOS 4.4 kernel** support to certain clone devices.  
Currently, I can only maintain the devices I personally own, but contributions are always welcome via PRs.

**💡 If you don't know what clone your device is but you have the DTB file, you can use [ DTB Analysis Tool Web](https://lcdyk0517.github.io/dtbTools.html) to help identify your clone type.**

## Supported Devices
---

### File Paths for Manual Configuration

| **Brand**            | **Device**                               | **Files to Copy**                                      |
|----------------------|------------------------------------------|--------------------------------------------------------|
| **YMC**               | **YMC A10MINI**                        | `logo/480P/`, `kernel/common/`, `consoles/a10mini/`     |
| **AISLPC**            | **GameConsole K36S**                    | `logo/480P/`, `kernel/common/`, `consoles/k36s/`        |
|                      | **GameConsole R36T**                    | `logo/480P/`, `kernel/common/`, `consoles/k36s/`        |
|                      | **GameConsole R36T MAX**                | `logo/720P/`, `kernel/common/`, `consoles/r36tmax/`     |
| **Batlexp**           | **Batlexp G350**                        | `logo/480P/`, `kernel/common/`, `consoles/g350/`         |
| **Kinhank**           | **K36 Origin Panel**                    | `logo/480P/`, `kernel/common/`, `consoles/k36/`         |
| **Clone R36s**        | **Clone Type 1 With Amplifier**         | `logo/480P/`, `kernel/common/`, `consoles/r36pro/` |
|                       | **Clone Type 1 Without Amplifier**      | `logo/480P/`, `kernel/common/`, `consoles/hg36/` |
|                      | **Clone Type 1 Without Amplifier And Invert Right Joystick** | `logo/480P/`, `kernel/common/`, `consoles/k36/` |
|                      | **Clone Type 2 With Amplifier**                         | `logo/480P/`, `kernel/common/`, `consoles/clone type2 amp/` |
|                      | **Clone Type 2 Without Amplifier**                         | `logo/480P/`, `kernel/common/`, `consoles/clone type2/` |
|                      | **Clone Type 3**                         | `logo/480P/`, `kernel/common/`, `consoles/clone type3/` |
|                      | **Clone Type 4**                         | `logo/480P/`, `kernel/common/`, `consoles/clone type4/` |
|                      | **Clone Type 5**                         | `logo/480P/`, `kernel/common/`, `consoles/clone type5/` |
| **GameConsole**      | **GameConsole R46H**                    | `logo/768P/`, `kernel/common/`, `consoles/r46h/`        |
|                      | **GameConsole R40XX**                    | `logo/768P/`, `kernel/common/`, `consoles/r40xx/`        |
|                      | **GameConsole R36sPlus**                | `logo/720P/`, `kernel/common/`, `consoles/r36splus/`    |
|                      | **GameConsole R36s Panel 0**            | `logo/480P/`, `kernel/common/`, `consoles/origin panel0/` |
|                      | **GameConsole R36s Panel 1**            | `logo/480P/`, `kernel/common/`, `consoles/origin panel1/` |
|                      | **GameConsole R36s Panel 2**            | `logo/480P/`, `kernel/common/`, `consoles/origin panel2/` |
|                      | **GameConsole R36s Panel 3**            | `logo/480P/`, `kernel/common/`, `consoles/origin panel3/` |
|                      | **GameConsole R36s Panel 4**            | `logo/480P/`, `kernel/common/`, `consoles/origin panel4/` |
|                      | **GameConsole R36s Panel 4 V22**            | `logo/480P/`, `kernel/common/`, `consoles/v22 panel4/` |
|                      | **GameConsole R36XX**                   | `logo/480P/`, `kernel/common/`, `consoles/origin panel4/` |
|                      | **GameConsole R36H**                    | `logo/480P/`, `kernel/common/`, `consoles/r36h/` |
|                      | **GameConsole O30S**                    | `logo/480P/`, `kernel/common/`, `consoles/r36h/` |
| **SoySauce R36s**    | **Soy Sauce V03**                       | `logo/480P/`, `kernel/common/`, `consoles/sauce v03/`    |
|                      | **Soy Sauce V04**                       | `logo/480P/`, `kernel/common/`, `consoles/sauce v04/`    |
| **XiFan HandHelds**   | **XiFan Mymini**                        | `logo/480P/`, `kernel/common/`, `consoles/mymini/`      |
|                      | **XiFan R36Max**                        | `logo/720P/`, `kernel/common/`, `consoles/r36max/`      |
|                      | **XiFan R36Pro**                        | `logo/480P/`, `kernel/common/`, `consoles/r36pro/`      |
|                      | **XiFan XF35H**                         | `logo/480P/`, `kernel/common/`, `consoles/xf35h/`       |
|                      | **XiFan XF40H**                         | `logo/720P/`, `kernel/common/`, `consoles/xf40h/`       |
|                      | **XiFan XF40V**                         | `logo/720P/`, `kernel/common/`, `consoles/dc40v/`       |
|                      | **XiFan DC35V**                         | `logo/480P/`, `kernel/common/`, `consoles/dc35v/`       |
|                      | **XiFan DC40V**                         | `logo/720P/`, `kernel/common/`, `consoles/dc40v/`       |
|**Other**             | **GameConsole HG36**                    | `logo/480P/`, `kernel/common/`, `consoles/hg36/`        |
|                      | **GameConsole R36Ultra**                | `logo/720P/`, `kernel/common/`, `consoles/r36ultra/`    |
|                      | **GameConsole RX6H**                    | `logo/480P/`, `kernel/common/`, `consoles/rx6h/`        |
|                       | **GameConsole XGB36**                   | `logo/480P/`, `kernel/common/`, `consoles/xgb36/`       |
|                      | **GameConsole T16MAX**                  | `logo/720P/`, `kernel/common/`, `consoles/t16max/`      |

---

## What We Did

To make ArkOS work on clone devices, the following changes and adaptations were made:

1. **Controller driver modification**
   - Kernel Source:[lcdyk0517/arkos.bsp.4.4: Linux kernel source tree](https://github.com/lcdyk0517/arkos.bsp.4.4)
2. **DTS reverse-porting for compatibility**
   - The DTS files were **reverse-ported from the 5.10 kernel to the 4.4 kernel** to ensure proper hardware support.
   - Reference: [AveyondFly/rocknix_dts](https://github.com/AveyondFly/rocknix_dts/tree/main/3326/arkos_4.4_dts)
3. - **Built on the ArkOS distribution maintained by AeolusUX**
     - Reference repo: [AeolusUX/ArkOS-R3XS](https://github.com/AeolusUX/ArkOS-R3XS)
4. - **351Files GitHub repo**
     - Reference repo: [lcdyk0517/351Files](https://github.com/lcdyk0517/351Files)
5. - **ogage GitHub repo**
     - Reference repo: [lcdyk0517/ogage](https://github.com/lcdyk0517/ogage)

## How to Use

1. Download the **ArkOS** release image.
2. Flash the image to the SD card and run `python3 dtb_selector.py` to select the corresponding device, then reboot the device.

## Remapping the Joystick Axes

Visit the [Joymux-Fix](https://github.com/lcdyk0517/joymux-fix) website for instructions on generating new `dtb` files
with custom controller axis mappings.

## Known Limitations

- **eMMC installation is not yet supported** — currently, only booting from the SD card is available.

## Future Work

1. Enable **eMMC installation**.

## Contribution

I can only test and maintain devices I physically own.  
If you have other clone devices and want to help improve compatibility, feel free to submit a **PR**!

# ❤️ **Support the Project**

If you find ArkOS4Clone helpful and want to support future development:\
👉 **https://ko-fi.com/lcdyk**

Every donation helps testing new devices, improving compatibility, and
speeding up development.\
Thank you for your support! 🙏
