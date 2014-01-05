# coding=windows-1251
from collections import Counter
import urllib
from datetime import datetime

__author__ = 'aafanasiev'
date_format_1c = '%d.%m.%Y'
date_format_rbc = '%Y-%m-%d'


def striped(line):
    return line.strip('\r\n')


class ExchangeRate(object):
    def __init__(self):
        self.startDate = datetime.date
        self.endDate = datetime.date
        self.ratesDict = Counter()

    def getRateFor(self, param):
        return float(self.ratesDict[param])

    def fetchRates(self, param, func):
        self.startDate = datetime.strptime(param[0], date_format_1c)
        self.endDate = datetime.strptime(param[1], date_format_1c)

        link = 'http://export.rbc.ru/free/cb.0/free.fcgi?period=DAILY&tickers=USD&d1=%s&m1=%s&y1=%s&d2=%s&m2=%s&y2=%s&separator=,&data_format=BROWSER&header=0' % (
            self.startDate.day, self.startDate.month, self.startDate.year, self.endDate.day, self.endDate.month,
            self.endDate.year)
        f = urllib.urlopen(link)
        print "Получены данные от РБК:"
        for line in f.read().split('\r\n'):
            tokens = line.split(',')
            if len(tokens) > 5:
                date = datetime.strptime(tokens[1], date_format_rbc).strftime(date_format_1c)
                self.ratesDict[date] = tokens[5]
                print date + " - " + tokens[5]


        func(self)


class Parser1C():
    def __init__(self):
        open('Export_USD.txt', 'w')

    def process(self, line, rates=ExchangeRate):
        outputfile = open('Export_USD.txt', 'a')
        tokens = striped(line).split("=")
        if tokens[0] == 'Дата':
            self.currentRate = rates.getRateFor(tokens[1])
        if tokens[0] == 'Сумма':
            usdValue = float(tokens[1])
            value = (self.currentRate * usdValue)
            outputfile.write("Сумма={:0.2f}\r\n".format(value))
            print value
        else:
            outputfile.write(line)


class ReadFile:
    def __init__(self, p):
        self.parser = p
        self.inputfile = open('Export_to_1c-4_USD.txt')


    def start(self, rates):
        self.inputfile = open('Export_to_1c-4_USD.txt')
        for line in self.inputfile:
            self.parser.process(line, rates)

    def bounds(self):
        boundDates = ['', '']
        for line in self.inputfile:
            tokens = striped(line).split('=')
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
