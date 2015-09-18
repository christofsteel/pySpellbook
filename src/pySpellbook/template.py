from jinja2 import Environment, PackageLoader, Template
from pkg_resources import resource_filename, resource_listdir
weasy = True
try:
    from weasyprint import HTML
except:
    weasy = False
import sys
import webbrowser
import re
import os
import tempfile
import shutil
import traceback
import subprocess
#from PySide import QtGui

def find_data_file(filename):
    if getattr(sys, 'frozen', False):
        # The application is frozen
        #QtGui.QMessageBox.critical(None, "Network Error",os.path.join(os.path.dirname(sys.executable), filename))
        return os.path.join(os.path.dirname(sys.executable), filename)
    else:
        # The application is not frozen
        # Change this bit to match where you store your data files:
        return resource_filename(__name__, filename)
def list_data_dir(filename):
    if getattr(sys, 'frozen', False):
        base_dir = find_data_file("templates/html/resources")
        #QtGui.QMessageBox.critical(None, "Network Error",os.listdir(base_dir))
        return os.listdir(base_dir)
    else:
        return resource_listdir(__name__,'templates/html/resources')

class LatexGenerator:

    def texify(self, string):
        round1 = {
            "</ul>(\s|<br />|<br/>|</p>)*": r"\\end{itemize}\n"
                }
        round2 = {
            "<li>": r"\\item ",
            "</li>": r"\n",
            "<ul>": r"\\begin{itemize}\n",
            "\s*(<br />\s*|<br/>\s*|</p>\s*)+": r"\\\\ \n",
            "<em>": r"\\textit{",
            "<a[^>]*>|</a>": r"",
            "<sup>": r"\\textsuperscript{",
            "\"": r"''",
            "</em>|</sup>": r"}",
            "%":r"\\%",
            "&": r" \\& ",
            u'\uFB02': r"fl",
            "_": r"\\_",
            "×": r"x",
            "<span[^>]*>|</span>":r"",
            "<table>.*</table>": r""
            }
        string = re.sub("^\s*<p>|&#13;|<p>|\r|\n|\t", "", string)
        string = re.sub("&amp;", "&", string)
        for k, v in round1.items():
            string = re.sub(k, v, string.strip(), flags=re.M)
        for k, v in round2.items():
            string = re.sub(k, v, string.strip(), flags=re.M)
        string = re.sub("<[^>]*>", "", string)
        return string.strip()


    def print_spells(self):
        print(self.spellbook['spells'])

    def __init__(self, template, models, title="My Spellbook", author="Sir Castalot", logo=None):
        self.env = Environment(loader=PackageLoader('pySpellbook', 'templates'))
        self.env.block_start_string = '<%'
        self.env.block_end_string = '%>'
        self.env.comment_start_string = '<#'
        self.env.comment_end_string = '#>'
        self.env.variable_start_string = '<<'
        self.env.variable_end_string = '>>'
        self.templatename = template
        self.template = self.env.get_template("%s/template.tex" % template)
        self.resourcefile = "%s/resource" % template
        self.spellbook = {}
        self.spellbook['title'] = title
        self.spellbook['logo'] = logo
        self.spellbook['author'] = author
        dict_spells = {}
        for model in models:
            for spell, state in model.checked.items():
                if state == 2:
                    if not model.d20class.name in dict_spells.keys():
                        dict_spells[model.d20class.name] = {}
                    if not model.level.level in dict_spells[model.d20class.name].keys():
                        dict_spells[model.d20class.name][model.level.level] = []
                    spell.levelstr = "%s %s" % (model.d20class.name, model.level.level)
                    spell.text_tex = self.texify(spell.text)
                    dict_spells[model.d20class.name][model.level.level].append(spell)
        self.spellbook['spells'] = dict_spells
        self.rendered = self.template.render(spellbook=self.spellbook)

    def save_tex(self, filename):
        with open(filename, 'w') as f:
           f.write(self.rendered)

    def compile_to_pdf(self, filename, callback):
        temppath = tempfile.TemporaryDirectory(prefix="mkSpellbook-")
        temptex = tempfile.NamedTemporaryFile(dir=temppath.name, delete=False, suffix=".tex", mode="w")
        try:
            with open("pySpellbook/templates/%s/resources" % self.templatename, 'r') as resourcesfile:
                resources = [r.strip() for r in resourcesfile.readlines()]
                for resource in resources:
                    try:
                        shutil.copy(os.path.join("pySpellbook","templates",self.templatename,resource),os.path.join(temppath.name,
                            resource))
                    except Exception:
                        print("Something went wrong copying %s" % resource)
                        traceback.print_exc()
        except Exception:
            print("Could not read resources:templates/%s/resources" % self.templatename )
        temptex.write(self.rendered)
        temptex.close()
        print(temptex.name)
        cwd = os.getcwd()
        os.chdir(temppath.name)
        subprocess.call(["pdflatex", "-output-directory", temppath.name, temptex.name])
        subprocess.call(["pdflatex", "-output-directory", temppath.name, temptex.name])
        subprocess.call(["pdflatex", "-output-directory", temppath.name, temptex.name])
        os.chdir(cwd)

        pdfname = os.path.splitext(temptex.name)[0] + ".pdf"
        shutil.copy(pdfname, filename)



