# Instructions to prepare for building Jetson base container images

To build Jetson, you must manually run following steps, unfortunately NVIDIA doesn't make it easy to fully automate the download of SDK Manager / JetPack

1. You need a free NVIDIA devzone account, as NVIDIA gate all free SDK files with a mandatory account sign in. If you don't have it, create one [here](https://developer.nvidia.com/).
2. Get NVIDIA's SDK Manager debian package (sdkmanager_<version>.deb), and place it under docker/jetson/deps folder
