from abc import ABCMeta, abstractmethod
from argparse import ArgumentParser
from calendar import MONDAY, TUESDAY, WEDNESDAY, THURSDAY, FRIDAY, SATURDAY, SUNDAY
from datetime import *
from sys import stdout
from typing import List


class Schedule(object, metaclass=ABCMeta):
  """
  A schedule for a periodic event. Examples:
  - monthly payment of salary
  - weekly drinking in the strip club
  - daily smoking of cigarettes
  """

  def __init__(self, firstDate=date.min, lastDate=date.max):
    self._firstDate = firstDate
    self._lastDate = lastDate

  @abstractmethod
  def periodLength(self) -> int:
    pass

  @abstractmethod
  def matchesDate(self, dateFromPeriod: date) -> bool:
    pass

  def dailyPortionOf(self, value) -> float:
    """
    Normalizes the given value to a daily basis,
    according to the period of this schedule.
    """
    if not value > 0:
      raise ValueError('value must be positive')
    return float(value) / self.periodLength()

  def datesForPeriod(self, startDate: date, endDate: date) -> List[date]:
    if startDate > endDate:
      raise ValueError('startDate must not be after endDate')

    # consider limits of active period
    if startDate < self._firstDate:
      startDate = self._firstDate
    if endDate > self._lastDate:
      endDate = self._lastDate

    result = []
    oneDay = timedelta(1)
    elem = startDate
    while elem <= endDate:
      if self.matchesDate(elem):
        result.append(elem)
      elem += oneDay
    return result


class OneTime(Schedule):
  """
  A special case of a one-time money transfer.
  """

  def __init__(self, transferDate: date):
    super().__init__(firstDate=transferDate, lastDate=transferDate)
    self.transferDate = transferDate

  def matchesDate(self, dateFromPeriod: date) -> bool:
    return dateFromPeriod == self._firstDate

  def periodLength(self) -> int:
    return 1


class Today(OneTime):
  """
  A money transfer that is supposed to happen today.
  """

  def __init__(self):
    super().__init__(date.today())


class Tomorrow(OneTime):
  """
  A money transfer that is supposed to happen tomorrow.
  """

  def __init__(self):
    super().__init__(date.today() + timedelta(1))


class AfterDays(OneTime):
  """
  A money transfer that is supposed to happen after a number of days.
  """

  def __init__(self, numberOfDays: int):
    super().__init__(date.today() + timedelta(numberOfDays))


class ThisWeek(OneTime):
  """
  A money transfer that is supposed to happen on some day during this week.
  """

  def __init__(self, dayOfWeek: int):
    super().__init__(ThisWeek.transferDate(date.today(), dayOfWeek))

  @staticmethod
  def transferDate(todayDate: date, dayOfWeek: int) -> date:
    if dayOfWeek < todayDate.weekday():
      raise ValueError("todayDate is in the past")
    result = todayDate
    while result.weekday() != dayOfWeek:
      result += timedelta(1)
    return result


class NextWeek(OneTime):
  """
  A money transfer that is supposed to happen on some day during next week.
  """

  def __init__(self, dayOfWeek: int):
    super().__init__(NextWeek.transferDate(date.today(), dayOfWeek))

  @staticmethod
  def transferDate(todayDate: date, dayOfWeek: int) -> date:
    result = todayDate
    if result.weekday() == dayOfWeek:
      result += timedelta(1)
    while result.weekday() != dayOfWeek:
      result += timedelta(1)
    return result


class EveryDay(Schedule):
  """
  A trivial schedule for something that happens every day.
  """

  def __init__(self, firstDate=date.min, lastDate=date.max):
    Schedule.__init__(self, firstDate, lastDate)

  def periodLength(self) -> int:
    return 1

  def matchesDate(self, dateFromPeriod: date) -> bool:
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

  def periodLength(self) -> int:
    return 30

  def matchesDate(self, dateFromPeriod: date) -> bool:
    return dateFromPeriod.day == self.firingDay


class EveryWeek(Schedule):
  """
  A schedule for something that happens periodically every week.
  """

  def __init__(self, weekday=1, firstDate=date.min, lastDate=date.max):
    Schedule.__init__(self, firstDate, lastDate)
    if weekday not in range(1, 8):
      raise ValueError('weekday must be in the range [1..7]')
    self.weekday = weekday

  def periodLength(self) -> int:
    return 7

  def matchesDate(self, dateFromPeriod: date) -> bool:
    return dateFromPeriod.isoweekday() == self.weekday


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

  def periodLength(self) -> int:
    return 14

  def matchesDate(self, dateFromPeriod: date) -> bool:
    if dateFromPeriod.isoweekday() == self.weekday:
      self.matchCount += 1
      if self.matchCount % 2 == 1:
        return True
    return False


