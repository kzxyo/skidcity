const fetch = require('node-fetch');

module.exports = {

    get: async function (params) {

        return fetch(`https://akaneko-api.herokuapp.com/api/${params}`)
            .then(res => res.json())
            .then(json => { return json.url });

    }
}