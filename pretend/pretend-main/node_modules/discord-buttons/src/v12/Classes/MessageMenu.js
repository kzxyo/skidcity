const { MessageComponentTypes } = require('../Constants.js');
const BaseMessageComponent = require('./interfaces/BaseMessageComponent');
const { resolveMaxValues, resolveMinValues } = require('../Util');
const MessageMenuOption = require('./MessageMenuOption');

class MessageMenu extends BaseMessageComponent {
  constructor(data = {}) {
    super({ type: 'SELECT_MENU' });
    this.setup(data);
  }

  setup(data) {
    this.placeholder = 'placeholder' in data ? data.placeholder : null;

    this.max_values = ('maxValues' in data) | ('max_values' in data) ? resolveMaxValues(data.maxValues, data.max_values) : undefined;

    this.min_values = ('minValues' in data) | ('min_values' in data) ? resolveMinValues(data.minValues, data.min_values) : undefined;

    this.options = [];
    if ('option' in data) {
      data.option.type = 'SELECT_MENU_OPTION';
      this.options.push(BaseMessageComponent.create(data.option));
    }

    if ('options' in data) {
      data.options.map((c) => {
        this.options.push(new MessageMenuOption(c).toJSON());
      });
    }

    if (('id' in data && data.id) || ('custom_id' in data && data.custom_id)) this.custom_id = data.id || data.custom_id;
    else this.custom_id = undefined;

    return this;
  }

  setPlaceholder(label) {
    this.placeholder = label;
    return this;
  }

  setID(id) {
    this.custom_id = id;
    return this;
  }

  setMaxValues(number) {
    this.max_values = resolveMaxValues(number);
    return this;
  }

  setMinValues(number) {
    this.min_values = resolveMinValues(number);
    return this;
  }

  addOption(option) {
    option.type = 'SELECT_MENU_OPTION';
    this.options.push(BaseMessageComponent.create(option));
    return this;
  }

  addOptions(...options) {
    this.options.push(...options.flat(Infinity).map((c) => new MessageMenuOption(c).toJSON()));
    return this;
  }

  removeOptions(index, deleteCount, ...options) {
    this.components.splice(index, deleteCount, ...options.flat(Infinity).map((c) => new MessageMenuOption(c).toJSON()));
    return this;
  }

  toJSON() {
    return {
      type: MessageComponentTypes.SELECT_MENU,
      placeholder: this.placeholder,
      custom_id: this.custom_id,
      max_values: this.max_values,
      min_values: this.min_values,
      options: this.options,
    };
  }
}

module.exports = MessageMenu;
