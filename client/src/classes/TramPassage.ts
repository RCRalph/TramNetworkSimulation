import { CircleMarker, latLng, LatLng, type Map as LeafletMap } from "leaflet"
import { Time } from "@classes/Time"

export interface PassageStop {
  name: string,
  position: LatLng
  time: Time
}

export class TramPassage {
  private readonly marker: CircleMarker
  private stopIndex = 0

  constructor(
    private readonly tram_line_number: string,
    private readonly passage_id: number,
    private readonly stops: PassageStop[],
  ) {
    if (!this.stops.length) {
      throw new Error("Empty stop array")
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
        time: new Time(item.hour, item.minute),
      })
    }

    return result
  }

  public move(map: LeafletMap, time: Time) {
    if (this.stopIndex == 0 && this.stops[this.stopIndex].time.equals(time)) {
      this.marker.addTo(map)
    } else if (this.stopIndex == this.stops.length - 1) {
      this.marker.removeFrom(map)
      this.stopIndex = 0
    } else if (this.stops[this.stopIndex + 1].time.equals(time)) {
      this.stopIndex++
      this.marker.setLatLng(this.stops[this.stopIndex].position)
    }
  }
}