class EveryYear(Schedule):
  """
  A schedule for something that happens periodically every year.
  """
  daysPerMonth = [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

  def __init__(self, monthInYear: int, dayInMonth: int, firstDate=date.min, lastDate=date.max):
    Schedule.__init__(self, firstDate, lastDate)

    if not 1 <= monthInYear <= 12:
      raise ValueError('invalid monthInYear supplied: ' + str(monthInYear))
    if not 1 <= dayInMonth <= EveryYear.daysPerMonth[monthInYear]:
      raise ValueError('invalid dayInMonth supplied: ' + str(dayInMonth))

    self.monthInYear = monthInYear
    self.dayInMonth = dayInMonth

  def periodLength(self) -> int:
    return 365  # TODO 366?

  def matchesDate(self, dateFromPeriod: date) -> bool:
    return (dateFromPeriod.month, dateFromPeriod.day) == (self.monthInYear, self.dayInMonth)


class Transfer(object):
  """
  A concrete transfer of money on a given date. Note the difference from
  Gain and Dump - a Gain or Dump is just the description of the incoming
  or outgoing money. A Transfer is the actual movement of the money
  on a concrete date, according to the schedule of the Gain or Dump.
  """

  @classmethod
  def leapsMonth(cls, transfer1, transfer2):
    return transfer1.atDate < transfer2.atDate and transfer1.atDate.month != transfer2.atDate.month

  def __init__(self, atDate: date, reason: str, amount: int):
    self.atDate = atDate
    self.reason = reason
    self.amount = amount

  def __eq__(self, other):
    equalDates = self.atDate == other.atDate
    equalReasons = self.reason == other.reason
    equalAmounts = self.amount == other.amount
    return equalDates and equalReasons and equalAmounts

  def sortingKey(self):
    return str(self.atDate) + self.reason

  def __repr__(self):
    return 'Transfer(' + str(self.atDate) + ',' + self.reason + ',' + str(self.amount) + ')'


class Change(object):
  """
  A change (positive or negative) in the money balance which
  has a fixed amount and happens periodically at a given schedule.
  """

  def __init__(self, description: str, amount: int, schedule: Schedule, **kwargs):
    self.description = description
    self.amount = amount
    self.schedule = schedule
    if kwargs is not None:
      self.goesFrom = kwargs.get('goesFrom')
      self.goesUntil = kwargs.get('goesUntil')

  def transfersForPeriod(self, startDate: date, endDate: date) -> List[Transfer]:
    # validate requested date interval
    if startDate > endDate:
      raise ValueError("startDate > endDate", startDate, endDate)
    # narrow the period bounds according to goesFrom and goesUntil
    if self.goesFrom is not None and startDate < self.goesFrom:
      startDate = self.goesFrom
    if self.goesUntil is not None and endDate > self.goesUntil:
      endDate = self.goesUntil
    # are we outside the interval range after narrowing?
    if startDate > endDate:
      return []
    # everythig is good, compute the transfers
    return [Transfer(atDate, self.description, self.amount)
            for atDate in self.schedule.datesForPeriod(startDate, endDate)]

  def dailyAverage(self) -> float:
    return self.schedule.dailyPortionOf(abs(self.amount))

  def __eq__(self, other):
    equalDescriptions = self.description == other.description
    equalAmounts = self.amount == other.amount
    return equalDescriptions and equalAmounts


class Gain(Change):
  """
  Incoming money that comes in periodically, based on a schedule.
  """

  def __init__(self, destination: str, amount: int, schedule: Schedule, **kwargs):
    Change.__init__(self, destination, +amount, schedule, **kwargs)


class Dump(Change):
  """
  Outgoing money that goes out periodically, based on a schedule.
  """

  def __init__(self, destination: str, amount: int, schedule: Schedule, **kwargs):
    Change.__init__(self, destination, -amount, schedule, **kwargs)


class Group(object):
  """
  A group of multiple Changes under a common category.
  """

  def __init__(self, name: str, changes: List[Change]):
    self.name = name
    self.changes = changes

  def dailyAverage(self) -> float:
    return sum([change.dailyAverage() for change in self.changes])

  def __eq__(self, other):
    eq1 = self.name == other.name
    eq2 = self.changes == other.changes
    return eq1 and eq2


class Portfolio(object):
  """
  The Portfolio contains the data for all Gains and Dumps of the user.
  """

  def __init__(self, groups: List[Group]):
    self.groups = groups

  # TODO: add monthlyGains, monthlyDumps, monthlyBalance to report
  # TODO: rename them to average...

  def monthlyGains(self) -> float:
    totalDailyGains = sum([change.dailyAverage()
                           for group in self.groups
                           for change in group.changes if change.amount > 0])
    return totalDailyGains * EveryMonth().periodLength()

  def monthlyDumps(self) -> float:
    totalDailyDumps = sum([change.dailyAverage()
                           for group in self.groups
                           for change in group.changes if change.amount < 0])
    return totalDailyDumps * EveryMonth().periodLength()

  def monthlyBalance(self) -> float:
    return self.monthlyGains() - self.monthlyDumps()

  def transfersForPeriod(self, startDate: date, endDate: date) -> List[Transfer]:
    allTransfers = [transfer
                    for group in self.groups
                    for change in group.changes
                    for transfer in change.transfersForPeriod(startDate, endDate)]
    return sorted(allTransfers, key=(lambda x: x.sortingKey()))

  def __eq__(self, other):
    return self.groups == other.groups


class MoneySheet(object):
  """
  The MoneySheet provides central methods for calculating the
  financial forecast. It is bundles the core logic of the app.
  """

  def __init__(self, initialBalance:float, portfolio:Portfolio):
    self.initialBalance = initialBalance
    self.portfolio = portfolio

  def forecastForPeriod(self, startDate:date, endDate:date) -> List[Transfer]:
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


class SheetReader(object):
  """
  A reader for reading the input file into a MoneySheet object.
  """

  def __init__(self, sheetFilePath:str):
    self.sheetFilePath = sheetFilePath

  def getMoneySheet(self) -> MoneySheet:
    sheetFile = open(self.sheetFilePath, 'r')
    sheetText = sheetFile.read()
    sheetText = sheetText.replace('from moneysheet import *', '')
    moneySheet = eval(sheetText)
    return moneySheet


class ForecastPrinter(object):
  """
  A printer for printing a forecast in a formatted way to file or stdout.
  """

  def __init__(self, outputFile=stdout):
    self.outputFile = outputFile

  @staticmethod
  def formatMoney(value:float) -> str:
    result = str(value)
    if value > 0:
      result = '(+) ' + str(value)
    if value < 0:
      result = '(-) ' + str(abs(value))
    return result.rjust(8)

  def printForecast(self, forecast:List[Transfer]):
    prevTransfer = None
    for element in forecast:
      transfer = element[0]
      balance = element[1]
      if prevTransfer and Transfer.leapsMonth(prevTransfer, transfer):
        print('', file=self.outputFile)
        print(transfer.atDate.ctime(), file=self.outputFile)
        print('------------------------', file=self.outputFile)
      print(str(transfer.atDate),
            '  ',
            self.formatMoney(transfer.amount),
            '',
            transfer.reason.ljust(40),
            '|',
            self.formatMoney(balance),
            file=self.outputFile)
      prevTransfer = transfer


class SystemCalendar(object):
  """
  An adapter for retrieving the current date from the operating system.
  The purpose of this class is to enable a time-agnostic replacement in a test.
  """

  def todayDate(self) -> date:
    nowDateTime = datetime.now()
    return nowDateTime.date()


class ForecastRunner(object):
  """
  This interactor executes a forecast run, the whole use-case.
  """

  def __init__(self,
               inputReader:SheetReader,
               outputPrinter:ForecastPrinter,
               calendar:SystemCalendar):
    self.inputReader = inputReader
    self.outputPrinter = outputPrinter
    self.calendar = calendar

  def runForPeriod(self, numberOfMonths:int):
    startDate = self.calendar.todayDate()
    endDate = startDate + timedelta(numberOfMonths * 30)
    moneySheet = self.inputReader.getMoneySheet()
    forecast = moneySheet.forecastForPeriod(startDate, endDate)
    self.outputPrinter.printForecast(forecast)


class ArgsParser(ArgumentParser):
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


def main():
  parser = ArgsParser()
  args = parser.parse_args()
  runner = ForecastRunner(SheetReader(args.input_file),
                          ForecastPrinter(),
                          SystemCalendar())
  runner.runForPeriod(args.forecast_months)


if __name__ == '__main__':
  main()
