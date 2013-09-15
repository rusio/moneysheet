#!/usr/bin/python

from datetime import *
import unittest
from moneysheet import *

########################################################################

class ScheduleTest(unittest.TestCase):
  def testNormalization_ExceptionForNegativeValue(self):
    self.assertRaises(ValueError,
                      Schedule.dailyPortionOf,
                      Schedule(),
                      -1)

  def testNormalization_1(self):
    schedule = EveryMonth(15)
    self.assertEquals(40, schedule.dailyPortionOf(1200))

  def testNormalization_2(self):
    schedule = EveryMonth(15)
    self.assertAlmostEquals(3.3333333, schedule.dailyPortionOf(100))

  def testNormalization_3(self):
    schedule = EveryWeek(3)
    self.assertAlmostEquals(50, schedule.dailyPortionOf(350))

  def testLimitedActivePeriod(self):
    schedule = EveryDay(firstDate=date(2011, 12, 24), lastDate=date(2011, 12, 26))
    self.assertEquals([date(2011, 12, 24),
                       date(2011, 12, 25),
                       date(2011, 12, 26)],
                      schedule.datesForPeriod(date(2011, 12, 20),
                                              date(2011, 12, 30)))


class EveryDayTest(unittest.TestCase):
  def testDatesForPeriod(self):
    schedule = EveryDay()
    self.assertEquals([date(2011, 12, 30),
                       date(2011, 12, 31),
                       date(2012, 1, 1),
                       date(2012, 1, 2)],
                      schedule.datesForPeriod(date(2011, 12, 30),
                                              date(2012, 1, 2)))

########################################################################

class EveryMonthTest(unittest.TestCase):
  def testExceptionForInvalidFiringDay(self):
    self.assertRaises(ValueError, EveryMonth, 0)
    self.assertRaises(ValueError, EveryMonth, 29)

  def testExceptionForInvalidInterval(self):
    schedule = EveryMonth(15)
    self.assertRaises(ValueError,
                      schedule.datesForPeriod,
                      [date(2013, 2, 10),
                       date(2012, 2, 20)],
      [])

  def testNoDateInsideInterval_0a(self):
    schedule = EveryMonth(15)
    self.assertEquals([],
      schedule.datesForPeriod(date(2012, 2, 10),
                              date(2012, 2, 14)))

  def testNoDateInsideInterval_0b(self):
    schedule = EveryMonth(15)
    self.assertEquals([],
      schedule.datesForPeriod(date(2012, 2, 16),
                              date(2012, 2, 20)))

  def testNoDateInsideInterval_1(self):
    schedule = EveryMonth(15)
    self.assertEquals([],
      schedule.datesForPeriod(date(2012, 2, 16),
                              date(2012, 3, 14)))

  def testNoDateInsideInterval_2(self):
    schedule = EveryMonth(15)
    self.assertEquals([],
      schedule.datesForPeriod(date(2012, 12, 16),
                              date(2013, 1, 14)))

  def testOneDateInsideInterval(self):
    schedule = EveryMonth(15)
    self.assertEquals([date(2012, 2, 15)],
                      schedule.datesForPeriod(date(2012, 2, 1),
                                              date(2012, 2, 28)))

  def testOneDateAtIntervalStart(self):
    schedule = EveryMonth(15)
    self.assertEquals([date(2012, 2, 15)],
                      schedule.datesForPeriod(date(2012, 2, 15),
                                              date(2012, 2, 28)))

  def testOneDateAtIntervalEnd(self):
    schedule = EveryMonth(15)
    self.assertEquals([date(2012, 2, 15)],
                      schedule.datesForPeriod(date(2012, 2, 1),
                                              date(2012, 2, 15)))

  def testOneDateAtSameStartAndEndDate(self):
    schedule = EveryMonth(15)
    self.assertEquals([date(2012, 2, 15)],
                      schedule.datesForPeriod(date(2012, 2, 15),
                                              date(2012, 2, 15)))

  def testTwoDatesInsideInterval_1(self):
    schedule = EveryMonth(15)
    self.assertEquals([date(2012, 2, 15), date(2012, 3, 15)],
                      schedule.datesForPeriod(date(2012, 2, 1),
                                              date(2012, 3, 31)))

  def testTwoDatesInsideInterval_2(self):
    schedule = EveryMonth(15)
    self.assertEquals([date(2012, 2, 15), date(2012, 3, 15)],
                      schedule.datesForPeriod(date(2012, 2, 14),
                                              date(2012, 3, 16)))

  def testTwoDatesInsideInterval_3(self):
    schedule = EveryMonth(15)
    self.assertEquals([date(2012, 2, 15), date(2012, 3, 15)],
                      schedule.datesForPeriod(date(2012, 1, 16),
                                              date(2012, 4, 14)))

  def testTwoDatesAtIntervalBorders_1(self):
    schedule = EveryMonth(15)
    self.assertEquals([date(2012, 2, 15), date(2012, 3, 15)],
                      schedule.datesForPeriod(date(2012, 2, 15),
                                              date(2012, 3, 15)))

  def testOneYearAtMiddleOfMonth(self):
    schedule = EveryMonth(15)
    self.assertEquals(12,
                      len(schedule.datesForPeriod(date(2012, 1, 1),
                                                  date(2013, 1, 1))))

  def testOneYearAtIntervalBorders(self):
    schedule = EveryMonth(15)
    self.assertEquals(13,
                      len(schedule.datesForPeriod(date(2012, 1, 15),
                                                  date(2013, 1, 15))))

  def testTwoYearsAtMiddleOfMonth(self):
    schedule = EveryMonth(15)
    self.assertEquals(24,
                      len(schedule.datesForPeriod(date(2012, 1, 1),
                                                  date(2014, 1, 1))))

  def testTwoYearsAtIntervalBorders(self):
    schedule = EveryMonth(15)
    self.assertEquals(25,
                      len(schedule.datesForPeriod(date(2012, 1, 15),
                                                  date(2014, 1, 15))))

