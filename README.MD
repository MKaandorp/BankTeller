
# BankTeller

BankTeller is a free, open source, fully offline, and colorful tool to analyze, categorize, and visualize your finances.

Currently supported banks:
* ING Bank (NL)
* RaboBank (NL)

## Screenshots

![Bar Chart](/screenshots/screenshot_bar.png)
![Pie Chart](/screenshots/screenshot_pie.png)
![Line Chart](/screenshots/screenshot_line.png)


## Getting Started

#### 1. Download and unpack the latest release for your system:
* [Python](distributables/bankteller-python.tar.gz) (Tested on Python 2.7.12 and 3.5.2)
* [Windows](distributables/bankteller-windows.zip) (Tested on Win10 64bit)

The archive should contain 4 files.
* BankTeller.py / BankTeller.exe
* categories.txt (File containing your categories and keywords, as well as the structure of CSV files from different banks. Edit to your liking.)
* plotly-basic.min.js (File containing the JavaScript library to display the graphs, made by [Plotly](https://github.com/plotly)).
* readme.txt

#### 2. Edit the categories.txt file, add categories and keywords
Instructions can be found in the file itself.

#### 3. Download a CSV file containing transactions from the website of your bank
Websites of most banks have an option to download your transactions. For example, the Dutch website of ING has an option "Af- en Bijschrijvingen downloaden".

#### 4. Start BankTeller
Double click the executable, or, if you use the python version, you can also start it from your terminal with `python BankTeller.py`.

#### 5. Choose your CSV file

#### 6. Fill out your current balance, or your balance on the last date in your CSV file

#### 7. Open the generated HTML file
It should be in the same folder as your CSV file, and can be opened with the browser of your choice.

## FAQ

#### Why is my 'other' category so big?
The default keywords probably don't work for you. You can easily add new categories and keywords by editing the categories.txt file. Instructions are in the file.

#### Is it safe?
BankTeller works fully offline. Your data does not leave your machine.

#### My bank is not supported?
Currently, only ING Bank (NL) and RaboBank (NL) are supported.
You can add support for your bank yourself by following the instructions at the bottom of categories.txt, or send the developer an email with an anonymized sample of your CSV file at [bnktllr@outlook.com](mailto:bnktllr@outlook.com).

## Built With

* [Plotly](https://github.com/plotly) - JavaScript library used to display graphs
* [PyInstaller](https://www.pyinstaller.org/) - Used to create Windows executable from Python script

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.
