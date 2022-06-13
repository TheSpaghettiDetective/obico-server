from discord_webhook import DiscordWebhook, DiscordEmbed
from lib import site

# color is an integer between the values of 0 and 0xffffff'
# text is self explanatory
# image_url is the url of the image of the printer's state
def send_discord_notification(printer, text, color, webhook_url, image_url=None):
    webhook = DiscordWebhook(url=webhook_url, username="Obico")
    embed = DiscordEmbed(title=printer.name, description=text, color=color)
    if image_url:
        embed.set_image(url=image_url)
    embed.set_author(name="Printer Notification", url=site.build_full_url('/printers/'), icon_url="https://github.com/TheSpaghettiDetective/TheSpaghettiDetective/raw/master/frontend/static/img/logo-compact.png")
    embed.set_timestamp()
    embed.set_footer(text="The Obico app")
    webhook.add_embed(embed)
    webhook.execute()
