#!/usr/bin/env python3
from io import StringIO
from unittest import TestCase

from moneysheet import *


class ScheduleTest(TestCase):
  def test_Normalization_ExceptionForNegativeValue(self):
    self.assertRaises(ValueError,
                      Schedule.dailyPortionOf,
                      Today(),
                      -1)

  def test_LimitedActivePeriod(self):
    schedule = EveryDay(firstDate=date(2011, 12, 24), lastDate=date(2011, 12, 26))
    self.assertEquals([date(2011, 12, 24),
                       date(2011, 12, 25),
                       date(2011, 12, 26)],
                      schedule.datesForPeriod(date(2011, 12, 20),
                                              date(2011, 12, 30)))


class OnceTestBase(metaclass=ABCMeta):
  @abstractmethod
  def getSut(self):
    pass

  def test_Normalization(self):
    schedule = self.getSut()
    self.assertEqual(1, schedule.dailyPortionOf(1))
    self.assertEqual(2, schedule.dailyPortionOf(2))

  def test_DatesForPeriod(self):
    schedule = self.getSut()
    self.assertEqual([schedule.transferDate],
                     schedule.datesForPeriod(schedule.transferDate,
                                             schedule.transferDate))
    self.assertEqual([schedule.transferDate],
                     schedule.datesForPeriod(schedule.transferDate - timedelta(1),
                                             schedule.transferDate))
    self.assertEqual([schedule.transferDate],
                     schedule.datesForPeriod(schedule.transferDate,
                                             schedule.transferDate + timedelta(1)))
    self.assertEqual([schedule.transferDate],
                     schedule.datesForPeriod(schedule.transferDate - timedelta(1),
                                             schedule.transferDate + timedelta(1)))
    self.assertEqual([],
                     schedule.datesForPeriod(schedule.transferDate + timedelta(1),
                                             schedule.transferDate + timedelta(2)))
    self.assertEqual([],
                     schedule.datesForPeriod(schedule.transferDate - timedelta(2),
                                             schedule.transferDate - timedelta(1)))


class OneTimeTest(TestCase, OnceTestBase):
  def getSut(self):
    return OneTime(date(1111, 11, 11))


class TodayTest(TestCase, OnceTestBase):
  def getSut(self):
    return Today()

  def test_consistency(self):
    self.assertEqual(date.today(), Today().transferDate)


class TomorrowTest(TestCase, OnceTestBase):
  def getSut(self):
    return Tomorrow()

  def test_consistency(self):
    self.assertEqual(Today().transferDate + timedelta(1), Tomorrow().transferDate)


class AfterDaysTest(TestCase, OnceTestBase):
  def getSut(self):
    return AfterDays(2)

  def test_consistency(self):
    self.assertEqual(Today().transferDate + timedelta(2), AfterDays(2).transferDate)
    self.assertEqual(Tomorrow().transferDate + timedelta(1), AfterDays(2).transferDate)


class ThisWeekTest(TestCase, OnceTestBase):
  def getSut(self):
    return ThisWeek(SUNDAY)

  def test_transferDate(self):
    monday = date(2016, 4, 11)
    self.assertEqual(ThisWeek.transferDate(monday, MONDAY), date(2016, 4, 11))
    self.assertEqual(ThisWeek.transferDate(monday, TUESDAY), date(2016, 4, 12))
    self.assertEqual(ThisWeek.transferDate(monday, WEDNESDAY), date(2016, 4, 13))
    self.assertEqual(ThisWeek.transferDate(monday, THURSDAY), date(2016, 4, 14))
    self.assertEqual(ThisWeek.transferDate(monday, FRIDAY), date(2016, 4, 15))
    self.assertEqual(ThisWeek.transferDate(monday, SATURDAY), date(2016, 4, 16))
    self.assertEqual(ThisWeek.transferDate(monday, SUNDAY), date(2016, 4, 17))

  def test_transferDate_Error(self):
    tuesday = date(2016, 4, 12)
    self.assertRaises(ValueError, ThisWeek.transferDate, tuesday, MONDAY)


