from dbot.extensions import get_current_bot, bot
class TestBot:
    def load_extensions(self, testb):
        print(get_current_bot())
        print(bot)


b = TestBot()
b.load_extensions(2)
