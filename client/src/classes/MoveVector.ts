import { LatLng } from "leaflet"

export class MoveVector {
  constructor(
    public readonly dLat = 0,
    public readonly dLng = 0,
  ) {
  }

  public static fromLatLng(start: LatLng, end: LatLng) {
    return new MoveVector(end.lat - start.lat, end.lng - start.lng)
  }

  public scale(factor: number) {
    return new MoveVector(this.dLat * factor, this.dLng * factor)
  }

  public translate(latlng: LatLng) {
    return new LatLng(latlng.lat + this.dLat, latlng.lng + this.dLng)
  }

  public get angle() {
    return Math.atan2(this.dLng, this.dLat) * 180 / Math.PI
  }
}
