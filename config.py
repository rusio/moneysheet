# from moneysheet import *

MoneySheet(
  300, # initial balance
  Portfolio(
    [
      Group('Fixed Gains',
            [
              Gain('salary', 400, EveryMonth(28)),
              Gain('scholarship', 150, EveryMonth(9)),
              Gain('parents', 100, EveryMonth(5)),
            ]),

      Group('Variable Gains',
            [
              Gain('nachhilfe', 50, EveryWeek()),
            ]),

      Group('Fixed Costs',
            [
              Dump('rental', 300, EveryMonth(1)),
              Dump('insurance', 65, EveryMonth(1)),
              Dump('university', 100, EveryMonth(20)),
              Dump('kvv', 50, EveryMonth(5)),
            ]),

      Group('Variable Costs',
            [
              Dump('telephone', 30, EveryMonth(10)),
              Dump('food for home', 50, EveryWeek(6)),
              Dump('food outside', 20, EveryWeek(3)),
              Dump('beer outside', 10, EveryWeek(5)),
            ]),

    ])
)

