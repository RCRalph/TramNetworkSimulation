import { LatLng } from "leaflet"

interface TramStop {
  node_id: number,
  name: string,
  coordinates: LatLng
}

export type {
  TramStop,
}
