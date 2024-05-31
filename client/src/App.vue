<template>
  <v-app>
    <v-main>
      <MapComponent
        v-if="tramStops.length && tramPassages.length && time"
        v-model:time="time"
        :tram-stops="tramStops"
        :tram-passages="tramPassages"
      ></MapComponent>
    </v-main>
  </v-app>
</template>

<script setup lang="ts">
import MapComponent from "@components/MapComponent.vue"
import { onMounted, Ref, ref } from "vue"
import { type TramStop } from "@interfaces/TramStop"
import axios from "axios"
import { latLng } from "leaflet"
import { TramPassage } from "@classes/TramPassage"
import { Time } from "@classes/Time"

const tramStops = ref<TramStop[]>([])
const tramPassages: Ref<TramPassage[]> = ref([])
const time = ref<Time>()

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
  return axios.get("/api/tram-passages")
    .then(response => response.data)
    .then(data => {
      for (const item of data) {
        const stops = TramPassage.getPassageStopArray(item.stops)

        if (!time.value || time.value.isLaterThan(stops[0].time)) {
          time.value = stops[0].time.clone()
        }

        tramPassages.value.push(new TramPassage(
          item.tram_line,
          item.passage_id,
          stops,
          15,
        ))
      }
    })
}

onMounted(async () => {
  await getTramStops()
  await getTramPassage()
})
</script>