class NextWeekTest(TestCase, OnceTestBase):
  def getSut(self):
    return NextWeek(MONDAY)

  def test_transferDate(self):
    sunday = date(2016, 4, 24)
    self.assertEqual(NextWeek.transferDate(sunday, MONDAY), date(2016, 4, 25))
    self.assertEqual(NextWeek.transferDate(sunday, TUESDAY), date(2016, 4, 26))
    self.assertEqual(NextWeek.transferDate(sunday, WEDNESDAY), date(2016, 4, 27))
    self.assertEqual(NextWeek.transferDate(sunday, THURSDAY), date(2016, 4, 28))
    self.assertEqual(NextWeek.transferDate(sunday, FRIDAY), date(2016, 4, 29))
    self.assertEqual(NextWeek.transferDate(sunday, SATURDAY), date(2016, 4, 30))
    self.assertEqual(NextWeek.transferDate(sunday, SUNDAY), date(2016, 5, 1))


class EveryDayTest(TestCase):
  def test_Normalization(self):
    schedule = EveryDay()
    self.assertEquals(10, schedule.dailyPortionOf(10))
    self.assertEquals(1, schedule.dailyPortionOf(1))
    self.assertLess(schedule.dailyPortionOf(0.9), 1)
    self.assertGreater(schedule.dailyPortionOf(1.1), 1)

  def test_DatesForPeriod(self):
    schedule = EveryDay()
    self.assertEquals([date(2011, 12, 30),
                       date(2011, 12, 31),
                       date(2012, 1, 1),
                       date(2012, 1, 2)],
                      schedule.datesForPeriod(date(2011, 12, 30),
                                              date(2012, 1, 2)))


class EveryMonthTest(TestCase):
  def test_ExceptionForInvalidFiringDay(self):
    self.assertRaises(ValueError, EveryMonth, 0)
    self.assertRaises(ValueError, EveryMonth, 29)

  def test_ExceptionForInvalidInterval(self):
    schedule = EveryMonth(15)
    self.assertRaises(ValueError,
                      schedule.datesForPeriod,
                      [date(2013, 2, 10),
                       date(2012, 2, 20)],
                      [])

  def test_Normalization(self):
    schedule = EveryMonth()
    self.assertEquals(10, schedule.dailyPortionOf(300))
    self.assertEquals(1, schedule.dailyPortionOf(30))
    self.assertLess(schedule.dailyPortionOf(29), 1)
    self.assertGreater(schedule.dailyPortionOf(31), 1)

  def test_NoDateInsideInterval_0a(self):
    schedule = EveryMonth(15)
    self.assertEquals([], schedule.datesForPeriod(date(2012, 2, 10),
                                                  date(2012, 2, 14)))

  def test_NoDateInsideInterval_0b(self):
    schedule = EveryMonth(15)
    self.assertEquals([], schedule.datesForPeriod(date(2012, 2, 16),
                                                  date(2012, 2, 20)))

  def test_NoDateInsideInterval_1(self):
    schedule = EveryMonth(15)
    self.assertEquals([], schedule.datesForPeriod(date(2012, 2, 16),
                                                  date(2012, 3, 14)))

  def test_NoDateInsideInterval_2(self):
    schedule = EveryMonth(15)
    self.assertEquals([], schedule.datesForPeriod(date(2012, 12, 16),
                                                  date(2013, 1, 14)))

  def test_OneDateInsideInterval(self):
    schedule = EveryMonth(15)
    self.assertEquals([date(2012, 2, 15)],
                      schedule.datesForPeriod(date(2012, 2, 1),
                                              date(2012, 2, 28)))

  def test_OneDateAtIntervalStart(self):
    schedule = EveryMonth(15)
    self.assertEquals([date(2012, 2, 15)],
                      schedule.datesForPeriod(date(2012, 2, 15),
                                              date(2012, 2, 28)))

  def test_OneDateAtIntervalEnd(self):
    schedule = EveryMonth(15)
    self.assertEquals([date(2012, 2, 15)],
                      schedule.datesForPeriod(date(2012, 2, 1),
                                              date(2012, 2, 15)))

  def test_OneDateAtSameStartAndEndDate(self):
    schedule = EveryMonth(15)
    self.assertEquals([date(2012, 2, 15)],
                      schedule.datesForPeriod(date(2012, 2, 15),
                                              date(2012, 2, 15)))

  def test_TwoDatesInsideInterval_1(self):
    schedule = EveryMonth(15)
    self.assertEquals([date(2012, 2, 15), date(2012, 3, 15)],
                      schedule.datesForPeriod(date(2012, 2, 1),
                                              date(2012, 3, 31)))

  def test_TwoDatesInsideInterval_2(self):
    schedule = EveryMonth(15)
    self.assertEquals([date(2012, 2, 15), date(2012, 3, 15)],
                      schedule.datesForPeriod(date(2012, 2, 14),
                                              date(2012, 3, 16)))

  def test_TwoDatesInsideInterval_3(self):
    schedule = EveryMonth(15)
    self.assertEquals([date(2012, 2, 15), date(2012, 3, 15)],
                      schedule.datesForPeriod(date(2012, 1, 16),
                                              date(2012, 4, 14)))

  def test_TwoDatesAtIntervalBorders_1(self):
    schedule = EveryMonth(15)
    self.assertEquals([date(2012, 2, 15), date(2012, 3, 15)],
                      schedule.datesForPeriod(date(2012, 2, 15),
                                              date(2012, 3, 15)))

  def test_OneYearAtMiddleOfMonth(self):
    schedule = EveryMonth(15)
    self.assertEquals(12,
                      len(schedule.datesForPeriod(date(2012, 1, 1),
                                                  date(2013, 1, 1))))

  def test_OneYearAtIntervalBorders(self):
    schedule = EveryMonth(15)
    self.assertEquals(13,
                      len(schedule.datesForPeriod(date(2012, 1, 15),
                                                  date(2013, 1, 15))))

  def test_TwoYearsAtMiddleOfMonth(self):
    schedule = EveryMonth(15)
    self.assertEquals(24,
                      len(schedule.datesForPeriod(date(2012, 1, 1),
                                                  date(2014, 1, 1))))

  def test_TwoYearsAtIntervalBorders(self):
    schedule = EveryMonth(15)
    self.assertEquals(25,
                      len(schedule.datesForPeriod(date(2012, 1, 15),
                                                  date(2014, 1, 15))))



