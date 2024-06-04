import { CircleMarker, latLng, LatLng, type Map as LeafletMap, Polyline } from "leaflet"
import { Time } from "@classes/Time"
import { TramRouteIndicator } from "@classes/TramRouteIndicator"
import { AdvancementOracle } from "@classes/AdvancementOracle"

export interface PassageStop {
  node_id: number
  name: string
  position: LatLng
  time: Time
}

export class TramPassage {
  public readonly marker: CircleMarker
  private stopIndex = 0
  private secondsLeftAtStop = 0
  private map: LeafletMap | undefined = undefined
  private tramRouteLocator: TramRouteIndicator | undefined = undefined

  constructor(
    public readonly tram_line_number: string,
    public readonly passage_id: number,
    private readonly stops: PassageStop[],
    private readonly stopDelay: number,
    private readonly advancementOracle: AdvancementOracle,
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

    this.marker.addEventListener("click", () => {
      if (this.map) {
        new Polyline(this.futureRoute(30)).addTo(this.map)
      }
    })
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

  private setNewTramRouteIndicator() {
    this.tramRouteLocator = new TramRouteIndicator(
      this.stops[this.stopIndex].node_id,
      this.stops[this.stopIndex + 1].node_id,
      (
        this.stops[this.stopIndex + 1].time.seconds -
        this.stops[this.stopIndex].time.seconds -
        this.stopDelay +
        Time.SECONDS_IN_HOUR
      ) % Time.SECONDS_IN_HOUR,
    )
  }

  private removeFromMap() {
    if (this.map) {
      this.marker.removeFrom(this.map)
    }

    this.advancementOracle.unregisterTram(this)
    this.tramRouteLocator = undefined
    this.stopIndex = 0
  }

  private addToMap() {
    if (this.map) {
      this.marker.addTo(this.map)
    }

    this.advancementOracle.registerTram(this)
    this.secondsLeftAtStop = this.stopDelay
    this.setNewTramRouteIndicator()
  }

  private futureRoute(seconds: number) {
    return this.tramRouteLocator?.getFutureRoute(seconds) ?? []
  }

  public move(time: Time) {
    if (this.secondsLeftAtStop > 0) {
      this.secondsLeftAtStop--
    } else if (this.stopIndex == this.stops.length - 1) {
      this.removeFromMap()
    } else if (this.stopIndex == 0 && this.stops[this.stopIndex].time.equals(time, this.stopDelay)) {
      this.addToMap()
    } else if (this.tramRouteLocator && this.advancementOracle.canAdvance(this, this.futureRoute(15), this.futureRoute(30))) {
      this.marker.setLatLng(this.tramRouteLocator.getNewTramLocation())

      if (this.tramRouteLocator.arrived) {
        this.stopIndex++
        this.secondsLeftAtStop = this.stopDelay
        this.marker.setLatLng(this.stops[this.stopIndex].position)

        if (this.stopIndex < this.stops.length - 1) {
          this.setNewTramRouteIndicator()
        }
      }
    }
  }
}
