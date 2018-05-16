'use strict'
const merge = require('webpack-merge')
const devEnv = require('./dev.env')

module.exports = merge(devEnv, {
  NODE_ENV: '"testing"',
  API_ADDR: '"http://localhost:5000/image_labeler/api/v1.0"'
})
