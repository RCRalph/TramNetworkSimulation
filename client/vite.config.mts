// Plugins
import Components from "unplugin-vue-components/vite"
import Vue from "@vitejs/plugin-vue"
import Vuetify, { transformAssetUrls } from "vite-plugin-vuetify"
import ViteFonts from "unplugin-fonts/vite"

// Utilities
import { defineConfig } from "vite"

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    Vue({
      template: {transformAssetUrls},
    }),
    // https://github.com/vuetifyjs/vuetify-loader/tree/master/packages/vite-plugin#readme
    Vuetify(),
    Components(),
    ViteFonts({
      google: {
        families: [{
          name: "Roboto",
          styles: "wght@100;300;400;500;700;900",
        }],
      },
    }),
  ],
  define: {"process.env": {}},
  resolve: {
    alias: {
      "@components": "/src/components",
      "@interfaces": "/src/interfaces",
    },
    extensions: [
      ".js",
      ".json",
      ".jsx",
      ".mjs",
      ".ts",
      ".tsx",
      ".vue",
    ],
  },
  server: {
    proxy: {
      "/api/": {
        target: "http://127.0.0.1:5000",
      },
    },
  },
})
