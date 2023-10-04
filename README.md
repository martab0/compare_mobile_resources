# compare_mobile_resources
Compare translations in mobile application resources for Android and iOS.

## SCENARIO
Android resources are in XML file, iOS resources are in XLIFF file. 
The Android and iOS files differ by list of strings, by sorting, and string keys.
English strings can be identical between Android and iOS files.
We need to check if translations are also identical for the strings that are identical in English.  
**The code is written with ChatGPT 4.0 in 8 prompts.**

## DEFINITIONS
Please update definitions at the top of `compare_mobile_resources.py` to your use case.

## FILES AND FOLDERS
Translated file names are created by appending _ and language code to source file name.
Put Android translated files in the same folder as Android source file.
Put iOS translated files in the same folder as iOS source file.

## HOW TO RUN
```
python3 compare_mobile_resources.py
```
No parameters.