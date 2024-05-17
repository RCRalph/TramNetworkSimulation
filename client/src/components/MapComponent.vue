<script setup lang="ts">
import {
  CircleMarker,
  LatLng,
  latLng,
  latLngBounds,
  map as leafletMapConstructor,
  Map as LeafletMap,
  tileLayer,
} from "leaflet"
import { onMounted } from "vue"
import { TramStop } from "@interfaces/tram_stop"

const props = defineProps<{
  tramStops: TramStop[],
  tramPassage: LatLng[]
}>()

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

  const leafletMap = leafletMapConstructor("map", {
    maxBounds: mapCenter.pad(1),
    center: mapCenter.getCenter(),
    zoom: 13,
  })

  tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 19,
    attribution: "&copy; <a href=\"https://www.openstreetmap.org/copyright\">OpenStreetMap</a>",
  }).addTo(leafletMap)

  return leafletMap
}

function placeTramStops(leaflet: LeafletMap) {
  for (const stop of props.tramStops) {
    new CircleMarker(
      stop.coordinates,
      {
        radius: 5,
        fill: true,
      },
    ).addTo(leaflet)
  }
}

async function runTramPassage(leaflet: LeafletMap) {
  const marker = new CircleMarker(
    props.tramPassage[0],
    {
      radius: 10,
      color: "red",
    },
  ).addTo(leaflet)

  for (const [i, item] of props.tramPassage.entries()) {
    setTimeout(() => marker.setLatLng(item), 1000 * i)
  }
}

onMounted(() => {
  const leaflet = prepareMap()

  placeTramStops(leaflet)
  runTramPassage(leaflet)
})
</script>

<template>
  <div id="map"></div>
</template>

<style scoped>
#map {
  width: 100%;
  height: 100%;
}
</style>
