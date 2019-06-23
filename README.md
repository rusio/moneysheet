Money Sheet
===========

A command-line tool for keeping track of personal finances and projecting
them *over time*. The money sheet simulates how much money you would have
in the near future. It sums your recurring expenses and income over time
and computes how your balance would change over time.

It is useful to gain a quick overview over your various personal
spendings (where and when does my money go). Most importantly, it helps
to see if and when your balance would drop below zero.


Entering Money Data
===================

You can enter your cash spendings in the file `sheetdata.py`, which is located
in the application directory.

Example:

    from moneysheet import *

    MoneySheet(
      300,  # my initial balance
      Portfolio(
        [
          Group('Fixed Gains',
                [
                  Gain('Salary at Work', 600, EveryMonth(28)),
                  Gain('Scholarship', 50, EveryMonth(9)),
                ]),
          Group('Variable Gains',
                [
                  Gain('Second Job', 120, EveryWeek()),
                ]),
          Group('Fixed Dumps',
                [
                  Dump('Rental', 800, EveryMonth(1)),
                  Dump('University', 300, EveryMonth(20)),
                ]),
          Group('Variable Dumps',
                [
                  Dump('Telephone', 30, EveryMonth(10)),
                  Dump('Food', 50, EveryWeek(6)),
                ]),
        ])
    )


Gains and Dumps
===============

The basic elements are `Gain` for incomes and `Dump` for expenses,
which either happen once or on a *periodic basis*. Each of these changes
is specified by a description, the amount of money that changes and
its time schedule.

For example: `Dump('Rental', 300, EveryMonth(1))` means that you have
a periodic expense called 'Rental' which amounts to 300 Euros/Dollars
and it is payed at the first day of the month.

Periodic Schedules
==================

These predefined *periodic* schedules for money transfers are available:

- EveryMonth: For something that happens periodically every month.
- EveryWeek: For something that happens periodically every week.
- EveryDay: For something that happens every day.
- OnceInTwoWeeks: For something that happens once in two weeks.
- EveryYear: For something that happens periodically every year.

There are also *one-time* schedules money transfers for special situations:

- OneTime: A one-time money transfer on a fixed date in the future.
- Today: A one-time transfer that is supposed to happen today.
- Tomorrow: A one-time transfer that is supposed to happen tomorrow.
- AfterDays: A one-time transfer that is supposed to happen after N days.
- ThisWeek: A one-time transfer that is supposed to happen this week.
- NextWeek: A one-time transfer that is supposed to happen next week.


Grouping Changes
================

The `Gain`s and `Dump`s can be put together in arbitrary groups for
a better overview.

One simple way is to group your expenses by their 'fixed costs' or
'variable costs' aspect. This is fast and easy to start with.

    Group('Fixed Costs',
          [
            Dump('House: Rental', 800, EveryMonth(1)),
            Dump('Sports: Membership', 60, EveryMonth(1)),
          ]),
    Group('Variable Costs',
          [
            Dump('House: Food', 60, EveryWeek(5)),
            Dump('Sports: Suppelements', 20, EveryWeek(6)),
          ]),

A slightly better way is to group changes that are related together by
their topic. For example you could have the groups 'House', 'Car' and
'Sports':

    Group('House',
          [
            Dump('House: Rental', 800, EveryMonth(1)),
            Dump('House: Food', 60, EveryWeek(1)),
          ]),
    Group('Sports',
          [
            Dump('Sports: Membership', 60, EveryMonth(1)),
            Dump('Sports: Food', 50, EveryWeek(1)),
            Dump('Sports: Suppelements', 20, EveryWeek(1)),
            Gain('Sports: Private Lessons', 20, EveryWeek(1)),
          ]),

Here we group under 'House' everything related to our house together and
nothing else. Same for our sports activity - our fixed costs for monthly
membership, our variable costs for food and supplements and our income from
private lessons (assuming we were teaching).


How to Run the Forecast
=======================

    # Running with Default Settings
    ./forecast.sh

    # To See a Forecast for 3 Months (default)
    python3 moneysheet.py

    # To Look One Year Ahead
    python3 moneysheet.py --forecast-months 12

    # To Use Another Data File
    python3 moneysheet.py --input-file another-file.py


What You Should See
===================

    2019-06-23           0  PERIOD-BEGIN                             |  (+) 300
    2019-06-24     (+) 120  Second Job                               |  (+) 420
    2019-06-28     (+) 600  Salary at Work                           | (+) 1020
    2019-06-29      (-) 50  Food                                     |  (+) 970

    Mon Jul  1 00:00:00 2019
    ------------------------
    2019-07-01     (-) 800  Rental                                   |  (+) 170
    2019-07-01     (+) 120  Second Job                               |  (+) 290
    2019-07-06      (-) 50  Food                                     |  (+) 240
    2019-07-08     (+) 120  Second Job                               |  (+) 360
    2019-07-09      (+) 50  Scholarship                              |  (+) 410
    2019-07-10      (-) 30  Telephone                                |  (+) 380
    2019-07-13      (-) 50  Food                                     |  (+) 330
    2019-07-15     (+) 120  Second Job                               |  (+) 450
    2019-07-20      (-) 50  Food                                     |  (+) 400
    2019-07-20     (-) 300  University                               |  (+) 100
    2019-07-22     (+) 120  Second Job                               |  (+) 220
    2019-07-27      (-) 50  Food                                     |  (+) 170
    2019-07-28     (+) 600  Salary at Work                           |  (+) 770
    2019-07-29     (+) 120  Second Job                               |  (+) 890

    Thu Aug  1 00:00:00 2019
    ------------------------
    2019-08-01     (-) 800  Rental                                   |   (+) 90
    2019-08-03      (-) 50  Food                                     |   (+) 40
    2019-08-05     (+) 120  Second Job                               |  (+) 160
    2019-08-09      (+) 50  Scholarship                              |  (+) 210
    2019-08-10      (-) 50  Food                                     |  (+) 160
    2019-08-10      (-) 30  Telephone                                |  (+) 130
    2019-08-12     (+) 120  Second Job                               |  (+) 250
    2019-08-17      (-) 50  Food                                     |  (+) 200
    2019-08-19     (+) 120  Second Job                               |  (+) 320
    2019-08-20     (-) 300  University                               |   (+) 20
    2019-08-24      (-) 50  Food                                     |   (-) 30
    2019-08-26     (+) 120  Second Job                               |   (+) 90
    2019-08-28     (+) 600  Salary at Work                           |  (+) 690
    2019-08-31      (-) 50  Food                                     |  (+) 640

    Sun Sep  1 00:00:00 2019
    ------------------------
    2019-09-01     (-) 800  Rental                                   |  (-) 160
    2019-09-02     (+) 120  Second Job                               |   (-) 40
    2019-09-07      (-) 50  Food                                     |   (-) 90
    2019-09-09      (+) 50  Scholarship                              |   (-) 40
    2019-09-09     (+) 120  Second Job                               |   (+) 80
    2019-09-10      (-) 30  Telephone                                |   (+) 50
    2019-09-14      (-) 50  Food                                     |        0
    2019-09-16     (+) 120  Second Job                               |  (+) 120
    2019-09-20     (-) 300  University                               |  (-) 180
    2019-09-21      (-) 50  Food                                     |  (-) 230
    2019-09-21           0  PERIOD-END                               |  (-) 230


The last column denotes your projected balance at the point in time.
The example forecast above denotes, that you would probably have a small
shortage in August and another problem in September.
