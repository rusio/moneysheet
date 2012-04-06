#!/usr/bin/python

from datetime import *
import sys

#########################################################################

class Schedule:
    '''
    A schedule for a periodic event. Examples:
    - monthly payment of salary
    - weekly drinking in the strip club
    - daily smoking of cigarettes
    '''

    def __init__(self, firstDate=date.min, lastDate=date.max):
        self._firstDate = firstDate
        self._lastDate = lastDate

    def dailyPortionOf(self, value):
        '''
        Normalizes the given value to a daily basis,
        according to the period of this schedule.
        '''
        if not value > 0:
            raise ValueError('value must be positive')
        return float(value) / self.periodLength()

    def periodLength(self): # abstract
        raise NotImplementedError('subclass must implement periodLength()')

    def datesForPeriod(self, startDate, endDate):
        if startDate > endDate:
            raise ValueError('startDate must not be after endDate')

        # consider limits of active period
        if startDate < self._firstDate:
            startDate = self._firstDate
        if endDate > self._lastDate:
            endDate = self._lastDate

        result = []
        oneDay = timedelta(1)
        date = startDate
        while date <= endDate:
            if self.matchesDate(date):
                result.append(date)
            date = date + oneDay
        return result

    def matchesDate(self, dateFromPeriod): # abstract
        raise NotImplementedError('subclass must implement matchesDate()')

#########################################################################

class EveryDay(Schedule):
    '''
    A trivial schedule for something that happens every day.
    '''

    def __init__(self, firstDate=date.min, lastDate=date.max):
        Schedule.__init__(self, firstDate, lastDate)


    def periodLength(self):
        return 1

    def matchesDate(self, dateFromPeriod):
        return True

class EveryMonth(Schedule):
    '''
    A schedule for something that happens periodically every month.
    '''

    def __init__(self, firingDay = 1, firstDate=date.min, lastDate=date.max):
        Schedule.__init__(self, firstDate, lastDate)
        if firingDay not in range(1, 29):
            raise ValueError('firingDay must be in the range [1..28]')
        self.firingDay = firingDay

    def periodLength(self):
        return 30

    def matchesDate(self, dateFromPeriod):
        return (dateFromPeriod.day == self.firingDay)

#########################################################################

class EveryWeek(Schedule):
    
    def __init__(self, weekday = 1, firstDate=date.min, lastDate=date.max):
        Schedule.__init__(self, firstDate, lastDate)
        if weekday not in range(1, 8):
            raise ValueError('weekday must be in the range [1..7]')
        self.weekday = weekday

    def periodLength(self):
        return 7

    def matchesDate(self, dateFromPeriod):
        return (dateFromPeriod.isoweekday() == self.weekday)

#########################################################################

class OnceInTwoWeeks(Schedule):
    
    def __init__(self, weekday = 1, firstDate=date.min, lastDate=date.max):
        Schedule.__init__(self, firstDate, lastDate)
        if weekday not in range(1, 8):
            raise ValueError('weekday must be in the range [1..7]')
        self.weekday = weekday
        self.matchCount = 0

    def periodLength(self):
        return 14

    def matchesDate(self, dateFromPeriod):
        if dateFromPeriod.isoweekday() == self.weekday:
            self.matchCount = self.matchCount + 1
            if self.matchCount % 2 == 1:
                return True
        return False

#########################################################################

class Change:
    
    def __init__(self, description, amount, schedule):
        self.description = description
        self.amount = amount
        self.schedule = schedule
        
    def transfersForPeriod(self, startDate, endDate):
        return [Transfer(date, self.description, self.amount) 
                for date in self.schedule.datesForPeriod(startDate, endDate)]

    def dailyAverage(self):
        return self.schedule.dailyPortionOf(abs(self.amount))

    def __eq__(self, other):
        equalDescriptions = self.description == other.description
        equalAmounts = self.amount == other.amount
        return equalDescriptions and equalAmounts

#########################################################################

class Gain(Change):
    '''
    Incoming money that comes periodically, based on a schedule.
    '''
    def __init__(self, destination, amount, schedule):
        Change.__init__(self, destination, +amount, schedule)

#########################################################################

class Dump(Change):
    '''
    Outgoing money that goes periodically, based on a schedule.
    '''
    
    def __init__(self, destination, amount, schedule):
        Change.__init__(self, destination, -amount, schedule)

#########################################################################

class Transfer:
    '''
    A concrete money transfer on a given date. Note the difference from 
    Gain and Dump - a Gain or Dump is just the description of the incoming
    or outgoing money. A Transfer is the actual movement of the money
    on a concrete date, according to the schedule of the Gain or Dump.
    '''
    
    def __init__(self, date, reason, amount):
        self.date = date
        self.reason = reason
        self.amount = amount

    def __eq__(self, other):
        equalDates = self.date == other.date
        equalReasons = self.reason == other.reason
        equalAmounts = self.amount == other.amount
        return equalDates and equalReasons and equalAmounts

    def __repr__(self):
        return 'Transfer(' + str(self.date) + ',' + self.reason + ',' + str(self.amount) + ')'

