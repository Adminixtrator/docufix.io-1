import io
import os
from flask import Flask, render_template, request, url_for
import requests
import pytesseract as pt
from PIL import Image
from PIL import ImageFilter
import fpdf as pd
from docx import Document

document = Document()
# Ensure coast is clear
try:
    os.remove('static/Docufix.txt')
    os.remove('static/Docufix.doc')
    os.remove('static/Docufix.pdf')
except:
    print('')

pt.pytesseract.tesseract_cmd = '/app/.apt/usr/bin/tesseract'
#pt.pytesseract.tesseract_cmd = 'Tesseract-OCR/tesseract.exe'

def _get_image(url):
    return Image.open(io.StringIO(requests.get(url).content))

# import our OCR function
def ocr_core(filename):
    """
    This function will handle the core OCR processing of images.
    """
    '''
    img = _get_image(filename)
    img.filter(ImageFilter.SHARPEN)
    '''
    # We'll use Pillow's Image class to open the image and pytesseract to detect the string in the image
    img = Image.open(filename)
    return pt.image_to_string(img)



# allow files of a specific type
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

app = Flask(__name__, template_folder='./')

# function to check the file extension
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    
# IMAGE SCANNER
@app.route('/', methods=['GET', 'POST'])
def imageScanner():   
    if request.method == 'POST':
        # check if there is a file in the request
        if 'file1' not in request.files:
            return render_template('imageScanner.html',)
        file1 = request.files['file1']
        # if no file is selected
        if file1.filename == '':
            return render_template('imageScanner.html', msg='No file selected')

        if file1 and allowed_file(file1.filename):

            # call the OCR function on it
            extracted_text = ocr_core(file1)
            # Save as text
            os.chdir('static/')
            f = open('Docufix.txt', 'w', encoding='utf-8')
            f.write(extracted_text)
            f.close()
            os.chdir('../')
            # Save as docx
            os.chdir('static/')
            document.add_paragraph(extracted_text)
            document.save('Docufix.doc')
            os.chdir('../')
            # Save as pdf
            os.chdir('static/')
            try:
                text = extracted_text
                f = pd.FPDF(format='letter')
                f.add_page()
                f.set_font("Arial", size=12)
                f.write(5,text)
                f.output("Docufix.pdf")
            except:
                extracted_text='Error occured in file encoding..'
                return render_template('imageScanner.html',
                                   msg='Error occured',
                                   extracted_text=extracted_text)
            os.chdir('../')
                     
            if extracted_text != '':
                extracted_text=extracted_text
            else:
                extracted_text='Could not identify text in image.. \nPlease check image and try again..'
            # extract the text and display it
            return render_template('imageScanner.html',
                                   msg='Successfully processed',
                                   extracted_text=extracted_text)
        else:
            return render_template('imageScanner.html',
                                   msg='Error occured',
                                   extracted_text='Error occured! Please check your file type and try again')
            
    elif request.method == 'GET':
        return render_template('imageScanner.html')


    
if __name__  == '__main__':
    app.run()