######################################################################## 

class EveryWeekTest(unittest.TestCase):
  def exceptionForInvalidWeekday(self):
    self.assertRaises(ValueError, EveryWeek, 0)
    self.assertRaises(ValueError, EveryWeek, 8)

  def testDatesForPeriod(self):
    schedule = EveryWeek(6)
    self.assertEquals([date(2011, 12, 24),
                       date(2011, 12, 31),
                       date(2012, 1, 7)],
                      schedule.datesForPeriod(date(2011, 12, 24),
                                              date(2012, 1, 7)))

  def testDatesForPeriod_SameStartAndEndDate(self):
    schedule = EveryWeek(6)
    self.assertEquals([date(2011, 12, 24)],
                      schedule.datesForPeriod(date(2011, 12, 24),
                                              date(2011, 12, 24)))

########################################################################

class OnceInTwoWeeksTest(unittest.TestCase):
  def exceptionForInvalidWeekday(self):
    self.assertRaises(ValueError, OnceInTwoWeeks, 0)
    self.assertRaises(ValueError, OnceInTwoWeeks, 8)

  def testDatesForPeriod(self):
    schedule = OnceInTwoWeeks(6)
    self.assertEquals([date(2011, 12, 24),
                       date(2012, 1, 7),
                       date(2012, 1, 21)],
                      schedule.datesForPeriod(date(2011, 12, 24),
                                              date(2012, 1, 21)))

  def testDatesForPeriod_SameStartAndEndDate(self):
    schedule = OnceInTwoWeeks(6)
    self.assertEquals([date(2011, 12, 24)],
                      schedule.datesForPeriod(date(2011, 12, 24),
                                              date(2011, 12, 24)))

########################################################################

