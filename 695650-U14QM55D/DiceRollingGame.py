import smartpy as sp

class DiceRollingGame(sp.Contract):
    def __init__(self, owner):
        self.init(
            players={},
            owner=owner
        )

    @sp.entry_point
    def join_game(self, params):
        sp.verify(sp.sender == self.data.owner, "Only the owner can invite players.")
        sp.verify(params.player_address not in self.data.players, "Player already invited.")

        self.data.players[params.player_address] = sp.record(
            guess=params.guess,
            bet=params.bet
        )

    @sp.entry_point
    def roll_dice(self, params):
        sp.verify(sp.sender == self.data.owner, "Only the owner can roll the dice.")
        sp.verify(len(self.data.players) > 0, "No players have joined the game.")

        random_number = sp.random(1, 6)

        winners = [player for player in self.data.players.keys() if self.data.players[player].guess == random_number]
        total_pool = sp.as_nat(sp.sum([self.data.players[player].bet for player in winners]))

        for winner in winners:
            self.data.players[winner].bet = 0

        sp.send(self.data.owner, total_pool)

@sp.add_test(name="Test Dice Rolling Game")
def test_dice_rolling_game():
    scenario = sp.test_scenario()

    # Define test accounts
    admin = sp.test_account("Admin")
    player1 = sp.test_account("Player1")

    # Deploy the contract
    contract = DiceRollingGame(admin.address)
    scenario += contract

    # Join the game
    scenario += contract.join_game(player_address=player1.address, guess=3, bet=5).run(sender=admin)

    # Attempt to join again with the same player address
    scenario += contract.join_game(player_address=player1.address, guess=5, bet=10).run(sender=admin, valid=False)

    # Attempt to join as a non-owner
    player2 = sp.test_account("Player2")
    scenario += contract.join_game(player_address=player2.address, guess=4, bet=8).run(sender=player2, valid=False)

    # Roll the dice and distribute winnings
    scenario += contract.roll_dice().run(sender=admin)