class EveryWeekTest(TestCase):
  def test_ExceptionForInvalidWeekday(self):
    self.assertRaises(ValueError, EveryWeek, 0)
    self.assertRaises(ValueError, EveryWeek, 8)

  def test_Normalization(self):
    schedule = EveryWeek()
    self.assertEquals(10, schedule.dailyPortionOf(70))
    self.assertEquals(1, schedule.dailyPortionOf(7))
    self.assertLess(schedule.dailyPortionOf(6), 1)
    self.assertGreater(schedule.dailyPortionOf(8), 1)

  def test_DatesForPeriod(self):
    schedule = EveryWeek(6)
    self.assertEquals([date(2011, 12, 24),
                       date(2011, 12, 31),
                       date(2012, 1, 7)],
                      schedule.datesForPeriod(date(2011, 12, 24),
                                              date(2012, 1, 7)))

  def test_DatesForPeriod_SameStartAndEndDate(self):
    schedule = EveryWeek(6)
    self.assertEquals([date(2011, 12, 24)],
                      schedule.datesForPeriod(date(2011, 12, 24),
                                              date(2011, 12, 24)))


class OnceInTwoWeeksTest(TestCase):
  def test_ExceptionForInvalidWeekday(self):
    self.assertRaises(ValueError, OnceInTwoWeeks, 0)
    self.assertRaises(ValueError, OnceInTwoWeeks, 8)

  def test_Normalization(self):
    schedule = OnceInTwoWeeks()
    self.assertEquals(10, schedule.dailyPortionOf(140))
    self.assertEquals(1, schedule.dailyPortionOf(14))
    self.assertLess(schedule.dailyPortionOf(13), 1)
    self.assertGreater(schedule.dailyPortionOf(15), 1)

  def test_DatesForPeriod(self):
    schedule = OnceInTwoWeeks(6)
    self.assertEquals([date(2011, 12, 24),
                       date(2012, 1, 7),
                       date(2012, 1, 21)],
                      schedule.datesForPeriod(date(2011, 12, 24),
                                              date(2012, 1, 21)))

  def test_DatesForPeriod_SameStartAndEndDate(self):
    schedule = OnceInTwoWeeks(6)
    self.assertEquals([date(2011, 12, 24)],
                      schedule.datesForPeriod(date(2011, 12, 24),
                                              date(2011, 12, 24)))


