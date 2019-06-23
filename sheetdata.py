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
