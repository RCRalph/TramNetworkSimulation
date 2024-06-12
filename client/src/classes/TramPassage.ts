import { icon, latLng, LatLng, type Map as LeafletMap, Marker } from "leaflet"
import "leaflet-rotatedmarker"
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
  public static readonly MIN_STOP_DELAY = 15
  private static readonly TRAM_ICON = icon({
    iconUrl: "tram-icon.png",
    iconSize: [20, 25],
    iconAnchor: [10, 15],
  })

  public readonly marker: Marker
  private stopIndex = 0
  private secondsLeftAtStop = 0
  private map: LeafletMap | undefined = undefined
  private tramRouteIndicator: TramRouteIndicator | undefined = undefined

  private stopDelay = 0

  constructor(
    public readonly tram_line_number: string,
    public readonly passage_id: number,
    readonly stops: PassageStop[],
    private readonly advancementOracle: AdvancementOracle,
  ) {
    if (this.stops.length < 2) {
      throw new Error("Not enough stops")
    }

    this.updateStopDelay()

    this.marker = new Marker(this.stops[this.stopIndex].position, {
      icon: TramPassage.TRAM_ICON,
    })


    this.marker.bindTooltip(this.tram_line_number, {
      permanent: true,
      direction: "center",
      className: "line-number-label",
    })
  }

  private updateStopDelay() {
    this.stopDelay = Math.round(Math.random() * 10) + 15

    return this.stopDelay
  }

  public setMap(map: LeafletMap) {
    this.map = map
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
    const scheduleTime = this.stops[this.stopIndex + 1].time.seconds - this.stops[this.stopIndex].time.seconds

    this.tramRouteIndicator = new TramRouteIndicator(
      this.stops[this.stopIndex].node_id,
      this.stops[this.stopIndex + 1].node_id,
      (scheduleTime - TramPassage.MIN_STOP_DELAY + Time.SECONDS_IN_DAY) % Time.SECONDS_IN_DAY,
    )
  }

  private removeFromMap() {
    if (this.map) {
      this.marker.removeFrom(this.map)
    }

    this.advancementOracle.unregisterTram(this)
    this.tramRouteIndicator = undefined
    this.stopIndex = 0
  }

  private addToMap() {
    this.advancementOracle.registerTram(this)
    this.secondsLeftAtStop = this.updateStopDelay()
    this.setNewTramRouteIndicator()

    if (this.map) {
      this.marker.setRotationAngle(this.tramRouteIndicator!.getTramRotation())
      this.marker.addTo(this.map)
    }
  }

  public move(time: Time, blockTime: number, checkTime: number) {
    if (this.secondsLeftAtStop > 0) {
      this.secondsLeftAtStop--
    } else if (this.stopIndex == this.stops.length - 1) {
      this.removeFromMap()
    } else if (this.stopIndex == 0 && this.stops[this.stopIndex].time.equals(time, this.stopDelay)) {
      this.addToMap()
    } else if (
      this.tramRouteIndicator && this.advancementOracle.canAdvance(
        this,
        this.tramRouteIndicator?.getFutureRoute(blockTime) ?? [],
        this.tramRouteIndicator?.getFutureRoute(checkTime) ?? [],
      )
    ) {
      this.marker.setRotationAngle(this.tramRouteIndicator.getTramRotation())
      this.marker.setLatLng(this.tramRouteIndicator.getNewTramLocation())

      if (this.tramRouteIndicator.arrived) {
        this.stopIndex++
        this.secondsLeftAtStop = this.updateStopDelay()
        this.marker.setLatLng(this.stops[this.stopIndex].position)

        if (this.stopIndex < this.stops.length - 1) {
          this.setNewTramRouteIndicator()
        }
      }
    }
  }

  public reset() {
    this.removeFromMap()
    this.marker.setLatLng(this.stops[0].position)
    this.advancementOracle.unregisterTram(this)
  }
}
