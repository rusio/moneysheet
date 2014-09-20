#!/usr/bin/env python3

from __future__ import print_function
from datetime import *
import argparse

#########################################################################
import sys


class Schedule:
  """
  A schedule for a periodic event. Examples:
  - monthly payment of salary
  - weekly drinking in the strip club
  - daily smoking of cigarettes
  """

  def __init__(self, firstDate=date.min, lastDate=date.max):
    self._firstDate = firstDate
    self._lastDate = lastDate

  def periodLength(self):  # abstract
    raise NotImplementedError('subclass must implement periodLength()')

  def matchesDate(self, dateFromPeriod):  # abstract
    raise NotImplementedError('subclass must implement matchesDate()')

  def dailyPortionOf(self, value):
    """
    Normalizes the given value to a daily basis,
    according to the period of this schedule.
    """
    if not value > 0:
      raise ValueError('value must be positive')
    return float(value) / self.periodLength()

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

#########################################################################


class EveryDay(Schedule):
  """
  A trivial schedule for something that happens every day.
  """

  def __init__(self, firstDate=date.min, lastDate=date.max):
    Schedule.__init__(self, firstDate, lastDate)

  def periodLength(self):
    return 1

  def matchesDate(self, dateFromPeriod):
    return True


class EveryMonth(Schedule):
  """
  A schedule for something that happens periodically every month.
  """

  def __init__(self, firingDay=1, firstDate=date.min, lastDate=date.max):
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
  """
  A schedule for something that happens periodically every week.
  """

  def __init__(self, weekday=1, firstDate=date.min, lastDate=date.max):
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
  """
  A schedule for something that happens once in two weeks.
  """

  def __init__(self, weekday=1, firstDate=date.min, lastDate=date.max):
    Schedule.__init__(self, firstDate, lastDate)
    if weekday not in range(1, 8):
      raise ValueError('weekday must be in the range [1..7]')
    self.weekday = weekday
    self.matchCount = 0

  def periodLength(self):
    return 14

  def matchesDate(self, dateFromPeriod):
    if dateFromPeriod.isoweekday() == self.weekday:
      self.matchCount += 1
      if self.matchCount % 2 == 1:
        return True
    return False

#########################################################################


