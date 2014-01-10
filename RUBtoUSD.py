# coding=utf-8
from collections import Counter
import urllib
from datetime import datetime, timedelta

__author__ = 'aafanasiev'
date_format_1c = '%d.%m.%Y'
date_format_rbc = '%Y-%m-%d'

# ==========================================
# Параметры
# ==========================================

input = 'Export_to_1c-4_USD.txt'  # входной файл
output = 'Export_USD.txt'  # выходной файл

# ==========================================

def imported(line):
    return line.decode('windows-1251').encode('utf-8').strip('\r\n')


def exported(line):
    return line.decode('utf-8').encode('windows-1251')


def showDate(date):
    return datetime.strftime(date, date_format_1c)


class ExchangeRate(object):
    def __init__(self):
        self.startDate = datetime.date
        self.endDate = datetime.date
        self.ratesDict = Counter()

    def getRateFor(self, date=datetime.date):
        rate = self.ratesDict[date]
        if rate == 0:
            date -= timedelta(days=1)
            return self.getRateFor(date)
        else:
            return float(rate)

    def fetchRates(self, param, func):
        self.startDate = datetime.strptime(param[0], date_format_1c)
        self.endDate = datetime.strptime(param[1], date_format_1c)

        link = 'http://export.rbc.ru/free/cb.0/free.fcgi?period=DAILY&tickers=USD&d1=%s&m1=%s&y1=%s&d2=%s&m2=%s&y2=%s&separator=,&data_format=BROWSER&header=0' % (
            self.startDate.day, self.startDate.month, self.startDate.year, self.endDate.day, self.endDate.month,
            self.endDate.year)
        f = urllib.urlopen(link)
        print "Получены данные от РБК:"
        print "-----------------------"
        for line in f.read().split('\r\n'):
            tokens = line.split(',')
            if len(tokens) > 5:
                date = datetime.strptime(tokens[1], date_format_rbc)
                self.ratesDict[date] = tokens[5]
                print showDate(date) + " - " + tokens[5]

        func(self)


class Parser1C():
    def __init__(self):
        open(output, 'w')

    def process(self, line, rates=ExchangeRate):
        outputfile = open(output, 'a')
        tokens = imported(line).split("=")
        if tokens[0] == 'Дата':
            date = datetime.strptime(tokens[1], date_format_1c)
            self.currenDate = date
            self.currentRate = rates.getRateFor(date)
        if tokens[0] == 'Сумма':
            usdValue = float(tokens[1])
            value = (self.currentRate * usdValue)
            exportLine = exported("Сумма={:0.2f}\r\n".format(value))
            outputfile.write(exportLine)
            print "Исправлено: {3} на {0:0.2f} по курсу: {1} на дату: {2}".format(value, self.currentRate, showDate(self.currenDate), usdValue)
        else:
            outputfile.write(line)


class ReadFile:
    def __init__(self, p):
        self.parser = p
        self.inputfile = open(input)


    def start(self, rates):
        self.inputfile = open(input)
        print "-----------------------"

        for line in self.inputfile:
            self.parser.process(line, rates)

    def bounds(self):
        boundDates = ['', '']
        for line in self.inputfile:
            tokens = imported(line).split('=')
            if tokens[0] == 'ДатаНачала':
                boundDates[0] = tokens[1]
            if tokens[0] == 'ДатаКонца':
                boundDates[1] = tokens[1]
                break
        return boundDates


parser = Parser1C()
t = ReadFile(parser)

rates = ExchangeRate()
t_bounds = t.bounds()
rates.fetchRates(t_bounds, t.start)
