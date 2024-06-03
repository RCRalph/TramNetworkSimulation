import { CircleMarker, latLng, LatLng, type Map as LeafletMap } from "leaflet"
import { Time } from "@classes/Time"
import { TramRouteIndicator } from "@classes/TramRouteIndicator"

export interface PassageStop {
  node_id: number
  name: string
  position: LatLng
  time: Time
}

export class TramPassage {
  private readonly marker: CircleMarker
  private stopIndex = 0
  private secondsLeftAtStop = 0
  private map: LeafletMap | undefined = undefined
  private tramRouteLocator: TramRouteIndicator | undefined = undefined

  constructor(
    private readonly tram_line_number: string,
    private readonly passage_id: number,
    private readonly stops: PassageStop[],
    private readonly stopDelay: number,
  ) {
    if (this.stops.length < 2) {
      throw new Error("Not enough stops")
    }

    this.marker = new CircleMarker(
      stops[0].position,
      {
        radius: 10,
        color: "red",
      },
    )

    this.marker.bindTooltip(this.tooltipText)
  }

  public setMap(map: LeafletMap) {
    this.map = map
  }

  private get tooltipText() {
    return `Line: ${this.tram_line_number}<br>Passage ID: ${this.passage_id}`
  }

  public static getPassageStopArray(arr: any[]) {
    const result: PassageStop[] = []

    for (const item of arr) {
      result.push({
        node_id: item.node_id,
        name: item.name,
        position: latLng(item.latitude, item.longitude),
        time: new Time(item.hour, item.minute, 0),
      })
    }

    return result
  }

  private removeFromMap(tramsOnMap: Set<CircleMarker>) {
    if (this.map) {
      this.marker.removeFrom(this.map)
    }

    tramsOnMap.delete(this.marker)
    this.tramRouteLocator = undefined
    this.stopIndex = 0
  }

  private addToMap(tramsOnMap: Set<CircleMarker>) {
    if (this.map) {
      this.marker.addTo(this.map)
    }

    tramsOnMap.add(this.marker)
    this.secondsLeftAtStop = this.stopDelay
    this.tramRouteLocator = new TramRouteIndicator(
      this.stops[0].node_id,
      this.stops[1].node_id,
      this.stops[1].time.seconds - this.stops[0].time.seconds - this.stopDelay,
    )
  }

  private laysOnSegment(start: LatLng, end: LatLng, point: LatLng) {
    const epsilon = 1e-9
    const triangleArea = Math.abs(start.lng * (end.lat - point.lat) + end.lng * (point.lat - start.lat) + point.lng * (start.lat - end.lat))

    return triangleArea <= epsilon &&
      Math.min(start.lat, end.lat) - epsilon <= point.lat && point.lat <= Math.max(start.lat, end.lat) + epsilon &&
      Math.min(start.lng, end.lng) - epsilon <= point.lng && point.lng <= Math.max(start.lng, end.lng) + epsilon
  }

  private canAdvance(tramsOnMap: Set<CircleMarker>) {
    if (!this.tramRouteLocator) return false

    const futureRoute = this.tramRouteLocator.getFutureRoute(10)

    for (let i = 1; i < futureRoute.length; i++) {
      for (const marker of tramsOnMap) {
        if (marker != this.marker && this.laysOnSegment(futureRoute[i - 1], futureRoute[i], marker.getLatLng())) {
          return false
        }
      }
    }

    return true
  }

  public move(time: Time, tramsOnMap: Set<CircleMarker>) {
    if (this.secondsLeftAtStop > 0) {
      this.secondsLeftAtStop--
    } else if (this.stopIndex == this.stops.length - 1) {
      this.removeFromMap(tramsOnMap)
    } else if (this.stopIndex == 0 && this.stops[this.stopIndex].time.equals(time, this.stopDelay)) {
      this.addToMap(tramsOnMap)
    } else if (this.tramRouteLocator && this.canAdvance(tramsOnMap)) {
      this.marker.setLatLng(this.tramRouteLocator.getNewTramLocation())

      if (this.tramRouteLocator.arrived) {
        this.stopIndex++
        this.secondsLeftAtStop = this.stopDelay
        this.marker.setLatLng(this.stops[this.stopIndex].position)

        if (this.stopIndex < this.stops.length - 1) {
          this.tramRouteLocator = new TramRouteIndicator(
            this.stops[this.stopIndex].node_id,
            this.stops[this.stopIndex + 1].node_id,
            this.stops[this.stopIndex + 1].time.seconds - this.stops[this.stopIndex].time.seconds - this.stopDelay,
          )
        }
      }
    }
  }
}