class EveryYearTest(TestCase):
  def test_Normalization(self):
    schedule = EveryYear(1, 1)
    self.assertEquals(10, schedule.dailyPortionOf(3650))
    self.assertEquals(1, schedule.dailyPortionOf(365))
    self.assertLess(schedule.dailyPortionOf(364), 1)
    self.assertGreater(schedule.dailyPortionOf(366), 1)

  def test_ValidMonthsInYear(self):
    dayInMonth = 1
    # should not raise for the months 1..12
    for monthInYear in range(1, 13):
      EveryYear(monthInYear, dayInMonth)
      # but raise for the invalid months 0 and 13
    self.assertRaises(ValueError, EveryYear, 0, dayInMonth)
    self.assertRaises(ValueError, EveryYear, 13, dayInMonth)

  def test_ValidDaysInJanuary(self):
    monthInYear = 1
    # should not raise for the valid days in this month
    for dayInMonth in range(1, 32):
      EveryYear(monthInYear, dayInMonth)
      # but raise for the invalid days in this month
    for dayInMonth in [0, 32]:
      self.assertRaises(ValueError, EveryYear, monthInYear, dayInMonth)

  def test_ValidDaysInFebruary(self):
    monthInYear = 2
    # should not raise for the valid days in this month
    for dayInMonth in range(1, 29):
      EveryYear(monthInYear, dayInMonth)
      # but raise for the invalid days in this month
    for dayInMonth in [0, 29]:
      self.assertRaises(ValueError, EveryYear, monthInYear, dayInMonth)

  def test_ValidDaysInMarch(self):
    monthInYear = 3
    # should not raise for the valid days in this month
    for dayInMonth in range(1, 32):
      EveryYear(monthInYear, dayInMonth)
      # but raise for the invalid days in this month
    for dayInMonth in [0, 32]:
      self.assertRaises(ValueError, EveryYear, monthInYear, dayInMonth)

  def test_ValidDaysInApril(self):
    monthInYear = 4
    # should not raise for the valid days in this month
    for dayInMonth in range(1, 31):
      EveryYear(monthInYear, dayInMonth)
      # but raise for the invalid days in this month
    for dayInMonth in [0, 31]:
      self.assertRaises(ValueError, EveryYear, monthInYear, dayInMonth)

  def test_ValidDaysInMai(self):
    monthInYear = 5
    # should not raise for the valid days in this month
    for dayInMonth in range(1, 31):
      EveryYear(monthInYear, dayInMonth)
      # but raise for the invalid days in this month
    for dayInMonth in [0, 32]:
      self.assertRaises(ValueError, EveryYear, monthInYear, dayInMonth)

  def test_ValidDaysInJune(self):
    monthInYear = 6
    # should not raise for the valid days in this month
    for dayInMonth in range(1, 31):
      EveryYear(monthInYear, dayInMonth)
      # but raise for the invalid days in this month
    for dayInMonth in [0, 31]:
      self.assertRaises(ValueError, EveryYear, monthInYear, dayInMonth)

  def test_ValidDaysInJuly(self):
    monthInYear = 7
    # should not raise for the valid days in this month
    for dayInMonth in range(1, 31):
      EveryYear(monthInYear, dayInMonth)
      # but raise for the invalid days in this month
    for dayInMonth in [0, 32]:
      self.assertRaises(ValueError, EveryYear, monthInYear, dayInMonth)

  def test_ValidDaysInAugust(self):
    monthInYear = 8
    # should not raise for the valid days in this month
    for dayInMonth in range(1, 31):
      EveryYear(monthInYear, dayInMonth)
      # but raise for the invalid days in this month
    for dayInMonth in [0, 32]:
      self.assertRaises(ValueError, EveryYear, monthInYear, dayInMonth)

  def test_ValidDaysInSeptember(self):
    monthInYear = 9
    # should not raise for the valid days in this month
    for dayInMonth in range(1, 31):
      EveryYear(monthInYear, dayInMonth)
      # but raise for the invalid days in this month
    for dayInMonth in [0, 31]:
      self.assertRaises(ValueError, EveryYear, monthInYear, dayInMonth)

  def test_ValidDaysInOctober(self):
    monthInYear = 10
    # should not raise for the valid days in this month
    for dayInMonth in range(1, 31):
      EveryYear(monthInYear, dayInMonth)
      # but raise for the invalid days in this month
    for dayInMonth in [0, 32]:
      self.assertRaises(ValueError, EveryYear, monthInYear, dayInMonth)

  def test_ValidDaysInNovember(self):
    monthInYear = 11
    # should not raise for the valid days in this month
    for dayInMonth in range(1, 31):
      EveryYear(monthInYear, dayInMonth)
      # but raise for the invalid days in this month
    for dayInMonth in [0, 31]:
      self.assertRaises(ValueError, EveryYear, monthInYear, dayInMonth)

  def test_ValidDaysInDecember(self):
    monthInYear = 12
    # should not raise for the valid days in this month
    for dayInMonth in range(1, 31):
      EveryYear(monthInYear, dayInMonth)
      # but raise for the invalid days in this month
    for dayInMonth in [0, 32]:
      self.assertRaises(ValueError, EveryYear, monthInYear, dayInMonth)

  def test_DatesForPeriod(self):
    schedule = EveryYear(12, 31)
    self.assertEquals([date(2011, 12, 31),
                       date(2012, 12, 31)], schedule.datesForPeriod(date(2011, 12, 24),
                                                                    date(2013, 1, 21)))


