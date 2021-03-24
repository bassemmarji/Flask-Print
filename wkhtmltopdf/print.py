import pandas as pd
import numpy as np
import jinja2
from flask import *
import pdfkit, os, uuid

PRG_Path = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
APP_ROOT = os.path.dirname(os.path.abspath(__file__))

def create_html_report():
    """
    Creates the HTML output of the report based on a predefined template
    :return: HTML output as string
    """

    #Sample DataFrame
    df = pd.DataFrame(np.random.randn(7,4)
                     ,columns=['one','two','three','four']
                     ,index=['a','b','c','d','e','f','g'])

    #Formatting rule
    def color_negative_red(val):
        color = 'red' if val<0 else 'black'
        return f'color: {color}'

    styler = df.style.applymap(color_negative_red)

    #Chart plotting
    filename = "".join([APP_ROOT, "\\static\\images\\" , "plot.svg"])
    #Plot
    ax = df.plot.bar()
    fig = ax.get_figure()
    fig.savefig(filename)

    #Template handling
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(searchpath='./templates/'))
    template = env.get_template('template.html')

    filename = "file:///" + filename
    html = template.render(my_table=styler.render(), img_url=filename)

    return html

app = Flask(__name__)


@app.route('/')
def index():
    """
    welcome message
    :return: welcome message
    """
    return 'Hello, try generating a report using wkhtmltopdf tool...'

@app.route("/preview")
def preview():
    """
    To preview the generated report
    :return: output report in html format
    """
    html = create_html_report()
    return html

@app.route("/download")
def downlaod():
    """
    To download the generated report
    """
    filename = str(uuid.uuid4()) + '.pdf'
    filename = os.path.join('./output' , filename)

    config  = pdfkit.configuration(wkhtmltopdf = PRG_Path)
    options = {
        'page-size': 'Letter'
       ,'margin-top': '0.75in'
       ,'margin-right': '0.75in'
       ,'margin-bottom': '0.75in'
       ,'margin-left': '0.75in'
       ,'no-outline': None
       ,'encoding':'UTF-8'
       ,'enable-local-file-access':None
       ,'quiet': ''
     # ,'javascript-delay':2000000
    }


    html = create_html_report()
    pdf = pdfkit.from_string(input=html, output_path=filename,configuration=config, options=options)
    pdfDownload = open(filename,'rb').read()

    response: Response = Response (
                          pdfDownload
                         ,mimetype="application/pdf"
                         ,headers={
                                    "Content-disposition": "attachment; filename=" + filename
                                   ,"Content-type": "application/force-download"
                          }
                        )
    return response

if __name__ == "__main__":
   app.run(debug=True)
