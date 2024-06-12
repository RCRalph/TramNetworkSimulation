import { LatLng } from "leaflet"

export interface TramStop {
  node_id: number,
  name: string,
  coordinates: LatLng
}
