<template>
  <v-app>
    <v-main>
      <MapComponent
        v-if="tramStops.length && tramPassage.length"
        :tram-stops="tramStops"
        :tram-passage="tramPassage"
      ></MapComponent>
    </v-main>
  </v-app>
</template>

<script setup lang="ts">
import MapComponent from "@components/MapComponent.vue"
import { onBeforeMount, ref } from "vue"
import { type TramStop } from "@interfaces/tram_stop"
import axios from "axios"
import { LatLng, latLng } from "leaflet"

const tramStops = ref<TramStop[]>([])
const tramPassage = ref<LatLng[]>([])

async function getTramStops() {
  return axios.get("/api/stop-locations")
    .then(response => response.data)
    .then(data => {
      for (const item of data) {
        tramStops.value.push({
          node_id: item.id,
          name: item.name,
          coordinates: latLng(item.latitude, item.longitude),
        })
      }
    })
}

async function getTramPassage() {
  return axios.get("/api/tram-passage")
    .then(response => response.data)
    .then(data => {
      for (const item of data) {
        tramPassage.value.push(latLng(item.latitude, item.longitude))
      }
    })
}

onBeforeMount(async () => {
  await getTramStops()
  await getTramPassage()
})
</script>
