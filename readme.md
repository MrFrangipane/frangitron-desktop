# Frangitron Desktop

Python utility to monitor and configure the Frangitron

## Requirements

### On the Pi

- `sysstat`

### On the desktop computer

- Ansible
- Python 3
- PySide 2 
- pexpect

## Install

Clone this repository wherever it suits you

## Launch

````bash
cd ~/frangitron-desktop/
python3 -m frangitron
````

## Notes & Links

### Tutorials

- https://arlencox.wordpress.com/2010/11/21/building-your-own-synthesizer-part-1-getting-started/
- http://www.martin-finke.de/blog/
- https://forum.cockos.com/showthread.php?t=210390
- https://lemariva.com/blog/2018/07/raspberry-pi-preempt-rt-patching-tutorial-for-kernel-4-14-y
- http://c4dm.eecs.qmul.ac.uk/audioengineering/compressors/documents/Reiss-Tutorialondynamicrangecompression.pdf

### Rt Scheduling

Edit limits `sudo nano /etc/security/limits.conf`

```text
@audio -    rtprio    90
@audio -    memlock   unlimited
pi     -    rtprio    90
pi     -    memlock   unlimited
```
