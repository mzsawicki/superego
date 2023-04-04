from superego.game.game import Card, Deck

demo_deck = Deck(
    name='Test Deck',
    cards=[
        Card(
            question='W środku nocy budzi cię głośna muzyka dobiegająca od sąsiada. Co robisz?',
            answer_A='Idę zwrócić mu uwagę',
            answer_B='Dzwonię na policję',
            answer_C='Staram się zasnąć'
        ),
        Card(
            question='Czy zabierasz autostopowiczów?',
            answer_A='Zawsze',
            answer_B='Czasami',
            answer_C='Rzadko lub nigdy'
        ),
        Card(
            question='W którym z miast chciałbyś / chciałabyś spędzić resztę życia?',
            answer_A='Lizbona',
            answer_B='Nowy Jork',
            answer_C='Rio de Janeiro'
        ),
    ]
)