class HTMLGenerator:

    def sanitizeQuotes(string):
        return string.replace('\'\'','"')

    def removeLinks(string):
        string = re.sub("<a[^>]*>", "<emph>", string);
        string = re.sub("</a[^>]*>", "</emph>", string);
        return string

    def __init__(self, model, title="My Spellbook", author="Sir Castalot", parent=None):
        self.parent = parent
        self.template_filename = find_data_file("templates/html/template.html")
        template_file = open(self.template_filename, "r")
        self.template = Template(template_file.read())
        template_file.close()
        #if sys.platform.startswith("win32"):
        #    self.template_filename = os.path.join(os.path.abspath(__file__), 'templates/html/template.html')
        #    template_file = open(self.template_filename, "r")        
        #    self.template = Template(template_file.read())
        #    template_file.close()
        #else:
        #    self.template_filename = resource_filename(__name__, 'templates/html/template.html')
        #    self.env = Environment(loader=PackageLoader('pySpellbook', 'templates'))        
        #    self.template = self.env.get_template("html/template.html")
        self.spellbook = {}
        self.spellbook['title'] = title
        self.spellbook['author'] = author
        self.tp_path = os.path.dirname(self.template_filename)
        if getattr(sys, 'frozen', False) and sys.platform == "darwin":
            self.resourcelist = [] # Weird OSX Errors
        else:
            self.resourcelist = [find_data_file(os.path.join("templates","html","resources",r)) for r in list_data_dir('templates/html/resources')]
        #QtGui.QMessageBox.critical(None, "Network Error","am i still here?")  
        dict_spells = model.getCheckedSpells()
        for d20class, levels in dict_spells.items():
            for level, spells in levels.items():
                for spell in spells:
                    spell.levelstr = "%s %s" % (d20class, level)
                    spell.text = HTMLGenerator.removeLinks(HTMLGenerator.sanitizeQuotes(spell.text))
        self.spellbook['spells'] = dict_spells
        self.rendered = self.template.render(spellbook=self.spellbook, template_path=self.tp_path)
        #QtGui.QMessageBox.critical(None, "Network Error","complete_a")  

    def make_book(self, filename, config):  
        #QtGui.QMessageBox.critical(None, "Network Error","make_book")       
        with tempfile.TemporaryDirectory(prefix="pySpellbook-") as tempdir:
            temphtml = tempfile.NamedTemporaryFile(dir=tempdir, delete=False, suffix=".html", mode="w")
            temphtml.write(self.rendered)
            #QtGui.QMessageBox.critical(None, "Network Error","wrote html")  
            tmpname = temphtml.name
            temphtml.close()
            #QtGui.QMessageBox.critical(None, "Network Error",tmpname)  
            #os.mkdir(os.path.join(tempdir, "resources"))
            #for r in self.resourcelist:
            #    shutil.copy(r, os.path.join(tempdir,"resources"))
            if config['backend'] == 'prince':
                os.system("\"%s\" %s -o %s" % (config['prince_path'], tmpname, filename))
            elif config['backend'] == 'HTML':
                shutil.copy(os.path.join(tempdir, tmpname), filename)
                webbrowser.open_new_tab("file:///%s" % filename)
            elif config['backend'] == 'custom':
                custom_command = config['custom'].replace("$INPUT", temphtml).replace("$OUTPUT", filename)
                shutil.copy(custom_command)
            else:
                if weasy:
                    html = HTML("file://%s" % tmpname)
                    html.write_pdf(target=filename)
                else:
                    import pySpellbook.qtpdf
                    os.chdir(tempdir)
                    printer = pySpellbook.qtpdf.Printer(self.parent)
                    printer.load(tmpname)
                    printer.print(filename)