class EveryYear(Schedule):
  """
  A schedule for something that happens periodically every year.
  """
  daysPerMonth = [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

  def __init__(self, monthInYear, dayInMonth, firstDate=date.min, lastDate=date.max):
    Schedule.__init__(self, firstDate, lastDate)

    if not 1 <= monthInYear <= 12:
      raise ValueError('invalid monthInYear supplied: ' + str(monthInYear))
    if not 1 <= dayInMonth <= EveryYear.daysPerMonth[monthInYear]:
      raise ValueError('invalid dayInMonth supplied: ' + str(dayInMonth))

    self.monthInYear = monthInYear
    self.dayInMonth = dayInMonth

  def periodLength(self):
    return 365  # TODO 366?

  def matchesDate(self, dateFromPeriod):
    return (dateFromPeriod.month, dateFromPeriod.day) == (self.monthInYear, self.dayInMonth)

#########################################################################


class Change:
  """
  A change (positive or negative) in the money balance which
  has a fixed amount and happens periodically at a given schedule.
  """

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
  """
  Incoming money that comes in periodically, based on a schedule.
  """

  def __init__(self, destination, amount, schedule):
    Change.__init__(self, destination, +amount, schedule)

#########################################################################


class Dump(Change):
  """
  Outgoing money that goes out periodically, based on a schedule.
  """

  def __init__(self, destination, amount, schedule):
    Change.__init__(self, destination, -amount, schedule)

#########################################################################


class Transfer:
  """
  A concrete transfer of money on a given date. Note the difference from
  Gain and Dump - a Gain or Dump is just the description of the incoming
  or outgoing money. A Transfer is the actual movement of the money
  on a concrete date, according to the schedule of the Gain or Dump.
  """

  @classmethod
  def leapsMonth(cls, transfer1, transfer2):
    if transfer1.date > transfer2.date:
      return False
    return transfer1.date.month < transfer2.date.month

  def __init__(self, date, reason, amount):
    self.date = date
    self.reason = reason
    self.amount = amount

  def __eq__(self, other):
    equalDates = self.date == other.date
    equalReasons = self.reason == other.reason
    equalAmounts = self.amount == other.amount
    return equalDates and equalReasons and equalAmounts

  def sortingKey(self):
    return str(self.date) + self.reason

  def __repr__(self):
    return 'Transfer(' + str(self.date) + ',' + self.reason + ',' + str(self.amount) + ')'

#########################################################################


class Group:
  """
  A group of multiple Changes under a common category.
  """

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
  """
  The Portfolio contains the data for all Gains and Dumps of the user.
  """

  def __init__(self, groups):
    self.groups = groups

  # TODO: add monthlyGains, monthlyDumps, monthlyBalance to report
  # TODO: rename them to average...

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
    return sorted(allTransfers, key=(lambda x: x.sortingKey()))

  def __eq__(self, other):
    return self.groups == other.groups

#########################################################################


class MoneySheet:
  """
  The MoneySheet provides central methods for calculating the
  financial forecast. It is bundles the core logic of the app.
  """

  def __init__(self, initialBalance, portfolio):
    self.initialBalance = initialBalance
    self.portfolio = portfolio

  def forecastForPeriod(self, startDate, endDate):
    balance = self.initialBalance
    transfers = self.portfolio.transfersForPeriod(startDate, endDate)
    forecast = [(Transfer(startDate, 'PERIOD-BEGIN', 0), self.initialBalance)]
    for transfer in transfers:
      balance += transfer.amount
      forecast.append((transfer, balance))
    forecast.append((Transfer(endDate, 'PERIOD-END', 0), balance))
    return forecast

  def __eq__(self, other):
    eq1 = self.initialBalance == other.initialBalance
    eq2 = self.portfolio == other.portfolio
    return eq1 and eq2

#########################################################################


class SheetReader:
  """
  A reader for reading the input file into a MoneySheet object.
  """

  def __init__(self, sheetFilePath):
    self.sheetFilePath = sheetFilePath

  def getMoneySheet(self):
    sheetFile = open(self.sheetFilePath, 'r')
    sheetText = sheetFile.read()
    sheetText = sheetText.replace('from moneysheet import *', '')
    moneySheet = eval(sheetText)
    return moneySheet

#########################################################################


class ForecastPrinter:
  """
  A printer for printing a forecast in a formatted way to file or stdout.
  """

  def __init__(self, outputFile=sys.stdout):
    self.outputFile = outputFile

  def printForecast(self, forecast):
    prevTransfer = None
    for element in forecast:
      transfer = element[0]
      balance = element[1]
      if prevTransfer and Transfer.leapsMonth(prevTransfer, transfer):
        print('', file=self.outputFile)
        print(transfer.date.ctime(), file=self.outputFile)
        print('------------------------', file=self.outputFile)
      print(str(transfer.date),
            self.formatMoney(transfer.amount),
            '',
            transfer.reason.ljust(20),
            '|',
            self.formatMoney(balance),
            file=self.outputFile)
      prevTransfer = transfer

  def formatMoney(self, value):
    result = str(value)
    if value > 0:
      result = '+' + result
    return result.rjust(8)

#########################################################################


class SystemCalendar:
  """
  An adapter for retrieving the current date from the operating system.
  The purpose of this class is to enable a time-agnostic replacement in a test.
  """

  def todayDate(self):
    nowDateTime = datetime.now()
    return nowDateTime.date()

#########################################################################


class ForecastRunner:
  """
  This interactor executes a forecast run, the whole use-case.
  """

  def __init__(self, inputReader, outputPrinter, calendar):
    self.inputReader = inputReader
    self.outputPrinter = outputPrinter
    self.calendar = calendar

  def runForPeriod(self, numberOfMonths):
    startDate = self.calendar.todayDate()
    endDate = startDate + timedelta(numberOfMonths * 30)
    moneySheet = self.inputReader.getMoneySheet()
    forecast = moneySheet.forecastForPeriod(startDate, endDate)
    self.outputPrinter.printForecast(forecast)

#########################################################################


class ArgsParser(argparse.ArgumentParser):
  """
  A parser for the command-line arguments of the console application.
  """

  def __init__(self):
    super().__init__(self)
    self.description = 'The money sheet estimates how much money you would have in the near future.'
    self.add_argument('-i', '--input-file',
                      default='sheetdata.py',
                      help='the input file to use for the forecast')
    self.add_argument('-m', '--forecast-months',
                      type=int,
                      default=3,
                      help='the number of months for the forecast period')

#########################################################################


class Application:
  """
  Basic console UI, a boundary point in the application.
  """

  def __init__(self,
               parser=ArgsParser(),
               printer=ForecastPrinter(),
               calendar=SystemCalendar()):
    self.parser = parser
    self.printer = printer
    self.calendar = calendar

  def run(self):
    args = self.parser.parse_args()
    runner = ForecastRunner(SheetReader(args.input_file),
                            self.printer,
                            self.calendar)
    runner.runForPeriod(args.forecast_months)

#########################################################################


if __name__ == '__main__':
  ui = Application()
  ui.run()

#########################################################################