class EveryYearTest(unittest.TestCase):
  def testValidMonthsInYear(self):
    dayInMonth = 1
    # should not raise for the months 1..12
    for monthInYear in range(1, 13):
      EveryYear(monthInYear, dayInMonth)
      # but raise for the invalid months 0 and 13
    self.assertRaises(ValueError, EveryYear, 0, dayInMonth)
    self.assertRaises(ValueError, EveryYear, 13, dayInMonth)

  def testValidDaysInJanuary(self):
    monthInYear = 1
    # should not raise for the valid days in this month
    for dayInMonth in range(1, 32):
      EveryYear(monthInYear, dayInMonth)
      # but raise for the invalid days in this month
    for dayInMonth in [0, 32]:
      self.assertRaises(ValueError, EveryYear, monthInYear, dayInMonth)

  def testValidDaysInFebruary(self):
    monthInYear = 2
    # should not raise for the valid days in this month
    for dayInMonth in range(1, 29):
      EveryYear(monthInYear, dayInMonth)
      # but raise for the invalid days in this month
    for dayInMonth in [0, 29]:
      self.assertRaises(ValueError, EveryYear, monthInYear, dayInMonth)

  def testValidDaysInMarch(self):
    monthInYear = 3
    # should not raise for the valid days in this month
    for dayInMonth in range(1, 32):
      EveryYear(monthInYear, dayInMonth)
      # but raise for the invalid days in this month
    for dayInMonth in [0, 32]:
      self.assertRaises(ValueError, EveryYear, monthInYear, dayInMonth)

  def testValidDaysInApril(self):
    monthInYear = 4
    # should not raise for the valid days in this month
    for dayInMonth in range(1, 31):
      EveryYear(monthInYear, dayInMonth)
      # but raise for the invalid days in this month
    for dayInMonth in [0, 31]:
      self.assertRaises(ValueError, EveryYear, monthInYear, dayInMonth)

  def testValidDaysInMai(self):
    monthInYear = 5
    # should not raise for the valid days in this month
    for dayInMonth in range(1, 31):
      EveryYear(monthInYear, dayInMonth)
      # but raise for the invalid days in this month
    for dayInMonth in [0, 32]:
      self.assertRaises(ValueError, EveryYear, monthInYear, dayInMonth)

  def testValidDaysInJune(self):
    monthInYear = 6
    # should not raise for the valid days in this month
    for dayInMonth in range(1, 31):
      EveryYear(monthInYear, dayInMonth)
      # but raise for the invalid days in this month
    for dayInMonth in [0, 31]:
      self.assertRaises(ValueError, EveryYear, monthInYear, dayInMonth)

  def testValidDaysInJuly(self):
    monthInYear = 7
    # should not raise for the valid days in this month
    for dayInMonth in range(1, 31):
      EveryYear(monthInYear, dayInMonth)
      # but raise for the invalid days in this month
    for dayInMonth in [0, 32]:
      self.assertRaises(ValueError, EveryYear, monthInYear, dayInMonth)

  def testValidDaysInAugust(self):
    monthInYear = 8
    # should not raise for the valid days in this month
    for dayInMonth in range(1, 31):
      EveryYear(monthInYear, dayInMonth)
      # but raise for the invalid days in this month
    for dayInMonth in [0, 32]:
      self.assertRaises(ValueError, EveryYear, monthInYear, dayInMonth)

  def testValidDaysInSeptember(self):
    monthInYear = 9
    # should not raise for the valid days in this month
    for dayInMonth in range(1, 31):
      EveryYear(monthInYear, dayInMonth)
      # but raise for the invalid days in this month
    for dayInMonth in [0, 31]:
      self.assertRaises(ValueError, EveryYear, monthInYear, dayInMonth)

  def testValidDaysInOctober(self):
    monthInYear = 10
    # should not raise for the valid days in this month
    for dayInMonth in range(1, 31):
      EveryYear(monthInYear, dayInMonth)
      # but raise for the invalid days in this month
    for dayInMonth in [0, 32]:
      self.assertRaises(ValueError, EveryYear, monthInYear, dayInMonth)

  def testValidDaysInNovemer(self):
    monthInYear = 11
    # should not raise for the valid days in this month
    for dayInMonth in range(1, 31):
      EveryYear(monthInYear, dayInMonth)
      # but raise for the invalid days in this month
    for dayInMonth in [0, 31]:
      self.assertRaises(ValueError, EveryYear, monthInYear, dayInMonth)

  def testValidDaysInDecember(self):
    monthInYear = 12
    # should not raise for the valid days in this month
    for dayInMonth in range(1, 31):
      EveryYear(monthInYear, dayInMonth)
      # but raise for the invalid days in this month
    for dayInMonth in [0, 32]:
      self.assertRaises(ValueError, EveryYear, monthInYear, dayInMonth)

  def testDatesForPeriod(self):
    schedule = EveryYear(12, 31)
    self.assertEquals([date(2011, 12, 31),
                       date(2012, 12, 31)], schedule.datesForPeriod(date(2011, 12, 24),
                                                                    date(2013, 1, 21)))


########################################################################

