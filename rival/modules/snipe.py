import discord
from discord.utils import remove_markdown, get
from discord.embeds import Embed
from datetime import datetime
from typing import List, Optional, Union
from abc import ABC
import os
from modules.exceptions import SnipeException


class Snipe(ABC):
	"""Base class for snipes, contains a timestamp for the snipe"""

	def __init__(self):
		self._timestamp = datetime.utcnow()

	@property
	def timestamp(self):
		"""
		The timestamp of when the message was deleted

		type: datetime.datetime
		"""
		return self._timestamp


# region Message Snipe


class MessageSnipe(Snipe):
	"""Represents a deleted Message on Discord"""
	IMAGE_EXTENSIONS = (".gif", ".png", ".jpg", ".jpeg", ".webp", ".jfif", ".pjpeg", ".pjp")

	def __init__(self, sender: Union[discord.User, discord.Member], content: str, guild_id: int, channel_id: int, reference: discord.MessageReference, attachments: Optional[List[discord.Attachment]], embeds: Optional[List[discord.Embed]]):
		super().__init__()
		self._sender: discord.User = sender
		self._content = content
		self._guild_id = guild_id
		self._channel_id = channel_id
		self._reference = reference
		self._attachments = attachments
		self._embeds = embeds

	@classmethod
	def from_message(cls, msg: discord.Message):
		"""Constructs a MessageSnipe from a discord Message"""
		sender = msg.author
		content = msg.clean_content
		guild_id = msg.guild.id
		channel_id = msg.channel.id
		reference = msg.reference
		attachments = msg.attachments
		embeds = msg.embeds

		return cls(sender, content, guild_id, channel_id, reference, attachments, embeds)

	@property
	def sender(self) -> Union[discord.User, discord.Member]:
		"""The User or Member whose message was deleted
		type: discord.User OR discord.Member
		"""
		return self._sender

	@sender.setter
	def sender(self, sender):
		if isinstance(sender, (discord.User, discord.Member)):
			self._sender = sender
		else:
			raise SnipeException("Invalid user passed")

	@property
	def user(self):
		"""Alias for sender
		type: discord.User OR discord.Member
		"""
		return self.sender

	@property
	def content(self) -> str:
		"""The content of the message that was deleted, markdown removed
		type: string
		"""
		return remove_markdown(self._content)

	@property
	def guild_id(self) -> int:
		"""The id of the guild the snipe is from
		type: int
		"""
		return self._guild_id

	@property
	def channel_id(self) -> int:
		"""The id of the channel the snipe is from
		type: int
		"""
		return self._channel_id

	@property
	def reference(self) -> Optional[discord.MessageReference]:
		"""Returns the MessageReference for the Snipe.
		type: MessageReference, None
		"""
		return self._reference

	@property
	def reference_url(self) -> Optional[str]:
		"""Returns the jump url for the Snipes MessageReference.
		type: str, None
		"""
		return self._reference.jump_url

	@property
	def attachements(self) -> List[discord.Attachment]:
		"""List of attachements to the deleted message, empty if none were present
		type: List[discord.Attachment]
		"""
		return self._attachments

	@property
	def embeds(self) -> List[discord.Embed]:
		"""List of embeds to the deleted message, empty if none were present
		type: List[discord.Embed]
		"""
		return self._embeds

	@property
	def has_embeds(self) -> bool:
		"""Whether the message had embeds
		type: bool
		"""
		return len(self.embeds) > 0

	@property
	def has_attachments(self) -> bool:
		"""Whether the message had attachments
		type: bool
		"""
		return len(self.attachements) > 0

	@property
	def embed(self) -> discord.Embed:
		"""Creates the embed for this snipe
		type: discord.Embed
		"""
		embed: discord.Embed = Embed(description=self.content, color=discord.Color.random())
		discord.Color.random()
		embed.set_author(name=self.sender.display_name, icon_url=self.sender.avatar_url)
		embed.timestamp = self.timestamp  # Formatted by the discord client

		if self.reference:
			embed.description += "\n\n"
			embed.description += f"[Message Replied To]({self.reference_url} \"Message Replied To\")"

		if self.has_attachments:
			embed.description += "\n\n"
			counter = 1
			for attachement in self.attachements:
				embed.description += f"[Attachment {counter}]({attachement.url} \"{attachement.filename}\")\n"  # add a link to every attachment
				counter += 1
			for attachement in self.attachements:
				if os.path.splitext(attachement.filename)[1].lower() in MessageSnipe.IMAGE_EXTENSIONS:  # make sure it's an image
					embed.set_image(url=attachement.proxy_url)
					break  # add only the first image to the embed
		return embed
