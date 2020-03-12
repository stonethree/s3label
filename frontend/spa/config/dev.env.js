'use strict'
const merge = require('webpack-merge')
const prodEnv = require('./prod.env')

module.exports = merge(prodEnv, {
  NODE_ENV: '"development"',
  API_ADDR: '"http://13.69.78.115:5000/image_labeler/api/v1.0"'
})