class ChangeTest(TestCase):
  def TODOtestEquals(self):
    change1 = Change('description', 100, None)
    pass

  def test_transfersForPeriod_WithoutLimits(self):
    change = Change("change", 1, EveryDay())
    self.assertEqual(1, len(change.transfersForPeriod(date(2017, 1, 1), date(2017, 1, 1))))
    self.assertEqual(2, len(change.transfersForPeriod(date(2017, 1, 1), date(2017, 1, 2))))
    self.assertEqual(31, len(change.transfersForPeriod(date(2017, 1, 1), date(2017, 1, 31))))
    self.assertEqual(2, len(change.transfersForPeriod(date(2017, 1, 31), date(2017, 2, 1))))
    self.assertEqual(32, len(change.transfersForPeriod(date(2017, 1, 1), date(2017, 2, 1))))
    self.assertRaises(ValueError, change.transfersForPeriod, date(2017, 1, 2), date(2017, 1, 1))

  def test_transfersForPeriod_ValidFrom(self):
    change = Change("change", 1, EveryDay(), goesFrom=date(2017, 1, 5))
    self.assertEqual(1, len(change.transfersForPeriod(date(2017, 1, 5), date(2017, 1, 5))))
    self.assertEqual(5, len(change.transfersForPeriod(date(2017, 1, 5), date(2017, 1, 9))))
    self.assertEqual(1, len(change.transfersForPeriod(date(2017, 1, 4), date(2017, 1, 5))))
    self.assertEqual(2, len(change.transfersForPeriod(date(2017, 1, 5), date(2017, 1, 6))))
    self.assertEqual(2, len(change.transfersForPeriod(date(2017, 1, 4), date(2017, 1, 6))))

  def test_transfersForPeriod_ValidUntil(self):
    change = Change("change", 1, EveryDay(), goesUntil=date(2017, 1, 5))
    self.assertEqual(1, len(change.transfersForPeriod(date(2017, 1, 5), date(2017, 1, 5))))
    self.assertEqual(5, len(change.transfersForPeriod(date(2017, 1, 1), date(2017, 1, 5))))
    self.assertEqual(1, len(change.transfersForPeriod(date(2017, 1, 5), date(2017, 1, 6))))
    self.assertEqual(2, len(change.transfersForPeriod(date(2017, 1, 4), date(2017, 1, 5))))
    self.assertEqual(2, len(change.transfersForPeriod(date(2017, 1, 4), date(2017, 1, 6))))

  def test_transfersForPeriod_FromUntil_0(self):
    change = Change("change", 1, EveryDay(), goesFrom=date(2017, 1, 4), goesUntil=date(2017, 1, 6))
    self.assertEqual(0, len(change.transfersForPeriod(date(2017, 1, 1), date(2017, 1, 3))))
    self.assertEqual(0, len(change.transfersForPeriod(date(2017, 1, 7), date(2017, 1, 9))))

  def test_transfersForPeriod_FromUntil_1(self):
    change = Change("change", 1, EveryDay(), goesFrom=date(2017, 1, 5), goesUntil=date(2017, 1, 5))
    self.assertEqual(1, len(change.transfersForPeriod(date(2017, 1, 5), date(2017, 1, 5))))

  def test_transfersForPeriod_FromUntil_2(self):
    change = Change("change", 1, EveryDay(), goesFrom=date(2017, 1, 4), goesUntil=date(2017, 1, 5))
    self.assertEqual(2, len(change.transfersForPeriod(date(2017, 1, 4), date(2017, 1, 5))))
    self.assertEqual(2, len(change.transfersForPeriod(date(2017, 1, 4), date(2017, 1, 6))))
    self.assertEqual(2, len(change.transfersForPeriod(date(2017, 1, 3), date(2017, 1, 6))))

  def test_transfersForPeriod_FromUntil_3(self):
    change = Change("change", 1, EveryDay(), goesFrom=date(2017, 1, 4), goesUntil=date(2017, 1, 6))
    self.assertEqual(1, len(change.transfersForPeriod(date(2017, 1, 5), date(2017, 1, 5))))
    self.assertEqual(1, len(change.transfersForPeriod(date(2017, 1, 4), date(2017, 1, 4))))
    self.assertEqual(1, len(change.transfersForPeriod(date(2017, 1, 6), date(2017, 1, 6))))
    self.assertEqual(2, len(change.transfersForPeriod(date(2017, 1, 4), date(2017, 1, 5))))
    self.assertEqual(2, len(change.transfersForPeriod(date(2017, 1, 5), date(2017, 1, 6))))
    self.assertEqual(3, len(change.transfersForPeriod(date(2017, 1, 4), date(2017, 1, 6))))
    self.assertEqual(3, len(change.transfersForPeriod(date(2017, 1, 3), date(2017, 1, 6))))
    self.assertEqual(3, len(change.transfersForPeriod(date(2017, 1, 4), date(2017, 1, 7))))
    self.assertEqual(3, len(change.transfersForPeriod(date(2017, 1, 3), date(2017, 1, 7))))