# endregion

# region EditSnipe


class EditSnipe(Snipe):
	"""Represents an edited Message on Discord"""
	IMAGE_EXTENSIONS = (".gif", ".png", ".jpg", ".jpeg", ".webp", ".jfif", ".pjpeg", ".pjp")

	def __init__(self, sender: Union[discord.User, discord.Member], before_content: str, after_content: str, guild_id: int, channel_id: int, message_id: int):
		super().__init__()
		self._sender: discord.User = sender
		self._before_content = before_content
		self._after_content = after_content
		self._guild_id = guild_id
		self._channel_id = channel_id
		self._message_id = message_id

	@classmethod
	def from_messages(cls, before: discord.Message, after: discord.Message):
		"""Constructs an EditSnipe from two discord messages.
		If the messages do not share the same id, a SnipeException is raised.
		"""
		if not before.id == after.id:
			raise SnipeException("The messages passed must be the same message.")
		sender = after.author
		before_content = before.clean_content
		after_content = after.clean_content
		guild_id = after.guild.id
		channel_id = after.channel.id
		message_id = after.id

		return cls(sender, before_content, after_content, guild_id, channel_id, message_id)

	@property
	def sender(self) -> Union[discord.User, discord.Member]:
		"""The User or Member whose message was deleted
		type: discord.User OR discord.Member
		"""
		return self._sender

	@sender.setter
	def sender(self, sender):
		if isinstance(sender, (discord.User, discord.Member)):
			self._sender = sender
		else:
			raise SnipeException("Invalid user passed.")

	@property
	def before_content(self) -> str:
		"""The content of the message that was edited before, markdown removed.
		type: string
		"""
		return remove_markdown(self._before_content)

	@property
	def after_content(self) -> str:
		"""The content of the message that was edited after, markdown removed.
		type: string
		"""
		return self._after_content

	@property
	def guild_id(self) -> int:
		"""The id of the guild the snipe is from
		type: int
		"""
		return self._guild_id

	@property
	def channel_id(self) -> int:
		"""The id of the channel the snipe is from
		type: int
		"""
		return self._channel_id

	@property
	def message_id(self) -> int:
		"""The id of the message the snipe is from
		type: int
		"""

	@property
	def embed(self) -> discord.Embed:
		"""Creates the embed for this snipe
		type: discord.Embed
		"""
		embed: discord.Embed = Embed(description=f"Changed\n\n{self.before_content}\n\nto\n\n{self.after_content}", color=discord.Color.random())
		embed.set_author(name=self.sender.display_name, icon_url=self.sender.avatar_url)
		embed.timestamp = self.timestamp

		return embed
# endregion

# region ReactionSnipe


