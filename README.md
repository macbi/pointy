# pointy
Simple tool for GIS point-data manipulation build with Python and HTML/JS

## How to run 

In app root directory, run in terminal:
`python Pointy.py `

## How to publish (Windows)

Eel documantation on how to publish app:
[Eel Documantation](https://github.com/python-eel/Eel/tree/main?tab=readme-ov-file#starting-the-app)

1. Create virtual environment
   `python -m venv ./venv` (you can specify different path of it)
   activate it
   `cd venv/Scripts`
   `./activate`

2. Install dependecies from `requirements.txt` file
    `pip install -r  requirements.txt`
    and PyInstaller
    `pip install PyInstaller`
3. Build app with PyInstaller
    `python -m eel Pointy.py web`
    If you are happy with results, you can build final app with additional flags
    `python -m eel Pointy.py web --onefile --noconsole --icon web/favicon.ico`


## Roadmap

- [x] 1. Add feature for excel file importing/exporting

- [x] 2. Add getting height method

- [x] 3. Add feature for transforming excel lat/long data into KML layer

- [x] 4. Create map-based data validation tool

- [x] 5. Add logging feature

- [x] 6. Polish UI/UX

- [x] 7. Re-run of failed api call feature

- [x] 8. Add logo and fix favicon

- [x] 9. Do proper QA for various excel inputs

- [x] 10. Release v0.1.0

- [x] 11. Convert coordinates feature

- [x] 12. Support for custom EPSG

- [ ] 13. Support for more input file types (older excels, csv) and output file (csv)

- [ ] 14. Polish UX/UI