class ChangeTest(unittest.TestCase):
  def TODOtestEquals(self):
    change1 = Change('description', 100, None)
    pass

########################################################################

class GainTest(unittest.TestCase):
  def testOneSalaryDuringOneMonth(self):
    gain = Gain('salary', 2000, EveryMonth(28))
    self.assertEquals([Transfer(date(2012, 1, 28), 'salary', 2000)],
                      gain.transfersForPeriod(date(2012, 1, 1),
                                              date(2012, 1, 31)))

  def testOneSalaryDuringAlmostTwoMonths(self):
    gain = Gain('salary', 2000, EveryMonth(28))
    self.assertEquals([Transfer(date(2012, 1, 28), 'salary', 2000)],
                      gain.transfersForPeriod(date(2012, 1, 1),
                                              date(2012, 2, 27)))

  def testTwoSalariesDuringTwoWholeMonths(self):
    gain = Gain('salary', 2000, EveryMonth(28))
    self.assertEquals([Transfer(date(2012, 2, 28), 'salary', 2000),
                       Transfer(date(2012, 3, 28), 'salary', 2000)],
                      gain.transfersForPeriod(date(2012, 2, 1),
                                              date(2012, 3, 31)))

  def testTwoSalariesForMinimalPeriod(self):
    gain = Gain('salary', 2000, EveryMonth(28))
    self.assertEquals([Transfer(date(2012, 2, 28), 'salary', 2000),
                       Transfer(date(2012, 3, 28), 'salary', 2000)],
                      gain.transfersForPeriod(date(2012, 2, 28),
                                              date(2012, 3, 28)))

  def testTwoSalariesForMaximalPeriod(self):
    gain = Gain('salary', 2000, EveryMonth(28))
    self.assertEquals([Transfer(date(2012, 2, 28), 'salary', 2000),
                       Transfer(date(2012, 3, 28), 'salary', 2000)],
                      gain.transfersForPeriod(date(2012, 1, 29),
                                              date(2012, 4, 27)))

  def testDailyAverage(self):
    gain = Gain('salary', 1800, EveryMonth(28))
    self.assertEquals(60, gain.dailyAverage())

######################################################################## 

class GroupTest(unittest.TestCase):
  def testDailyAverage(self):
    group = Group('g1', [Gain('salary', 1000, EveryMonth(28)),
                         Gain('stocks', 5000, EveryMonth(1))])
    self.assertEquals(200, group.dailyAverage())

######################################################################## 

class PortfolioTest(unittest.TestCase):
  def setUp(self):
    g1 = Group('work', [Gain('salary', 2000, EveryMonth(28)),
                        Gain('lessons', 100, EveryMonth(15))])
    g2 = Group('help', [Gain('kindergeld', 300, EveryMonth(10))])
    d1 = Group('fixed', [Dump('school', 200, EveryMonth(1)),
                         Dump('rental', 600, EveryMonth(1))])
    d2 = Group('variable', [Dump('car', 400, EveryMonth(10)),
                            Dump('dope', 500, EveryMonth(20))])
    self.portfolio = Portfolio([g1, g2, d1, d2])

  def testMonthlyGains(self):
    self.assertAlmostEquals(2400, self.portfolio.monthlyGains())

  def testMonthlyDumps(self):
    self.assertAlmostEquals(1700, self.portfolio.monthlyDumps())

  def testMonthlyBalance(self):
    self.assertAlmostEquals(700, self.portfolio.monthlyBalance())

  def testTransfersForPeriod(self):
    self.assertEquals([Transfer(date(2012, 2, 1), 'rental', -600),
                       Transfer(date(2012, 2, 1), 'school', -200),
                       Transfer(date(2012, 2, 10), 'car', -400),
                       Transfer(date(2012, 2, 10), 'kindergeld', 300),
                       Transfer(date(2012, 2, 15), 'lessons', 100),
                       Transfer(date(2012, 2, 20), 'dope', -500),
                       Transfer(date(2012, 2, 28), 'salary', 2000)],
                      self.portfolio.transfersForPeriod(date(2012, 2, 1),
                                                        date(2012, 2, 28)))


######################################################################## 

