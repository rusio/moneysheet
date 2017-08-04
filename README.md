Money Sheet
===========

The "money sheet" forecasts how much money you would have in the near
future. It sums up your incomes and expenses and computes how your
balance would change over time.

It is useful to gain a quick overview over your various personal
spendings (where and when does my money go) and helps to see if
your balance would drop below zero.


Setting up Cash Data
====================

Enter your cash spendings in the file `sheetdata.py`. Example:

    from moneysheet import *

    MoneySheet(
      300,  # my initial balance
      Portfolio(
        [
          Group('Fixed Gains',
                [
                  Gain('salary at work', 400, EveryMonth(28)),
                  Gain('scholarship', 150, EveryMonth(9)),
                ]),
          Group('Variable Gains',
                [
                  Gain('second job', 50, EveryWeek()),
                ]),
          Group('Fixed Dumps',
                [
                  Dump('rental', 300, EveryMonth(1)),
                  Dump('university', 100, EveryMonth(20)),
                ]),
          Group('Variable Dumps',
                [
                  Dump('telephone', 30, EveryMonth(10)),
                  Dump('food', 50, EveryWeek(6)),
                ]),
        ])
    )


How to Run the Forecast
=======================

    # To Show a Three Month Forecast
    python3 moneysheet.py

    # To Look One Year Ahead
    python3 moneysheet.py --forecast-months 12 | less

    # To Use Another Data File
    python3 moneysheet.py --input-file another-file.py


What You Should See
===================

    2017-08-04           0  PERIOD-BEGIN                             |  (+) 300
    2017-08-05      (-) 50  food                                     |  (+) 250
    2017-08-07      (+) 50  second job                               |  (+) 300
    2017-08-09     (+) 150  scholarship                              |  (+) 450
    2017-08-10      (-) 30  telephone                                |  (+) 420
    2017-08-12      (-) 50  food                                     |  (+) 370
    2017-08-14      (+) 50  second job                               |  (+) 420
    2017-08-19      (-) 50  food                                     |  (+) 370
    2017-08-20     (-) 100  university                               |  (+) 270
    2017-08-21      (+) 50  second job                               |  (+) 320
    2017-08-26      (-) 50  food                                     |  (+) 270
    2017-08-28     (+) 400  salary at work                           |  (+) 670
    2017-08-28      (+) 50  second job                               |  (+) 720

    Fri Sep  1 00:00:00 2017
    ------------------------
    2017-09-01     (-) 300  rental                                   |  (+) 420
    2017-09-02      (-) 50  food                                     |  (+) 370
    2017-09-04      (+) 50  second job                               |  (+) 420
    2017-09-09      (-) 50  food                                     |  (+) 370
    2017-09-09     (+) 150  scholarship                              |  (+) 520

