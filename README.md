# GhidraDeepSeekDecomprove

The GhidraDeepSeekDecomprove.py is a Ghidra script designed to enhance the readability of decompiled code by leveraging the DeepSeek Chat API. It intelligently renames variables based on their usage and optionally adds explanatory comments to the code. Integrated seamlessly into Ghidra, the script allows users to select specific functions, improve their decompiled output, and either save the results to a file or display them in a popup window with options to copy the code. It handles errors gracefully, such as failed decompilation or API issues, and provides feedback through Ghidra's logging system. The script is customizable, supporting different DeepSeek models and output configurations, making it a valuable tool for reverse engineers and security researchers aiming to streamline their workflow and improve code understanding.

# Video
[![enhance the readability of decompiled code](https://img.youtube.com/vi/QrSUxFgh1Vg/maxresdefault.jpg)](https://youtu.be/QrSUxFgh1Vg)

# Usage
- Add your DeekSeek API key `deepSeekApiKey = "your_deepseek_api"`
- Go to `Window > Script Manager`
- Choose `Create New Script`

![Screenshot 2025-01-26 at 4 22 39 AM](https://github.com/user-attachments/assets/15b4b46f-c35b-422f-8a0c-7361e32de257)

- Then `Jython`, Enter the script name and finally, Paste and save the code.
- Mark the `In Tool` check box. So, You can have quick access to it through the tools bar.

![Screenshot 2025-01-26 at 4 26 34 AM](https://github.com/user-attachments/assets/0184b6f7-9c7e-4156-8b27-94e9c1a0225d)

![Screenshot 2025-01-26 at 4 28 29 AM](https://github.com/user-attachments/assets/c94d1005-5d7b-465a-98a9-56d31ed08b6e)
