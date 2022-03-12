from superego.game.game import Card, Deck

test_deck = Deck(
    name='Test Deck',
    cards=[
        Card(
            question='Which color do you like the most?',
            answer_A='Blue',
            answer_B='Red',
            answer_C='Green'
        ),
        Card(
            question='Which animals do you like the most?',
            answer_A='Dogs',
            answer_B='Cats',
            answer_C='Rabbits'
        ),
        Card(
            question='Which music genre do you like the most?',
            answer_A='Rock/Metal',
            answer_B='Pop/Dance',
            answer_C='Classical'
        ),
        Card(
            question='What would be your choice for your spare time?',
            answer_A='Movie',
            answer_B='Computer game',
            answer_C='Book'
        ),
        Card(
            question='Which fruit do you like the most?',
            answer_A='Apples',
            answer_B='Oranges',
            answer_C='Bananas'
        ),
        Card(
            question='Which color do you like the most?',
            answer_A='Blue',
            answer_B='Red',
            answer_C='Green'
        ),
        Card(
            question='Which movie genre do you like the most?',
            answer_A='Horror',
            answer_B='Criminal',
            answer_C='Comedy'
        ),
        Card(
            question='You consider yourself...',
            answer_A='Introvert',
            answer_B='Extravert',
            answer_C='Ambivert'
        ),
        Card(
            question='Which musical instrument do you like the most?',
            answer_A='Guitar',
            answer_B='Piano',
            answer_C='Saxophone'
        ),
        Card(
            question='Which of communicators do you use the most often?',
            answer_A='Messenger',
            answer_B='Discord',
            answer_C='Telegram'
        ),
    ]
)