#########################################################################

class Group:
    '''
    A group of multiple Changes under a common category.
    '''

    def __init__(self, name, changes):
        self.name = name
        self.changes = changes

    def dailyAverage(self):
        return sum([change.dailyAverage() for change in self.changes])

    def __eq__(self, other):
        eq1 = self.name == other.name
        eq2 = self.changes == other.changes
        return eq1 and eq2

#########################################################################

class Portfolio:
    '''
    The Portfolio contains the data for all Gains and Dumps grouped in groups.
    '''

    def __init__(self, groups):
        self.groups = groups

    def monthlyGains(self):
        totalDailyGains = sum([change.dailyAverage() 
                               for group in self.groups
                               for change in group.changes if change.amount > 0])
        return totalDailyGains * EveryMonth().periodLength()

    def monthlyDumps(self):
        totalDailyDumps = sum([change.dailyAverage() 
                               for group in self.groups
                               for change in group.changes if change.amount < 0])
        return totalDailyDumps * EveryMonth().periodLength()


    def monthlyBalance(self):
        return self.monthlyGains() - self.monthlyDumps()

    def transfersForPeriod(self, startDate, endDate):
        allTransfers = [transfer 
                        for group in self.groups
                        for change in group.changes
                        for transfer in change.transfersForPeriod(startDate, endDate)]
        return sorted(allTransfers, self.compareTwoTransfers)

    def compareTwoTransfers(self, t1, t2):
        result = cmp(t1.date, t2.date)
        if (result == 0):
            result = cmp(t1.reason, t2.reason)
        return result

    def __eq__(self, other):
        return self.groups == other.groups

#########################################################################

class MoneySheet:
    '''
    The MoneySheet provides methods for calculating financial indicators.
    '''

    def __init__(self, initialBalance, portfolio):
        self.initialBalance = initialBalance
        self.portfolio = portfolio

    def forecastForPeriod(self, startDate, endDate):
        balance = self.initialBalance
        transfers = self.portfolio.transfersForPeriod(startDate, endDate)
        forecast = []
        forecast.append((Transfer(startDate, 'period-begin', 0), self.initialBalance))
        for transfer in transfers:
            balance = balance + transfer.amount
            forecast.append((transfer, balance))
        forecast.append((Transfer(endDate, 'period-end', 0), balance))
        return forecast

    def __eq__(self, other):
        eq1 = self.initialBalance == other.initialBalance
        eq2 = self.portfolio == other.portfolio
        return eq1 and eq2

#########################################################################

class InputReader:

    def __init__(self, sheetFilePath):
        self.sheetFilePath = sheetFilePath

    def getMoneySheet(self):
        sheetFile = open(self.sheetFilePath, 'r')
        sheetText = sheetFile.read()
        moneySheet = eval(sheetText)
        return moneySheet

#########################################################################

class OutputPrinter:
    '''
    Reads objects from strings and writes them to strings.
    '''

    def printForecast(self, forecast):
        prevTransfer = Transfer(date(1, 1, 2), 'empty', 0)
        for element in forecast:
            transfer = element[0]
            balance = element[1]
            if transfer.date.day == 1 and prevTransfer.date.day != 1:
                print ''
                print transfer.date.ctime()
                print '------------------------'
            print str(transfer.date), self.formatMoney(transfer.amount), '', transfer.reason.ljust(20), '|', self.formatMoney(balance)
            prevTransfer = transfer

    def formatMoney(self, value):
        result = str(value)
        if value > 0:
            result = '+' + result
        return result.rjust(8)
 
#########################################################################

class Calendar:

    def todayDate(self):
        nowDateTime = datetime.now()
        return nowDateTime.date()

#########################################################################

class AppRunner:

    def __init__(self,
                 inputReader = InputReader('config.py'),
                 outputPrinter = OutputPrinter(),
                 calendar = Calendar()):
        self.inputReader = inputReader
        self.outputPrinter = outputPrinter
        self.calendar = calendar

    # TODO: use mocked InputReader and OutputWriter for testing

    def runApplication(self, startDate, endDate):
        moneySheet = self.inputReader.getMoneySheet()
        forecast = moneySheet.forecastForPeriod(startDate, endDate)
        self.outputPrinter.printForecast(forecast)

    def main(self, cmdLineArgs):
        # read args TODO: check args
        numberOfMonths = int(cmdLineArgs[1]) if len(cmdLineArgs) > 1 else 3
        startDate = self.calendar.todayDate()
        endDate = startDate + timedelta(numberOfMonths * 30)
        self.runApplication(startDate, endDate)

#########################################################################

if __name__ == '__main__':
    print sys.argv
    runner = AppRunner()
    runner.main(sys.argv)


#########################################################################

#########################################################################