class GainTest(TestCase):
  def test_OneSalaryDuringOneMonth(self):
    gain = Gain('salary', 2000, EveryMonth(28))
    self.assertEquals([Transfer(date(2012, 1, 28), 'salary', 2000)],
                      gain.transfersForPeriod(date(2012, 1, 1),
                                              date(2012, 1, 31)))

  def test_OneSalaryDuringAlmostTwoMonths(self):
    gain = Gain('salary', 2000, EveryMonth(28))
    self.assertEquals([Transfer(date(2012, 1, 28), 'salary', 2000)],
                      gain.transfersForPeriod(date(2012, 1, 1),
                                              date(2012, 2, 27)))

  def test_TwoSalariesDuringTwoWholeMonths(self):
    gain = Gain('salary', 2000, EveryMonth(28))
    self.assertEquals([Transfer(date(2012, 2, 28), 'salary', 2000),
                       Transfer(date(2012, 3, 28), 'salary', 2000)],
                      gain.transfersForPeriod(date(2012, 2, 1),
                                              date(2012, 3, 31)))

  def test_TwoSalariesForMinimalPeriod(self):
    gain = Gain('salary', 2000, EveryMonth(28))
    self.assertEquals([Transfer(date(2012, 2, 28), 'salary', 2000),
                       Transfer(date(2012, 3, 28), 'salary', 2000)],
                      gain.transfersForPeriod(date(2012, 2, 28),
                                              date(2012, 3, 28)))

  def test_TwoSalariesForMaximalPeriod(self):
    gain = Gain('salary', 2000, EveryMonth(28))
    self.assertEquals([Transfer(date(2012, 2, 28), 'salary', 2000),
                       Transfer(date(2012, 3, 28), 'salary', 2000)],
                      gain.transfersForPeriod(date(2012, 1, 29),
                                              date(2012, 4, 27)))

  def test_DailyAverage(self):
    gain = Gain('salary', 1800, EveryMonth(28))
    self.assertEquals(60, gain.dailyAverage())


class TransferTest(TestCase):
  def test_LeapMonth_SameDate(self):
    t1 = Transfer(date(2014, 1, 1), 't1', 100)
    t2 = Transfer(date(2014, 1, 1), 't2', 100)
    self.assertFalse(Transfer.leapsMonth(t1, t2))

  def test_LeapMonth_SameMonth(self):
    t1 = Transfer(date(2014, 1, 1), 't1', 100)
    t2 = Transfer(date(2014, 1, 2), 't2', 100)
    self.assertFalse(Transfer.leapsMonth(t1, t2))

  def test_LeapMonth_WrongOrder_1(self):
    t1 = Transfer(date(2014, 1, 2), 't1', 100)
    t2 = Transfer(date(2014, 1, 1), 't2', 100)
    self.assertFalse(Transfer.leapsMonth(t1, t2))

  def test_LeapMonth_WrongOrder_2(self):
    t1 = Transfer(date(2014, 1, 1), 't1', 100)
    t2 = Transfer(date(2013, 2, 1), 't2', 100)
    self.assertFalse(Transfer.leapsMonth(t1, t2))

  def test_LeapMonth_RightOrder_1(self):
    t1 = Transfer(date(2014, 1, 1), 't1', 100)
    t2 = Transfer(date(2014, 2, 1), 't2', 100)
    self.assertTrue(Transfer.leapsMonth(t1, t2))

  def test_LeapMonth_RightOrder_2(self):
    t1 = Transfer(date(2014, 1, 31), 't1', 100)
    t2 = Transfer(date(2014, 2, 1), 't2', 100)
    self.assertTrue(Transfer.leapsMonth(t1, t2))

  def test_LeapMonth_RightOrder_3(self):
    t1 = Transfer(date(2014, 1, 31), 't1', 100)
    t2 = Transfer(date(2014, 2, 28), 't2', 100)
    self.assertTrue(Transfer.leapsMonth(t1, t2))

  def test_LeapMonth_RightOrder_4(self):
    t1 = Transfer(date(2014, 1, 1), 't1', 100)
    t2 = Transfer(date(2014, 2, 28), 't2', 100)
    self.assertTrue(Transfer.leapsMonth(t1, t2))

  def test_StringRepresentation(self):
    transfer = Transfer(date(2014, 1, 1), 'New Year', 200)
    self.assertEqual(transfer.__repr__(),
                     'Transfer(2014-01-01,New Year,200)')