class ReactionSnipe(Snipe):
	"""Represents a removed Reaction on Discord"""

	def __init__(self, user: Union[discord.User, discord.Member], emoji: discord.PartialEmoji,  guild_id: Optional[int], channel_id: int, message_id: int):
		super().__init__()
		self._user = user
		self._emoji = emoji
		self._guild_id = guild_id
		self._channel_id = channel_id
		self._message_id = message_id

	@classmethod
	def from_reaction_remove(cls, user: discord.User, payload: discord.RawReactionActionEvent):
		"""Constructs a ReactionSnipe from a given User and a payload.
		Raises a SnipeException if the payload is not a "REACTION_REMOVE" OR there is no guild id.
		"""
		if not payload.event_type == "REACTION_REMOVE":
			raise SnipeException("Invalid payload passed to constructor, must be a reaction remove")
		if not payload.guild_id:
			raise SnipeException("Invalid payload passed to constructor, must have a guild id")

		emoji = payload.emoji
		guild_id = payload.guild_id
		channel_id = payload.channel_id
		message_id = payload.message_id

		return cls(user, emoji, guild_id, channel_id, message_id)

	@property
	def user(self) -> Union[discord.User, discord.Member]:
		"""The user whose reaction was removed"""
		return self._user

	@user.setter
	def user(self, user):
		if isinstance(user, (discord.User, discord.Member)):
			self._user = user
		else:
			raise SnipeException("Invalid user passed.")

	@property
	def emoji(self) -> discord.PartialEmoji:
		"""The emoji that was removed"""
		return self._emoji

	@property
	def is_unicode_emoji(self) -> bool:
		"""Whether the emoji was a unicode emoji."""
		return self.emoji.is_unicode_emoji()

	@property
	def is_custom_emoji(self) -> bool:
		"""Whether the emoji was a custom one."""
		return self.emoji.is_custom_emoji()

	@property
	def is_animated_emoji(self) -> bool:
		"""Whether the emoji was animated, only applicable for custom ones"""
		if self.is_unicode_emoji:
			return False
		else:
			return self.emoji.animated

	@property
	def emoji_name(self) -> Union[str, None]:
		if self.is_custom_emoji:
			return self.emoji.name

	@property
	def guild_id(self) -> int:
		"""ID of the guild the reaction was in.
		Can be None
		"""
		return self._guild_id

	@property
	def channel_id(self) -> int:
		"""ID of the channel the reaction was in."""
		return self._channel_id

	@property
	def message_id(self) -> int:
		"""ID of the message that was reacted to."""
		return self._message_id

	@property
	def message_link(self) -> str:
		"""Link to the discord message that was reacted to.
		format: https://discord.com/channels/{guild_id}/{channel_id}/{message_id}
		"""
		return f"https://discord.com/channels/{self.guild_id}/{self.channel_id}/{self.message_id}"

	@property
	def embed(self) -> discord.Embed:
		"""Generates the embed to send
		type: discord.Embed
		"""
		embed: discord.Embed = Embed(description="", color=0x00FF77)
		embed.set_author(name=self.user.display_name, icon_url=self.user.display_avatar)
		embed.description = f"[Message Link]({self.message_link})\n"
		if self.is_unicode_emoji:
			embed.description = self.emoji.name
		if self.is_custom_emoji:
			embed.description = f"{self.emoji_name}\n[Emoji Link]({self.emoji.url} \"{self.emoji_name}\")\n"
			if self.is_animated_emoji:
				embed.set_image(url=str(self.emoji.url))  # str on an Asset returns the URL for that Asset
			else:
				embed.set_image(url=str(self.emoji.url))
		embed.timestamp = self.timestamp

		return embed
# endregion

# region Purge Snipe


class PurgeSnipe(Snipe):  # NOT FINISHED
	"""Represents a bulk delete of messages, timestamp should be a UTC timestamp"""

	def __init__(self, messages: List[discord.Message], channel_id: int):
		super().__init__()
		self._messages = messages
		self._channel_id = channel_id

	@property
	def messages(self) -> List[discord.Message]:
		"""The messages that were removed.
		type: List[discord.Message]
		"""
		return self._messages

	@property
	def channel_id(self):
		"""The channel id the messages were removed in .
		type: int
		"""
		return self.channel_id

	@property
	def timestamp(self) -> datetime:
		"""When the bot stored this information. Is a UTC datetime
		type: datetime
		"""
		return self._timestamp

	@property
	def embed(self) -> discord.Embed:
		"""Generates the embed to send
		type: discord.Embed
		"""
		embed: discord.Embed = Embed(title="Messages", color=discord.Color.random())
		embed.timestamp = self.timestamp

		for message in self.messages:
			embed.add_field(name=message.author.display_name, value=message.clean_content[:25])

		return embed

	def get_message_by_id(self, message_id: int) -> Union[discord.Message, None]:
		"""Returns the first message found in self.messages with the id passed.
		Returns None if doesn't exist.
		"""
		return get(self.messages, id=message_id)  # first Message or None

	def get_snipe_embed_by_id(self, message_id: int) -> Union[discord.Embed, None]:
		"""Converts the message with the id given to a MessageSnipe, then returns it's embed.
		Returns None if doesn't exist.
		"""
		msg = self.get_message_by_id(message_id)  # Can be none
		if msg:
			# use self.timestamp for the timestamp
			snipe_obj = MessageSnipe(msg.author, msg.content, self.timestamp, msg.guild.id, msg.channel.id, msg.attachments, msg.embeds)  # Convert to a snipe for consistency in embeds.
			return snipe_obj.embed
		else:
			return None  # Message not found

# endregion