import sys
import os

from PyQt5 import QtWidgets, QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QBitmap
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsPixmapItem

from PyQt5 import *

import numpy as np
import matplotlib.pyplot as plt
import dashboard

plt.rcdefaults()

characters = ['.', ',', '<', '>', '/', '?', ';', ':', '\'', '\"',
              '[', '{', ']', '}', '\\', '|', '=', '+', '-', '_', '(', ')',
              '*', '&', '^', '%', '$', '#', '@', '!', '«', '»', '', '°', '\ufeff']

eng_di = ["TH", "EN", "NG", "HE", "AT", "AL", "IN", "ED", "IT",
          "ER", "ND", "AS", "AN", "TO", "IS", "RE", "OR", "HA",
          "ES", "EA", "ET", "ON", "TI", "SE", "ST", "AR", "OU",
          "NT", "TE", "OF"]

eng_tri = ["THE", "ERE", "HES", "AND", "TIO", "VER", "ING", "TER",
           "HIS", "ENT", "EST", "OFT", "ION", "ERS", "ITH", "HER",
           "ATI", "FTH", "FOR", "HAT", "STH", "THA", "ATE", "OTH",
           "NTH", "ALL", "RES", "INT", "ETH", "ONT", "NOT"]

ger_di = ["ER", "ST", "SE", "EN", "NE", "IT", "CH", "BE", "DI", "DE",
          "ES", "IC", "EI", "UN", "SC", "TE", "RE", "LE", "IN", "AN",
          "DA", "ND", "HE", "NS", "IE", "AU", "IS", "GE", "NG", "RA"]

ger_tri = ["DER", "INE", "BER", "EIN", "TER", "ENS", "SCH", "GEN",
           "NGE", "ICH", "END", "RDE", "NDE", "ERS", "VER", "DIE",
           "STE", "EIT", "CHE", "CHT", "HEN", "DEN", "UNG", "ERD",
           "TEN", "DAS", "REI", "UND", "ERE", "IND"]

ukr_di = ["НА", "СТ", "РО", "КО", "АН", "ОВ", "НИ", "ЕР", "ТА", "РА",
          "НО", "НІ", "АЛ", "ОР", "ЕН", "ПО", "ВА", "ЛИ", "ВІ", "ЬК",
          "ГО", "РЕ", "ТИ", "ПР", "ІВ", "ТО", "СЬ", "ОМ", "ОС", "ВИ",
          "ЦІ", "ОЛ", "НН"]

ukr_tri = ["СЬК", "ОГО", "ННЯ", "ЬКО", "ЕРЕ", "ПРО", "ВІД", "СТА",
           "УВА", "ПЕР", "ЕНН", "ЬКИ", "ЛЬН", "ІСТ", "АЛИ", "ПРИ",
           "НИХ", "ВАН", "ОВИ", "АНН", "ОСТ", "ВАЛ", "ТАН", "ІЛЬ",
           "БУЛ", "АЛЬ", "НСЬ"]

rus_di = ["СТ", "АН", "ВО", "ЕН", "ОС", "ЕС", "ОВ", "ПО", "АЛ", "НО",
          "ГО", "ЛИ", "НИ", "ЕР", "ОЛ", "НА", "ОД", "ОМ", "РА", "РЕ",
          "ЛЕ", "КО", "ОР", "СК", "ТО", "ПР", "ВА", "РО", "ТА", "ЕТ"]

rus_tri = ["ЕНИ", "ЛЬН", "СТО", "ОСТ", "ОВА", "ПОЛ", "ОГО", "НИЯ", "НОВ",
           "СТВ", "НИЕ", "ЛЕН", "СКО", "ПРИ", "СТИ", "СТА", "ЕНН", "ПЕР",
           "АНИ", "ГОД", "ЕГО", "ПРО", "ОРО", "ТСЯ", "ЕСТ", "ТЕЛ", "АСТ",
           "ТОР", "СКИ", "РОВ"]


