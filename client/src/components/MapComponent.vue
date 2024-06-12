<script setup lang="ts">
import {
  CircleMarker,
  latLng,
  latLngBounds,
  map as leafletMapConstructor,
  Map as LeafletMap,
  tileLayer,
} from "leaflet"
import { onMounted, ref } from "vue"
import { TramStop } from "@interfaces/TramStop"
import { TramPassage } from "@classes/TramPassage"
import { Time } from "@classes/Time"

const props = defineProps<{
  tramStops: TramStop[],
  tramPassages: TramPassage[],
  running: boolean,
  timeout: number
}>()

const time = defineModel<Time>("time", {required: true})

const leafletMap = ref<LeafletMap>()

function getMapCenter() {
  return latLngBounds(
    latLng(
      Math.min(...props.tramStops.map(item => item.coordinates.lat)),
      Math.min(...props.tramStops.map(item => item.coordinates.lng)),
    ),
    latLng(
      Math.max(...props.tramStops.map(item => item.coordinates.lat)),
      Math.max(...props.tramStops.map(item => item.coordinates.lng)),
    ),
  )
}

function prepareMap() {
  const mapCenter = getMapCenter()

  leafletMap.value = leafletMapConstructor("map", {
    maxBounds: mapCenter.pad(1),
    center: mapCenter.getCenter(),
    zoom: 13,
  })

  tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 19,
    attribution: "&copy; <a href=\"https://www.openstreetmap.org/copyright\">OpenStreetMap</a>",
  }).addTo(leafletMap.value)
}

function placeTramStops() {
  if (!leafletMap.value) {
    throw new Error("Map not initialized")
  }

  for (const stop of props.tramStops) {
    new CircleMarker(
      stop.coordinates,
      {
        radius: 5,
        fill: true,
      },
    ).addTo(leafletMap.value)
  }
}

onMounted(async () => {
  prepareMap()
  placeTramStops()

  while (true) {
    while (!leafletMap.value) {
      await new Promise(resolve => setTimeout(resolve, 10))
    }

    while (!props.running) {
      await new Promise(resolve => setTimeout(resolve, 10))
    }

    for (const item of props.tramPassages) {
      item.setMap(leafletMap.value)
    }

    while (props.running) {
      for (const item of props.tramPassages) {
        item.move(time.value)
      }

      time.value.advance()
      await new Promise(resolve => setTimeout(resolve, props.timeout))
    }
  }
})
</script>

<template>
  <div id="map"></div>
</template>

<style scoped>
#map {
  width: 100%;
  height: calc(100vh - 64px);
}
</style>
