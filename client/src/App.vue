<template>
  <v-app>
    <v-main v-if="ready">
      <HeaderComponent
        v-model:running="running"
        v-model:loading="loading"
        v-model:day-type="dayType"
        v-model:disable-changes="disableChanges"
        :time="time as Time"
        :day-types="dayTypes"
        @reset="resetTramPassages"
      ></HeaderComponent>

      <MapComponent
        v-model:time="time as Time"
        :tram-stops="tramStops"
        :tram-passages="tramPassages as TramPassage[]"
        :running="running"
        :timeout="timeout"
        :block-time="nodeBlocking"
        :check-time="nodeChecking"
      ></MapComponent>

      <FooterComponent
        v-model:timeout="timeout"
        v-model:node-blocking="nodeBlocking"
        v-model:node-checking="nodeChecking"
        :disable-changes="disableChanges"
      ></FooterComponent>
    </v-main>

    <v-overlay
      v-else
      :model-value="true"
      opacity="0"
      class="d-flex justify-center align-center"
    >
      <v-progress-circular
        indeterminate
        size="128"
      ></v-progress-circular>
    </v-overlay>
  </v-app>
</template>

<script setup lang="ts">
import axios from "axios"
import { onMounted, ref, watch } from "vue"
import { LatLng, latLng } from "leaflet"

import MapComponent from "@components/MapComponent.vue"
import HeaderComponent from "@components/HeaderComponent.vue"
import FooterComponent from "@components/FooterComponent.vue"

import { TramStop } from "@interfaces/TramStop"
import { GlobalSettings, TramPassages } from "@interfaces/API"

import { TramPassage } from "@classes/TramPassage"
import { Time } from "@classes/Time"
import { TramRouteIndicator } from "@classes/TramRouteIndicator"
import { AdvancementOracle } from "@classes/AdvancementOracle"

const ready = ref(false)
const loading = ref(false)

const time = ref(new Time())

const timeout = ref(10)
const nodeBlocking = ref(5)
const nodeChecking = ref(10)
const disableChanges = ref(false)

const running = ref(false)
const dayType = ref("")

const tramStops: TramStop[] = []
const dayTypes: string[] = []

function useTramPassages() {
  let initialTime = new Time()
  const advancementOracle = new AdvancementOracle()

  const tramPassages = ref<TramPassage[]>([])

  async function setTramPassages() {
    return axios.get(`/api/tram-passages/${dayType.value}`)
      .then(response => response.data)
      .then((data: TramPassages[]) => {
        for (const item of data) {
          const stops = TramPassage.getPassageStopArray(item.stops)

          if (!initialTime.seconds || initialTime.isLaterThan(stops[0].time)) {
            initialTime = stops[0].time.clone()
          }

          tramPassages.value.push(new TramPassage(
            item.tram_line,
            item.passage_id,
            stops,
            advancementOracle,
          ))
        }

        time.value = initialTime.subtractMinute().clone()
      })
  }

  function resetTramPassages() {
    time.value = initialTime.clone()
    tramPassages.value.forEach(item => item.reset())
  }

  watch(dayType, async () => {
    if (!ready.value) return

    loading.value = true
    running.value = false

    resetTramPassages()
    initialTime = new Time().subtractMinute()
    tramPassages.value = []

    setTramPassages().then(() => loading.value = false)
  })

  return {setTramPassages, resetTramPassages, tramPassages}
}

const {setTramPassages, resetTramPassages, tramPassages} = useTramPassages()

onMounted(() => {
  axios.get("/api/global-settings")
    .then(response => response.data)
    .then((data: GlobalSettings) => {
      if (!data.day_types.length) {
        throw new Error("Invalid day types")
      }

      for (const item of data.day_types) {
        dayTypes.push(item)
      }

      dayType.value = dayTypes[0]

      for (const item of data.stop_locations) {
        tramStops.push({
          node_id: item.id,
          name: item.name,
          coordinates: latLng(item.latitude, item.longitude),
        })
      }

      for (const [startNode, endNodes] of Object.entries(data.tram_routes)) {
        for (const [endNode, route] of Object.entries(endNodes)) {
          TramRouteIndicator.addRoute(
            Number(startNode),
            Number(endNode),
            route.map(item => ({
              coordinates: new LatLng(item.latitude, item.longitude),
              distance: item.distance,
            })),
          )
        }
      }
    })
    .then(setTramPassages)
    .then(() => new Promise(resolve => setTimeout(resolve, 10000)))
    .then(() => ready.value = true)
})
</script>

<style>
@import url('https://fonts.googleapis.com/css2?family=Archivo+Black&display=swap');

.leaflet-tooltip.line-number-label {
  font-family: "Archivo Black", sans-serif;
  font-weight: 400;
  font-style: normal;
  color: black;
  font-size: 12px;

  background-color: transparent;
  border: transparent;
  box-shadow: none;
}
</style>
