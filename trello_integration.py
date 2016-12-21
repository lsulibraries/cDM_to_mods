#! usr/bin/env python3

from trello import TrelloClient
import json


"""Usage:
client = setup_client('trello_keys.json')
IslandoraETL = lookup_board(client, 'Islandora ETL')
move_card_to_target_column(IslandoraETL, 'CLF', 'Needs Troubleshooting')
make_comment(IslandoraETL, 'CLF', 'this is an interesting comment')
"""


def setup_client(keyfile):
    with open(keyfile, 'r', encoding='utf-8') as f:
        keys_text = f.read()
    keys_parsed = json.loads(keys_text)

    my_api_key = keys_parsed["api_key"]
    my_api_secret = keys_parsed["api_secret"]
    my_token = keys_parsed["token"]

    client = TrelloClient(
        api_key=my_api_key,
        api_secret=my_api_secret,
        token=my_token,
    )
    return client


def lookup_board(client, boardname):
    boards_list = [i.id for i in client.list_boards() if boardname == i.name]
    if len(boards_list) == 1:
        board_id = [i.id for i in client.list_boards() if boardname == i.name][0]
        board = client.get_board(board_id)
        return board
    return False


def move_card_to_target_column(board, alias, target_column):
    card = find_card(board, alias)
    target_column = find_column(board, target_column)
    if card and target_column:
        card.change_list(target_column.id)


def find_column(board, partial_name):
    Matching_Column = []
    for column in board.all_lists():
        if partial_name in column.name:
            Matching_Column.append(column)
    if len(Matching_Column) == 1:
        return Matching_Column[0]
    return False


def find_card(board, partial_name):
    matching_cards = [card for card in board.open_cards() if partial_name in card.name]
    if len(matching_cards) == 1:
        return matching_cards[0]
    return False
