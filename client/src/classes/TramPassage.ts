import { CircleMarker, latLng, LatLng, type Map as LeafletMap } from "leaflet"
import { Time } from "@classes/Time"
import { MoveVector } from "@classes/MoveVector"

export interface PassageStop {
  name: string,
  position: LatLng
  time: Time
}

export class TramPassage {
  private readonly marker: CircleMarker
  private readonly moveVector = new MoveVector()
  private stopIndex = 0
  private currentStopDelay = 0
  private onMap = false

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
        name: item.name,
        position: latLng(item.latitude, item.longitude),
        time: new Time(item.hour, item.minute, 0),
      })
    }

    return result
  }

  public move(map: LeafletMap, time: Time) {
    if (this.stopIndex == 0 && this.stops[this.stopIndex].time.equals(time, this.stopDelay)) {
      this.moveVector.setUsingStops(this.stops[this.stopIndex], this.stops[this.stopIndex + 1], this.stopDelay)
      this.currentStopDelay = this.stopDelay
      this.marker.addTo(map)
      this.onMap = true
    } else if (this.stopIndex == this.stops.length - 1) {
      this.marker.removeFrom(map)
      this.stopIndex = 0
      this.onMap = false
    } else if (this.currentStopDelay > 0) {
      this.currentStopDelay--
    } else if (this.onMap) {
      this.marker.setLatLng(this.moveVector.movePosition(this.marker.getLatLng()))

      if (this.stops[this.stopIndex + 1].time.equals(time, this.stopDelay)) {
        this.stopIndex++
        this.currentStopDelay = this.stopDelay
        if (this.stopIndex + 1 < this.stops.length) {
          this.moveVector.setUsingStops(this.stops[this.stopIndex], this.stops[this.stopIndex + 1], this.stopDelay)
        }
      }
    }
  }
}