class MoneySheetTest(unittest.TestCase):
  def setUp(self):
    g1 = Group('work', [Gain('salary', 2000, EveryMonth(28)),
                        Gain('lessons', 100, EveryMonth(15))])
    g2 = Group('help', [Gain('kindergeld', 300, EveryMonth(10))])
    d1 = Group('fixed', [Dump('school', 200, EveryMonth(1)),
                         Dump('rental', 600, EveryMonth(1))])
    d2 = Group('variable', [Dump('car', 400, EveryMonth(10)),
                            Dump('dope', 500, EveryMonth(20))])
    portfolio = Portfolio([g1, g2, d1, d2])
    initialBalance = 1000
    self.moneySheet = MoneySheet(initialBalance, portfolio)

  def testForecast(self):
    self.assertEquals([(Transfer(date(2012, 2, 1), 'PERIOD-BEGIN', 0), 1000),
                       (Transfer(date(2012, 2, 1), 'rental', -600), 400),
                       (Transfer(date(2012, 2, 1), 'school', -200), 200),
                       (Transfer(date(2012, 2, 10), 'car', -400), -200),
                       (Transfer(date(2012, 2, 10), 'kindergeld', 300), 100),
                       (Transfer(date(2012, 2, 15), 'lessons', 100), 200),
                       (Transfer(date(2012, 2, 20), 'dope', -500), -300),
                       (Transfer(date(2012, 2, 28), 'salary', 2000), 1700),
                       (Transfer(date(2012, 2, 28), 'PERIOD-END', 0), 1700)],
                      self.moneySheet.forecastForPeriod(date(2012, 2, 1),
                                                        date(2012, 2, 28)))

######################################################################## 


class ForecastPrinterTest(unittest.TestCase):
  def testFormattingOfMoneyValues(self):
    printer = ForecastPrinter()
    self.assertEquals('       0', printer.formatMoney(0))
    self.assertEquals('    -123', printer.formatMoney(-123))
    self.assertEquals('    +456', printer.formatMoney(456))

######################################################################## 


class MoneySheetReaderTest(unittest.TestCase):
  def testReadingOfMoneysheetData(self):
    expectedSheet = MoneySheet(
      22000,
      Portfolio(
        [
          Group('Red Hot Chilly Peppers',
                [
                  Gain('concert', 50000, EveryMonth()),
                  Gain('advertising', 2000, EveryWeek()),
                  Dump('equipment', 600, EveryWeek()),
                  Dump('prostitutes', 2000, EveryWeek()),
                ]),
          Group('Mars, Bruno',
                [
                  Gain('sales', 80000, EveryMonth()),
                  Dump('cosmetics', 2000, EveryWeek()),
                  Dump('gay-porn', 800, EveryWeek()),
                ]),
        ])
    )

    reader = MoneySheetReader('impresario.sheet')
    actualSheet = reader.getMoneySheet()
    self.assertEquals(expectedSheet, actualSheet)

######################################################################## 

class MockReader:
  def getMoneySheet(self):
    testData = MoneySheet(
      1000,
      Portfolio([
        Group('my-gains', [
          Gain('scholarship', 400, EveryMonth()),
        ]),
        Group('my-dumps', [
          Dump('train-card', 120, EveryMonth()),
        ]),
      ]))
    return testData


class MockPrinter():
  def printForecast(self, actualForecast):
    expectedForecast = ([
                          (Transfer(date(2012, 2, 28), 'PERIOD-BEGIN', 0), 1000),
                          (Transfer(date(2012, 3, 1), 'scholarship', +400), 1400),
                          (Transfer(date(2012, 3, 1), 'train-card', -120), 1280),
                          (Transfer(date(2012, 3, 29), 'PERIOD-END', 0), 1280),
                        ])
    self.expectationsMatch = (actualForecast == expectedForecast)


class MockCalendar:
  def todayDate(self):
    return date(2012, 2, 28)


class ForecastRunnerTest(unittest.TestCase):
  def testRunForOneMonth(self):
    mockReader = MockReader()
    mockPrinter = MockPrinter()
    mockCalendar = MockCalendar()
    runner = ForecastRunner(mockReader, mockPrinter, mockCalendar)
    numberOfMonths = 1
    runner.runForPeriod(numberOfMonths)
    self.assertTrue(mockPrinter.expectationsMatch)

########################################################################

# TODO: test for Application

######################################################################## 

if __name__ == '__main__':
  unittest.main()


