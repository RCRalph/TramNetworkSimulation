import { CircleMarker, latLng, LatLng, type Map as LeafletMap } from "leaflet"
import { Time } from "@classes/Time"
import { TramRouteLocator } from "@classes/TramRouteLocator"

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
  private tramRouteLocator: TramRouteLocator | undefined = undefined

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

    this.marker.bindTooltip(this.getTooltipText())
  }

  private getTooltipText() {
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

  public move(map: LeafletMap, time: Time) {
    if (this.secondsLeftAtStop > 0) {
      this.secondsLeftAtStop--
    } else if (this.stopIndex == this.stops.length - 1) {
      this.marker.removeFrom(map)
      this.tramRouteLocator = undefined
      this.stopIndex = 0
    } else if (this.stopIndex == 0 && this.stops[this.stopIndex].time.equals(time, this.stopDelay)) {
      this.marker.addTo(map)
      this.secondsLeftAtStop = this.stopDelay
      this.tramRouteLocator = new TramRouteLocator(
        this.stops[0].node_id,
        this.stops[1].node_id,
        this.stops[1].time.seconds - this.stops[0].time.seconds - this.stopDelay,
      )
    } else if (typeof this.tramRouteLocator != "undefined") {
      this.marker.setLatLng(this.tramRouteLocator.getNewTramLocation())

      if (this.tramRouteLocator.arrived) {
        this.stopIndex++
        this.secondsLeftAtStop = this.stopDelay
        this.marker.setLatLng(this.stops[this.stopIndex].position)

        if (this.stopIndex < this.stops.length - 1) {
          this.tramRouteLocator = new TramRouteLocator(
            this.stops[this.stopIndex].node_id,
            this.stops[this.stopIndex + 1].node_id,
            this.stops[this.stopIndex + 1].time.seconds - this.stops[this.stopIndex].time.seconds - this.stopDelay,
          )
        }
      }
    }
  }
}
