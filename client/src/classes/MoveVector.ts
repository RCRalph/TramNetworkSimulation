import { LatLng } from "leaflet"

export class MoveVector {
  public dLat = 0
  public dLng = 0

  public setUsingCoordinates(start: LatLng, end: LatLng) {
    this.dLat = end.lat - start.lat
    this.dLng = end.lng - start.lng

    return this
  }

  public scale(factor: number) {
    this.dLat *= factor
    this.dLng *= factor

    return this
  }

  public movePosition(position: LatLng) {
    return new LatLng(position.lat + this.dLat, position.lng + this.dLng)
  }
}