class GroupTest(TestCase):
  def test_DailyAverage(self):
    group = Group('g1', [Gain('salary', 1000, EveryMonth(28)),
                         Gain('stocks', 5000, EveryMonth(1))])
    self.assertEquals(200, group.dailyAverage())


class PortfolioTest(TestCase):
  def setUp(self):
    g1 = Group('work', [Gain('salary', 2000, EveryMonth(28)),
                        Gain('lessons', 100, EveryMonth(15))])
    g2 = Group('help', [Gain('kindergeld', 300, EveryMonth(10))])
    d1 = Group('fixed', [Dump('school', 200, EveryMonth(1)),
                         Dump('rental', 600, EveryMonth(1))])
    d2 = Group('variable', [Dump('car', 400, EveryMonth(10)),
                            Dump('dope', 500, EveryMonth(20))])
    self.portfolio = Portfolio([g1, g2, d1, d2])

  def test_MonthlyGains(self):
    self.assertAlmostEquals(2400, self.portfolio.monthlyGains())

  def test_MonthlyDumps(self):
    self.assertAlmostEquals(1700, self.portfolio.monthlyDumps())

  def test_MonthlyBalance(self):
    self.assertAlmostEquals(700, self.portfolio.monthlyBalance())

  def test_TransfersForPeriod(self):
    self.assertEquals([Transfer(date(2012, 2, 1), 'rental', -600),
                       Transfer(date(2012, 2, 1), 'school', -200),
                       Transfer(date(2012, 2, 10), 'car', -400),
                       Transfer(date(2012, 2, 10), 'kindergeld', 300),
                       Transfer(date(2012, 2, 15), 'lessons', 100),
                       Transfer(date(2012, 2, 20), 'dope', -500),
                       Transfer(date(2012, 2, 28), 'salary', 2000)],
                      self.portfolio.transfersForPeriod(date(2012, 2, 1),
                                                        date(2012, 2, 28)))


class MoneySheetTest(TestCase):
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

  def test_Forecast(self):
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