class ProjectUi(QtWidgets.QMainWindow, dashboard.Ui_MainWindow):
    # set class fields
    img_dir = 'img'
    find_name = ""
    plot_scenes = []
    file_cont = []
    lang_found = ''
    which_plot = ''
    colors = ['blue', 'red', 'green']

    lang_list = ["ENG", "GER", "UKR", "RUS"]

    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # set Event listeners
        self.actionOpen.triggered.connect(self.file_open)
        self.showLangBT.clicked.connect(self.find_lang)
        self.generatePlotsBT.clicked.connect(self.draw_all_plots)
        self.enlargeLettersBT.clicked.connect(self.enlargeL)
        self.enlargeDigramsBT.clicked.connect(self.enlargeD)
        self.enlargeTrigramsBT.clicked.connect(self.enlargeT)

        # create directory for images if not exists
        if not os.path.exists(self.img_dir):
            os.makedirs(self.img_dir)

        # set all scenes for plots
        self.plot_scenes = [self.label_letters,
                            self.label_digram,
                            self.label_trigram]

        self.show()

    def find_lang(self):
        best_score = -1
        best_lang = ''

        for lang in self.lang_list:
            score = self.find_di_tri(lang)[0]
            if score > best_score:
                best_score = score
                best_lang = lang

        self.lang_found = best_lang
        self.textLang.setText(best_lang)

    def find_di_tri(self, lang):
        di_counter = 0
        tri_counter = 0
        letter_counter = 0

        letter_dct = {}
        di_dct = {}
        tri_dct = {}

        if lang == "ENG":
            di_list, tri_list = eng_di, eng_tri
            for i in eng_di:
                di_dct[i] = 0
            for j in eng_tri:
                tri_dct[j] = 0

        elif lang == "GER":
            di_list, tri_list = ger_di, ger_tri
            for i in ger_di:
                di_dct[i] = 0
            for j in ger_tri:
                tri_dct[j] = 0

        elif lang == "UKR":
            di_list, tri_list = ukr_di, ukr_tri
            for i in ukr_di:
                di_dct[i] = 0
            for j in ukr_tri:
                tri_dct[j] = 0

        else:
            di_list, tri_list = rus_di, rus_tri
            for i in rus_di:
                di_dct[i] = 0
            for j in rus_tri:
                tri_dct[j] = 0

        for line in self.file_cont:
            line = self.replace_multiple(line, characters, '')
            for word in line.split():
                word = word.upper()
                for i in word:
                    letter_counter += 1
                    if i in letter_dct:
                        letter_dct[i] += 1
                    else:
                        letter_dct[i] = 1
                for dig in di_list:
                    if dig in word:
                        di_counter += 1
                        #print("di", dig, word)
                        if dig in di_dct:
                            di_dct[dig] += 1
                for trig in tri_list:
                    if trig in word:
                        tri_counter += 1
                        #print("tri", trig, word)
                        if trig in tri_dct:
                            tri_dct[trig] += 1

        #print(di_counter + tri_counter,di_dct, tri_dct)
        return di_counter + tri_counter, letter_dct, di_dct, tri_dct

    @staticmethod
    def replace_multiple(main_string, replaces, new_string):
        for elem in replaces:
            if elem in main_string:
                main_string = main_string.replace(elem, new_string)
        return main_string

    def enlarge(self):
        #print(self.which_plot)
        e = self.find_di_tri(self.lang_found)
        letter_dct = e[1]
        di_dct = e[2]
        tri_dct = e[3]
        if (self.which_plot == 'L'):
            self.plot(letter_dct, 'Wykres liter', 'litera', self.lang_found + '_letters', 0)
        elif (self.which_plot == 'D'):
            self.plot(di_dct, 'Wykres digramów', 'digram', self.lang_found + '_digram', 1)
        elif (self.which_plot == 'T'):
            self.plot(tri_dct, 'Wykres trigramów', 'trigram', self.lang_found + '_trigram', 2)
                
    def enlargeL(self):
        self.which_plot = 'L'
        self.enlarge()

    def enlargeD(self):
        self.which_plot = 'D'
        self.enlarge()

    def enlargeT(self):
        self.which_plot = 'T'
        self.enlarge()

    def file_open(self):
        """
        This function reads file, save its lines to class field and show it in text widget
        :return: none
        """
        filename, _ = QtWidgets.QFileDialog.getOpenFileName(self, 'Open File')

        with open(filename, 'r', encoding="utf8") as file:
            self.file_cont = file.readlines()
            self.textToAnalize.setText(''.join(self.file_cont))

    def draw_all_plots(self):
        """
        This function creates all plots and set them into widgets
        :return:
        """

        plot_names = []
        e = self.find_di_tri(self.lang_found)
        letter_dct = e[1]
        di_dct = e[2]
        tri_dct = e[3]

        plot_name = self.lang_found + '_letters'
        self.wykres(letter_dct, 'Wyres liter', 'litera', plot_name, 0)
        plot_names.append(plot_name)
        plot_name = self.lang_found + '_digram'
        self.wykres(di_dct, 'Wykres digramów', 'digram', plot_name, 1)
        plot_names.append(plot_name)
        plot_name = self.lang_found + '_trigram'
        self.wykres(tri_dct, 'Wykres trigramów', 'trigram', plot_name, 2)
        plot_names.append(plot_name)

        for cnt, plt_scn in enumerate(self.plot_scenes):
            pic = QtGui.QPixmap(self.img_dir + '/' + plot_names[cnt] + ".png")
            plt_scn.setPixmap(pic.scaled(427, 320, Qt.KeepAspectRatio))

    def plot(self, dct_name, title, xlabel, plot_name, num):
        objects = []
        performance = []
        for i in dct_name:
            objects.append(i)
            performance.append(dct_name[i])
        y_pos = np.arange(len(objects))

        plt.clf()
        plt.bar(y_pos, performance, align='center', alpha=1, color=self.colors[num])
        plt.xticks(y_pos, objects, rotation=90)
        plt.ylabel('Liczba wystąpień')
        plt.xlabel(xlabel)
        plt.title(title)
        plt.show()
        plt.savefig('img/' + plot_name + '.png', dip=100)

    def wykres(self, dct_name, title, xlabel, plot_name, num):
        objects = []
        performance = []
        for i in dct_name:
            objects.append(i)
            performance.append(dct_name[i])
        y_pos = np.arange(len(objects))

        plt.clf()
        plt.bar(y_pos, performance, align='center', alpha=1, color=self.colors[num])
        plt.xticks(y_pos, objects, rotation=90)
        plt.ylabel('Liczba wystąpień')
        plt.xlabel(xlabel)
        plt.title(title)
        plt.savefig('img/' + plot_name + '.png', dip=100)


def main():
    
    app = QtWidgets.QApplication(sys.argv)
    window = ProjectUi()
    window.show()
    app.exec_()


if __name__ == '__main__':
    main()
