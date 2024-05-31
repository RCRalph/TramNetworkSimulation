import { PassageStop } from "@classes/TramPassage"
import { LatLng } from "leaflet"

export class MoveVector {
  public dx = 0
  public dy = 0

  public setUsingStops(startStop: PassageStop, endStop: PassageStop, stopDelay: number) {
    const denominator = (endStop.time.seconds - startStop.time.seconds) - stopDelay

    this.dx = (endStop.position.lat - startStop.position.lat) / denominator
    this.dy = (endStop.position.lng - startStop.position.lng) / denominator
  }

  public movePosition(position: LatLng) {
    return new LatLng(position.lat + this.dx, position.lng + this.dy)
  }
}