class ForecastPrinterTest(TestCase):
  def setUp(self):
      self.maxDiff = None

  def test_FormattingOfMoneyValues(self):
    printer = ForecastPrinter()
    self.assertEquals('       0', printer.formatMoney(0))
    self.assertEquals(' (-) 123', printer.formatMoney(-123))
    self.assertEquals(' (+) 456', printer.formatMoney(456))

  def TODOtest_FormattingOfBallanceMoneyValues(self):
    self.assertEquals('       0', printer.formatBallance(0))
    self.assertEquals(' (-) 123', printer.formatBallance(-123))
    self.assertEquals(' (+) 456', printer.formatBallance(456))

  def test_FormattingOfForecast_1(self):
    outputFile = StringIO()
    printer = ForecastPrinter(outputFile)
    printer.printForecast(())
    self.assertEqual('', outputFile.getvalue())

  def test_FormattingOfForecast_2(self):
    outputFile = StringIO()
    printer = ForecastPrinter(outputFile)
    printer.printForecast([
      (Transfer(date(2014, 1, 2), 'Transfer-2', 100), 1100),
      (Transfer(date(2014, 1, 3), 'Transfer-3', 200), 1300)
    ])
    expectedOutput = ''
    expectedOutput += '2014-01-02     (+) 100  Transfer-2                               | (+) 1100\n'
    expectedOutput += '2014-01-03     (+) 200  Transfer-3                               | (+) 1300\n'
    self.assertEqual(expectedOutput, outputFile.getvalue())

  def test_FormattingOfForecast_3(self):
    outputFile = StringIO()
    printer = ForecastPrinter(outputFile)
    printer.printForecast([
      (Transfer(date(2014, 1, 31), 'Transfer-1', 100), 1100),
      (Transfer(date(2014, 2, 1), 'Transfer-2', 100), 1200),
    ])
    expectedOutput = ''
    expectedOutput += '2014-01-31     (+) 100  Transfer-1                               | (+) 1100\n'
    expectedOutput += '\n'
    expectedOutput += 'Sat Feb  1 00:00:00 2014\n'
    expectedOutput += '------------------------\n'
    expectedOutput += '2014-02-01     (+) 100  Transfer-2                               | (+) 1200\n'
    self.assertEqual(expectedOutput, outputFile.getvalue())

  def test_FormattingOfForecast_OverNewYear(self):
    outputFile = StringIO()
    printer = ForecastPrinter(outputFile)
    printer.printForecast([
      (Transfer(date(2016, 12, 31), 'Transfer-1', 100), 1100),
      (Transfer(date(2017, 1, 1), 'Transfer-2', 100), 1200),
    ])
    expectedOutput = ''
    expectedOutput += '2016-12-31     (+) 100  Transfer-1                               | (+) 1100\n'
    expectedOutput += '\n'
    expectedOutput += 'Sun Jan  1 00:00:00 2017\n'
    expectedOutput += '------------------------\n'
    expectedOutput += '2017-01-01     (+) 100  Transfer-2                               | (+) 1200\n'
    self.assertEqual(expectedOutput, outputFile.getvalue())


class SystemCalendarTest(TestCase):
  def test_todayDate(self):
    calendar = SystemCalendar()
    self.assertIsNotNone(calendar.todayDate())


class SheetReaderTest(TestCase):
  def test_ReadingOfMoneysheetData(self):
    expectedSheet = MoneySheet(
      22000,
      Portfolio(
        [
          Group('Red Hot Chilly Peppers',
                [
                  Gain('concert', 50000, EveryMonth()),
                  Gain('advertising', 2000, EveryWeek()),
                  Dump('equipment', 600, EveryWeek()),
                  Dump('destruction', 2000, EveryWeek()),
                ]),
          Group('Mars, Bruno',
                [
                  Gain('sales', 80000, EveryMonth()),
                  Dump('cosmetics', 2000, EveryWeek()),
                  Dump('wellness', 800, EveryWeek()),
                ]),
        ])
    )
    reader = SheetReader('test_impresario.sheet')
    actualSheet = reader.getMoneySheet()
    self.assertEquals(expectedSheet, actualSheet)


########################################################################


class ForecastRunnerTest(TestCase):
  def test_RunForOneMonth(self):
    mockReader = MockReader()
    mockPrinter = MockPrinter()
    mockCalendar = MockCalendar()
    runner = ForecastRunner(mockReader, mockPrinter, mockCalendar)
    numberOfMonths = 1
    runner.runForPeriod(numberOfMonths)
    self.assertTrue(mockPrinter.expectationsMatch)


class MockReader(object):
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


class MockPrinter(object):
  def printForecast(self, actualForecast):
    expectedForecast = (
      [
        (Transfer(date(2012, 2, 28), 'PERIOD-BEGIN', 0), 1000),
        (Transfer(date(2012, 3, 1), 'scholarship', +400), 1400),
        (Transfer(date(2012, 3, 1), 'train-card', -120), 1280),
        (Transfer(date(2012, 3, 29), 'PERIOD-END', 0), 1280),
      ])
    self.expectationsMatch = (actualForecast == expectedForecast)


class MockCalendar(object):
  def todayDate(self):
    return date(2012, 2, 28)


class ArgsParserTest(TestCase):
  def setUp(self):
    self.parser = ArgsParser()

  def test_ParseLongArguments(self):
    scriptArgs = ['--input-file', '/some/file', '--forecast-months', '5']
    self.parseAndCheck(scriptArgs)

  def test_ParseShortArguments(self):
    scriptArgs = ['-i', '/some/file', '-m', '5']
    self.parseAndCheck(scriptArgs)

  def parseAndCheck(self, scriptArgs):
    parsedArgs = self.parser.parse_args(args=scriptArgs)
    self.assertEqual('/some/file', parsedArgs.input_file)
    self.assertEqual(5, parsedArgs.forecast_months)


if __name__ == '__main__':
  main()
