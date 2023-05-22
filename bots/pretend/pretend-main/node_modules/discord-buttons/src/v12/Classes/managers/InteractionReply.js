const { InteractionReplyTypes } = require('../../Constants');
const { sendAPICallback } = require('../APIMessage');

class InteractionReply {
  constructor(client, component, webhook) {
    this.client = client;

    this.component = component;

    this.webhook = webhook;

    this.has = false;

    this.isEphemeral = undefined;
  }

  async send(content, options) {
    if (this.has) throw new Error('BUTTON_ALREADY_REPLIED: This button already has a reply');

    if (options === null && options !== undefined) options = { components: null };

    if (typeof options === 'boolean' && options === true) options = { flags: 1 << 6 };

    let apiMessage;
    if (content instanceof sendAPICallback) {
      apiMessage = content.resolveData();
    } else {
      apiMessage = sendAPICallback.create(this, content, options).resolveData();
    }

    if (Array.isArray(apiMessage.data.content)) {
      apiMessage.data.content = apiMessage.data.content[0];
    }

    const { data, files } = await apiMessage.resolveFiles();

    if (data.flags === 1 << 6) this.isEphemeral = true;

    await this.client.api.interactions(this.component.discordID, this.component.token).callback.post({
      data: {
        data: data,
        type: InteractionReplyTypes.CHANNEL_MESSAGE_WITH_SOURCE,
      },
      files,
    });
    this.has = true;
    return this;
  }

  async edit(content, options) {
    if (!this.has) throw new Error('BUTTON_HAS_NO_REPLY: This button has no reply');

    if (options === null && options !== undefined) options = { components: null };

    return await this.webhook.editMessage('@original', content, options);
  }

  async defer(ephemeral = false) {
    if (this.has) throw new Error('BUTTON_ALREADY_REPLIED: This button already has a reply');

    if (ephemeral) this.isEphemeral = true;

    await this.client.api.interactions(this.component.discordID, this.component.token).callback.post({
      data: {
        data: {
          flags: ephemeral ? 1 << 6 : null,
        },
        type: InteractionReplyTypes.DEFFERED_UPDATE_MESSAGE,
      },
    });
    this.has = true;
    return this;
  }

  async think(ephemeral = false) {
    if (this.has) throw new Error('BUTTON_ALREADY_REPLIED: This button already has a reply');

    if (ephemeral) this.isEphemeral = true;

    await this.client.api.interactions(this.component.discordID, this.component.token).callback.post({
      data: {
        data: {
          flags: ephemeral ? 1 << 6 : null,
        },
        type: InteractionReplyTypes.DEFFERED_CHANNEL_MESSAGE_WITH_SOURCE,
      },
    });
    this.has = true;
    return this;
  }

  async fetch() {
    if (this.isEphemeral) throw new Error('REPLY_EPHEMERAL: The reply for this button is ephemeral');
    return await this.webhook.fetchMessage('@original');
  }

  async delete() {
    if (!this.has) throw new Error('BUTTON_HAS_NO_REPLY: This button has no reply');
    if (this.isEphemeral) throw new Error('REPLY_EPHEMERAL: The reply for this button is ephemeral');
    return await this.webhook.deleteMessage('@original');
  }
}

module.exports = InteractionReply;
