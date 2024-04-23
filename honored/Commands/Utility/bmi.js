const { MessageEmbed } = require("discord.js");
const { displayCommandInfo } = require("/root/rewrite/Utils/command.js");

module.exports = {
    configuration: {
        commandName: 'bmi',
        aliases: ['none'],
        description: 'Shows the body mass index (BMI)',
        module: 'utility',
        syntax: 'bmi <height> <weight>',
        example: 'bmi 5\'11 180',
        parameters: 'height weight'
    },

    run: async (session, message, args) => {
        
        if (args.length !== 2) {
            return displayCommandInfo(module.exports, session, message);
        }

        const height = args[0];
        const weight = args[1];

        const heightMatch = height.match(/^(\d+)'(\d+)$/);
        if (!heightMatch) {
            console.log("Invalid height format");
            return displayCommandInfo(module.exports, session, message);
        }

        const feet = parseInt(heightMatch[1]);
        const inches = parseInt(heightMatch[2]);

        const heightInInches = feet * 12 + inches;
        const heightInMeters = heightInInches * 0.0254;

        const weightInPounds = parseFloat(weight);

        if (isNaN(heightInMeters) || isNaN(weightInPounds)) {
            console.log("Invalid height or weight value");
            return displayCommandInfo(module.exports, session, message);
        }

        const bmi = 703 * (weightInPounds / (heightInInches * heightInInches));

        let category;
        if (bmi < 16) {
            category = 'Severe Thinness';
        } else if (bmi >= 16 && bmi < 17) {
            category = 'Moderate Thinness';
        } else if (bmi >= 17 && bmi < 18.5) {
            category = 'Mild Thinness';
        } else if (bmi >= 18.5 && bmi < 25) {
            category = 'Normal';
        } else if (bmi >= 25 && bmi < 30) {
            category = 'Overweight';
        } else if (bmi >= 30 && bmi < 35) {
            category = 'Obese Class I';
        } else if (bmi >= 35 && bmi < 40) {
            category = 'Obese Class II';
        } else {
            category = 'Obese Class III';
        }

        message.channel.send({ embeds: [
            new MessageEmbed()
            .setColor(session.color)
            .setDescription(`:man_lifting_weights: ${message.author}: Your body mass index is ${bmi.toFixed(2)} and your weight class is ${category}`)
        ]});
    }
}
