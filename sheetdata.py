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

