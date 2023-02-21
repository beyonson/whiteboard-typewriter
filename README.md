# Assistive Whiteboard Typewriter

### Authors
* Garrett Marcinak
* Yasser Morsy
* Justin Harnishfeger
* Reece Bashore

### Background

The purpose of this project is to allow near real time writing on a white board for those who may not be able to physically get up and write based on various reasons. This project will allow for multiple fonts to be selected, and merges old technology with new.

## Modules

### Character Preprocessing / UI

The input to our system is a simple text editor that allows for font modification. The text that is typed in the UI is snipped character by character and ran through a preprocessing system. The system consists of:

* Upscaling
* Binarization
* Skeletonization

Once the character has skeletonization ran on it, the preprocessing is complete.
